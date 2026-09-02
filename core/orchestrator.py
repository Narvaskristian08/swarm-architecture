"""Central workflow coordinator for the NORA agent swarm."""

from datetime import datetime
import json
import logging
from pathlib import Path, PurePosixPath
import re
from typing import Any, Dict, List, Optional
import uuid

from .base_agent import AgentMessage, BaseAgent

logger = logging.getLogger(__name__)

SUCCESS_STATUSES = {"success"}
FAILURE_STATUSES = {"error", "failed", "skipped"}
KNOWN_AGENTS = {
    "planner", "research", "coder", "tester", "reviewer",
    "installer", "memory_agent", "reflection",
}


class WorkflowState:
    """Tracks the durable, user-visible state of one workflow."""

    def __init__(self, workflow_id: str, goal: str):
        self.workflow_id = workflow_id
        self.goal = goal
        self.status = "created"
        self.created_at = datetime.now()
        self.completed_at = None
        self.tasks: List[Dict[str, Any]] = []
        self.results: Dict[str, Dict[str, Any]] = {}
        self.agent_assignments: Dict[str, Dict[str, Any]] = {}
        self.current_task = None
        self.files_created: List[str] = []
        self.errors: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "goal": self.goal,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tasks": self.tasks,
            "results": self.results,
            "current_task": self.current_task,
            "files_created": self.files_created,
            "errors": self.errors,
        }


class Orchestrator(BaseAgent):
    """Coordinates planning, task execution, artifacts, memory, and reflection."""

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        tool_manager=None,
        memory_manager=None,
    ):
        super().__init__(
            agent_id="orchestrator",
            name="Orchestrator",
            description="Coordinates agent collaboration and manages workflows",
        )
        self.capabilities = ["coordinate", "route", "workflow_management"]
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.active_workflows: Dict[str, WorkflowState] = {}
        self.message_queue: List[AgentMessage] = []
        self.workspace_root = (workspace_root or Path.cwd()).resolve()
        self.workspace_root.mkdir(parents=True, exist_ok=True)

        if tool_manager is None:
            from tools import ToolManager

            tool_manager = ToolManager(self.workspace_root)
        self.tool_manager = tool_manager
        self.memory_manager = memory_manager

    def register_agent(self, agent: BaseAgent):
        self.registered_agents[agent.agent_id] = agent
        logger.info("Registered agent: %s (%s)", agent.name, agent.agent_id)

    def unregister_agent(self, agent_id: str):
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self.registered_agents.get(agent_id)

    def find_capable_agents(self, task_type: str) -> List[BaseAgent]:
        return [agent for agent in self.registered_agents.values() if agent.can_handle(task_type)]

    def create_workflow(self, goal: str) -> str:
        workflow_id = str(uuid.uuid4())
        self.active_workflows[workflow_id] = WorkflowState(workflow_id, goal.strip())
        self.log_action("workflow_created", {"workflow_id": workflow_id, "goal": goal})
        return workflow_id

    def assign_task_to_agent(self, workflow_id: str, agent_id: str, task: Dict) -> bool:
        agent = self.get_agent(agent_id)
        workflow = self.active_workflows.get(workflow_id)
        if not agent or not workflow:
            return False
        message = self.send_message(
            receiver=agent_id,
            content=str(task),
            message_type="task",
            metadata={"workflow_id": workflow_id, "task": task},
        )
        self.route_message(message)
        workflow.agent_assignments[task.get("id", agent_id)] = {
            "agent": agent_id,
            "task": task,
        }
        return True

    def route_message(self, message: AgentMessage):
        receiver = self.get_agent(message.receiver)
        if receiver:
            receiver.receive_message(message)
        else:
            self.message_queue.append(message)

    def process_agent_outputs(self):
        for agent in self.registered_agents.values():
            for message in agent.get_outgoing_messages():
                self.route_message(message)

    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {"status": "error", "message": "Workflow not found"}
        if not workflow.goal:
            return self._finish_early(workflow, "failed", "A non-empty goal is required")

        llm_health = self._llm_health()
        if not llm_health.get("ready"):
            return self._finish_early(
                workflow,
                "blocked",
                llm_health.get("message", "The configured model is not ready"),
                error_code="model_not_ready",
            )

        session_started = False
        try:
            if self.memory_manager:
                self.memory_manager.start_session(
                    workflow.goal, {"workflow_id": workflow.workflow_id}
                )
                session_started = True

            workflow.status = "planning"
            self.state.update("working", f"Planning workflow: {workflow.goal}")
            planner = self.get_agent("planner")
            if not planner:
                raise RuntimeError("Planner agent is not registered")

            plan_result = planner.process({"type": "create_plan", "goal": workflow.goal})
            if plan_result.get("status") != "success":
                raise RuntimeError(
                    plan_result.get("message", "Planner did not return a valid plan")
                )

            plan = plan_result.get("plan", {})
            workflow.tasks = self._normalize_tasks(plan.get("tasks", []))
            ordered_tasks = self._resolve_task_order(workflow.tasks)
            workflow.status = "executing"

            for task in ordered_tasks:
                self._execute_task(workflow, task, plan)

            failed = [
                task_id for task_id, result in workflow.results.items()
                if result.get("status") in FAILURE_STATUSES
            ]
            blocked = [
                task_id for task_id, result in workflow.results.items()
                if result.get("status") in {"blocked", "awaiting_confirmation"}
            ]
            succeeded = [
                task_id for task_id, result in workflow.results.items()
                if result.get("status") in SUCCESS_STATUSES
            ]

            if blocked and not succeeded and not failed:
                workflow.status = "blocked"
                message = f"Workflow blocked on {len(blocked)} task(s)"
            elif failed or blocked:
                workflow.status = "completed_with_errors"
                message = (
                    f"Workflow completed with {len(failed)} failed and "
                    f"{len(blocked)} blocked task(s)"
                )
            else:
                workflow.status = "completed"
                message = "Workflow completed successfully"

            workflow.completed_at = datetime.now()
            self._run_completion_hooks(workflow, message)
            self.state.update("done", message)
            return {
                "workflow_id": workflow.workflow_id,
                "status": workflow.status,
                "message": message,
                "tasks_completed": len(succeeded),
                "tasks_failed": len(failed),
                "tasks_blocked": len(blocked),
                "files_created": workflow.files_created,
                "workspace": str(self.workspace_root),
                "plan": plan,
                "results": workflow.results,
            }
        except Exception as exc:
            logger.exception("Workflow execution failed")
            workflow.errors.append(str(exc))
            return self._finish_early(
                workflow, "failed", f"Workflow execution failed: {exc}"
            )
        finally:
            if session_started and self.memory_manager:
                try:
                    self.memory_manager.end_session(
                        f"{workflow.status}: {len(workflow.files_created)} files created"
                    )
                except Exception:
                    logger.exception("Could not close workflow memory session")

    def _execute_task(
        self, workflow: WorkflowState, task: Dict[str, Any], plan: Dict[str, Any]
    ) -> None:
        task_id = task["id"]
        dependencies = task.get("dependencies", [])
        bad_dependencies = [
            dep for dep in dependencies
            if workflow.results.get(dep, {}).get("status") not in SUCCESS_STATUSES
        ]
        if bad_dependencies:
            workflow.results[task_id] = {
                "status": "skipped",
                "message": "Dependency did not complete successfully",
                "dependencies": bad_dependencies,
            }
            return

        agent = self._select_agent_for_task(task)
        if not agent:
            workflow.results[task_id] = {
                "status": "failed",
                "error": f"Agent '{task.get('agent')}' is not registered",
            }
            return

        workflow.current_task = task_id
        workflow.agent_assignments[task_id] = {"agent": agent.agent_id, "task": task}
        self.state.update("working", f"Task: {task['description'][:80]}")
        context = self._build_task_context(task, workflow.results)
        task_input = self._build_agent_input(
            agent.agent_id, task, workflow.goal, context, plan, workflow.results
        )

        try:
            result = agent.process(task_input)
            if not isinstance(result, dict):
                raise TypeError("Agent result must be a dictionary")

            if agent.agent_id == "tester" and result.get("test_code"):
                result["code_blocks"] = result["test_code"]

            status = result.get("status", "error")
            result["status"] = "failed" if status == "partial" else status

            if result["status"] == "success" and result.get("code_blocks"):
                saved = self._save_code_to_files(
                    result, workflow.goal, task["description"], task_id
                )
                result["files_created"] = saved
                workflow.files_created.extend(saved)
                if not saved:
                    result["status"] = "failed"
                    result["error"] = "Agent produced code, but no files could be saved"

            workflow.results[task_id] = result
        except Exception as exc:
            logger.error("Task %s failed: %s", task_id, exc)
            workflow.results[task_id] = {"status": "failed", "error": str(exc)}

    def _normalize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not isinstance(tasks, list) or not tasks:
            raise ValueError("Planner returned an empty or invalid task list")

        normalized = []
        seen = set()
        for index, raw in enumerate(tasks, 1):
            if not isinstance(raw, dict) or not str(raw.get("description", "")).strip():
                raise ValueError(f"Task {index} has no description")
            task_id = str(raw.get("id") or f"task_{index}").strip()
            if task_id in seen:
                raise ValueError(f"Duplicate task id: {task_id}")
            seen.add(task_id)
            dependencies = raw.get("dependencies") or []
            if not isinstance(dependencies, list):
                raise ValueError(f"Dependencies for {task_id} must be a list")
            normalized.append({
                **raw,
                "id": task_id,
                "description": str(raw["description"]).strip(),
                "dependencies": [str(dep) for dep in dependencies],
                "agent": str(raw.get("agent", "")).strip().lower(),
                "language": str(raw.get("language", "python")).strip().lower(),
            })

        for task in normalized:
            unknown = [dep for dep in task["dependencies"] if dep not in seen]
            if unknown:
                raise ValueError(f"Task {task['id']} has unknown dependencies: {unknown}")
            if task["id"] in task["dependencies"]:
                raise ValueError(f"Task {task['id']} depends on itself")
        return normalized

    def _resolve_task_order(self, tasks: List[Dict]) -> List[Dict]:
        if not tasks:
            return []
        task_map = {task["id"]: task for task in tasks}
        if len(task_map) != len(tasks):
            raise ValueError("Task IDs must be unique")
        in_degree = {task_id: 0 for task_id in task_map}
        for task in tasks:
            for dependency in task.get("dependencies", []):
                if dependency not in task_map:
                    raise ValueError(
                        f"Task {task['id']} depends on unknown task {dependency}"
                    )
                in_degree[task["id"]] += 1

        queue = sorted(task_id for task_id, degree in in_degree.items() if degree == 0)
        ordered = []
        while queue:
            task_id = queue.pop(0)
            ordered.append(task_map[task_id])
            for task in tasks:
                if task_id in task.get("dependencies", []):
                    in_degree[task["id"]] -= 1
                    if in_degree[task["id"]] == 0:
                        queue.append(task["id"])
                        queue.sort()
        if len(ordered) != len(tasks):
            raise ValueError("Plan contains circular task dependencies")
        return ordered

    def _select_agent_for_task(self, task: Dict) -> Optional[BaseAgent]:
        suggested = str(task.get("agent", "")).lower()
        if suggested in KNOWN_AGENTS and self.get_agent(suggested):
            return self.get_agent(suggested)

        description = str(task.get("description", "")).lower()
        mappings = [
            (("research", "investigate", "find", "search", "learn"), "research"),
            (("test", "verify", "validate", "check"), "tester"),
            (("review", "evaluate", "assess", "audit"), "reviewer"),
            (("install", "dependency", "package", "setup"), "installer"),
            (("remember", "store knowledge", "memory"), "memory_agent"),
            (("reflect", "lessons learned"), "reflection"),
            (("plan", "architecture", "breakdown"), "planner"),
        ]
        for words, agent_id in mappings:
            if any(word in description for word in words):
                return self.get_agent(agent_id)
        return self.get_agent("coder")

    def _build_task_context(self, task: Dict, results: Dict[str, Any]) -> str:
        parts = []
        for dependency in task.get("dependencies", []):
            result = results.get(dependency, {})
            parts.append(f"Results from {dependency} (status={result.get('status', 'unknown')}):")
            for block in result.get("code_blocks", [])[:8]:
                path = block.get("path") or "unspecified file"
                code = block.get("code", "")[:6000]
                parts.append(f"FILE: {path}\n```{block.get('language', '')}\n{code}\n```")
            for key in ("summary", "findings", "review", "analysis", "message"):
                value = result.get(key)
                if value:
                    text = json.dumps(value, default=str) if not isinstance(value, str) else value
                    parts.append(f"{key}: {text[:4000]}")
            if result.get("error"):
                parts.append(f"error: {result['error']}")
        return "\n\n".join(parts)[:24000]

    def _dependency_code(self, task: Dict, results: Dict[str, Any]) -> str:
        blocks = []
        for dependency in task.get("dependencies", []):
            for block in results.get(dependency, {}).get("code_blocks", []):
                blocks.append(block.get("code", ""))
        return "\n\n".join(blocks)[:24000]

    def _build_agent_input(
        self,
        agent_id: str,
        task: Dict[str, Any],
        goal: str,
        context: str,
        plan: Dict[str, Any],
        results: Dict[str, Any],
    ) -> Dict[str, Any]:
        description = task["description"]
        language = task.get("language", "python")
        code = self._dependency_code(task, results)

        if agent_id == "research":
            return {"type": "research_topic", "topic": description, "context": context}
        if agent_id == "tester":
            if code:
                return {
                    "type": "generate_test_code",
                    "code": code,
                    "language": language,
                    "test_framework": task.get("test_framework", "pytest"),
                    "specification": description,
                }
            return {"type": "design_tests", "specification": description, "language": language}
        if agent_id == "reviewer":
            return {
                "type": "review_code",
                "code": code or context,
                "language": language,
                "context": f"Goal: {goal}\n{description}",
            }
        if agent_id == "planner":
            return {"type": "create_plan", "goal": description, "context": context}
        if agent_id == "installer":
            return {
                "type": "suggest_framework",
                "purpose": description,
                "language": language,
                "context": context,
                "auto_install": False,
            }
        if agent_id == "memory_agent":
            return {
                "type": "store", "category": "workflow", "title": description,
                "content": context or description,
            }
        if agent_id == "reflection":
            return {
                "type": "analyze_workflow", "goal": goal,
                "outcome": description, "workflow_data": plan,
            }
        return {
            "type": "implement_feature",
            "specification": description,
            "requirements": task.get("requirements") or task.get("deliverables", ""),
            "language": language,
            "context": f"Overall goal: {goal}\n\n{context}".strip(),
        }

    def _save_code_to_files(
        self,
        agent_result: Dict[str, Any],
        goal: str,
        task_desc: str,
        task_id: str = "task",
    ) -> List[str]:
        saved = []
        for index, block in enumerate(agent_result.get("code_blocks", [])):
            code = block.get("code", "")
            if not code.strip():
                continue
            filename = block.get("path") or self._infer_filename(
                goal, task_desc, block.get("language", "python"), index
            )
            filename = self._safe_artifact_path(filename)
            filename = self._unique_filename(filename, task_id, saved)
            result = self.tool_manager.write_file(filename, code)
            if result.get("status") == "success":
                saved.append(filename)
            else:
                logger.error("Could not save %s: %s", filename, result.get("error"))
        return saved

    def _safe_artifact_path(self, filename: str) -> str:
        candidate = PurePosixPath(str(filename).replace("\\", "/").strip())
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"Unsafe generated file path: {filename}")
        cleaned = PurePosixPath(*(part for part in candidate.parts if part not in {"", "."}))
        if not cleaned.parts:
            raise ValueError("Generated file path is empty")
        return str(cleaned)

    def _unique_filename(self, filename: str, task_id: str, current: List[str]) -> str:
        path = Path(filename)
        if filename not in current and not (self.workspace_root / path).exists():
            return filename
        suffix = re.sub(r"[^a-zA-Z0-9_-]", "_", task_id)
        candidate = path.with_name(f"{path.stem}_{suffix}{path.suffix}")
        counter = 2
        while str(candidate) in current or (self.workspace_root / candidate).exists():
            candidate = path.with_name(f"{path.stem}_{suffix}_{counter}{path.suffix}")
            counter += 1
        return str(candidate)

    def _infer_filename(
        self, goal: str, task_desc: str, language: str, index: int
    ) -> str:
        goal_lower = goal.lower()
        if "calculator" in goal_lower:
            project_name = "calculator"
        elif "todo" in goal_lower:
            project_name = "todo"
        elif "budget" in goal_lower:
            project_name = "budget"
        elif "api" in goal_lower or "rest" in goal_lower:
            project_name = "api"
        else:
            words = re.findall(r"\b[a-z0-9]+\b", goal_lower)
            project_name = (
                words[1] if len(words) > 1 and words[0] in {"create", "build", "make"}
                else words[0] if words else "project"
            )
        extension = {
            "python": ".py", "javascript": ".js", "typescript": ".ts",
            "java": ".java", "cpp": ".cpp", "c": ".c", "go": ".go",
            "rust": ".rs", "markdown": ".md",
        }.get(language.lower(), ".txt")
        lowered = task_desc.lower()
        if "test" in lowered:
            return f"{project_name}/tests/test_{project_name}{extension}"
        if "readme" in lowered or "document" in lowered:
            return f"{project_name}/README.md"
        if "main" in lowered or index == 0:
            return f"{project_name}/main{extension}"
        return f"{project_name}/{project_name}_{index}{extension}"

    def _run_completion_hooks(self, workflow: WorkflowState, message: str) -> None:
        if self.memory_manager:
            try:
                self.memory_manager.store_knowledge(
                    category="workflow",
                    title=workflow.goal[:120],
                    content=json.dumps(workflow.to_dict(), default=str)[:20000],
                    source="orchestrator",
                    tags=[workflow.status],
                    enable_semantic_search=False,
                )
            except Exception:
                logger.exception("Could not persist workflow knowledge")

        reflection = self.get_agent("reflection")
        if reflection:
            try:
                workflow.results["_reflection"] = reflection.process({
                    "type": "analyze_workflow", "goal": workflow.goal, "outcome": message,
                    "workflow_data": {
                        "tasks": workflow.tasks,
                        "agents": sorted({item["agent"] for item in workflow.agent_assignments.values()}),
                        "duration": (workflow.completed_at - workflow.created_at).total_seconds(),
                    },
                })
            except Exception as exc:
                workflow.results["_reflection"] = {"status": "failed", "error": str(exc)}

    def _llm_health(self) -> Dict[str, Any]:
        if not self.llm_client:
            return {"provider": None, "ready": False, "message": "No LLM client is configured"}
        health = getattr(self.llm_client, "health", None)
        if callable(health):
            return health()
        return {
            "provider": getattr(self.llm_client, "provider", "custom"),
            "ready": True,
            "model": getattr(self.llm_client, "model_identifier", "custom"),
            "message": "Custom LLM client is ready",
        }

    def _finish_early(
        self,
        workflow: WorkflowState,
        status: str,
        message: str,
        error_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        workflow.status = status
        workflow.completed_at = datetime.now()
        if status == "failed":
            workflow.errors.append(message)
            self.state.update("error", message)
        else:
            self.state.update("waiting", message)
        result = {
            "workflow_id": workflow.workflow_id, "status": status, "message": message,
            "files_created": workflow.files_created, "workspace": str(self.workspace_root),
            "results": workflow.results,
        }
        if error_code:
            result["error_code"] = error_code
        return result

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "unknown")
        if task_type == "create_workflow":
            workflow_id = self.create_workflow(task.get("goal", ""))
            return {"status": "success", "workflow_id": workflow_id}
        if task_type == "execute_workflow":
            return self.execute_workflow(task.get("workflow_id"))
        if task_type == "status":
            return self.get_system_status()
        return {"status": "error", "message": f"Unknown task type: {task_type}"}

    def get_system_status(self) -> Dict[str, Any]:
        return {
            "orchestrator_status": self.get_status(),
            "llm": self._llm_health(),
            "workspace": str(self.workspace_root),
            "registered_agents": {
                agent_id: agent.get_status() for agent_id, agent in self.registered_agents.items()
            },
            "active_workflows": len(self.active_workflows),
            "queued_messages": len(self.message_queue),
        }

    def shutdown(self):
        for agent in self.registered_agents.values():
            agent.reset()
        self.active_workflows.clear()
        self.message_queue.clear()
