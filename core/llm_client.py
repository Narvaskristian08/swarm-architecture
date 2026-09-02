"""Provider-neutral local LLM clients used by every NORA agent.

Neither provider downloads models.  The direct GGUF backend imports and loads
``llama_cpp`` lazily, so diagnostics and non-LLM commands work without it.
"""
from abc import ABC, abstractmethod
import importlib.util
import json
import logging
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Generator, List, Optional

import requests

from config import (
    LLAMA_CONTEXT_SIZE,
    LLAMA_GPU_LAYERS,
    LLAMA_MAX_TOKENS,
    LLAMA_MODEL_PATH,
    LLAMA_THREADS,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClientError(RuntimeError):
    """Raised when a configured LLM cannot satisfy a request."""


class LLMClient(ABC):
    """Small common interface shared by local inference providers."""

    provider: str

    @property
    @abstractmethod
    def model_identifier(self) -> str:
        """Human-readable configured model name or path."""

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Return provider readiness without downloading anything."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text from a prompt."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate a chat response."""

    def list_models(self) -> List[str]:
        """Return locally available models when the provider supports it."""
        return [self.model_identifier] if self.health().get("ready") else []


class OllamaClient(LLMClient):
    """HTTP client for a user-managed Ollama service."""

    provider = "ollama"
    
    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        timeout: int = OLLAMA_TIMEOUT
    ):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout

    @property
    def model_identifier(self) -> str:
        return self.model

    def health(self) -> Dict[str, Any]:
        """Check service availability and whether the configured tag exists."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = [item.get("name", "") for item in response.json().get("models", [])]
            ready = self.model in models
            return {
                "provider": self.provider,
                "ready": ready,
                "runtime_available": True,
                "model": self.model,
                "models": models,
                "message": (
                    "Ollama and the configured model are ready"
                    if ready
                    else f"Ollama is running, but model '{self.model}' is not available"
                ),
            }
        except requests.exceptions.RequestException as e:
            return {
                "provider": self.provider,
                "ready": False,
                "runtime_available": False,
                "model": self.model,
                "models": [],
                "message": f"Cannot connect to Ollama at {self.base_url}: {e}",
            }
    
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
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                stream=stream,
            )
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
    

class LlamaCppClient(LLMClient):
    """Lazy direct-GGUF client backed by the optional llama-cpp-python package."""

    provider = "llama_cpp"

    def __init__(
        self,
        model_path: str = LLAMA_MODEL_PATH,
        context_size: int = LLAMA_CONTEXT_SIZE,
        max_tokens: int = LLAMA_MAX_TOKENS,
        gpu_layers: int = LLAMA_GPU_LAYERS,
        threads: int = LLAMA_THREADS,
    ):
        self.model_path = Path(model_path).expanduser() if model_path else None
        self.context_size = context_size
        self.max_tokens = max_tokens
        self.gpu_layers = gpu_layers
        self.threads = threads
        self._model = None
        self._load_lock = Lock()

    @property
    def model_identifier(self) -> str:
        return str(self.model_path) if self.model_path else ""

    def health(self) -> Dict[str, Any]:
        runtime_available = importlib.util.find_spec("llama_cpp") is not None
        path_configured = self.model_path is not None
        model_exists = bool(path_configured and self.model_path.is_file())

        if not path_configured:
            message = "Set LLAMA_MODEL_PATH to the absolute path of a GGUF model"
        elif not model_exists:
            message = f"GGUF model not found at {self.model_path}"
        elif not runtime_available:
            message = (
                "llama-cpp-python is not installed; install requirements-llama.txt "
                "when you are ready to use the GGUF model"
            )
        else:
            message = "Direct GGUF runtime and model path are ready"

        return {
            "provider": self.provider,
            "ready": runtime_available and model_exists,
            "runtime_available": runtime_available,
            "model": self.model_identifier,
            "model_exists": model_exists,
            "loaded": self._model is not None,
            "message": message,
        }

    def _get_model(self):
        status = self.health()
        if not status["ready"]:
            raise LLMClientError(status["message"])

        if self._model is None:
            with self._load_lock:
                if self._model is None:
                    try:
                        from llama_cpp import Llama

                        kwargs = {
                            "model_path": str(self.model_path),
                            "n_ctx": self.context_size,
                            "n_gpu_layers": self.gpu_layers,
                            "verbose": False,
                        }
                        if self.threads > 0:
                            kwargs["n_threads"] = self.threads
                        self._model = Llama(**kwargs)
                    except Exception as exc:
                        raise LLMClientError(
                            f"Failed to load GGUF model '{self.model_path}': {exc}"
                        ) from exc
        return self._model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        if stream:
            return {
                "response": "",
                "error": "Streaming is not exposed by the NORA llama.cpp adapter",
                "metadata": {"error": True, "provider": self.provider},
            }

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        started = datetime.now()
        try:
            result = self._get_model().create_completion(
                prompt=full_prompt,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature,
                stream=False,
            )
            return {
                "response": result.get("choices", [{}])[0].get("text", ""),
                "metadata": {
                    "provider": self.provider,
                    "model": self.model_identifier,
                    "duration_seconds": (datetime.now() - started).total_seconds(),
                    "usage": result.get("usage", {}),
                },
            }
        except LLMClientError as exc:
            return {
                "response": "",
                "error": str(exc),
                "metadata": {"error": True, "provider": self.provider},
            }

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        started = datetime.now()
        try:
            result = self._get_model().create_chat_completion(
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature,
                stream=False,
            )
            return {
                "response": (
                    result.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                ),
                "metadata": {
                    "provider": self.provider,
                    "model": self.model_identifier,
                    "duration_seconds": (datetime.now() - started).total_seconds(),
                    "usage": result.get("usage", {}),
                },
            }
        except LLMClientError as exc:
            return {
                "response": "",
                "error": str(exc),
                "metadata": {"error": True, "provider": self.provider},
            }


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
_llm_client: Optional[LLMClient] = None
_llm_provider: Optional[str] = None


def get_llm_client(provider: Optional[str] = None, reset: bool = False) -> LLMClient:
    """Get the configured local client without loading or downloading a model."""
    global _llm_client, _llm_provider

    selected = (provider or LLM_PROVIDER).strip().lower()
    if selected not in {"llama_cpp", "ollama"}:
        raise ValueError("provider must be 'llama_cpp' or 'ollama'")

    if reset or _llm_client is None or _llm_provider != selected:
        _llm_client = LlamaCppClient() if selected == "llama_cpp" else OllamaClient()
        _llm_provider = selected
    return _llm_client
