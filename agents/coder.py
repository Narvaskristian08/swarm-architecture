"""
Coder Agent
Writes clean, efficient, and maintainable code based on specifications.
"""
import json
from typing import Dict, Any, List, Optional
import logging

from core import BaseAgent, PromptTemplate, ResponseParser

logger = logging.getLogger(__name__)


class CoderAgent(BaseAgent):
    """
    Coder Agent - Implements features and writes code.
    
    Responsibilities:
    1. Write code according to specifications
    2. Follow language-specific best practices
    3. Include comments and documentation
    4. Handle edge cases and errors
    5. Keep code modular and testable
    """
    
    def __init__(self):
        super().__init__(
            agent_id="coder",
            name="Coder",
            description="Writes clean, efficient code based on specifications"
        )
        self.capabilities = ["code_generation", "code_modification", "documentation"]
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a coding task.
        
        Args:
            task: Dictionary containing:
                - type: Task type (implement_feature, modify_code, write_function, etc.)
                - specification: What to implement
                - language: Programming language
                - context: Optional existing code or context
                - requirements: Specific requirements
                
        Returns:
            Dictionary containing generated code and metadata
        """
        task_type = task.get("type", "implement_feature")
        
        if task_type == "implement_feature":
            return self._implement_feature(task)
        elif task_type == "modify_code":
            return self._modify_code(task)
        elif task_type == "write_function":
            return self._write_function(task)
        elif task_type == "fix_bug":
            return self._fix_bug(task)
        elif task_type == "add_documentation":
            return self._add_documentation(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
    
    def _implement_feature(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a complete feature"""
        specification = task.get("specification", "")
        language = task.get("language", "python")
        context = task.get("context", "")
        requirements = task.get("requirements", "")
        
        if not specification:
            return {"status": "error", "message": "No specification provided"}
        
        self.state.update("working", f"Implementing feature in {language}")
        logger.info(f"Implementing feature: {specification[:50]}...")
        
        # Build prompt
        prompt = self._build_implementation_prompt(
            specification, language, context, requirements
        )
        
        # Query LLM
        system_prompt = PromptTemplate.get_system_prompt("coder")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.3)
        
        # Extract code blocks
        code_blocks = ResponseParser.extract_code_blocks(response)
        
        if not code_blocks:
            # Try to find code in the response
            code_blocks = [{"language": language, "code": response}]
        
        self.state.update("done", "Feature implemented")
        
        return {
            "status": "success",
            "code_blocks": code_blocks,
            "raw_response": response,
            "language": language
        }
    
    def _modify_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Modify existing code"""
        existing_code = task.get("existing_code", "")
        modifications = task.get("modifications", "")
        language = task.get("language", "python")
        
        if not existing_code or not modifications:
            return {
                "status": "error",
                "message": "Existing code and modifications required"
            }
        
        self.state.update("working", "Modifying code")
        
        prompt = f"""Here is the existing code:

```{language}
{existing_code}
```

Requested modifications:
{modifications}

Please provide the modified code with clear comments explaining the changes."""
        
        system_prompt = PromptTemplate.get_system_prompt("coder")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.3)
        
        code_blocks = ResponseParser.extract_code_blocks(response)
        
        self.state.update("done", "Code modified")
        
        return {
            "status": "success",
            "code_blocks": code_blocks,
            "raw_response": response,
            "language": language
        }
    
    def _write_function(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Write a specific function"""
        function_spec = task.get("specification", "")
        language = task.get("language", "python")
        signature = task.get("signature", "")
        
        if not function_spec:
            return {"status": "error", "message": "No function specification provided"}
        
        self.state.update("working", f"Writing function in {language}")
        
        prompt_parts = [f"Write a {language} function with the following specification:"]
        
        if signature:
            prompt_parts.append(f"\nFunction signature:\n{signature}")
        
        prompt_parts.append(f"\nDescription:\n{function_spec}")
        
        prompt_parts.append("""
Requirements:
1. Include type hints (if language supports them)
2. Add docstring/comments
3. Handle edge cases
4. Include error handling
5. Follow best practices

Provide the complete, production-ready function.""")
        
        prompt = "\n".join(prompt_parts)
        
        system_prompt = PromptTemplate.get_system_prompt("coder")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.3)
        
        code_blocks = ResponseParser.extract_code_blocks(response)
        
        self.state.update("done", "Function written")
        
        return {
            "status": "success",
            "code_blocks": code_blocks,
            "raw_response": response,
            "language": language
        }
    
    def _fix_bug(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Fix a bug in existing code"""
        buggy_code = task.get("code", "")
        bug_description = task.get("bug_description", "")
        error_message = task.get("error_message", "")
        language = task.get("language", "python")
        
        if not buggy_code or not bug_description:
            return {
                "status": "error",
                "message": "Buggy code and bug description required"
            }
        
        self.state.update("working", "Fixing bug")
        
        prompt = f"""Here is code with a bug:

```{language}
{buggy_code}
```

Bug description:
{bug_description}"""
        
        if error_message:
            prompt += f"\n\nError message:\n{error_message}"
        
        prompt += "\n\nPlease provide the fixed code with an explanation of the bug and the fix."
        
        system_prompt = PromptTemplate.get_system_prompt("coder")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.3)
        
        code_blocks = ResponseParser.extract_code_blocks(response)
        sections = ResponseParser.extract_sections(response)
        
        self.state.update("done", "Bug fixed")
        
        return {
            "status": "success",
            "code_blocks": code_blocks,
            "explanation": sections.get("explanation", ""),
            "raw_response": response,
            "language": language
        }
    
    def _add_documentation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Add documentation to existing code"""
        code = task.get("code", "")
        language = task.get("language", "python")
        doc_type = task.get("doc_type", "inline")  # inline, api, user
        
        if not code:
            return {"status": "error", "message": "No code provided"}
        
        self.state.update("working", "Adding documentation")
        
        prompt = f"""Add comprehensive {doc_type} documentation to this {language} code:

```{language}
{code}
```

Include:
1. Module/class docstrings
2. Function docstrings with parameters and return values
3. Inline comments for complex logic
4. Usage examples (if appropriate)"""
        
        system_prompt = PromptTemplate.get_system_prompt("coder")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.3)
        
        code_blocks = ResponseParser.extract_code_blocks(response)
        
        self.state.update("done", "Documentation added")
        
        return {
            "status": "success",
            "code_blocks": code_blocks,
            "raw_response": response,
            "language": language
        }
    
    def _build_implementation_prompt(
        self,
        specification: str,
        language: str,
        context: str = "",
        requirements: str = ""
    ) -> str:
        """Build a detailed implementation prompt"""
        prompt_parts = [
            f"Implement the following feature in {language}:",
            f"\nSpecification:\n{specification}"
        ]
        
        if context:
            prompt_parts.append(f"\nContext/Existing Code:\n{context}")
        
        if requirements:
            prompt_parts.append(f"\nAdditional Requirements:\n{requirements}")
        
        prompt_parts.append(f"""
Implementation Guidelines:
1. Write clean, readable {language} code
2. Follow {language} best practices and conventions
3. Include appropriate error handling
4. Add comments explaining complex logic
5. Make code modular and reusable
6. Consider edge cases
7. Use type hints/annotations where applicable

Return every generated file using this exact format:

FILE: relative/path/to/file.ext
```{language}
complete file contents
```

Use a separate FILE marker and fenced block for every file. Paths must be
relative, must not contain ``..``, and should include the project directory.
Provide complete, production-ready code with proper structure.""")
        
        return "\n".join(prompt_parts)
    
    def write_code(
        self,
        specification: str,
        language: str = "python",
        context: str = ""
    ) -> Dict[str, Any]:
        """Convenience method for quick code generation"""
        return self.process({
            "type": "implement_feature",
            "specification": specification,
            "language": language,
            "context": context
        })
