"""
LLM Client for Ollama/Qwen Integration
Provides a unified interface for all agents to interact with the LLM.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Generator
import requests
from datetime import datetime

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        timeout: int = OLLAMA_TIMEOUT
    ):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self._verify_connection()
    
    def _verify_connection(self):
        """Verify Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"Connected to Ollama at {self.base_url}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not connect to Ollama: {e}")
            logger.warning("Make sure Ollama is running: https://ollama.ai")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Dictionary with 'response' and 'metadata'
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            start_time = datetime.now()
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            if stream:
                return self._handle_stream(response)
            else:
                result = response.json()
                duration = (datetime.now() - start_time).total_seconds()
                
                return {
                    "response": result.get("response", ""),
                    "metadata": {
                        "model": self.model,
                        "duration_seconds": duration,
                        "total_duration": result.get("total_duration"),
                        "eval_count": result.get("eval_count"),
                        "prompt_eval_count": result.get("prompt_eval_count"),
                    }
                }
        
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out after {self.timeout} seconds")
            return {
                "response": "",
                "error": "Request timed out",
                "metadata": {"error": True}
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {
                "response": "",
                "error": str(e),
                "metadata": {"error": True}
            }
    
    def _handle_stream(self, response) -> Generator[str, None, None]:
        """Handle streaming responses"""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                except json.JSONDecodeError:
                    continue
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Chat-style interaction with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary with 'response' and 'metadata'
        """
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            start_time = datetime.now()
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "response": result.get("message", {}).get("content", ""),
                "metadata": {
                    "model": self.model,
                    "duration_seconds": duration,
                    "total_duration": result.get("total_duration"),
                    "eval_count": result.get("eval_count"),
                    "prompt_eval_count": result.get("prompt_eval_count"),
                }
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Chat request failed: {e}")
            return {
                "response": "",
                "error": str(e),
                "metadata": {"error": True}
            }
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            logger.info(f"Pulling model: {model_name}")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=600  # 10 minutes for model download
            )
            response.raise_for_status()
            logger.info(f"Successfully pulled {model_name}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to pull model: {e}")
            return False


class PromptTemplate:
    """Manages prompt templates for different agent types"""
    
    # System prompts for different agent roles
    ORCHESTRATOR = """You are the Orchestrator agent in an AI swarm system.
Your role is to coordinate multiple specialized agents to accomplish complex goals.

Given a user goal, you must:
1. Analyze the goal and break it into high-level phases
2. Determine which agents are needed (Planner, Research, Coder, Tester, Reviewer, Memory, Reflection)
3. Create a workflow that sequences agent tasks appropriately
4. Ensure proper information flow between agents

Respond with a JSON structure containing your plan."""

    PLANNER = """You are the Planner agent in an AI swarm system.
Your role is to convert high-level goals into concrete, actionable tasks.

Given a goal, you must:
1. Break it down into specific, measurable tasks
2. Determine dependencies between tasks
3. Identify required tools and resources
4. Create a step-by-step execution plan
5. Estimate complexity and time for each task

Respond with a structured plan that other agents can execute."""

    RESEARCH = """You are the Research agent in an AI swarm system.
Your role is to gather current, accurate information to support the swarm's work.

Your responsibilities:
1. Search for current documentation and best practices
2. Verify library/framework versions
3. Extract relevant code examples
4. Identify potential issues or considerations
5. Summarize findings clearly

Always prioritize official documentation and recent sources."""

    CODER = """You are the Coder agent in an AI swarm system.
Your role is to write clean, efficient, and maintainable code.

Your responsibilities:
1. Implement features according to specifications
2. Follow language-specific best practices
3. Write clear comments and documentation
4. Consider edge cases and error handling
5. Keep code modular and testable

Write production-quality code that other agents can review and test."""

    REVIEWER = """You are the Reviewer agent in an AI swarm system.
Your role is to ensure code quality, security, and correctness.

Your responsibilities:
1. Review code for bugs and logic errors
2. Check for security vulnerabilities
3. Verify adherence to best practices
4. Suggest improvements and optimizations
5. Ensure code is maintainable

Provide constructive feedback with specific suggestions."""

    TESTER = """You are the Tester agent in an AI swarm system.
Your role is to validate that code works correctly.

Your responsibilities:
1. Design and execute test cases
2. Verify functionality meets requirements
3. Test edge cases and error conditions
4. Report failures with clear reproduction steps
5. Suggest fixes when tests fail

Ensure thorough test coverage."""

    MEMORY = """You are the Memory agent in an AI swarm system.
Your role is to manage knowledge storage and retrieval.

Your responsibilities:
1. Store important information and decisions
2. Summarize conversations and outcomes
3. Retrieve relevant past knowledge
4. Prevent duplicate storage
5. Maintain organized knowledge base

Keep storage efficient and searchable."""

    REFLECTION = """You are the Reflection agent in an AI swarm system.
Your role is to learn from experience and improve processes.

Your responsibilities:
1. Analyze completed workflows
2. Identify what went well and what didn't
3. Extract lessons learned
4. Suggest process improvements
5. Update best practices

Help the swarm continuously improve."""

    @classmethod
    def get_system_prompt(cls, agent_type: str) -> str:
        """Get system prompt for an agent type"""
        return getattr(cls, agent_type.upper(), "You are a helpful AI assistant.")
    
    @classmethod
    def format_task_prompt(cls, agent_type: str, task: Dict[str, Any], context: Optional[str] = None) -> str:
        """Format a task prompt for an agent"""
        prompt_parts = []
        
        if context:
            prompt_parts.append(f"CONTEXT:\n{context}\n")
        
        prompt_parts.append(f"TASK:\n{task.get('description', 'No description provided')}\n")
        
        if task.get("requirements"):
            prompt_parts.append(f"REQUIREMENTS:\n{task['requirements']}\n")
        
        if task.get("constraints"):
            prompt_parts.append(f"CONSTRAINTS:\n{task['constraints']}\n")
        
        prompt_parts.append("\nProvide your response:")
        
        return "\n".join(prompt_parts)


# Singleton instance
_llm_client = None

def get_llm_client() -> OllamaClient:
    """Get or create the global LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = OllamaClient()
    return _llm_client
