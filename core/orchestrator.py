"""
Orchestrator Agent
Coordinates all agents, manages workflow, and routes messages.
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
from .base_agent import BaseAgent, AgentMessage
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowState:
    """Tracks the state of a workflow"""
    
    def __init__(self, workflow_id: str, goal: str):
        self.workflow_id = workflow_id
        self.goal = goal
        self.status = "created"  # created, planning, executing, testing, reviewing, completed, failed, completed_with_errors
        self.created_at = datetime.now()
        self.completed_at = None
        self.tasks = []
        self.results = {}
        self.agent_assignments = {}
        self.current_task = None
        self.files_created = []
        self.errors = []
    
    def to_dict(self) -> Dict:
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
            "errors": self.errors
        }


class Orchestrator(BaseAgent):
    """
    Central coordinator for the AI swarm.
    Receives user goals, coordinates agents, and manages workflow execution.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        super().__init__(
            agent_id="orchestrator",
            name="Orchestrator",
            description="Coordinates agent collaboration and manages workflows"
        )
        self.capabilities = ["coordinate", "route", "workflow_management"]
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.active_workflows: Dict[str, WorkflowState] = {}
        self.message_queue: List[AgentMessage] = []
        self.workspace_root = workspace_root or Path.cwd()
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.registered_agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get a registered agent by ID"""
        return self.registered_agents.get(agent_id)
    
    def find_capable_agents(self, task_type: str) -> List[BaseAgent]:
        """Find all agents capable of handling a task type"""
        return [
            agent for agent in self.registered_agents.values()
            if agent.can_handle(task_type)
        ]
    
    def create_workflow(self, goal: str) -> str:
        """Create a new workflow for a user goal"""
        import uuid
        workflow_id = str(uuid.uuid4())
        workflow = WorkflowState(workflow_id, goal)
        self.active_workflows[workflow_id] = workflow
        
        logger.info(f"Created workflow {workflow_id}: {goal}")
        self.log_action("workflow_created", {"workflow_id": workflow_id, "goal": goal})
        
        return workflow_id
    
    def assign_task_to_agent(self, workflow_id: str, agent_id: str, task: Dict) -> bool:
        """Assign a task to a specific agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return False
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            return False
        
        # Send task message to agent
        message = self.send_message(
            receiver=agent_id,
            content=str(task),
            message_type="task",
            metadata={"workflow_id": workflow_id, "task": task}
        )
        
        # Route the message
        self.route_message(message)
        
        # Track assignment
        workflow.agent_assignments[agent_id] = task
        logger.info(f"Assigned task to {agent.name}: {task.get('description', 'No description')}")
        
        return True
    
    def route_message(self, message: AgentMessage):
        """Route a message to the appropriate agent"""
        receiver = self.get_agent(message.receiver)
        if receiver:
            receiver.receive_message(message)
            logger.debug(f"Routed message from {message.sender} to {message.receiver}")
        else:
            logger.warning(f"Cannot route message: receiver {message.receiver} not found")
            self.message_queue.append(message)  # Queue for later
    
    def process_agent_outputs(self):
        """Collect and route messages from all agents"""
        for agent in self.registered_agents.values():
            outgoing = agent.get_outgoing_messages()
            for message in outgoing:
                self.route_message(message)
    
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow by coordinating agents.
        
        Flow:
        1. Get workflow and goal
        2. Send to Planner to create task plan
        3. Resolve task dependencies (topological sort)
        4. Execute tasks sequentially
        5. Pass context between dependent tasks
        6. Save code to files
        7. Track results and errors
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {"status": "error", "message": "Workflow not found"}
        
        workflow.status = "planning"
        self.state.update("working", f"Planning workflow: {workflow.goal}")
        logger.info(f"Starting workflow execution: {workflow.goal}")
        
        try:
            # Step 1: Get plan from Planner
            planner = self.get_agent("planner")
            if not planner:
                raise Exception("Planner agent not found. Ensure planner is registered.")
            
            logger.info("Requesting plan from Planner...")
            plan_result = planner.process({
                "type": "create_plan",
                "goal": workflow.goal
            })
            
            if plan_result.get("status") != "success":
                raise Exception(f"Planning failed: {plan_result.get('message', 'Unknown error')}")
            
            plan = plan_result.get("plan", {})
            workflow.tasks = plan.get("tasks", [])
            
            if not workflow.tasks:
                raise Exception("Planner returned empty task list")
            
            logger.info(f"Plan created with {len(workflow.tasks)} tasks")
            
            # Step 2: Execute tasks in dependency order
            workflow.status = "executing"
            self.state.update("working", "Executing tasks...")
            
            ordered_tasks = self._resolve_task_order(workflow.tasks)
            logger.info(f"Task execution order: {[t['id'] for t in ordered_tasks]}")
            
            files_created = []
            
            for task in ordered_tasks:
                task_id = task.get("id", "unknown")
                task_desc = task.get("description", "No description")
                
                logger.info(f"Executing task: {task_id} - {task_desc[:50]}")
                self.state.update("working", f"Task: {task_desc[:50]}...")
                
                # Step 3: Select agent for task
                agent = self._select_agent_for_task(task)
                if not agent:
                    logger.warning(f"No agent found for task {task_id}, skipping")
                    workflow.results[task_id] = {
                        "status": "skipped",
                        "message": "No capable agent found"
                    }
                    continue
                
                # Step 4: Prepare task context from dependencies
                task_context = self._build_task_context(task, workflow.results)
                
                # Step 5: Execute task
                try:
                    task_input = {
                        "type": self._map_task_to_operation(task),
                        "specification": task_desc,
                        "context": task_context,
                        "language": "python"  # Default, could be inferred from goal
                    }
                    
                    result = agent.process(task_input)
                    workflow.results[task_id] = result
                    
                    # Step 6: Save code to files if Coder returned code
                    if result.get("status") == "success" and "code_blocks" in result:
                        saved_files = self._save_code_to_files(result, workflow.goal, task_desc)
                        files_created.extend(saved_files)
                        result["files_created"] = saved_files
                    
                    logger.info(f"Task {task_id} completed: {result.get('status')}")
                    
                except Exception as e:
                    logger.error(f"Task {task_id} failed: {e}")
                    workflow.results[task_id] = {
                        "status": "failed",
                        "error": str(e)
                    }
            
            # Step 7: Determine overall workflow status
            failed_tasks = [
                tid for tid, res in workflow.results.items()
                if res.get("status") == "failed"
            ]
            
            if failed_tasks:
                workflow.status = "completed_with_errors"
                message = f"Workflow completed with {len(failed_tasks)} failed tasks"
            else:
                workflow.status = "completed"
                message = "Workflow completed successfully"
            
            workflow.completed_at = datetime.now()
            self.state.update("done", message)
            
            return {
                "workflow_id": workflow_id,
                "status": workflow.status,
                "message": message,
                "tasks_completed": len(workflow.results),
                "tasks_failed": len(failed_tasks),
                "files_created": files_created,
                "plan": plan,
                "results": workflow.results
            }
            
        except Exception as e:
            workflow.status = "failed"
            workflow.completed_at = datetime.now()
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(error_msg)
            self.state.update("error", error_msg)
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "message": error_msg,
                "error": str(e)
            }
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process orchestrator-level tasks"""
        task_type = task.get("type", "unknown")
        
        if task_type == "create_workflow":
            goal = task.get("goal", "")
            workflow_id = self.create_workflow(goal)
            return {"status": "success", "workflow_id": workflow_id}
        
        elif task_type == "execute_workflow":
            workflow_id = task.get("workflow_id")
            return self.execute_workflow(workflow_id)
        
        elif task_type == "status":
            return self.get_system_status()
        
        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}
    
    def get_system_status(self) -> Dict:
        """Get status of entire swarm system"""
        return {
            "orchestrator_status": self.get_status(),
            "registered_agents": {
                agent_id: agent.get_status()
                for agent_id, agent in self.registered_agents.items()
            },
            "active_workflows": len(self.active_workflows),
            "queued_messages": len(self.message_queue)
        }
    
    def _resolve_task_order(self, tasks: List[Dict]) -> List[Dict]:
        """
        Resolve task execution order using topological sort.
        Handles dependencies to ensure tasks execute in correct order.
        """
        if not tasks:
            return []
        
        # Build dependency graph
        task_map = {task["id"]: task for task in tasks}
        in_degree = {task["id"]: 0 for task in tasks}
        
        # Calculate in-degrees (count how many tasks depend on each task)
        for task in tasks:
            for dep_id in task.get("dependencies", []):
                if dep_id in in_degree:
                    in_degree[task["id"]] += 1  # This task depends on dep_id
        
        # Find tasks with no dependencies (in-degree == 0)
        queue = [tid for tid, degree in in_degree.items() if degree == 0]
        ordered = []
        
        while queue:
            # Sort queue for deterministic ordering
            queue.sort()
            task_id = queue.pop(0)
            ordered.append(task_map[task_id])
            
            # Find tasks that depended on this one
            for other_task in tasks:
                if task_id in other_task.get("dependencies", []):
                    in_degree[other_task["id"]] -= 1
                    if in_degree[other_task["id"]] == 0:
                        queue.append(other_task["id"])
        
        # Check for circular dependencies
        if len(ordered) != len(tasks):
            logger.warning("Circular dependencies detected, returning partial order")
            # Add remaining tasks
            remaining = [t for t in tasks if t not in ordered]
            ordered.extend(remaining)
        
        return ordered
    
    def _select_agent_for_task(self, task: Dict) -> Optional[BaseAgent]:
        """
        Select the best agent for a task based on capabilities.
        Uses task's suggested agent field and agent capabilities.
        """
        suggested_agent = task.get("agent", "").lower()
        
        # Try suggested agent first
        if suggested_agent:
            agent = self.get_agent(suggested_agent)
            if agent:
                logger.debug(f"Using suggested agent: {agent.name}")
                return agent
        
        # Map task descriptions to agent capabilities
        task_desc = task.get("description", "").lower()
        
        if any(word in task_desc for word in ["plan", "design", "architecture", "breakdown"]):
            return self.get_agent("planner")
        elif any(word in task_desc for word in ["research", "investigate", "find", "search", "learn"]):
            return self.get_agent("research")
        elif any(word in task_desc for word in ["test", "verify", "validate", "check"]):
            return self.get_agent("tester")
        elif any(word in task_desc for word in ["review", "evaluate", "assess", "audit"]):
            return self.get_agent("reviewer")
        elif any(word in task_desc for word in ["install", "dependency", "package", "setup"]):
            return self.get_agent("installer")
        elif any(word in task_desc for word in ["code", "implement", "create", "build", "write", "develop"]):
            return self.get_agent("coder")
        
        # Default to coder for general tasks
        return self.get_agent("coder")
    
    def _build_task_context(self, task: Dict, results: Dict[str, Any]) -> str:
        """
        Build context for a task from its dependencies' results.
        Only includes relevant information from dependent tasks.
        """
        dependencies = task.get("dependencies", [])
        if not dependencies:
            return ""
        
        context_parts = []
        for dep_id in dependencies:
            if dep_id in results:
                dep_result = results[dep_id]
                context_parts.append(f"Results from {dep_id}:")
                
                # Include relevant parts of dependency result
                if dep_result.get("status") == "success":
                    # For code generation, include generated code
                    if "code_blocks" in dep_result:
                        for block in dep_result["code_blocks"][:2]:  # Limit to 2 blocks
                            code_preview = block.get("code", "")[:500]  # First 500 chars
                            context_parts.append(f"```{block.get('language', '')}\n{code_preview}\n```")
                    
                    # For planning, include summary
                    if "plan" in dep_result:
                        plan = dep_result["plan"]
                        context_parts.append(f"Plan summary: {plan.get('summary', '')}")
                else:
                    context_parts.append(f"Status: {dep_result.get('status', 'unknown')}")
                    if "error" in dep_result:
                        context_parts.append(f"Error: {dep_result.get('error', 'Unknown error')}")
        
        return "\n\n".join(context_parts)
    
    def _map_task_to_operation(self, task: Dict) -> str:
        """
        Map a task to a specific operation type for the agent.
        """
        task_desc = task.get("description", "").lower()
        agent_type = task.get("agent", "").lower()
        
        # Coder operations
        if agent_type == "coder":
            if "fix" in task_desc or "bug" in task_desc:
                return "fix_bug"
            elif "modify" in task_desc or "update" in task_desc:
                return "modify_code"
            elif "document" in task_desc:
                return "add_documentation"
            else:
                return "implement_feature"
        
        # Planner operations
        elif agent_type == "planner":
            return "create_plan"
        
        # Research operations
        elif agent_type == "research":
            return "research_topic"
        
        # Tester operations
        elif agent_type == "tester":
            return "create_tests"
        
        # Reviewer operations
        elif agent_type == "reviewer":
            return "review_code"
        
        # Default
        return "implement_feature"
    
    def _save_code_to_files(
        self,
        agent_result: Dict[str, Any],
        goal: str,
        task_desc: str
    ) -> List[str]:
        """
        Save code blocks from agent result to actual files.
        Infers file names from goal and task description.
        """
        from tools import get_tool_manager
        
        code_blocks = agent_result.get("code_blocks", [])
        if not code_blocks:
            return []
        
        tool_manager = get_tool_manager(self.workspace_root if hasattr(self, 'workspace_root') else None)
        saved_files = []
        
        for i, block in enumerate(code_blocks):
            code = block.get("code", "")
            language = block.get("language", "python")
            
            # Infer filename from context
            filename = self._infer_filename(goal, task_desc, language, i)
            
            try:
                result = tool_manager.write_file(filename, code)
                
                if result.get("status") == "success":
                    saved_files.append(filename)
                    logger.info(f"Saved code to: {filename}")
                else:
                    logger.error(f"Failed to save {filename}: {result.get('error')}")
            
            except Exception as e:
                logger.error(f"Error saving file {filename}: {e}")
        
        return saved_files
    
    def _infer_filename(
        self,
        goal: str,
        task_desc: str,
        language: str,
        index: int
    ) -> str:
        """
        Infer an appropriate filename from context.
        Creates project structure based on goal.
        """
        import re
        
        # Extract project name from goal
        goal_lower = goal.lower()
        
        # Common patterns
        if "calculator" in goal_lower:
            project_name = "calculator"
        elif "todo" in goal_lower:
            project_name = "todo"
        elif "budget" in goal_lower:
            project_name = "budget"
        elif "api" in goal_lower or "rest" in goal_lower:
            project_name = "api"
        else:
            # Extract first significant word
            words = re.findall(r'\b[a-z]+\b', goal_lower)
            project_name = words[1] if len(words) > 1 and words[0] in ["create", "build", "make"] else words[0] if words else "project"
        
        # Determine file extension
        ext_map = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java",
            "cpp": ".cpp",
            "c": ".c",
            "go": ".go",
            "rust": ".rs"
        }
        ext = ext_map.get(language, ".txt")
        
        # Determine file type from task description
        task_lower = task_desc.lower()
        
        if "test" in task_lower:
            return f"{project_name}/tests/test_{project_name}{ext}"
        elif "main" in task_lower or index == 0:
            return f"{project_name}/main{ext}"
        elif "readme" in task_lower:
            return f"{project_name}/README.md"
        else:
            return f"{project_name}/{project_name}_{index}{ext}"
    
    def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        logger.info("Shutting down orchestrator...")
        for agent in self.registered_agents.values():
            agent.reset()
        self.active_workflows.clear()
        self.message_queue.clear()
        logger.info("Orchestrator shutdown complete")