"""
Configuration Management
"""
import os
from pathlib import Path
from typing import Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "swarm.db"
VECTOR_DB_PATH = DATA_DIR / "vector_store"

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))

# Memory configuration
MAX_SHORT_TERM_MESSAGES = int(os.getenv("MAX_SHORT_TERM_MESSAGES", "50"))
VECTOR_COLLECTION_NAME = os.getenv("VECTOR_COLLECTION_NAME", "swarm_knowledge")
SUMMARIZATION_THRESHOLD = int(os.getenv("SUMMARIZATION_THRESHOLD", "100"))

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

__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR",
    "DB_PATH",
    "VECTOR_DB_PATH",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "OLLAMA_TIMEOUT",
    "MAX_SHORT_TERM_MESSAGES",
    "VECTOR_COLLECTION_NAME",
    "REQUIRE_CONFIRMATION_FOR_DANGEROUS_COMMANDS",
    "DANGEROUS_COMMAND_PATTERNS",
    "ENABLE_WEB_RESEARCH",
    "ENABLE_GIT_TOOLS",
    "MAX_FILE_SIZE_MB",
    "LOG_LEVEL",
    "LOG_FILE",
]
