# AI Swarm Setup Guide

Complete setup instructions for the Local AI Swarm system.

## Prerequisites

- Python 3.9 or higher
- macOS, Linux, or Windows
- 8GB+ RAM recommended
- 2GB free disk space (for models)

## Step-by-Step Setup

### 1. Install Ollama

#### macOS
```bash
# Download from https://ollama.ai
# Or use Homebrew
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Download the installer from [https://ollama.ai](https://ollama.ai)

### 2. Start Ollama Service

```bash
# Start Ollama (runs in background)
ollama serve
```

### 3. Pull Qwen Model

```bash
# Pull the recommended model (7B parameters)
ollama pull qwen2.5:7b

# Verify installation
ollama list
```

**Alternative Models:**
- `qwen2.5:3b` - Lighter, faster (4GB RAM)
- `qwen2.5:14b` - More capable (16GB RAM)
- `llama3:8b` - Alternative LLM

### 4. Clone/Download Project

```bash
git clone <repository-url>
cd ai-swarm
```

### 5. Set Up Python Environment

#### Using venv (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Using conda
```bash
conda create -n aiswarm python=3.10
conda activate aiswarm
```

### 6. Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- `ollama` - LLM client
- `chromadb` - Vector database
- `requests` - HTTP client
- `beautifulsoup4` - Web scraping
- `rich` - CLI interface
- `pydantic` - Data validation

### 7. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration (optional)
nano .env
```

**Key Settings:**
```bash
# Change model if using different one
OLLAMA_MODEL=qwen2.5:7b

# Adjust timeout for slower systems
OLLAMA_TIMEOUT=180

# Disable web research if needed
ENABLE_WEB_RESEARCH=false
```

### 8. Verify Installation

```bash
# Test Ollama connection
python -c "import ollama; print(ollama.list())"

# Test ChromaDB
python -c "import chromadb; print('ChromaDB OK')"
```

### 9. Run the Swarm

```bash
python main.py
```

You should see:
```
╔═══════════════════════════════════════╗
║     AI SWARM - Local Architecture     ║
║      Powered by Qwen via Ollama       ║
╚═══════════════════════════════════════╝

Initializing AI Swarm...
✓ Connected to Ollama (available models: X)
✓ Memory system ready
✓ Initialized 4 tools
✓ Registered 7 agents
✓ AI Swarm initialized successfully!

swarm>
```

## Troubleshooting

### Ollama Not Found

**Problem:** `Connection refused` or `Ollama not found`

**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# Check API endpoint
curl http://localhost:11434/api/tags
```

### Model Not Loaded

**Problem:** `Model not found` error

**Solution:**
```bash
# List available models
ollama list

# Pull the model
ollama pull qwen2.5:7b

# Verify it appears in list
ollama list
```

### ChromaDB Installation Issues

**Problem:** ChromaDB fails to install

**Solution:**
```bash
# On macOS with Apple Silicon
pip install --upgrade pip
pip install chromadb

# If still failing, try without ChromaDB
# The system will work without vector memory
```

### Memory Errors

**Problem:** Out of memory when running model

**Solution:**
```bash
# Use smaller model
ollama pull qwen2.5:3b

# Update .env
OLLAMA_MODEL=qwen2.5:3b

# Or reduce context in config
MAX_SHORT_TERM_MESSAGES=20
```

### Permission Errors

**Problem:** Cannot write to `data/` directory

**Solution:**
```bash
# Create data directory
mkdir -p data

# Fix permissions
chmod 755 data

# Or change data location in .env
```

### Import Errors

**Problem:** `ModuleNotFoundError`

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check Python version
python --version  # Should be 3.9+

# Check pip version
pip --version
```

## Optional Enhancements

### Use GPU Acceleration (if available)

Ollama automatically uses GPU if available. To verify:
```bash
# Check GPU usage while model is running
ollama info
```

### Increase Performance

1. **Use Smaller Model**: `qwen2.5:3b`
2. **Reduce Temperature**: Lower values in prompts
3. **Limit Context**: Reduce `MAX_SHORT_TERM_MESSAGES`
4. **Close Other Apps**: Free up RAM

### Enable Advanced Features

```bash
# In .env

# Enable all web research
ENABLE_WEB_RESEARCH=true

# Enable git operations
ENABLE_GIT_TOOLS=true

# Increase file size limit
MAX_FILE_SIZE_MB=50
```

## Testing Installation

### Quick Test

```bash
python main.py
```

At the prompt:
```bash
swarm> status
swarm> agents
swarm> quit
```

### Test Individual Components

```python
# test_setup.py
from core import get_llm_client
from memory import get_memory_manager
from tools import get_tool_manager

# Test LLM
llm = get_llm_client()
result = llm.generate("Hello!")
print("LLM:", result.get("response")[:50])

# Test Memory
mem = get_memory_manager()
stats = mem.get_statistics()
print("Memory:", stats)

# Test Tools
tools = get_tool_manager()
print("Tools:", len(tools.list_tools()))

print("All tests passed!")
```

Run: `python test_setup.py`

## Uninstallation

```bash
# Remove virtual environment
deactivate
rm -rf venv/

# Remove data
rm -rf data/

# Remove Ollama (optional)
# macOS
brew uninstall ollama

# Linux
sudo rm -rf /usr/local/bin/ollama
```

## Next Steps

1. Read [README.md](README.md) for usage examples
2. Try the example workflows
3. Customize agent behaviors
4. Add your own tools and agents

## Support

For issues:
1. Check troubleshooting section
2. Verify Ollama is running: `ollama list`
3. Check logs in `data/swarm.log`
4. Review configuration in `.env`

## System Requirements Summary

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.9 | 3.10+ |
| **RAM** | 4GB | 8GB+ |
| **Storage** | 5GB | 10GB+ |
| **CPU** | Any | Multi-core |
| **GPU** | None | Optional (faster) |

## Performance Benchmarks

Model response times (approximate):

| Model | RAM Usage | Speed | Quality |
|-------|-----------|-------|---------|
| qwen2.5:3b | 3-4GB | Fast (1-3s) | Good |
| qwen2.5:7b | 6-8GB | Medium (2-5s) | Better |
| qwen2.5:14b | 12-16GB | Slow (5-15s) | Best |

*Times vary by hardware and prompt complexity*
