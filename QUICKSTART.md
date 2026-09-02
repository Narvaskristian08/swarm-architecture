# NORA Quick Start Guide

Get up and running with NORA in under 5 minutes!

## Overview

**NORA** (Neural Orchestration & Research Assistant) is an AI swarm that builds complete applications from simple descriptions. Just tell it what you want - it plans, codes, tests, and creates the files.

---

## Installation (2 minutes)

### 1. Clone and Setup

```bash
git clone https://github.com/Narvaskristian08/swarm-architecture.git
cd swarm-architecture
./setup.sh
```

### 2. Choose Your LLM Provider

**Option A: llama.cpp (Recommended for offline use)**

1. Download a GGUF model file:
   - [Qwen2.5-7B-Instruct-Q4_K_M.gguf](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/blob/main/qwen2.5-7b-instruct-q4_k_m.gguf) (4.4GB)

2. Install llama-cpp-python:
   ```bash
   pip install -r requirements-llama.txt
   ```

3. Edit `.env`:
   ```bash
   LLM_PROVIDER=llama_cpp
   LLAMA_MODEL_PATH=/absolute/path/to/your/model.gguf
   ```

**Option B: Ollama (Easier initial setup)**

1. Install Ollama:
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Or macOS with Homebrew
   brew install ollama
   ```

2. Start Ollama and pull a model:
   ```bash
   ollama serve  # Keep running in another terminal
   ollama pull qwen2.5:7b
   ```

3. Edit `.env`:
   ```bash
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=qwen2.5:7b
   ```

---

## First Run (1 minute)

### Start NORA

```bash
./run.sh
```

You should see:
```
╔═══════════════════════════════════════╗
║              N O R A                   ║
║   Neural Orchestration & Research     ║
║           Assistant                   ║
╚═══════════════════════════════════════╝

nora>
```

### Verify Setup

```
nora> doctor
```

Look for:
- ✓ All checks passed! NORA is ready to build.

If you see warnings, follow the suggestions to fix them.

---

## Your First Application (2 minutes)

### Example 1: Simple Calculator

```
nora> goal Create a simple Python calculator with add, subtract, multiply, and divide functions
```

NORA will:
1. 🧠 Plan the implementation
2. 💻 Generate the code
3. 📁 Create files in `./projects/calculator/`

Result:
```
✓ Success
Files created (1):
  • calculator/main.py

Location: /path/to/ai-swarm/projects
```

Check the generated code:
```bash
cat projects/calculator/main.py
```

### Example 2: Todo List Application

```
nora> goal Create a command-line todo application with add, list, complete, and delete functions
```

NORA builds a complete todo app with:
- Core functionality
- Data persistence
- Command-line interface

### Example 3: With Testing

```
nora> goal Create a temperature converter with Celsius to Fahrenheit and vice versa. Include unit tests.
```

NORA will:
- Create the converter logic
- Generate comprehensive tests
- Organize in proper project structure

---

## Essential Commands

### Check System Status

```
nora> status
```

Shows:
- Orchestrator status
- LLM provider and model
- Active workflows
- Workspace location

### List Available Agents

```
nora> agents
```

Shows all 8 specialized agents:
- Planner, Coder, Reviewer
- Research, Tester, Memory, Reflection, Installer

### Framework Suggestions

```
nora> suggest web framework for Python REST API
```

NORA will research and recommend the best framework for your needs.

### Install Packages

```
nora> install requests
```

NORA will:
1. Research the package
2. Check if it's already installed
3. Ask for confirmation
4. Install if approved

### Get Help

```
nora> help
```

Shows all available commands.

### Exit NORA

```
nora> exit
```

---

## What You Can Build

### Web Applications
```
nora> goal Create a Flask API with user authentication and database
```

### Data Processing
```
nora> goal Create a data analysis script that reads CSV and generates charts
```

### Automation Scripts
```
nora> goal Create a file backup script with compression and scheduling
```

### Desktop Tools
```
nora> goal Create a GUI password manager using tkinter
```

### Machine Learning
```
nora> goal Create an image classifier using PyTorch with data loading and training
```

---

## Understanding Workflows

### How NORA Works

1. **You provide a goal** - Describe what you want in plain English
2. **Planner creates a plan** - Breaks your goal into specific tasks
3. **Agents execute tasks** - Specialized agents handle each task:
   - Research agents find documentation
   - Coder agents write the implementation
   - Reviewer agents check code quality
   - Tester agents create tests
4. **Files are created** - Complete, working code is saved to `./projects/`
5. **Memory is stored** - NORA remembers for future reference

### Project Structure

Generated projects follow this structure:
```
projects/
└── your_project/
    ├── main.py          # Main implementation
    ├── tests/           # Test files (if requested)
    │   └── test_*.py
    └── README.md        # Documentation (if generated)
```

---

## Tips for Best Results

### ✅ Good Goals (Specific and Clear)

```
✓ Create a Python calculator with add, subtract, multiply, divide
✓ Build a command-line todo app with SQLite storage
✓ Make a REST API for managing books with CRUD operations
```

### ❌ Vague Goals (Too General)

```
✗ Create something cool
✗ Build an app
✗ Make it better
```

### Pro Tips

1. **Be specific** - More details = better results
2. **Mention language** - "Python web scraper" vs "web scraper"
3. **Include requirements** - "with error handling and logging"
4. **Request tests** - "Include unit tests" ensures quality
5. **Use frameworks** - "Using Flask" vs letting NORA choose

---

## Common Workflows

### Workflow 1: From Scratch

```
nora> goal Create a weather app that fetches data from OpenWeather API and displays it
```

### Workflow 2: Analyze Existing Project

```
nora> check-project
```

NORA will scan your current directory and show:
- Detected frameworks
- Languages used
- Dependencies
- Package managers

### Workflow 3: Research Frameworks

```
nora> research-frameworks
```

Automatically detects and researches all frameworks in your project.

### Workflow 4: Add Features

```
nora> goal Add user authentication to the existing Flask app
```

(When run in a project directory, NORA understands the existing code)

---

## Troubleshooting

### No files created

**Check:**
1. Did the workflow complete successfully?
2. Check `./projects/` directory
3. Run `status` to see workspace location

### Model not responding

**Solutions:**
1. **For Ollama:** Check `ollama serve` is running
2. **For llama.cpp:** Verify `LLAMA_MODEL_PATH` in `.env`
3. Run `doctor` to diagnose

### Slow generation

**Solutions:**
- Use a smaller model (qwen2.5:3b instead of 7b)
- Enable GPU acceleration (see SETUP.md)
- Increase timeout: `OLLAMA_TIMEOUT=300` in `.env`

### Import errors

```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

## Next Steps

### Learn More

- 📖 [Setup Guide](SETUP.md) - Detailed installation and configuration
- 🏃 [Run Guide](RUN_GUIDE.md) - Complete command reference
- 🎯 [Examples](EXAMPLES.md) - Sample projects and workflows
- ✨ [Features](FEATURES.md) - Full capabilities overview
- 🧪 [Testing Guide](TESTING_GUIDE.md) - How to validate NORA

### Explore Advanced Features

```
nora> help
```

Try different commands and experiment with various project types!

### Join the Community

- Report bugs and request features on GitHub
- Share your created projects
- Contribute improvements

---

## Quick Reference Card

```
Commands:
  goal <desc>          Build anything
  status               System status
  doctor               Run diagnostics
  agents               List agents
  workflows            Show workflows
  suggest <purpose>    Get recommendations
  install <package>    Install with research
  check-project        Analyze current project
  research-frameworks  Auto-research detected frameworks
  help                 Show all commands
  exit                 Quit NORA

Examples:
  goal Create a Python web scraper
  goal Build a REST API with Flask
  goal Make a todo app with tests
  suggest Python GUI framework
  install flask
```

---

**Ready to build? Start with:**

```
nora> goal Create a simple Python calculator
```

And watch NORA work its magic! ✨
