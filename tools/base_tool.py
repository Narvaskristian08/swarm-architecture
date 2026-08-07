"""
Base Tool Class
All tools inherit from this base class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Base class for all agent tools.
    Provides common interface and safety features.
    """
    
    def __init__(self, tool_id: str, name: str, description: str):
        self.tool_id = tool_id
        self.name = name
        self.description = description
        self.enabled = True
        self.usage_count = 0
        self.last_error: Optional[str] = None
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.
        
        Returns:
            Dictionary with 'status', 'result', and optional 'error'
        """
        pass
    
    @abstractmethod
    def validate_params(self, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Validate parameters before execution.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the tool with validation and error handling.
        """
        if not self.enabled:
            return {
                "status": "error",
                "error": f"Tool {self.name} is disabled"
            }
        
        # Validate parameters
        is_valid, error_msg = self.validate_params(**kwargs)
        if not is_valid:
            self.last_error = error_msg
            return {
                "status": "error",
                "error": error_msg
            }
        
        # Execute
        try:
            result = self.execute(**kwargs)
            self.usage_count += 1
            self.last_error = None
            return result
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Tool {self.name} execution failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "usage_count": self.usage_count,
            "last_error": self.last_error
        }
    
    def enable(self):
        """Enable the tool"""
        self.enabled = True
    
    def disable(self):
        """Disable the tool"""
        self.enabled = False
    
    def reset_stats(self):
        """Reset usage statistics"""
        self.usage_count = 0
        self.last_error = None
