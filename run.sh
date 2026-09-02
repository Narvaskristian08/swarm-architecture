#!/bin/bash
# NORA Run Script
# Quick script to activate environment and run

set -e  # Exit on error

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    echo "   Run: ./setup.sh"
    exit 1
fi

# Read LLM provider from .env if it exists
LLM_PROVIDER="llama_cpp"
if [ -f ".env" ]; then
    # Extract LLM_PROVIDER value
    PROVIDER_LINE=$(grep "^LLM_PROVIDER=" .env 2>/dev/null || echo "")
    if [ -n "$PROVIDER_LINE" ]; then
        LLM_PROVIDER=$(echo "$PROVIDER_LINE" | cut -d'=' -f2 | tr -d ' "'"'"'')
    fi
fi

# Warn if no LLM is configured (but still allow running)
echo "🤖 Checking LLM configuration..."

if [ "$LLM_PROVIDER" = "ollama" ]; then
    echo "   Provider: Ollama"
    
    # Check if Ollama is accessible
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        MODEL_COUNT=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('models', [])))" 2>/dev/null || echo "0")
        if [ "$MODEL_COUNT" -gt 0 ]; then
            echo "   ✓ Ollama is ready with $MODEL_COUNT model(s)"
        else
            echo "   ⚠️  Ollama is running but no models found"
            echo "      Example: ollama pull qwen2.5:7b"
            echo ""
        fi
    else
        echo "   ⚠️  Cannot connect to Ollama"
        echo "      Start Ollama: ollama serve (in another terminal)"
        echo "      Or configure llama.cpp in .env"
        echo ""
    fi

elif [ "$LLM_PROVIDER" = "llama_cpp" ]; then
    echo "   Provider: llama.cpp (direct GGUF)"
    
    # Check if llama-cpp-python is installed
    if python -c "import llama_cpp" 2>/dev/null; then
        echo "   ✓ llama-cpp-python is installed"
        
        # Check if model path is configured
        if [ -f ".env" ]; then
            MODEL_PATH=$(grep "^LLAMA_MODEL_PATH=" .env | cut -d'=' -f2 | tr -d ' "'"'"'')
            if [ -n "$MODEL_PATH" ] && [ "$MODEL_PATH" != "" ]; then
                if [ -f "$MODEL_PATH" ]; then
                    echo "   ✓ Model file found: $MODEL_PATH"
                else
                    echo "   ⚠️  Model file not found: $MODEL_PATH"
                    echo "      Set LLAMA_MODEL_PATH in .env to your GGUF file"
                    echo ""
                fi
            else
                echo "   ⚠️  LLAMA_MODEL_PATH not set in .env"
                echo "      Set it to the path of your GGUF model file"
                echo ""
            fi
        fi
    else
        echo "   ⚠️  llama-cpp-python not installed"
        echo "      Install: pip install -r requirements-llama.txt"
        echo "      Or switch to Ollama in .env"
        echo ""
    fi
else
    echo "   ⚠️  Unknown provider: $LLM_PROVIDER"
    echo ""
fi

echo ""
echo "🚀 Starting NORA..."
echo "   Type 'doctor' in the CLI to check full system status"
echo "   Type 'help' to see available commands"
echo ""

# Run NORA
python main.py
