"""
Tool Manager
Coordinates all tools available to agents.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from .base_tool import BaseTool
from .file_tool import FileTool
from .terminal_tool import TerminalTool
from .git_tool import GitTool
from .web_tool import WebTool
from .project_analyzer import ProjectAnalyzerTool

logger = logging.getLogger(__name__)


class ToolManager:
    """
    Manages all tools available to agents.
    Provides unified interface for tool access and execution.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.tools: Dict[str, BaseTool] = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all available tools"""
        # File tool
        self.tools["file"] = FileTool(workspace_root=self.workspace_root)
        
        # Terminal tool
        self.tools["terminal"] = TerminalTool(working_directory=str(self.workspace_root))
        
        # Git tool
        self.tools["git"] = GitTool(repo_path=str(self.workspace_root))
        
        # Web tool
        self.tools["web"] = WebTool()
        
        # Project analyzer tool
        self.tools["project"] = ProjectAnalyzerTool(project_root=self.workspace_root)
        
        logger.info(f"Initialized {len(self.tools)} tools")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [tool.get_info() for tool in self.tools.values()]
    
    def execute_tool(
        self,
        tool_name: str,
        operation: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a tool operation.
        
        Args:
            tool_name: Name of the tool to use
            operation: Operation to perform (for tools with multiple operations)
            **kwargs: Operation parameters
            
        Returns:
            Operation result
        """
        tool = self.get_tool(tool_name)
        
        if not tool:
            return {
                "status": "error",
                "error": f"Tool not found: {tool_name}",
                "available_tools": list(self.tools.keys())
            }
        
        if not tool.enabled:
            return {
                "status": "error",
                "error": f"Tool {tool_name} is disabled"
            }
        
        # Execute tool
        if operation:
            return tool.run(operation=operation, **kwargs)
        else:
            return tool.run(**kwargs)
    
    def enable_tool(self, tool_name: str) -> bool:
        """Enable a tool"""
        tool = self.get_tool(tool_name)
        if tool:
            tool.enable()
            logger.info(f"Enabled tool: {tool_name}")
            return True
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """Disable a tool"""
        tool = self.get_tool(tool_name)
        if tool:
            tool.disable()
            logger.warning(f"Disabled tool: {tool_name}")
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for all tools"""
        stats = {}
        for name, tool in self.tools.items():
            stats[name] = {
                "enabled": tool.enabled,
                "usage_count": tool.usage_count,
                "last_error": tool.last_error
            }
        return stats
    
    # Convenience methods for common operations
    
    def read_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Read a file"""
        return self.execute_tool("file", operation="read", file_path=file_path, **kwargs)
    
    def write_file(self, file_path: str, content: str, **kwargs) -> Dict[str, Any]:
        """Write a file"""
        return self.execute_tool("file", operation="write", file_path=file_path, content=content, **kwargs)
    
    def run_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Run a terminal command"""
        return self.execute_tool("terminal", command=command, **kwargs)
    
    def git_commit(self, message: str, files: str = ".", **kwargs) -> Dict[str, Any]:
        """Make a git commit"""
        git_tool = self.get_tool("git")
        if git_tool:
            return git_tool.quick_commit(message, files, **kwargs)
        return {"status": "error", "error": "Git tool not available"}
    
    def fetch_url(self, url: str, **kwargs) -> Dict[str, Any]:
        """Fetch a web page"""
        return self.execute_tool("web", operation="fetch_text", url=url, **kwargs)
    
    def search_files(self, search_term: str, **kwargs) -> Dict[str, Any]:
        """Search for text in files"""
        return self.execute_tool("file", operation="search", search_term=search_term, **kwargs)
    
    def analyze_project(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Analyze project to detect frameworks and libraries"""
        return self.execute_tool("project", operation="analyze", path=path)


# Tool managers are cached per resolved workspace. A single global instance can
# silently write generated files into the wrong project when tests or workflows
# use different roots.
_tool_managers: Dict[Path, ToolManager] = {}


def get_tool_manager(workspace_root: Optional[Path] = None) -> ToolManager:
    """Get or create a tool manager scoped to one resolved workspace."""
    root = (workspace_root or Path.cwd()).resolve()
    if root not in _tool_managers:
        _tool_managers[root] = ToolManager(root)
    return _tool_managers[root]
