#!/bin/bash
# AI Swarm Run Script
# Quick script to activate environment and run

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    echo "Run ./setup.sh first"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "⚠️  Warning: Ollama doesn't appear to be running"
    echo "   Start it with: ollama serve"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run the swarm
python main.py
