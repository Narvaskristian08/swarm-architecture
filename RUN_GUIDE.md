# 🚀 AI Swarm - Complete Setup & Run Guide

## 📋 Prerequisites

Before you start, make sure you have:
- **Python 3.9+** installed
- **Ollama** installed and running
- **Git** (you already have this)

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Create Virtual Environment
```bash
cd /Users/deb/ai-swarm

# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# You should see (venv) in your terminal prompt now
```

### Step 2: Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

This installs:
- `requests` - Web requests
- `python-dotenv` - Environment variables
- `chromadb` - Vector database
- `rich` - Beautiful terminal output
- `beautifulsoup4` - Web scraping

### Step 3: Set Up Ollama

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai or use:
brew install ollama  # macOS

# Start Ollama
ollama serve

# In another terminal, pull the Qwen model
ollama pull qwen2.5:7b
```

### Step 4: Configure Environment
```bash
# Copy the example config
cp .env.example .env

# Edit .env if needed (optional - defaults work fine)
nano .env  # or use any editor
```

### Step 5: Run the Swarm!
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the swarm
python main.py
```

---

## 🎮 Using the Swarm

### Basic Commands

Once running, you'll see:
```
╔══════════════════════════════════════════╗
║         AI Swarm System v1.0             ║
╚══════════════════════════════════════════╝

✓ Connected to Ollama (available models: 3)
✓ Memory system ready
✓ Initialized 6 tools
✓ Registered 8 agents

swarm> _
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show all commands | `help` |
| `goal <description>` | Give the swarm a task | `goal Create a REST API` |
| `status` | System status | `status` |
| `agents` | List all agents | `agents` |
| `check-project` | Analyze current project | `check-project` |
| `research-frameworks` | Auto-research frameworks | `research-frameworks` |
| `suggest <purpose>` | AI suggests framework | `suggest object detection` |
| `install <framework>` | Install a framework | `install ultralytics` |
| `clear` | Clear screen | `clear` |
| `exit` or `quit` | Exit swarm | `exit` |

---

## 💡 Example Usage Scenarios

### Scenario 1: Build a License Plate Detector

```bash
swarm> goal Build a system that detects license plates and cars

# The swarm will:
# 1. Create a plan (Planner Agent)
# 2. Research YOLO and OCR (Research Agent)
# 3. Suggest frameworks (Installer Agent)
# 4. Write the code (Coder Agent)
# 5. Create tests (Tester Agent)
# 6. Review everything (Reviewer Agent)
```

### Scenario 2: Need Help Choosing a Framework

```bash
swarm> suggest web framework for Python REST API

# AI Response:
Recommended: fastapi
Why: Modern, fast, automatic docs, type hints, async support
Alternatives: flask, django
Install: pip install fastapi

swarm> install fastapi

# System will:
# 1. Research FastAPI
# 2. Check if installed
# 3. Ask confirmation
# 4. Install it
# 5. Verify success
```

### Scenario 3: Analyze Your Project

```bash
swarm> check-project

# Output:
Project Type: Python Application
Languages: Python
Libraries: 10 detected
  • requests
  • chromadb
  • rich
  ...

Recommendations:
  • Found 2 outdated packages
  • Run 'pip install --upgrade <package>'
```

### Scenario 4: Research Unknown Frameworks

```bash
swarm> research-frameworks

# System will:
# 1. Scan project files
# 2. Detect all frameworks
# 3. Research important ones
# 4. Store findings in memory
# 5. Provide recommendations
```

---

## 🔧 Troubleshooting

### Problem: "Cannot connect to Ollama"

**Solution:**
```bash
# Start Ollama in another terminal
ollama serve

# Pull a model if you haven't
ollama pull qwen2.5:7b
```

### Problem: "ChromaDB error"

**Solution:**
```bash
# Install/reinstall ChromaDB
pip install --upgrade chromadb

# If still failing, remove data directory
rm -rf data/
# Then restart
```

### Problem: "Module not found"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Problem: Virtual environment not working

**Solution:**
```bash
# Delete and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📂 Project Structure

```
ai-swarm/
├── venv/                      # Virtual environment (created)
├── data/                      # Runtime data (auto-created)
│   ├── swarm.db              # SQLite long-term memory
│   └── chroma_db/            # Vector memory
├── agents/                    # 8 Specialized agents
│   ├── planner.py            # Task planning
│   ├── coder.py              # Code generation
│   ├── reviewer.py           # Code review
│   ├── research.py           # Web research
│   ├── tester.py             # Test creation
│   ├── memory_agent.py       # Knowledge management
│   ├── reflection.py         # Learning & improvement
│   └── installer.py          # Framework installation
├── core/                      # Core system
│   ├── orchestrator.py       # Agent coordination
│   ├── base_agent.py         # Agent base class
│   ├── llm_client.py         # Ollama integration
│   └── response_parser.py    # LLM response parsing
├── memory/                    # 3-layer memory system
│   ├── short_term.py         # Runtime memory
│   ├── long_term.py          # SQLite persistence
│   ├── vector_memory.py      # ChromaDB semantic search
│   └── memory_manager.py     # Unified interface
├── tools/                     # Tool system
│   ├── file_tool.py          # File operations
│   ├── terminal_tool.py      # Command execution
│   ├── git_tool.py           # Version control
│   ├── web_tool.py           # Web scraping
│   └── project_analyzer.py   # Framework detection
├── examples/                  # Demo scripts
│   ├── auto_research_frameworks.py
│   └── demo_complete_workflow.py
├── main.py                    # Entry point
├── cli.py                     # Command-line interface
├── requirements.txt           # Dependencies
├── .env                       # Your config (don't commit)
└── .env.example              # Config template
```

---

## 🎯 Step-by-Step First Run

### Complete Walkthrough

```bash
# 1. Navigate to project
cd /Users/deb/ai-swarm

# 2. Create virtual environment (one-time)
python3 -m venv venv

# 3. Activate it (every time you start)
source venv/bin/activate

# 4. Install dependencies (one-time)
pip install -r requirements.txt

# 5. Make sure Ollama is running (in another terminal)
ollama serve

# 6. Make sure model is downloaded (one-time)
ollama pull qwen2.5:7b

# 7. Run the swarm
python main.py

# 8. Try a command
swarm> help
swarm> agents
swarm> suggest object detection
swarm> goal Create a hello world Flask app

# 9. Exit when done
swarm> exit
```

---

## 🔄 Daily Usage

Every time you want to use the swarm:

```bash
# Terminal 1: Start Ollama (if not running)
ollama serve

# Terminal 2: Run the swarm
cd /Users/deb/ai-swarm
source venv/bin/activate
python main.py
```

---

## 🎨 Demo Scripts

Try the example scripts:

```bash
# Activate environment first
source venv/bin/activate

# 1. Auto-research frameworks in your project
python examples/auto_research_frameworks.py

# 2. Complete workflow demo (suggestion → install)
python examples/demo_complete_workflow.py

# 3. YOLO research demo
python examples/demo_yolo_research.py
```

---

## ⚙️ Configuration Options

Edit `.env` to customize:

```bash
# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# Memory settings
ENABLE_VECTOR_MEMORY=true
VECTOR_DB_PATH=./data/chroma_db

# Tool settings
ENABLE_WEB_RESEARCH=true
MAX_FILE_SIZE_MB=10

# Development
DEBUG=false
LOG_LEVEL=INFO
```

---

## 📊 System Requirements

### Minimum
- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 10GB free
- **OS**: macOS, Linux, Windows (WSL)

### Recommended
- **CPU**: 8+ cores (Apple Silicon preferred)
- **RAM**: 16GB+
- **Disk**: 20GB+ free
- **GPU**: Optional (for faster LLM inference)

---

## 🆘 Getting Help

### Check System Status
```bash
swarm> status

# Shows:
# - Ollama connection
# - Available agents
# - Memory statistics
# - Tool availability
```

### Test Individual Components
```bash
# Test Ollama connection
ollama list

# Test Python environment
python -c "import chromadb; print('OK')"

# Check installed packages
pip list
```

---

## 🚀 Next Steps

After setup, try:

1. **Simple Task**: `swarm> goal Create a Python calculator`
2. **Framework Suggestion**: `swarm> suggest machine learning framework`
3. **Project Analysis**: `swarm> check-project`
4. **Install Something**: `swarm> install requests`
5. **Complex Task**: `swarm> goal Build a license plate detector`

---

## 📖 Additional Documentation

- `README.md` - Project overview
- `INTELLIGENT_RESEARCH.md` - Framework research system
- `INSTALLER_GUIDE.md` - Installation system details
- `SETUP.md` - Detailed setup instructions

---

## ✅ Quick Checklist

Before running, ensure:
- [ ] Python 3.9+ installed
- [ ] Virtual environment created (`python3 -m venv venv`)
- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Ollama installed and running (`ollama serve`)
- [ ] Model downloaded (`ollama pull qwen2.5:7b`)
- [ ] `.env` file exists (copy from `.env.example`)

Then:
- [ ] Run `python main.py`
- [ ] Type `help` to see commands
- [ ] Try `goal Create a simple web scraper`

---

## 🎉 You're Ready!

The AI Swarm is now ready to help you build anything! Just describe what you want, and the agents will handle the rest.

**Happy coding!** 🤖✨
