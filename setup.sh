#!/bin/bash
# NORA Setup Script
# Run this once to set up the environment

set -e  # Exit on error

echo "╔══════════════════════════════════════════╗"
echo "║     NORA Setup Script                    ║"
echo "║  Neural Orchestration & Research Assistant"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check Python
echo "📋 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✓ Found $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate and install core dependencies
echo "📦 Installing core dependencies..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt
echo "✓ Core dependencies installed"
echo ""

# Setup .env
echo "⚙️  Configuring environment..."
if [ -f ".env" ]; then
    echo "✓ .env file already exists"
else
    cp .env.example .env
    echo "✓ Created .env from template"
    echo ""
    echo "   📝 Edit .env to configure your LLM provider:"
    echo "      - For llama.cpp: Set LLAMA_MODEL_PATH to your GGUF file"
    echo "      - For Ollama: Set OLLAMA_MODEL to your model name"
fi
echo ""

# Create required directories
echo "📁 Creating directories..."
mkdir -p data
mkdir -p projects
echo "✓ data/ - Database and logs"
echo "✓ projects/ - Generated applications (configurable via SWARM_WORKSPACE_PATH)"
echo ""

# Check LLM providers
echo "🤖 Checking LLM providers..."
echo ""

# Check for llama-cpp-python
if python -c "import llama_cpp" 2>/dev/null; then
    echo "✓ llama-cpp-python is installed (llama.cpp backend available)"
else
    echo "ℹ️  llama-cpp-python not installed (optional)"
    echo "   To use direct GGUF inference:"
    echo "   - For CPU: pip install -r requirements-llama.txt"
    echo "   - For Metal (macOS): CMAKE_ARGS=\"-DLLAMA_METAL=on\" pip install llama-cpp-python"
    echo "   - For CUDA: CMAKE_ARGS=\"-DLLAMA_CUBLAS=on\" pip install llama-cpp-python"
fi
echo ""

# Check Ollama
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo "✓ Ollama is running"
        
        # Check for models
        MODEL_COUNT=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
        if [ "$MODEL_COUNT" -gt 0 ]; then
            echo "✓ Found $MODEL_COUNT Ollama model(s)"
        else
            echo "ℹ️  No Ollama models found"
            echo "   Example: ollama pull qwen2.5:7b"
        fi
    else
        echo "ℹ️  Ollama installed but not running"
        echo "   Start with: ollama serve (in another terminal)"
    fi
else
    echo "ℹ️  Ollama not installed (optional)"
    echo "   Install from: https://ollama.ai"
    echo "   Or: brew install ollama"
fi
echo ""

echo "╔══════════════════════════════════════════╗"
echo "║          Setup Complete! 🎉               ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "🔧 Next Steps:"
echo ""
echo "1. Configure your LLM provider in .env:"
echo "   • For llama.cpp: Set LLAMA_MODEL_PATH=/path/to/model.gguf"
echo "   • For Ollama: Set OLLAMA_MODEL=qwen2.5:7b (or your model)"
echo ""
echo "2. (Optional) Install llama-cpp-python if using GGUF:"
echo "   pip install -r requirements-llama.txt"
echo ""
echo "3. Run NORA:"
echo "   ./run.sh"
echo "   or: source venv/bin/activate && python main.py"
echo ""
echo "4. Check system status:"
echo "   Run 'doctor' command in NORA CLI"
echo ""
echo "📖 For more details:"
echo "   • Quick Start: QUICKSTART.md"
echo "   • Setup Guide: SETUP.md"
echo "   • Run Guide: RUN_GUIDE.md"
echo ""
