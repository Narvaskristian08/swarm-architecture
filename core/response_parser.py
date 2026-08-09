"""
Response Parser
Utilities for parsing and validating LLM responses
"""
import json
import re
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parse and validate LLM responses"""
    
    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from LLM response, handling markdown code blocks.
        
        Args:
            text: The response text
            
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        # Try to find JSON in code blocks first
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Try to find raw JSON
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            # Try the longest match first (most likely to be complete)
            for match in sorted(matches, key=len, reverse=True):
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Try parsing the entire text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Could not extract JSON from response")
            return None
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[Dict[str, str]]:
        """
        Extract code blocks from markdown text.
        
        Returns:
            List of dicts with 'language' and 'code' keys
        """
        pattern = r'```(\w+)?\s*\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        code_blocks = []
        for language, code in matches:
            code_blocks.append({
                "language": language or "unknown",
                "code": code.strip()
            })
        
        return code_blocks
    
    @staticmethod
    def extract_list(text: str) -> List[str]:
        """
        Extract a list from text (numbered or bulleted).
        
        Returns:
            List of items
        """
        items = []
        
        # Try numbered lists (1. item or 1) item)
        numbered_pattern = r'^\d+[\.)]\s*(.+)$'
        
        # Try bulleted lists (- item or * item)
        bullet_pattern = r'^[\-\*]\s*(.+)$'
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check numbered
            match = re.match(numbered_pattern, line)
            if match:
                items.append(match.group(1).strip())
                continue
            
            # Check bulleted
            match = re.match(bullet_pattern, line)
            if match:
                items.append(match.group(1).strip())
                continue
        
        return items
    
    @staticmethod
    def validate_plan(plan: Dict[str, Any]) -> bool:
        """
        Validate a plan structure from Planner agent.
        
        Expected structure:
        {
            "goal": "...",
            "tasks": [{"description": "...", "dependencies": [...]}],
            "resources": [...]
        }
        """
        required_keys = ["goal", "tasks"]
        
        if not all(key in plan for key in required_keys):
            logger.warning(f"Plan missing required keys: {required_keys}")
            return False
        
        if not isinstance(plan["tasks"], list):
            logger.warning("Plan tasks must be a list")
            return False
        
        for task in plan["tasks"]:
            if not isinstance(task, dict) or "description" not in task:
                logger.warning("Each task must have a description")
                return False
        
        return True
    
    @staticmethod
    def validate_workflow(workflow: Dict[str, Any]) -> bool:
        """
        Validate a workflow structure from Orchestrator agent.
        
        Expected structure:
        {
            "phases": [...],
            "agent_assignments": {...},
            "dependencies": {...}
        }
        """
        required_keys = ["phases", "agent_assignments"]
        
        if not all(key in workflow for key in required_keys):
            logger.warning(f"Workflow missing required keys: {required_keys}")
            return False
        
        if not isinstance(workflow["phases"], list):
            logger.warning("Workflow phases must be a list")
            return False
        
        if not isinstance(workflow["agent_assignments"], dict):
            logger.warning("Agent assignments must be a dict")
            return False
        
        return True
    
    @staticmethod
    def extract_sections(text: str) -> Dict[str, str]:
        """
        Extract sections from text based on headers.
        
        Returns:
            Dict mapping section names to content
        """
        sections = {}
        current_section = "intro"
        current_content = []
        
        for line in text.split('\n'):
            # Check for markdown headers
            header_match = re.match(r'^#+\s+(.+)$', line)
            if header_match:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = header_match.group(1).lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    @staticmethod
    def clean_response(text: str) -> str:
        """
        Clean up LLM response by removing common artifacts.
        """
        # Remove multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_action(text: str) -> Optional[Dict[str, Any]]:
        """
        Extract an action from agent response.
        
        Looks for patterns like:
        ACTION: tool_name
        PARAMETERS: {...}
        """
        action_pattern = r'ACTION:\s*(\w+)'
        param_pattern = r'PARAMETERS:\s*(\{.*?\})'
        
        action_match = re.search(action_pattern, text, re.IGNORECASE)
        param_match = re.search(param_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if action_match:
            action = {
                "action": action_match.group(1),
                "parameters": {}
            }
            
            if param_match:
                try:
                    action["parameters"] = json.loads(param_match.group(1))
                except json.JSONDecodeError:
                    logger.warning("Could not parse action parameters")
            
            return action
        
        return None