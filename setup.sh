#!/bin/bash
# AI Swarm Setup Script
# Run this once to set up everything

set -e  # Exit on error

echo "╔══════════════════════════════════════════╗"
echo "║     AI Swarm Setup Script                ║"
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

# Activate and install
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check Ollama
echo "🤖 Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found"
    echo "   Install from: https://ollama.ai"
    echo "   Or run: brew install ollama"
else
    echo "✓ Ollama installed"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo "✓ Ollama is running"
        
        # Check for model
        if ollama list | grep -q "qwen2.5:7b"; then
            echo "✓ Model qwen2.5:7b found"
        else
            echo "⚠️  Model qwen2.5:7b not found"
            echo "   Run: ollama pull qwen2.5:7b"
        fi
    else
        echo "⚠️  Ollama not running"
        echo "   Run in another terminal: ollama serve"
        echo "   Then run: ollama pull qwen2.5:7b"
    fi
fi
echo ""

# Setup .env
echo "⚙️  Configuring environment..."
if [ -f ".env" ]; then
    echo "✓ .env file already exists"
else
    cp .env.example .env
    echo "✓ Created .env from template"
fi
echo ""

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data
echo "✓ Data directory ready"
echo ""

echo "╔══════════════════════════════════════════╗"
echo "║          Setup Complete! 🎉               ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "🚀 To run the swarm:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "📖 For detailed guide, see: RUN_GUIDE.md"
echo ""
