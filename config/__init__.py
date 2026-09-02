"""Environment-backed configuration for NORA.

The project ``.env`` file is loaded here, before any constants are evaluated.
Real environment variables keep precedence over values in the file.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)


def _path_from_env(name: str, default: str) -> Path:
    """Resolve a configurable path relative to the project root."""
    value = Path(os.getenv(name, default)).expanduser()
    return value if value.is_absolute() else (PROJECT_ROOT / value).resolve()


DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "swarm.db"
VECTOR_DB_PATH = _path_from_env("VECTOR_DB_PATH", "data/vector_store")
SWARM_WORKSPACE_PATH = _path_from_env("SWARM_WORKSPACE_PATH", "projects")

# LLM provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "llama_cpp").strip().lower()
if LLM_PROVIDER not in {"llama_cpp", "ollama"}:
    raise ValueError("LLM_PROVIDER must be 'llama_cpp' or 'ollama'")

# Direct GGUF / llama.cpp configuration. Importing NORA never loads the model;
# the client does so lazily on the first generation request.
LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", "").strip()
LLAMA_CONTEXT_SIZE = int(os.getenv("LLAMA_CONTEXT_SIZE", "8192"))
LLAMA_MAX_TOKENS = int(os.getenv("LLAMA_MAX_TOKENS", "2048"))
LLAMA_GPU_LAYERS = int(os.getenv("LLAMA_GPU_LAYERS", "0"))
LLAMA_THREADS = int(os.getenv("LLAMA_THREADS", "0"))

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))

# Memory configuration
MAX_SHORT_TERM_MESSAGES = int(os.getenv("MAX_SHORT_TERM_MESSAGES", "50"))
VECTOR_COLLECTION_NAME = os.getenv("VECTOR_COLLECTION_NAME", "swarm_knowledge")
SUMMARIZATION_THRESHOLD = int(os.getenv("SUMMARIZATION_THRESHOLD", "100"))
ENABLE_VECTOR_MEMORY = os.getenv("ENABLE_VECTOR_MEMORY", "false").lower() == "true"

# Safety configuration
REQUIRE_CONFIRMATION_FOR_DANGEROUS_COMMANDS = os.getenv("REQUIRE_CONFIRMATION", "true").lower() == "true"
DANGEROUS_COMMAND_PATTERNS = [
    r"rm\s+-rf",
    r"sudo\s+rm",
    r"del\s+/[sf]",
    r"format\s+",
    r"DROP\s+DATABASE",
    r"DROP\s+TABLE",
]

# Tool configuration
ENABLE_WEB_RESEARCH = os.getenv("ENABLE_WEB_RESEARCH", "true").lower() == "true"
ENABLE_GIT_TOOLS = os.getenv("ENABLE_GIT_TOOLS", "true").lower() == "true"
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = DATA_DIR / "swarm.log"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)
SWARM_WORKSPACE_PATH.mkdir(parents=True, exist_ok=True)

__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR",
    "DB_PATH",
    "VECTOR_DB_PATH",
    "SWARM_WORKSPACE_PATH",
    "LLM_PROVIDER",
    "LLAMA_MODEL_PATH",
    "LLAMA_CONTEXT_SIZE",
    "LLAMA_MAX_TOKENS",
    "LLAMA_GPU_LAYERS",
    "LLAMA_THREADS",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "OLLAMA_TIMEOUT",
    "MAX_SHORT_TERM_MESSAGES",
    "VECTOR_COLLECTION_NAME",
    "ENABLE_VECTOR_MEMORY",
    "REQUIRE_CONFIRMATION_FOR_DANGEROUS_COMMANDS",
    "DANGEROUS_COMMAND_PATTERNS",
    "ENABLE_WEB_RESEARCH",
    "ENABLE_GIT_TOOLS",
    "MAX_FILE_SIZE_MB",
    "LOG_LEVEL",
    "LOG_FILE",
]
