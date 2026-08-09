# 🤖 NORA - Neural Orchestration & Research Assistant

**N**eural **O**rchestration & **R**esearch **A**ssistant

**Intelligent Multi-Agent System with Autonomous Framework Management**

A local, privacy-focused AI assistant featuring 8 specialized agents, 3-layer memory system, and intelligent framework detection, research, and installation capabilities. Build complete applications just by describing what you want!

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Required-green.svg)](https://ollama.ai)

---

## ✨ Key Features

### 🧠 **8 Specialized AI Agents**
- **Orchestrator** - Coordinates all agents and workflows
- **Planner** - Breaks down goals into structured tasks
- **Coder** - Writes production-ready code
- **Reviewer** - Performs comprehensive code reviews
- **Research** - Fetches documentation and researches frameworks
- **Tester** - Creates and runs automated tests
- **Memory** - Manages knowledge storage and retrieval
- **Reflection** - Learns from experience and improves
- **Installer** - Suggests, researches, and installs frameworks

### 💾 **3-Layer Memory System**
- **Short-term Memory** - Runtime session state and message queues
- **Long-term Memory** - SQLite database for persistent storage
- **Vector Memory** - ChromaDB for semantic search and knowledge retrieval

### 🛠️ **Powerful Tool System**
- **File Tool** - Read, write, and search files
- **Terminal Tool** - Safe command execution
- **Git Tool** - Version control operations
- **Web Tool** - Scrape documentation and research online
- **Project Analyzer** - Detect and analyze frameworks

### 🔍 **Intelligent Framework Management**
- 🎯 **Auto-detect ANY framework** in your existing projects
- 🧠 **AI decides** which frameworks to use for new tasks
- 📚 **Automatically research** documentation for chosen frameworks
- 💡 **AI suggests** best frameworks when asked directly
- 📦 **Research, check, and install** packages with confirmation
- 🧠 **Stores knowledge** in memory for future reference
- ✅ **Verifies** installation and compatibility

**Key Feature**: You describe what you want to build, NORA decides which frameworks are needed, researches them, and uses them - no need for you to know the technical stack!

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.ai) installed and running
- 8GB+ RAM recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/Narvaskristian08/swarm-architecture.git
cd swarm-architecture

# Run automated setup
./setup.sh

# Pull Ollama model
ollama pull qwen2.5:7b

# Run the swarm
./run.sh
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Start Ollama (in another terminal)
ollama serve
ollama pull qwen2.5:7b

# Run the swarm
python main.py
```

---

## 💡 Usage Examples

### Example 1: Build Any Application From Scratch

```bash
nora> goal Create me an application for budget tracking

# NORA will:
# 1. Understand the requirement: budget tracking app
# 2. Plan the features: income/expense tracking, categories, reports
# 3. Decide the tech stack automatically (e.g., Python + SQLite + GUI framework)
# 4. Research the chosen frameworks
# 5. Install dependencies
# 6. Write complete application code
# 7. Create tests
# 8. Generate documentation
# 
# Result: Complete budget tracking application ready to run!
```

### Example 2: Build a License Plate Detector

```bash
nora> goal Build a system that detects license plates and cars, then takes pictures

# NORA will:
# 1. Analyze: Need object detection + OCR + image capture
# 2. AI decides: "Let's use computer vision + OCR libraries"
# 3. Research automatically chosen frameworks
# 4. Install everything needed
# 5. Write the complete system
# 6. Test it
# 
# You don't specify frameworks - NORA figures it all out!
```

### Example 3: Any Type of Application

```bash
# Web applications
nora> goal Create a todo list web app with user accounts

# Desktop applications  
nora> goal Build a password manager desktop app

# Data applications
nora> goal Create a stock price analyzer that sends alerts

# Games
nora> goal Build a simple snake game

# Automation
nora> goal Create a script that backs up my files daily

# NORA handles everything: planning, framework selection, 
# research, installation, coding, testing!
```

### Example 4: Ask for Specific Framework (Optional)

```bash
nora> suggest web framework for Python
# Only when YOU want to know options

nora> install fastapi
# Only when YOU want a specific framework

# But normally, just describe what you want and NORA decides!
```

---

## 🧪 More Application Examples

**Just describe what you want in plain English - NORA builds the entire application!**

### 💰 Finance & Business
- `goal Create me an application for budget tracking`
- `goal Build an invoice generator`
- `goal Make an expense tracker with charts`
- `goal Create a cryptocurrency price monitor`

### 🌐 Web Applications
- `goal Build a todo list web app`
- `goal Create a blog with commenting system`
- `goal Make a URL shortener service`
- `goal Build an online poll maker`

### 🤖 AI & Computer Vision
- `goal Build a license plate detector`
- `goal Create a face recognition system`
- `goal Make a document scanner app`
- `goal Build an object counter from images`

### 📊 Data & Analytics
- `goal Create a stock price analyzer`
- `goal Build a CSV data visualizer`
- `goal Make a weather dashboard`
- `goal Create a log file analyzer`

### 🎮 Games & Entertainment
- `goal Build a snake game`
- `goal Create a quiz application`
- `goal Make a tic-tac-toe game with AI`
- `goal Build a dice rolling simulator`

### 🔧 Utilities & Automation
- `goal Create a password generator tool`
- `goal Build a file backup script`
- `goal Make a download manager`
- `goal Create a system resource monitor`

**The beauty of NORA**: You don't need to know frameworks, libraries, or how to code. Just describe what you want and NORA:
- ✓ Understands your requirement
- ✓ Plans the architecture
- ✓ Chooses the best frameworks
- ✓ Researches documentation
- ✓ Installs dependencies
- ✓ Writes all the code
- ✓ Creates tests
- ✓ Delivers a working application

---

## 📋 Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show all commands | `help` |
| `goal <description>` | **Build anything** - Just describe it! | `goal Create a budget tracking app` |
| `status` | Show system status | `status` |
| `agents` | List all agents | `agents` |
| `suggest <purpose>` | Ask AI for framework recommendations | `suggest web framework` |
| `install <framework>` | Install specific framework | `install flask` |
| `check-project` | Analyze existing project | `check-project` |
| `research-frameworks` | Research frameworks in current project | `research-frameworks` |
| `exit` / `quit` | Exit NORA | `exit` |

**Main Command You'll Use:**
```bash
nora> goal <describe what you want to build>
```
That's it! NORA handles everything else.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface (CLI)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Orchestrator Agent                       │
│          (Coordinates workflow & agent communication)        │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Planner    │   │   Research   │   │   Installer  │
│    Agent     │   │    Agent     │   │    Agent     │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       │         ┌────────┴────────┐         │
       │         │                 │         │
       ▼         ▼                 ▼         ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│    Coder     │   │   Reviewer   │   │    Tester    │
│    Agent     │   │    Agent     │   │    Agent     │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │         Memory System             │
          │  ┌─────────────────────────────┐  │
          │  │  Short-term (Runtime)       │  │
          │  ├─────────────────────────────┤  │
          │  │  Long-term (SQLite)         │  │
          │  ├─────────────────────────────┤  │
          │  │  Vector (ChromaDB)          │  │
          │  └─────────────────────────────┘  │
          └───────────────┬───────────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │          Tool System              │
          │  • File  • Terminal  • Git        │
          │  • Web   • Project Analyzer       │
          └───────────────────────────────────┘
```

---

## 📂 Project Structure

```
swarm-architecture/
├── agents/                    # 8 Specialized AI agents
│   ├── planner.py            # Task planning & decomposition
│   ├── coder.py              # Code generation
│   ├── reviewer.py           # Code review & quality checks
│   ├── research.py           # Documentation research
│   ├── tester.py             # Test creation & execution
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
│   ├── demo_complete_workflow.py
│   └── demo_yolo_research.py
├── main.py                    # Entry point
├── cli.py                     # Command-line interface
├── requirements.txt           # Dependencies
├── setup.sh                   # Automated setup script
├── run.sh                     # Quick run script
└── README.md                  # This file
```

---

## 🎯 How NORA Works

### The Simple Way: Just Describe What You Want

```bash
# No need to know frameworks, libraries, or technical details
# Just tell NORA what application you need!

nora> goal Create me an application for budget tracking
nora> goal Build a weather dashboard
nora> goal Make a file organizer script
nora> goal Create a chatbot for customer service
nora> goal Build an image resizer tool

# NORA handles:
# ✓ Understanding your requirement
# ✓ Planning the architecture
# ✓ Choosing the best frameworks
# ✓ Researching documentation
# ✓ Installing dependencies  
# ✓ Writing all the code
# ✓ Creating tests
# ✓ Making it work!
```

### What Makes NORA Different?

#### ❌ Traditional Development
```
You: Need to build a budget tracker
You: Research web frameworks (days)
You: Choose Flask vs Django vs FastAPI (hours)
You: Learn the framework (weeks)
You: Write code (days)
You: Debug issues (days)
You: Write tests (hours)
Total: Weeks of work
```

#### ✅ With NORA
```
You: "Create me an application for budget tracking"
NORA: *Analyzes → Plans → Chooses tech → Researches → Builds → Tests*
Total: Minutes to hours (depending on complexity)

You focus on WHAT you want.
NORA figures out HOW to build it.
```

---

## 🧪 Real-World Use Cases

### How NORA Works: AI-Driven Framework Selection

**You don't need to know which frameworks to use!** Just describe what you want:

#### Example: Computer Vision Task
```bash
nora> goal Create a real-time object detection system

# What happens:
# 1. Planner: "We need object detection, camera input, real-time processing"
# 2. Research: AI decides to research object detection frameworks
# 3. Installer: AI suggests best option (could be YOLO, TensorFlow, etc.)
# 4. System installs chosen framework
# 5. Coder: Writes code using that framework
# 
# You just described the goal - NORA figured out the technical stack!
```

#### Example: Web Development
```bash
nora> goal Build a REST API with authentication

# NORA decides:
# - Best Python web framework (FastAPI, Flask, Django?)
# - Authentication method (JWT, OAuth, session-based?)
# - Database (SQLite, PostgreSQL, MongoDB?)
# 
# Then researches, installs, and implements everything!
```

#### Example: Data Processing
```bash
nora> goal Analyze CSV data and create visualizations

# NORA automatically:
# - Chooses data analysis libraries (pandas, polars?)
# - Selects visualization tools (matplotlib, plotly, seaborn?)
# - Researches their documentation
# - Generates complete analysis scripts
```

### Direct Framework Requests

You can also ask for specific frameworks:

```bash
nora> suggest cross-platform mobile framework
# AI recommends Flutter, React Native, etc. with reasoning

nora> install tensorflow
# Researches TensorFlow specifically and installs it
```

---

## 🎯 Key Difference

### ❌ Old Way: You Decide Everything
```
You: "I need FastAPI, SQLAlchemy, Alembic, pytest, black..."
Tool: Installs what you tell it
```

### ✅ NORA Way: AI Decides Based on Task
```
You: "Build me a REST API with database"
NORA: Analyzes → Chooses frameworks → Researches → Installs → Builds
```

**You focus on WHAT you want. NORA figures out HOW to build it!**

---

## 🧪 More Examples

### Computer Vision
```bash
nora> goal Create a real-time object detection system with YOLO
# Builds complete CV pipeline with camera integration
```

### Web Development
```bash
nora> goal Build a FastAPI REST API with JWT authentication
# Creates production-ready API with auth, docs, tests
```

### Data Science
```bash
nora> goal Analyze CSV data and create visualizations
# Generates analysis scripts with pandas, matplotlib
```

### Mobile Apps
```bash
nora> suggest cross-platform mobile framework
# AI recommends Flutter with reasoning and examples
```

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 2 minutes
- **[RUN_GUIDE.md](RUN_GUIDE.md)** - Complete setup and usage guide
- **[INTELLIGENT_RESEARCH.md](INTELLIGENT_RESEARCH.md)** - Framework research system
- **[INSTALLER_GUIDE.md](INSTALLER_GUIDE.md)** - Installation system details

---

## 🔧 Configuration

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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📊 System Requirements

### Minimum
- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 10GB free
- **OS**: macOS, Linux, Windows (WSL)

### Recommended
- **CPU**: 8+ cores (Apple Silicon M1/M2 preferred)
- **RAM**: 16GB+
- **Disk**: 20GB+ free
- **GPU**: Optional (for faster LLM inference)

---

## 🐛 Troubleshooting

### "Cannot connect to Ollama"
```bash
# Start Ollama in another terminal
ollama serve
```

### "Model not found"
```bash
ollama pull qwen2.5:7b
```

### "ChromaDB error"
```bash
pip install --upgrade chromadb
rm -rf data/  # Reset if needed
```

### "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🌟 Features Roadmap

- [ ] Support for more LLM providers (OpenAI, Anthropic)
- [ ] Web UI interface
- [ ] Multi-project workspace management
- [ ] Real-time collaboration features
- [ ] Plugin system for custom agents
- [ ] Docker deployment option
- [ ] Cloud deployment templates

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Ollama](https://ollama.ai) for local LLM inference
- Uses [ChromaDB](https://www.trychroma.com/) for vector memory
- CLI powered by [Rich](https://github.com/Textualize/rich)
- Framework detection inspired by modern package managers

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Narvaskristian08/swarm-architecture/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Narvaskristian08/swarm-architecture/discussions)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Built with ❤️ by developers, for developers**

[Get Started](#-quick-start) • [Documentation](#-documentation) • [Examples](#-usage-examples)

</div>
