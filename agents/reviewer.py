"""
Reviewer Agent
Reviews code for quality, security, and correctness.
"""
import json
from typing import Dict, Any, List, Optional
import logging

from core import BaseAgent, PromptTemplate, ResponseParser

logger = logging.getLogger(__name__)


class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent - Ensures code quality and security.
    
    Responsibilities:
    1. Review code for bugs and logic errors
    2. Check for security vulnerabilities
    3. Verify best practices adherence
    4. Suggest improvements and optimizations
    5. Ensure code maintainability
    """
    
    def __init__(self):
        super().__init__(
            agent_id="reviewer",
            name="Reviewer",
            description="Reviews code for quality, security, and correctness"
        )
        self.capabilities = [
            "code_review",
            "security_analysis",
            "quality_assessment",
            "optimization_suggestions"
        ]
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a review task.
        
        Args:
            task: Dictionary containing:
                - type: Task type (review_code, security_check, etc.)
                - code: Code to review
                - language: Programming language
                - focus: Optional focus areas
                
        Returns:
            Dictionary containing review findings and suggestions
        """
        task_type = task.get("type", "review_code")
        
        if task_type == "review_code":
            return self._review_code(task)
        elif task_type == "security_check":
            return self._security_check(task)
        elif task_type == "performance_review":
            return self._performance_review(task)
        elif task_type == "compare_implementations":
            return self._compare_implementations(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
    
    def _review_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive code review"""
        code = task.get("code", "")
        language = task.get("language", "python")
        focus = task.get("focus", "all")  # all, bugs, style, performance, security
        context = task.get("context", "")
        
        if not code:
            return {"status": "error", "message": "No code provided"}
        
        self.state.update("working", f"Reviewing {language} code")
        logger.info(f"Reviewing code (focus: {focus})")
        
        # Build review prompt
        prompt = self._build_review_prompt(code, language, focus, context)
        
        # Query LLM
        system_prompt = PromptTemplate.get_system_prompt("reviewer")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.4)
        
        # Parse review
        review = self._parse_review(response)
        
        self.state.update("done", "Review complete")
        
        return {
            "status": "success",
            "review": review,
            "raw_response": response,
            "language": language
        }
    
    def _security_check(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Focused security analysis"""
        code = task.get("code", "")
        language = task.get("language", "python")
        
        if not code:
            return {"status": "error", "message": "No code provided"}
        
        self.state.update("working", "Performing security analysis")
        
        prompt = f"""Perform a security analysis of this {language} code:

```{language}
{code}
```

Check for:
1. Injection vulnerabilities (SQL, command, etc.)
2. Authentication/authorization issues
3. Insecure data handling
4. Cryptography misuse
5. Input validation problems
6. Information disclosure
7. Hardcoded secrets
8. Unsafe dependencies

Provide:
- List of security issues found (with severity: critical/high/medium/low)
- Specific line numbers or code snippets
- Remediation recommendations
- Best practice suggestions

Use this JSON structure:
{
  "security_issues": [
    {
      "severity": "high",
      "category": "injection",
      "description": "...",
      "location": "line X or code snippet",
      "remediation": "..."
    }
  ],
  "overall_assessment": "...",
  "recommendations": [...]
}"""
        
        system_prompt = PromptTemplate.get_system_prompt("reviewer")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.3)
        
        # Try to parse as JSON
        security_report = ResponseParser.extract_json(response)
        
        if not security_report:
            security_report = {"raw_analysis": response}
        
        self.state.update("done", "Security analysis complete")
        
        return {
            "status": "success",
            "security_report": security_report,
            "raw_response": response
        }
    
    def _performance_review(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review code for performance issues"""
        code = task.get("code", "")
        language = task.get("language", "python")
        
        if not code:
            return {"status": "error", "message": "No code provided"}
        
        self.state.update("working", "Analyzing performance")
        
        prompt = f"""Analyze this {language} code for performance issues:

```{language}
{code}
```

Check for:
1. Algorithmic complexity (time and space)
2. Inefficient loops or data structures
3. Unnecessary computations
4. Memory leaks or excessive allocations
5. I/O bottlenecks
6. Database query inefficiencies

Provide:
- Performance issues with severity
- Estimated complexity (Big O notation where relevant)
- Optimization suggestions with code examples
- Trade-offs to consider"""
        
        system_prompt = PromptTemplate.get_system_prompt("reviewer")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.4)
        
        sections = ResponseParser.extract_sections(response)
        
        self.state.update("done", "Performance analysis complete")
        
        return {
            "status": "success",
            "performance_analysis": sections,
            "raw_response": response
        }
    
    def _compare_implementations(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Compare multiple implementations"""
        implementations = task.get("implementations", [])
        language = task.get("language", "python")
        
        if len(implementations) < 2:
            return {
                "status": "error",
                "message": "At least 2 implementations required"
            }
        
        self.state.update("working", "Comparing implementations")
        
        prompt = f"Compare these {len(implementations)} {language} implementations:\n\n"
        
        for i, impl in enumerate(implementations, 1):
            prompt += f"Implementation {i}:\n```{language}\n{impl}\n```\n\n"
        
        prompt += """Compare them on:
1. Correctness
2. Performance
3. Readability
4. Maintainability
5. Best practices adherence

Recommend the best approach or suggest a hybrid solution."""
        
        system_prompt = PromptTemplate.get_system_prompt("reviewer")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.5)
        
        self.state.update("done", "Comparison complete")
        
        return {
            "status": "success",
            "comparison": response,
            "raw_response": response
        }
    
    def _build_review_prompt(
        self,
        code: str,
        language: str,
        focus: str,
        context: str = ""
    ) -> str:
        """Build a comprehensive review prompt"""
        prompt_parts = [f"Review this {language} code:"]
        
        if context:
            prompt_parts.append(f"\nContext:\n{context}")
        
        prompt_parts.append(f"\nCode to review:\n```{language}\n{code}\n```")
        
        focus_areas = {
            "all": [
                "Correctness and logic",
                "Bugs and potential errors",
                "Code style and readability",
                "Best practices adherence",
                "Performance considerations",
                "Security vulnerabilities",
                "Documentation quality",
                "Maintainability"
            ],
            "bugs": ["Correctness", "Logic errors", "Edge cases", "Error handling"],
            "style": ["Code style", "Naming", "Structure", "Readability"],
            "performance": ["Algorithmic efficiency", "Resource usage", "Optimizations"],
            "security": ["Security vulnerabilities", "Input validation", "Data handling"]
        }
        
        areas = focus_areas.get(focus, focus_areas["all"])
        
        prompt_parts.append("\nReview focus areas:")
        for area in areas:
            prompt_parts.append(f"- {area}")
        
        prompt_parts.append("""
Provide your review in this structure:

## Issues Found
List each issue with:
- Severity (critical/high/medium/low)
- Description
- Location (line number or code snippet)
- Impact

## Positive Aspects
What's done well in the code

## Suggestions
Concrete improvements with examples where helpful

## Overall Assessment
Summary and recommendation (approve/approve with changes/needs work)""")
        
        return "\n".join(prompt_parts)
    
    def _parse_review(self, response: str) -> Dict[str, Any]:
        """Parse review response into structured format"""
        sections = ResponseParser.extract_sections(response)
        
        review = {
            "issues": [],
            "positive_aspects": [],
            "suggestions": [],
            "overall_assessment": "",
            "recommendation": "approve"  # default
        }
        
        # Extract issues
        issues_text = sections.get("issues_found", "")
        if issues_text:
            issue_items = ResponseParser.extract_list(issues_text)
            for item in issue_items:
                # Try to determine severity
                severity = "medium"
                if any(word in item.lower() for word in ["critical", "severe", "dangerous"]):
                    severity = "critical"
                elif any(word in item.lower() for word in ["high", "important", "serious"]):
                    severity = "high"
                elif any(word in item.lower() for word in ["low", "minor", "trivial"]):
                    severity = "low"
                
                review["issues"].append({
                    "severity": severity,
                    "description": item
                })
        
        # Extract positive aspects
        positive_text = sections.get("positive_aspects", "")
        if positive_text:
            review["positive_aspects"] = ResponseParser.extract_list(positive_text)
        
        # Extract suggestions
        suggestions_text = sections.get("suggestions", "")
        if suggestions_text:
            review["suggestions"] = ResponseParser.extract_list(suggestions_text)
        
        # Overall assessment
        assessment = sections.get("overall_assessment", "")
        review["overall_assessment"] = assessment
        
        # Determine recommendation
        assessment_lower = assessment.lower()
        if "needs work" in assessment_lower or "reject" in assessment_lower:
            review["recommendation"] = "needs_work"
        elif "approve with changes" in assessment_lower:
            review["recommendation"] = "approve_with_changes"
        
        return review
    
    def review(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Convenience method for quick code review"""
        return self.process({
            "type": "review_code",
            "code": code,
            "language": language,
            "focus": "all"
        })
