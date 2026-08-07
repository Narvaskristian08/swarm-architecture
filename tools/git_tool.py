"""
Git Tool
Provides git operations for version control.
"""
import subprocess
from typing import Dict, Any, Optional, List
import logging

from .base_tool import BaseTool

logger = logging.getLogger(__name__)


class GitTool(BaseTool):
    """
    Git operations tool.
    Manages version control operations.
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        super().__init__(
            tool_id="git_tool",
            name="Git Tool",
            description="Git version control operations"
        )
        self.repo_path = repo_path
    
    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute a git operation"""
        operations = {
            "status": self._status,
            "add": self._add,
            "commit": self._commit,
            "push": self._push,
            "pull": self._pull,
            "branch": self._branch,
            "checkout": self._checkout,
            "log": self._log,
            "diff": self._diff,
            "init": self._init,
            "clone": self._clone,
        }
        
        if operation not in operations:
            return {
                "status": "error",
                "error": f"Unknown operation: {operation}"
            }
        
        return operations[operation](**kwargs)
    
    def validate_params(self, operation: str = None, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate parameters"""
        if not operation:
            return False, "Operation is required"
        
        return True, None
    
    def _run_git_command(self, args: List[str], **kwargs) -> Dict[str, Any]:
        """Run a git command"""
        try:
            timeout = kwargs.get("timeout", 30)
            cwd = kwargs.get("cwd", self.repo_path)
            
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "output": result.stdout.strip(),
                    "stderr": result.stderr.strip() if result.stderr else None
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr.strip() or result.stdout.strip(),
                    "return_code": result.returncode
                }
        
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "Git command timed out"
            }
        except FileNotFoundError:
            return {
                "status": "error",
                "error": "Git not found. Is it installed?"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _status(self, **kwargs) -> Dict[str, Any]:
        """Get git status"""
        return self._run_git_command(["status"], **kwargs)
    
    def _add(self, files: str = ".", **kwargs) -> Dict[str, Any]:
        """Stage files"""
        return self._run_git_command(["add", files], **kwargs)
    
    def _commit(self, message: str, **kwargs) -> Dict[str, Any]:
        """Commit changes"""
        if not message:
            return {
                "status": "error",
                "error": "Commit message is required"
            }
        return self._run_git_command(["commit", "-m", message], **kwargs)
    
    def _push(self, remote: str = "origin", branch: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Push changes"""
        args = ["push", remote]
        if branch:
            args.append(branch)
        return self._run_git_command(args, **kwargs)
    
    def _pull(self, remote: str = "origin", branch: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Pull changes"""
        args = ["pull", remote]
        if branch:
            args.append(branch)
        return self._run_git_command(args, **kwargs)
    
    def _branch(self, branch_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """List or create branches"""
        if branch_name:
            return self._run_git_command(["branch", branch_name], **kwargs)
        else:
            return self._run_git_command(["branch", "-a"], **kwargs)
    
    def _checkout(self, branch: str, create: bool = False, **kwargs) -> Dict[str, Any]:
        """Checkout a branch"""
        args = ["checkout"]
        if create:
            args.append("-b")
        args.append(branch)
        return self._run_git_command(args, **kwargs)
    
    def _log(self, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """Get commit log"""
        return self._run_git_command(
            ["log", f"-{limit}", "--oneline"],
            **kwargs
        )
    
    def _diff(self, file_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Show diff"""
        args = ["diff"]
        if file_path:
            args.append(file_path)
        return self._run_git_command(args, **kwargs)
    
    def _init(self, **kwargs) -> Dict[str, Any]:
        """Initialize a git repository"""
        return self._run_git_command(["init"], **kwargs)
    
    def _clone(self, url: str, directory: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Clone a repository"""
        args = ["clone", url]
        if directory:
            args.append(directory)
        return self._run_git_command(args, **kwargs)
    
    # Convenience methods
    
    def quick_commit(self, message: str, files: str = ".", **kwargs) -> Dict[str, Any]:
        """Stage and commit in one operation"""
        # Stage files
        add_result = self._add(files, **kwargs)
        if add_result["status"] != "success":
            return add_result
        
        # Commit
        return self._commit(message, **kwargs)
    
    def is_repository(self, **kwargs) -> bool:
        """Check if current directory is a git repository"""
        result = self._run_git_command(["rev-parse", "--git-dir"], **kwargs)
        return result["status"] == "success"
    
    def get_current_branch(self, **kwargs) -> Optional[str]:
        """Get current branch name"""
        result = self._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], **kwargs)
        if result["status"] == "success":
            return result["output"]
        return None
