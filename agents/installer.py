"""
Installer Agent
Researches, suggests, and helps install new frameworks/libraries.
"""
from typing import Dict, Any, List, Optional
import logging
import re
import shlex
import subprocess
import sys

from core import BaseAgent, PromptTemplate, ResponseParser

logger = logging.getLogger(__name__)


class InstallerAgent(BaseAgent):
    """
    Installer Agent - Researches and installs frameworks.
    
    Responsibilities:
    1. Research suggested frameworks
    2. Check if already installed
    3. Verify compatibility
    4. Install with user confirmation
    5. Verify successful installation
    """
    
    def __init__(self):
        super().__init__(
            agent_id="installer",
            name="Installer",
            description="Researches and installs frameworks/libraries"
        )
        self.capabilities = ["research_framework", "check_installed", "install_package"]
        self.terminal_tool = None
        self.web_tool = None
    
    def set_terminal_tool(self, terminal_tool):
        """Set terminal tool for installations"""
        self.terminal_tool = terminal_tool
    
    def set_web_tool(self, web_tool):
        """Set web tool for research"""
        self.web_tool = web_tool
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an installation task.
        
        Args:
            task: Dictionary containing:
                - type: Task type (suggest_framework, install_package, etc.)
                - framework: Framework name
                - language: Programming language
                - purpose: What it's needed for
                
        Returns:
            Dictionary containing installation results
        """
        task_type = task.get("type", "suggest_framework")
        
        if task_type == "suggest_framework":
            return self._suggest_framework(task)
        elif task_type == "research_and_install":
            return self._research_and_install(task)
        elif task_type == "check_installed":
            return self._check_installed(task)
        elif task_type == "install_package":
            return self._install_package(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
    
    def _suggest_framework(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest appropriate framework for a task"""
        purpose = task.get("purpose", "")
        language = task.get("language", "python")
        context = task.get("context", "")
        
        if not purpose:
            return {"status": "error", "message": "Purpose required"}
        
        self.state.update("thinking", "Suggesting framework")
        logger.info(f"Suggesting framework for: {purpose}")
        
        # Build prompt
        prompt = f"""Suggest the best framework/library for this purpose:

Purpose: {purpose}
Language: {language}
Context: {context}

Provide your recommendation in this JSON format:
{{
  "framework": "framework-name",
  "reason": "why this is the best choice",
  "alternatives": ["alternative1", "alternative2"],
  "installation": "installation command",
  "difficulty": "easy/medium/hard",
  "documentation": "official docs URL",
  "use_cases": ["use case 1", "use case 2"]
}}

Consider:
1. Popularity and community support
2. Ease of use and learning curve
3. Performance and features
4. Maintenance and updates
5. Compatibility with {language}"""
        
        system_prompt = PromptTemplate.get_system_prompt("research")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.6)
        
        # Parse suggestion
        suggestion = ResponseParser.extract_json(response)
        
        if suggestion:
            self.state.update("done", "Suggestion ready")
            return {
                "status": "success",
                "suggestion": suggestion,
                "raw_response": response
            }
        else:
            # Fallback: extract from text
            self.state.update("done", "Suggestion extracted from text")
            return {
                "status": "success",
                "suggestion": {"framework": "Unknown", "reason": response},
                "raw_response": response
            }
    
    def _research_and_install(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Complete workflow: research, check, and install framework"""
        framework = task.get("framework", "")
        language = task.get("language", "python")
        auto_install = task.get("auto_install", False)
        
        if not framework:
            return {"status": "error", "message": "Framework name required"}
        if not self._is_valid_package_name(framework, language):
            return {"status": "error", "message": "Invalid framework/package name"}
        
        workflow_result = {
            "status": "success",
            "framework": framework,
            "steps": []
        }
        
        # Step 1: Research the framework
        self.state.update("working", f"Researching {framework}")
        
        research_prompt = f"""Research the framework: {framework}

Provide:
1. What is it and what does it do?
2. Current stable version
3. Installation command for {language}
4. Basic usage example
5. Official documentation URL
6. System requirements
7. Known issues or considerations

Be concise but complete."""
        
        system_prompt = PromptTemplate.get_system_prompt("research")
        research_response = self.query_llm(research_prompt, system_prompt=system_prompt, temperature=0.5)
        
        workflow_result["steps"].append({
            "step": "research",
            "status": "completed",
            "findings": research_response[:500] + "..."
        })
        
        # Step 2: Check if already installed
        self.state.update("working", f"Checking if {framework} is installed")
        
        is_installed = self._check_if_installed(framework, language)
        
        workflow_result["steps"].append({
            "step": "check_installed",
            "status": "completed",
            "installed": is_installed
        })
        
        if is_installed:
            workflow_result["message"] = f"{framework} is already installed"
            return workflow_result
        
        # Step 3: Prepare installation
        install_command = self._get_install_command(framework, language)
        
        workflow_result["installation_command"] = install_command
        workflow_result["steps"].append({
            "step": "prepare_install",
            "status": "completed",
            "command": install_command
        })
        
        # Step 4: Install (with confirmation if not auto)
        if auto_install:
            self.state.update("working", f"Installing {framework}")
            install_result = self._execute_install(framework, language, install_command)
            
            workflow_result["steps"].append({
                "step": "install",
                "status": "completed" if install_result else "failed",
                "result": install_result
            })
            
            if install_result:
                workflow_result["message"] = f"{framework} installed successfully"
            else:
                workflow_result["status"] = "partial"
                workflow_result["message"] = f"{framework} installation failed"
        else:
            workflow_result["status"] = "awaiting_confirmation"
            workflow_result["message"] = f"Ready to install {framework}. Run: {install_command}"
        
        self.state.update("done", "Installation workflow complete")
        return workflow_result
    
    def _check_installed(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a package is installed"""
        framework = task.get("framework", "")
        language = task.get("language", "python")
        
        if not framework:
            return {"status": "error", "message": "Framework name required"}
        if not self._is_valid_package_name(framework, language):
            return {"status": "error", "message": "Invalid framework/package name"}
        
        self.state.update("working", f"Checking {framework}")
        
        is_installed = self._check_if_installed(framework, language)
        version = self._get_installed_version(framework, language) if is_installed else None
        
        return {
            "status": "success",
            "framework": framework,
            "installed": is_installed,
            "version": version
        }
    
    def _install_package(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Install a specific package"""
        framework = task.get("framework", "")
        language = task.get("language", "python")
        version = task.get("version")  # Optional specific version
        confirm = task.get("confirm", False)
        
        if not framework:
            return {"status": "error", "message": "Framework name required"}
        if not self._is_valid_package_name(framework, language):
            return {"status": "error", "message": "Invalid framework/package name"}
        
        if not confirm:
            return {
                "status": "error",
                "message": "Installation requires confirmation (confirm=True)"
            }
        
        self.state.update("working", f"Installing {framework}")
        
        install_command = self._get_install_command(framework, language, version)
        result = self._execute_install(framework, language, install_command)
        
        if result:
            return {
                "status": "success",
                "framework": framework,
                "message": f"Successfully installed {framework}",
                "command": install_command
            }
        else:
            return {
                "status": "error",
                "framework": framework,
                "message": f"Failed to install {framework}",
                "command": install_command
            }
    
    def _check_if_installed(self, framework: str, language: str) -> bool:
        """Check if a framework is installed"""
        try:
            if language.lower() == "python":
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", framework],
                    capture_output=True,
                    timeout=10
                )
                return result.returncode == 0
            
            elif language.lower() in ["javascript", "nodejs", "node"]:
                result = subprocess.run(
                    ["npm", "list", framework],
                    capture_output=True,
                    timeout=10
                )
                return result.returncode == 0
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if {framework} is installed: {e}")
            return False
    
    def _get_installed_version(self, framework: str, language: str) -> Optional[str]:
        """Get installed version of a framework"""
        try:
            if language.lower() == "python":
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", framework],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            return line.split(':', 1)[1].strip()
            
            return None
            
        except Exception:
            return None
    
    def _get_install_command(self, framework: str, language: str, version: Optional[str] = None) -> str:
        """Get installation command for framework"""
        if language.lower() == "python":
            python = shlex.quote(sys.executable)
            if version:
                return f"{python} -m pip install {framework}=={version}"
            else:
                return f"{python} -m pip install {framework}"
        
        elif language.lower() in ["javascript", "nodejs", "node"]:
            if version:
                return f"npm install {framework}@{version}"
            else:
                return f"npm install {framework}"
        
        elif language.lower() == "dart" or framework.lower() == "flutter":
            return f"flutter pub add {framework}"
        
        elif language.lower() == "ruby":
            return f"gem install {framework}"
        
        elif language.lower() == "go":
            return f"go get {framework}"
        
        else:
            return f"# Manual installation required for {framework}"

    def _is_valid_package_name(self, framework: str, language: str) -> bool:
        """Reject options and shell syntax before constructing install commands."""
        if not isinstance(framework, str) or len(framework) > 200:
            return False
        if language.lower() == "python":
            return bool(re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9._-]*(?:\[[A-Za-z0-9_,.-]+\])?",
                framework,
            ))
        if language.lower() in {"javascript", "nodejs", "node"}:
            return bool(re.fullmatch(
                r"(?:@[A-Za-z0-9._-]+/)?[A-Za-z0-9._-]+",
                framework,
            ))
        return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/@+-]*", framework))
    
    def _execute_install(self, framework: str, language: str, command: str) -> bool:
        """Execute installation command"""
        if not self.terminal_tool:
            logger.error("Terminal tool not configured")
            return False
        
        try:
            logger.info(f"Executing: {command}")
            
            result = self.terminal_tool.run(command=command, timeout=300)  # 5 min timeout
            
            if result.get("status") == "success" and result.get("return_code") == 0:
                logger.info(f"Successfully installed {framework}")
                return True
            else:
                logger.error(f"Installation failed: {result.get('stderr')}")
                return False
                
        except Exception as e:
            logger.error(f"Installation error: {e}")
            return False
    
    def suggest_and_install(
        self,
        purpose: str,
        language: str = "python",
        auto_install: bool = False
    ) -> Dict[str, Any]:
        """Convenience method: suggest and optionally install"""
        # First, get suggestion
        suggestion_result = self.process({
            "type": "suggest_framework",
            "purpose": purpose,
            "language": language
        })
        
        if suggestion_result.get("status") != "success":
            return suggestion_result
        
        suggestion = suggestion_result.get("suggestion", {})
        framework = suggestion.get("framework")
        
        if not framework:
            return {"status": "error", "message": "No framework suggested"}
        
        # Then research and optionally install
        return self.process({
            "type": "research_and_install",
            "framework": framework,
            "language": language,
            "auto_install": auto_install
        })
