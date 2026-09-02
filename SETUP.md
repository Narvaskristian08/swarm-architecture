# NORA Setup Guide

Complete installation and configuration guide for NORA (Neural Orchestration & Research Assistant).

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [LLM Provider Configuration](#llm-provider-configuration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows (with WSL)
- **Python**: 3.9 or higher
- **RAM**: 8GB minimum (16GB recommended for larger models)
- **Disk**: 10GB free space (for models and dependencies)

### Recommended
- **RAM**: 16GB+ for optimal performance
- **CPU**: Modern multi-core processor
- **GPU**: Optional (Metal on macOS, CUDA on Linux/Windows) for faster inference

---

## Installation Methods

### Automated Setup (Recommended)

```bash
git clone https://github.com/Narvaskristian08/swarm-architecture.git
cd swarm-architecture
./setup.sh
```

The setup script will:
- Check Python version
- Create virtual environment
- Install core dependencies
- Check for LLM providers
- Create configuration files
- Create data and workspace directories

### Manual Setup

If you prefer manual installation or the automated script fails:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install core dependencies
pip install -r requirements.txt

# 3. Create configuration
cp .env.example .env

# 4. Create directories
mkdir -p data projects

# 5. (Optional) Install llama-cpp-python
pip install -r requirements-llama.txt
```

---

## LLM Provider Configuration

NORA supports two LLM backends. Choose ONE based on your needs:

### Option 1: llama.cpp (Direct GGUF Inference) - DEFAULT

**Pros:**
- No separate server needed
- Direct model loading
- Fine control over model parameters
- Works offline completely

**Cons:**
- Requires downloading GGUF model files
- Compilation may be needed for GPU support

#### Setup Steps:

1. **Download a GGUF Model**

Popular options:
- [Qwen2.5-7B-Instruct-Q4_K_M.gguf](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/blob/main/qwen2.5-7b-instruct-q4_k_m.gguf) (~4.4GB)
- [Llama-3.2-3B-Instruct-Q4_K_M.gguf](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/blob/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf) (~1.9GB)
- [Mistral-7B-Instruct-v0.3-Q4_K_M.gguf](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.3-GGUF/blob/main/mistral-7b-instruct-v0.3.Q4_K_M.gguf) (~4.4GB)

Download to a known location, e.g., `~/models/qwen2.5-7b-instruct-q4_k_m.gguf`

2. **Install llama-cpp-python**

For **CPU-only** (simplest):
```bash
pip install -r requirements-llama.txt
```

For **Metal** (Apple Silicon):
```bash
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
```

For **CUDA** (NVIDIA GPUs):
```bash
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```

For **ROCm** (AMD GPUs):
```bash
CMAKE_ARGS="-DLLAMA_HIPBLAS=on" pip install llama-cpp-python
```

3. **Configure .env**

Edit `.env` and set:

```bash
LLM_PROVIDER=llama_cpp
LLAMA_MODEL_PATH=/absolute/path/to/your/model.gguf
LLAMA_CONTEXT_SIZE=8192
LLAMA_MAX_TOKENS=2048
LLAMA_GPU_LAYERS=0        # 0 for CPU, -1 for all GPU layers, or specific number
LLAMA_THREADS=0           # 0 for auto-detect
```

**Important:** Use the full absolute path to your GGUF file.

### Option 2: Ollama (Server-Based)

**Pros:**
- Easier initial setup
- No manual model downloads
- Automatic model management
- Multiple models available via `ollama pull`

**Cons:**
- Requires Ollama server running
- Less control over model parameters
- Slight overhead from HTTP communication

#### Setup Steps:

1. **Install Ollama**

```bash
# macOS or Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or on macOS with Homebrew
brew install ollama
```

Windows: Download from [ollama.ai](https://ollama.ai)

2. **Start Ollama Server**

```bash
ollama serve
```

Leave this running in a separate terminal.

3. **Pull a Model**

```bash
# Recommended: Qwen2.5 7B (good balance of speed and quality)
ollama pull qwen2.5:7b

# Alternative smaller model (faster, less capable)
ollama pull qwen2.5:3b

# Alternative larger model (slower, more capable)
ollama pull qwen2.5:14b
```

4. **Configure .env**

Edit `.env` and set:

```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=120
```

---

## Verification

After setup, verify your installation:

### 1. Start NORA

```bash
./run.sh
# or
source venv/bin/activate && python main.py
```

### 2. Run Doctor Command

In the NORA CLI:

```
nora> doctor
```

This will check:
- Python version
- Orchestrator status
- Workspace configuration
- LLM provider status
- Registered agents
- Available tools
- Memory system

### 3. Check Status

```
nora> status
```

Should show:
- Orchestrator: ready
- LLM Provider: your configured provider
- Model Status: Ready (if model is available)

### 4. Test with Simple Goal

```
nora> goal Create a simple Python calculator
```

If everything is configured correctly, NORA will:
1. Plan the implementation
2. Generate code
3. Create files in `./projects/calculator/`

---

## Troubleshooting

### Common Issues

#### "LLAMA_MODEL_PATH not set" or "Model file not found"

**Solution:**
- Verify the path in `.env` is absolute (starts with `/` on Linux/macOS or `C:\` on Windows)
- Check the file exists: `ls -lh /path/to/model.gguf`
- Ensure no typos in the path

#### "llama-cpp-python is not installed"

**Solution:**
```bash
pip install -r requirements-llama.txt
```

For GPU support, see [Option 1 Setup Steps](#option-1-llamacpp-direct-gguf-inference---default).

#### "Cannot connect to Ollama"

**Solution:**
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Start Ollama: `ollama serve`
3. Verify model is pulled: `ollama list`

#### "Model qwen2.5:7b is not available"

**Solution:**
```bash
ollama pull qwen2.5:7b
```

#### "Request timed out"

**Solution:**
- Increase timeout in `.env`: `OLLAMA_TIMEOUT=300`
- Use a smaller model (qwen2.5:3b instead of 7b)
- Add more RAM or enable GPU acceleration

#### Import errors or missing dependencies

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

#### "Permission denied" when running scripts

**Solution:**
```bash
chmod +x setup.sh run.sh
```

---

## Switching Between Providers

You can easily switch between llama.cpp and Ollama:

1. Edit `.env`
2. Change `LLM_PROVIDER=llama_cpp` or `LLM_PROVIDER=ollama`
3. Ensure the appropriate dependencies are installed
4. Restart NORA

No code changes needed!

---

## Advanced Configuration

### Memory System

Enable vector memory for semantic search (optional):

```bash
ENABLE_VECTOR_MEMORY=true
VECTOR_DB_PATH=./data/vector_store
```

### Workspace Location

Change where NORA creates projects:

```bash
SWARM_WORKSPACE_PATH=/path/to/your/projects
```

### Model Parameters (llama.cpp)

Fine-tune model behavior:

```bash
LLAMA_CONTEXT_SIZE=8192    # Increase for longer conversations
LLAMA_MAX_TOKENS=4096      # Max tokens per response
LLAMA_GPU_LAYERS=35        # GPU acceleration (model-specific)
LLAMA_THREADS=8            # CPU threads (0 = auto)
```

### Safety Settings

```bash
REQUIRE_CONFIRMATION=true   # Confirm before installing packages
LOG_LEVEL=INFO             # DEBUG, INFO, WARNING, ERROR
```

---

## Next Steps

Once setup is complete:

1. Read the [Quick Start Guide](QUICKSTART.md)
2. See [Run Guide](RUN_GUIDE.md) for usage instructions
3. Check [Examples](EXAMPLES.md) for sample workflows
4. Review [Features](FEATURES.md) for detailed capabilities

---

## Getting Help

If you encounter issues not covered here:

1. Run `doctor` command in NORA CLI for diagnostics
2. Check the logs in `data/swarm.log`
3. Review error messages carefully
4. Open an issue on GitHub with:
   - OS and Python version
   - Output of `doctor` command
   - Error messages
   - Steps to reproduce

---

**Need More Help?**
- Run `help` in NORA CLI for command reference
- See `TESTING_GUIDE.md` for validation procedures
- Check existing GitHub issues
