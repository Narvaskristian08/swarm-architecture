"""
Tester Agent
Validates functionality through testing and verification.
"""
from typing import Dict, Any, List, Optional
import logging

from core import BaseAgent, PromptTemplate, ResponseParser

logger = logging.getLogger(__name__)


class TesterAgent(BaseAgent):
    """
    Tester Agent - Validates code through testing.
    
    Responsibilities:
    1. Design test cases
    2. Execute tests
    3. Verify functionality
    4. Report failures clearly
    5. Suggest fixes
    """
    
    def __init__(self):
        super().__init__(
            agent_id="tester",
            name="Tester",
            description="Validates code functionality through testing"
        )
        self.capabilities = ["test_design", "test_execution", "result_analysis"]
        self.terminal_tool = None
    
    def set_terminal_tool(self, terminal_tool):
        """Set the terminal tool for test execution"""
        self.terminal_tool = terminal_tool
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a testing task.
        
        Args:
            task: Dictionary containing:
                - type: Task type (design_tests, run_tests, analyze_results)
                - code: Code to test
                - language: Programming language
                
        Returns:
            Dictionary containing test results
        """
        task_type = task.get("type", "design_tests")
        
        if task_type == "design_tests":
            return self._design_tests(task)
        elif task_type == "run_tests":
            return self._run_tests(task)
        elif task_type == "analyze_failure":
            return self._analyze_failure(task)
        elif task_type == "generate_test_code":
            return self._generate_test_code(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
    
    def _design_tests(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Design test cases for given code"""
        code = task.get("code", "")
        language = task.get("language", "python")
        specification = task.get("specification", "")
        
        if not code and not specification:
            return {"status": "error", "message": "Code or specification required"}
        
        self.state.update("working", "Designing test cases")
        logger.info("Designing test cases")
        
        # Build prompt
        prompt = self._build_test_design_prompt(code, language, specification)
        
        # Query LLM
        system_prompt = PromptTemplate.get_system_prompt("tester")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.4)
        
        # Parse test cases
        test_cases = self._parse_test_cases(response)
        
        self.state.update("done", "Test design complete")
        
        return {
            "status": "success",
            "test_cases": test_cases,
            "raw_response": response,
            "language": language
        }
    
    def _run_tests(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tests"""
        test_command = task.get("test_command", "pytest")
        test_path = task.get("test_path", ".")
        
        if not self.terminal_tool:
            return {
                "status": "error",
                "message": "Terminal tool not configured"
            }
        
        self.state.update("working", "Running tests")
        logger.info(f"Running tests: {test_command}")
        
        # Build full command
        full_command = f"{test_command} {test_path}"
        
        # Execute tests
        result = self.terminal_tool.run(command=full_command, timeout=60)
        
        # Analyze results
        passed = result.get("return_code") == 0
        
        self.state.update("done", "Tests executed")
        
        return {
            "status": "success",
            "tests_passed": passed,
            "return_code": result.get("return_code"),
            "stdout": result.get("stdout"),
            "stderr": result.get("stderr"),
            "command": full_command
        }
    
    def _analyze_failure(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test failure and suggest fixes"""
        failure_output = task.get("failure_output", "")
        code = task.get("code", "")
        test_code = task.get("test_code", "")
        
        if not failure_output:
            return {"status": "error", "message": "No failure output provided"}
        
        self.state.update("working", "Analyzing test failure")
        
        prompt = f"""Analyze this test failure:

Test Output:
{failure_output}

"""
        
        if code:
            prompt += f"Code being tested:\n```\n{code}\n```\n\n"
        
        if test_code:
            prompt += f"Test code:\n```\n{test_code}\n```\n\n"
        
        prompt += """Provide:
1. **Root Cause**: What caused the failure
2. **Expected vs Actual**: What was expected vs what happened
3. **Fix Suggestions**: Specific code changes needed
4. **Prevention**: How to prevent similar issues

Be specific and actionable."""
        
        system_prompt = PromptTemplate.get_system_prompt("tester")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.4)
        
        sections = ResponseParser.extract_sections(response)
        
        self.state.update("done", "Failure analysis complete")
        
        return {
            "status": "success",
            "analysis": sections,
            "raw_response": response
        }
    
    def _generate_test_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actual test code"""
        code = task.get("code", "")
        language = task.get("language", "python")
        test_framework = task.get("test_framework", "pytest")
        
        if not code:
            return {"status": "error", "message": "No code provided"}
        
        self.state.update("working", "Generating test code")
        
        prompt = f"""Generate {test_framework} tests for this {language} code:

```{language}
{code}
```

Requirements:
1. Test all public functions/methods
2. Include edge cases
3. Test error conditions
4. Use appropriate assertions
5. Follow {test_framework} best practices
6. Include docstrings explaining what each test verifies

Provide complete, runnable test code."""
        
        system_prompt = PromptTemplate.get_system_prompt("tester")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.3)
        
        # Extract code blocks
        code_blocks = ResponseParser.extract_code_blocks(response)
        
        self.state.update("done", "Test code generated")
        
        return {
            "status": "success",
            "test_code": code_blocks,
            "framework": test_framework,
            "raw_response": response
        }
    
    def _build_test_design_prompt(
        self,
        code: str,
        language: str,
        specification: str = ""
    ) -> str:
        """Build test design prompt"""
        prompt_parts = [f"Design comprehensive test cases for this {language} code:"]
        
        if specification:
            prompt_parts.append(f"\nSpecification:\n{specification}")
        
        if code:
            prompt_parts.append(f"\nCode:\n```{language}\n{code}\n```")
        
        prompt_parts.append("""
Design test cases covering:

1. **Happy Path**: Normal, expected usage
2. **Edge Cases**: Boundary conditions, empty inputs, large inputs
3. **Error Cases**: Invalid inputs, exception handling
4. **Integration**: How it works with other components
5. **Performance**: If applicable

For each test case, specify:
- Test name/description
- Input data
- Expected output/behavior
- Rationale

Format as a clear test plan.""")
        
        return "\n".join(prompt_parts)
    
    def _parse_test_cases(self, response: str) -> List[Dict[str, Any]]:
        """Parse test cases from response"""
        sections = ResponseParser.extract_sections(response)
        test_items = ResponseParser.extract_list(response)
        
        test_cases = []
        for i, item in enumerate(test_items):
            test_cases.append({
                "id": f"test_{i+1}",
                "description": item,
                "category": "general"
            })
        
        # Try to categorize
        for category in ["happy_path", "edge_cases", "error_cases"]:
            if category in sections:
                items = ResponseParser.extract_list(sections[category])
                for item in items:
                    test_cases.append({
                        "id": f"test_{category}_{len(test_cases)+1}",
                        "description": item,
                        "category": category
                    })
        
        return test_cases
    
    def test(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Convenience method for quick test design"""
        return self.process({
            "type": "design_tests",
            "code": code,
            "language": language
        })
