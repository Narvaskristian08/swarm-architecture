"""
File Tool
Provides safe file operations for agents.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from .base_tool import BaseTool
from config import MAX_FILE_SIZE_MB

logger = logging.getLogger(__name__)


class FileTool(BaseTool):
    """
    File operations tool.
    Allows agents to read, write, and search files safely.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        super().__init__(
            tool_id="file_tool",
            name="File Tool",
            description="Read, write, and search files"
        )
        self.workspace_root = workspace_root or Path.cwd()
        self.max_file_size = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
    
    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute a file operation"""
        operations = {
            "read": self._read_file,
            "write": self._write_file,
            "append": self._append_file,
            "delete": self._delete_file,
            "list": self._list_files,
            "exists": self._check_exists,
            "search": self._search_files,
            "get_info": self._get_file_info,
        }
        
        if operation not in operations:
            return {
                "status": "error",
                "error": f"Unknown operation: {operation}"
            }
        
        return operations[operation](**kwargs)
    
    def validate_params(self, operation: str, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate parameters"""
        if not operation:
            return False, "Operation is required"
        
        # Validate file path for operations that require it
        if operation in ["read", "write", "append", "delete", "exists", "get_info"]:
            file_path = kwargs.get("file_path")
            if not file_path:
                return False, f"file_path is required for operation: {operation}"
            
            # Check if path is within workspace (security)
            try:
                full_path = (self.workspace_root / file_path).resolve()
                if not str(full_path).startswith(str(self.workspace_root.resolve())):
                    return False, "Path must be within workspace root"
            except Exception as e:
                return False, f"Invalid path: {e}"
        
        return True, None
    
    def _read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read file contents"""
        try:
            full_path = self.workspace_root / file_path
            
            # Check size
            if full_path.stat().st_size > self.max_file_size:
                return {
                    "status": "error",
                    "error": f"File too large (max {MAX_FILE_SIZE_MB}MB)"
                }
            
            # Read file
            with open(full_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "status": "success",
                "content": content,
                "file_path": str(file_path),
                "size": full_path.stat().st_size
            }
        
        except FileNotFoundError:
            return {
                "status": "error",
                "error": f"File not found: {file_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to read file: {e}"
            }
    
    def _write_file(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> Dict[str, Any]:
        """Write content to file"""
        try:
            full_path = self.workspace_root / file_path
            
            # Create directories if needed
            if create_dirs:
                full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {
                "status": "success",
                "message": f"File written: {file_path}",
                "file_path": str(file_path),
                "size": full_path.stat().st_size
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to write file: {e}"
            }
    
    def _append_file(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """Append content to file"""
        try:
            full_path = self.workspace_root / file_path
            
            # Append to file
            with open(full_path, 'a', encoding=encoding) as f:
                f.write(content)
            
            return {
                "status": "success",
                "message": f"Content appended to: {file_path}",
                "file_path": str(file_path),
                "size": full_path.stat().st_size
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to append to file: {e}"
            }
    
    def _delete_file(self, file_path: str, confirm: bool = False) -> Dict[str, Any]:
        """Delete a file"""
        if not confirm:
            return {
                "status": "error",
                "error": "File deletion requires confirmation (confirm=True)"
            }
        
        try:
            full_path = self.workspace_root / file_path
            
            if not full_path.exists():
                return {
                    "status": "error",
                    "error": f"File not found: {file_path}"
                }
            
            full_path.unlink()
            
            return {
                "status": "success",
                "message": f"File deleted: {file_path}"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to delete file: {e}"
            }
    
    def _list_files(
        self,
        directory: str = ".",
        pattern: str = "*",
        recursive: bool = False
    ) -> Dict[str, Any]:
        """List files in directory"""
        try:
            dir_path = self.workspace_root / directory
            
            if not dir_path.is_dir():
                return {
                    "status": "error",
                    "error": f"Not a directory: {directory}"
                }
            
            # List files
            if recursive:
                files = [str(p.relative_to(self.workspace_root)) 
                        for p in dir_path.rglob(pattern) if p.is_file()]
            else:
                files = [str(p.relative_to(self.workspace_root))
                        for p in dir_path.glob(pattern) if p.is_file()]
            
            return {
                "status": "success",
                "files": files,
                "count": len(files),
                "directory": str(directory)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to list files: {e}"
            }
    
    def _check_exists(self, file_path: str) -> Dict[str, Any]:
        """Check if file exists"""
        try:
            full_path = self.workspace_root / file_path
            exists = full_path.exists()
            
            result = {
                "status": "success",
                "exists": exists,
                "file_path": str(file_path)
            }
            
            if exists:
                result["is_file"] = full_path.is_file()
                result["is_dir"] = full_path.is_dir()
                if full_path.is_file():
                    result["size"] = full_path.stat().st_size
            
            return result
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to check existence: {e}"
            }
    
    def _search_files(
        self,
        search_term: str,
        directory: str = ".",
        file_pattern: str = "*",
        case_sensitive: bool = False
    ) -> Dict[str, Any]:
        """Search for text in files"""
        try:
            dir_path = self.workspace_root / directory
            matches = []
            
            # Search files
            for file_path in dir_path.rglob(file_pattern):
                if not file_path.is_file():
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Search
                    search_content = content if case_sensitive else content.lower()
                    search_pattern = search_term if case_sensitive else search_term.lower()
                    
                    if search_pattern in search_content:
                        # Find line numbers
                        lines = content.split('\n')
                        matching_lines = [
                            (i + 1, line) for i, line in enumerate(lines)
                            if search_pattern in (line if case_sensitive else line.lower())
                        ]
                        
                        matches.append({
                            "file": str(file_path.relative_to(self.workspace_root)),
                            "matches": len(matching_lines),
                            "lines": matching_lines[:5]  # First 5 matches
                        })
                
                except Exception:
                    continue  # Skip files that can't be read
            
            return {
                "status": "success",
                "search_term": search_term,
                "matches": matches,
                "files_found": len(matches)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Search failed: {e}"
            }
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""
        try:
            full_path = self.workspace_root / file_path
            
            if not full_path.exists():
                return {
                    "status": "error",
                    "error": f"File not found: {file_path}"
                }
            
            stat = full_path.stat()
            
            return {
                "status": "success",
                "file_path": str(file_path),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "is_file": full_path.is_file(),
                "is_dir": full_path.is_dir(),
                "extension": full_path.suffix
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to get file info: {e}"
            }
