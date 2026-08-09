# ⚡ AI Swarm - Quickstart (2 Minutes)

## 🎯 Super Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
# One command to set everything up
./setup.sh

# Then run
./run.sh
```

### Option 2: Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy config
cp .env.example .env

# 5. Make sure Ollama is running (in another terminal)
ollama serve

# 6. Pull model (if not done already)
ollama pull qwen2.5:7b

# 7. Run!
python main.py
```

## 🎮 First Commands to Try

```bash
swarm> help                    # See all commands
swarm> agents                  # List agents
swarm> suggest web framework   # Get AI recommendation
swarm> check-project          # Analyze your project
swarm> goal Create a Flask API # Give it a task
```

## 🚨 Common Issues

### "Cannot connect to Ollama"
```bash
# In another terminal:
ollama serve
```

### "Model not found"
```bash
ollama pull qwen2.5:7b
```

### "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 📖 Full Documentation

- **RUN_GUIDE.md** - Complete setup & usage guide
- **INTELLIGENT_RESEARCH.md** - Framework research system
- **INSTALLER_GUIDE.md** - Installation system details

## 🎉 That's It!

You're ready to use the AI Swarm! Just describe what you need:

```bash
swarm> goal Build a license plate detector
```

The swarm will handle everything else! 🤖✨
