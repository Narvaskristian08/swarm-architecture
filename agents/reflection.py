"""
Reflection Agent
Learns from experience and improves processes.
"""
from typing import Dict, Any, List, Optional
import logging

from core import BaseAgent, PromptTemplate, ResponseParser

logger = logging.getLogger(__name__)


class ReflectionAgent(BaseAgent):
    """
    Reflection Agent - Learns from experience.
    
    Responsibilities:
    1. Analyze completed workflows
    2. Identify successes and failures
    3. Extract lessons learned
    4. Suggest process improvements
    5. Update best practices
    """
    
    def __init__(self):
        super().__init__(
            agent_id="reflection",
            name="Reflection",
            description="Learns from experience and improves processes"
        )
        self.capabilities = ["analysis", "learning", "improvement_suggestions"]
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a reflection task.
        
        Args:
            task: Dictionary containing:
                - type: Task type (analyze_workflow, extract_lessons, suggest_improvements)
                - data: Data to reflect on
                
        Returns:
            Dictionary containing reflection insights
        """
        task_type = task.get("type", "analyze_workflow")
        
        if task_type == "analyze_workflow":
            return self._analyze_workflow(task)
        elif task_type == "extract_lessons":
            return self._extract_lessons(task)
        elif task_type == "suggest_improvements":
            return self._suggest_improvements(task)
        elif task_type == "compare_approaches":
            return self._compare_approaches(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
    
    def _analyze_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a completed workflow"""
        workflow_data = task.get("workflow_data", {})
        goal = task.get("goal", "")
        outcome = task.get("outcome", "")
        
        if not workflow_data and not goal:
            return {"status": "error", "message": "Workflow data or goal required"}
        
        self.state.update("working", "Analyzing workflow")
        logger.info("Analyzing completed workflow")
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(workflow_data, goal, outcome)
        
        # Query LLM
        system_prompt = PromptTemplate.get_system_prompt("reflection")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.6)
        
        # Parse analysis
        sections = ResponseParser.extract_sections(response)
        
        self.state.update("done", "Analysis complete")
        
        return {
            "status": "success",
            "analysis": sections,
            "raw_response": response
        }
    
    def _extract_lessons(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Extract lessons learned from experience"""
        experience = task.get("experience", "")
        context = task.get("context", "")
        
        if not experience:
            return {"status": "error", "message": "No experience data provided"}
        
        self.state.update("working", "Extracting lessons")
        
        prompt = f"""Analyze this experience and extract lessons learned:

Experience:
{experience}

"""
        
        if context:
            prompt += f"Context:\n{context}\n\n"
        
        prompt += """Extract:
1. **What Went Well**: Successes and effective approaches
2. **What Didn't Work**: Failures and ineffective approaches
3. **Key Insights**: Important discoveries or realizations
4. **Lessons Learned**: Concrete takeaways
5. **Action Items**: How to apply these lessons in the future

Be specific and actionable."""
        
        system_prompt = PromptTemplate.get_system_prompt("reflection")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.6)
        
        sections = ResponseParser.extract_sections(response)
        lessons = ResponseParser.extract_list(response)
        
        self.state.update("done", "Lessons extracted")
        
        return {
            "status": "success",
            "lessons": lessons,
            "detailed_analysis": sections,
            "raw_response": response
        }
    
    def _suggest_improvements(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest process improvements"""
        current_process = task.get("current_process", "")
        problems = task.get("problems", [])
        goals = task.get("goals", [])
        
        if not current_process:
            return {"status": "error", "message": "Current process description required"}
        
        self.state.update("working", "Suggesting improvements")
        
        prompt = f"""Analyze this process and suggest improvements:

Current Process:
{current_process}

"""
        
        if problems:
            prompt += f"Known Problems:\n"
            for problem in problems:
                prompt += f"- {problem}\n"
            prompt += "\n"
        
        if goals:
            prompt += f"Goals:\n"
            for goal in goals:
                prompt += f"- {goal}\n"
            prompt += "\n"
        
        prompt += """Provide:
1. **Process Analysis**: Current strengths and weaknesses
2. **Improvement Suggestions**: Specific, actionable improvements
3. **Priority**: Which improvements to implement first
4. **Expected Impact**: How each improvement helps
5. **Implementation**: How to apply each improvement

Be practical and consider feasibility."""
        
        system_prompt = PromptTemplate.get_system_prompt("reflection")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.7)
        
        sections = ResponseParser.extract_sections(response)
        suggestions = ResponseParser.extract_list(response)
        
        self.state.update("done", "Improvements suggested")
        
        return {
            "status": "success",
            "suggestions": suggestions,
            "detailed_plan": sections,
            "raw_response": response
        }
    
    def _compare_approaches(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Compare different approaches to the same problem"""
        approaches = task.get("approaches", [])
        problem = task.get("problem", "")
        
        if len(approaches) < 2:
            return {"status": "error", "message": "At least 2 approaches required"}
        
        self.state.update("working", "Comparing approaches")
        
        prompt = f"Compare these different approaches to solving: {problem}\n\n"
        
        for i, approach in enumerate(approaches, 1):
            prompt += f"Approach {i}:\n{approach}\n\n"
        
        prompt += """Compare them on:
1. Effectiveness
2. Efficiency
3. Maintainability
4. Scalability
5. Complexity

Provide:
- Pros and cons of each
- Best use cases for each
- Overall recommendation
- Hybrid approach if applicable"""
        
        system_prompt = PromptTemplate.get_system_prompt("reflection")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.6)
        
        self.state.update("done", "Comparison complete")
        
        return {
            "status": "success",
            "comparison": response,
            "approaches_count": len(approaches)
        }
    
    def _build_analysis_prompt(
        self,
        workflow_data: Dict,
        goal: str,
        outcome: str
    ) -> str:
        """Build workflow analysis prompt"""
        prompt_parts = ["Analyze this completed workflow:"]
        
        if goal:
            prompt_parts.append(f"\n**Goal**: {goal}")
        
        if outcome:
            prompt_parts.append(f"\n**Outcome**: {outcome}")
        
        if workflow_data:
            prompt_parts.append(f"\n**Workflow Data**:")
            prompt_parts.append(f"- Tasks: {len(workflow_data.get('tasks', []))}")
            prompt_parts.append(f"- Duration: {workflow_data.get('duration', 'unknown')}")
            prompt_parts.append(f"- Agents involved: {', '.join(workflow_data.get('agents', []))}")
        
        prompt_parts.append("""
Provide a comprehensive analysis:

1. **Success Assessment**: Did we achieve the goal? Why or why not?
2. **Efficiency**: Was the workflow efficient? Any bottlenecks?
3. **Agent Coordination**: How well did agents work together?
4. **Decision Quality**: Were good decisions made? Any mistakes?
5. **Lessons Learned**: What should we remember for next time?
6. **Improvement Opportunities**: How can we do better?

Be honest and constructive.""")
        
        return "\n".join(prompt_parts)
    
    def reflect(self, experience: str, context: str = "") -> Dict[str, Any]:
        """Convenience method for quick reflection"""
        return self.process({
            "type": "extract_lessons",
            "experience": experience,
            "context": context
        })
