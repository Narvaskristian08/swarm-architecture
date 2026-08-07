"""
Planner Agent
Converts high-level goals into concrete, actionable task plans.
"""
import json
from typing import Dict, Any, List, Optional
import logging

from core import BaseAgent, PromptTemplate, ResponseParser

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """
    Planner Agent - Breaks down goals into structured execution plans.
    
    Responsibilities:
    1. Analyze user goals and requirements
    2. Break goals into specific, measurable tasks
    3. Identify task dependencies
    4. Determine required tools and resources
    5. Create step-by-step execution plans
    """
    
    def __init__(self):
        super().__init__(
            agent_id="planner",
            name="Planner",
            description="Breaks down goals into concrete execution plans"
        )
        self.capabilities = ["planning", "task_decomposition", "dependency_analysis"]
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a planning request.
        
        Args:
            task: Dictionary containing:
                - goal: The high-level goal to plan for
                - context: Optional context information
                - constraints: Optional constraints
                
        Returns:
            Dictionary containing the execution plan
        """
        task_type = task.get("type", "create_plan")
        
        if task_type == "create_plan":
            return self._create_plan(task)
        elif task_type == "refine_plan":
            return self._refine_plan(task)
        elif task_type == "validate_plan":
            return self._validate_plan(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
    
    def _create_plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed execution plan from a goal"""
        goal = task.get("goal", "")
        context = task.get("context", "")
        constraints = task.get("constraints", "")
        
        if not goal:
            return {"status": "error", "message": "No goal provided"}
        
        self.state.update("thinking", f"Planning for: {goal[:50]}...")
        logger.info(f"Creating plan for goal: {goal}")
        
        # Build prompt
        prompt = self._build_planning_prompt(goal, context, constraints)
        
        # Query LLM
        system_prompt = PromptTemplate.get_system_prompt("planner")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.7)
        
        # Parse response
        plan = ResponseParser.extract_json(response)
        
        if not plan:
            # Fallback: Try to extract as structured text
            plan = self._extract_plan_from_text(response)
        
        # Validate plan structure
        if ResponseParser.validate_plan(plan):
            self.state.update("done", "Plan created successfully")
            return {
                "status": "success",
                "plan": plan,
                "raw_response": response
            }
        else:
            self.state.update("done", "Plan created but validation failed")
            return {
                "status": "partial_success",
                "plan": plan,
                "raw_response": response,
                "message": "Plan structure may be incomplete"
            }
    
    def _refine_plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Refine an existing plan based on feedback"""
        original_plan = task.get("plan", {})
        feedback = task.get("feedback", "")
        
        if not original_plan or not feedback:
            return {
                "status": "error",
                "message": "Original plan and feedback required"
            }
        
        self.state.update("thinking", "Refining plan...")
        
        prompt = f"""Original Plan:
{json.dumps(original_plan, indent=2)}

Feedback:
{feedback}

Please provide a refined plan that addresses the feedback while maintaining the same JSON structure."""
        
        system_prompt = PromptTemplate.get_system_prompt("planner")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.7)
        
        refined_plan = ResponseParser.extract_json(response)
        
        if refined_plan:
            self.state.update("done", "Plan refined")
            return {
                "status": "success",
                "plan": refined_plan,
                "raw_response": response
            }
        else:
            return {
                "status": "error",
                "message": "Failed to refine plan",
                "raw_response": response
            }
    
    def _validate_plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a plan for completeness and feasibility"""
        plan = task.get("plan", {})
        
        if not plan:
            return {"status": "error", "message": "No plan provided"}
        
        self.state.update("thinking", "Validating plan...")
        
        issues = []
        
        # Check structure
        if not ResponseParser.validate_plan(plan):
            issues.append("Plan structure is invalid")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(plan):
            issues.append("Plan contains circular task dependencies")
        
        # Check task descriptions
        tasks = plan.get("tasks", [])
        for i, task in enumerate(tasks):
            if not task.get("description"):
                issues.append(f"Task {i+1} missing description")
        
        self.state.update("done", "Validation complete")
        
        return {
            "status": "success",
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def _build_planning_prompt(
        self,
        goal: str,
        context: str = "",
        constraints: str = ""
    ) -> str:
        """Build a detailed planning prompt"""
        prompt_parts = [f"Goal: {goal}"]
        
        if context:
            prompt_parts.append(f"\nContext: {context}")
        
        if constraints:
            prompt_parts.append(f"\nConstraints: {constraints}")
        
        prompt_parts.append("""
Please create a detailed execution plan with the following JSON structure:

{
  "goal": "Restate the goal clearly",
  "summary": "Brief overview of the approach",
  "tasks": [
    {
      "id": "task_1",
      "description": "Clear, actionable task description",
      "dependencies": ["task_ids this depends on"],
      "agent": "suggested agent type (planner/research/coder/tester/reviewer)",
      "estimated_complexity": "low/medium/high",
      "tools_needed": ["list of tools"],
      "deliverables": ["expected outputs"]
    }
  ],
  "resources": ["required resources or knowledge"],
  "risks": ["potential challenges"],
  "success_criteria": ["how to know when done"]
}

Ensure tasks are:
1. Specific and actionable
2. Properly ordered with clear dependencies
3. Assigned to appropriate agent types
4. Realistic in scope

Provide the plan as valid JSON.""")
        
        return "\n".join(prompt_parts)
    
    def _extract_plan_from_text(self, text: str) -> Dict[str, Any]:
        """Extract plan structure from unstructured text as fallback"""
        sections = ResponseParser.extract_sections(text)
        tasks = ResponseParser.extract_list(text)
        
        # Build basic plan structure
        plan = {
            "goal": sections.get("goal", ""),
            "summary": sections.get("summary", sections.get("intro", "")),
            "tasks": [],
            "resources": [],
            "risks": [],
            "success_criteria": []
        }
        
        # Convert extracted tasks to structured format
        for i, task_desc in enumerate(tasks):
            plan["tasks"].append({
                "id": f"task_{i+1}",
                "description": task_desc,
                "dependencies": [],
                "agent": "coder",  # Default
                "estimated_complexity": "medium",
                "tools_needed": [],
                "deliverables": []
            })
        
        return plan
    
    def _has_circular_dependencies(self, plan: Dict[str, Any]) -> bool:
        """Check for circular dependencies in task graph"""
        tasks = plan.get("tasks", [])
        task_ids = {task.get("id") for task in tasks}
        
        def has_cycle(task_id: str, visited: set, rec_stack: set) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            # Find task
            task = next((t for t in tasks if t.get("id") == task_id), None)
            if not task:
                return False
            
            # Check dependencies
            for dep_id in task.get("dependencies", []):
                if dep_id not in task_ids:
                    continue
                
                if dep_id not in visited:
                    if has_cycle(dep_id, visited, rec_stack):
                        return True
                elif dep_id in rec_stack:
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        visited = set()
        for task in tasks:
            task_id = task.get("id")
            if task_id and task_id not in visited:
                if has_cycle(task_id, visited, set()):
                    return True
        
        return False
    
    def create_quick_plan(self, goal: str) -> Dict[str, Any]:
        """Convenience method for quick plan creation"""
        return self.process({
            "type": "create_plan",
            "goal": goal
        })
