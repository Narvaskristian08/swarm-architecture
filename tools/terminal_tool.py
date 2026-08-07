"""
Terminal Tool
Safely executes shell commands for agents.
"""
import subprocess
import re
from typing import Dict, Any, Optional, List
import logging

from .base_tool import BaseTool
from config import REQUIRE_CONFIRMATION_FOR_DANGEROUS_COMMANDS, DANGEROUS_COMMAND_PATTERNS

logger = logging.getLogger(__name__)


class TerminalTool(BaseTool):
    """
    Terminal operations tool.
    Executes shell commands with safety checks.
    """
    
    def __init__(self, working_directory: Optional[str] = None):
        super().__init__(
            tool_id="terminal_tool",
            name="Terminal Tool",
            description="Execute shell commands safely"
        )
        self.working_directory = working_directory
        self.command_history: List[Dict] = []
        self.max_history = 100
    
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a shell command"""
        timeout = kwargs.get("timeout", 30)
        capture_output = kwargs.get("capture_output", True)
        shell = kwargs.get("shell", True)
        cwd = kwargs.get("cwd", self.working_directory)
        
        # Safety check
        if self._is_dangerous_command(command):
            return {
                "status": "error",
                "error": "Dangerous command detected. Requires explicit confirmation.",
                "command": command,
                "dangerous": True
            }
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            
            # Record in history
            self._add_to_history(command, result.returncode, result.stdout, result.stderr)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": f"Command timed out after {timeout} seconds",
                "command": command
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "command": command
            }
    
    def validate_params(self, command: str = None, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate command parameters"""
        if not command:
            return False, "Command is required"
        
        if not isinstance(command, str):
            return False, "Command must be a string"
        
        if len(command.strip()) == 0:
            return False, "Command cannot be empty"
        
        return True, None
    
    def _is_dangerous_command(self, command: str) -> bool:
        """Check if command is potentially dangerous"""
        if not REQUIRE_CONFIRMATION_FOR_DANGEROUS_COMMANDS:
            return False
        
        command_lower = command.lower()
        
        # Check against patterns
        for pattern in DANGEROUS_COMMAND_PATTERNS:
            if re.search(pattern, command_lower):
                logger.warning(f"Dangerous command detected: {command}")
                return True
        
        return False
    
    def _add_to_history(self, command: str, return_code: int, stdout: str, stderr: str):
        """Add command to history"""
        self.command_history.append({
            "command": command,
            "return_code": return_code,
            "stdout": stdout[:500],  # Truncate
            "stderr": stderr[:500],
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        
        # Keep history size manageable
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get command history"""
        return self.command_history[-limit:]
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
    
    # Convenience methods for common operations
    
    def run_tests(self, test_command: str = "pytest", **kwargs) -> Dict[str, Any]:
        """Run tests"""
        return self.run(command=test_command, **kwargs)
    
    def install_package(self, package: str, **kwargs) -> Dict[str, Any]:
        """Install a Python package"""
        return self.run(command=f"pip install {package}", **kwargs)
    
    def check_version(self, tool: str) -> Dict[str, Any]:
        """Check version of a tool"""
        return self.run(command=f"{tool} --version", timeout=5)
