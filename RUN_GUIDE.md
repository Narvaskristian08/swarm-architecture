# NORA Run Guide

Complete guide to running and using NORA (Neural Orchestration & Research Assistant).

## Prerequisites

Before running NORA, ensure you have completed the setup:

1. ✅ Python 3.9+ installed
2. ✅ Virtual environment created and activated
3. ✅ Dependencies installed (`pip install -r requirements.txt`)
4. ✅ LLM provider configured (llama.cpp or Ollama)
5. ✅ `.env` file configured

If you haven't completed setup, see [SETUP.md](SETUP.md) first.

---

## Starting NORA

### Quick Start

```bash
./run.sh
```

This script will:
- Activate the virtual environment
- Check LLM provider status
- Start NORA CLI

### Manual Start

```bash
source venv/bin/activate
python main.py
```

### Troubleshooting Startup

If you see warnings:
- **"Cannot connect to Ollama"** - Start Ollama: `ollama serve`
- **"Model file not found"** - Check `LLAMA_MODEL_PATH` in `.env`
- **"llama-cpp-python not installed"** - Run: `pip install -r requirements-llama.txt`

NORA will still start but won't be able to generate code without an LLM.

---

## CLI Commands Reference

### Core Commands

#### `goal <description>`

Build anything by describing what you want.

**Examples:**
```
goal Create a Python calculator with add, subtract, multiply, divide
goal Build a REST API with Flask and SQLite database
goal Make a command-line todo app with persistent storage
```

**What happens:**
1. Planner agent creates a structured plan
2. Agents execute tasks in order
3. Code is generated and saved to `./projects/`
4. Results show files created and status

---

#### `status`

Display comprehensive system status.

**Shows:**
- Orchestrator status
- LLM provider and model
- Model readiness
- Active workflows
- Workspace location

**Example output:**
```
System Status

Orchestrator: ready
Active Workflows: 0
Queued Messages: 0
Workspace: /path/to/ai-swarm/projects

LLM Provider: llama_cpp
Model Status: Ready
Model: /path/to/model.gguf
```

---

#### `doctor`

Run comprehensive system diagnostics.

**Checks:**
- Python version
- Orchestrator status
- Workspace configuration
- LLM provider status
- Registered agents count
- Available tools
- Memory system

**When to use:**
- First time setup verification
- Troubleshooting issues
- After configuration changes

---

#### `agents`

List all registered agents and their capabilities.

**Shows:**
- Agent ID
- Name
- Status
- Capabilities

**Example:**
```
Registered Agents

planner    Planner      ready    planning, task_breakdown
coder      Coder        ready    code_generation, implementation
reviewer   Reviewer     ready    code_review, quality_assurance
tester     Tester       ready    test_design, test_execution
research   Research     ready    web_research, documentation
...
```

---

#### `workflows`

Show active and recent workflows.

**Displays:**
- Workflow ID
- Goal
- Status
- Creation time

---

### Framework & Package Commands

#### `suggest <purpose>`

Get AI-powered framework recommendations.

**Examples:**
```
suggest web framework for Python REST API
suggest object detection library for Python
suggest GUI framework for desktop app
```

**Returns:**
- Recommended framework
- Why it's recommended
- Alternatives
- Installation command
- Difficulty level
- Documentation link

---

#### `install <framework>`

Research and install a framework with confirmation.

**Examples:**
```
install flask
install ultralytics
install tensorflow
```

**Process:**
1. Researches the framework
2. Checks if already installed
3. Shows findings
4. Asks for confirmation
5. Installs if approved

**Safety:** Always asks before installing.

---

#### `check-project`

Analyze current project and detect frameworks.

**Detects:**
- Project type
- Languages used
- Frameworks
- Libraries
- Package managers
- Config files

**Use when:**
- Starting work on existing project
- Understanding project structure
- Identifying dependencies

---

#### `research-frameworks`

Automatically research all detected frameworks in your project.

**Process:**
1. Scans project for frameworks
2. Identifies AI/ML frameworks
3. Provides research summary
4. Suggests next steps

---

### Utility Commands

#### `help`

Display all available commands with descriptions.

#### `clear`

Clear the screen and show banner.

#### `exit` or `quit`

Exit NORA (asks for confirmation).

---

## Understanding Workflows

### Workflow Lifecycle

1. **Created** - Goal submitted
2. **Planning** - Planner creates task breakdown
3. **Executing** - Agents execute tasks
4. **Completed/Failed** - Final status

### Workflow Statuses

- **completed** - All tasks succeeded
- **completed_with_errors** - Some tasks failed
- **blocked** - Cannot proceed (e.g., no LLM)
- **failed** - Critical error occurred

### Checking Results

After a workflow completes:

```bash
# Check generated files
ls -R projects/

# View specific file
cat projects/calculator/main.py

# Run generated code
python projects/calculator/main.py
```

---

## LLM Provider Management

### Switching Providers

Edit `.env` and change:

```bash
# Switch to llama.cpp
LLM_PROVIDER=llama_cpp

# Or switch to Ollama
LLM_PROVIDER=ollama
```

Then restart NORA. No code changes needed!

### Provider-Specific Issues

#### llama.cpp

**"Model file not found"**
- Verify path is absolute
- Check file exists: `ls -lh /path/to/model.gguf`
- Ensure `.gguf` extension

**"llama-cpp-python not installed"**
```bash
pip install -r requirements-llama.txt
```

**Slow generation**
- Enable GPU: Set `LLAMA_GPU_LAYERS=-1` in `.env`
- Or use smaller model

#### Ollama

**"Cannot connect to Ollama"**
```bash
ollama serve  # In another terminal
```

**"Model not available"**
```bash
ollama pull qwen2.5:7b
```

**Timeout errors**
- Increase timeout in `.env`: `OLLAMA_TIMEOUT=300`

---

## Best Practices

### Writing Good Goals

✅ **Specific and Clear:**
```
goal Create a Python REST API with Flask, SQLite database, and CRUD operations
```

❌ **Too Vague:**
```
goal Make an API
```

### Iterative Development

1. Start with basic version:
   ```
   goal Create a basic calculator
   ```

2. Add features incrementally:
   ```
   goal Add scientific functions to the calculator (sin, cos, tan)
   ```

3. Include tests:
   ```
   goal Add unit tests for the calculator
   ```

### Project Organization

NORA organizes generated projects:

```
projects/
├── calculator/
│   ├── main.py
│   └── tests/
│       └── test_calculator.py
├── todo_app/
│   ├── main.py
│   ├── todo.db
│   └── tests/
└── api/
    ├── app.py
    ├── requirements.txt
    └── tests/
```

---

## Advanced Usage

### Multiple Goals

Run multiple workflows in sequence:

```
nora> goal Create a utility functions library
nora> goal Create a command-line interface for the library
nora> goal Add comprehensive tests for the library
```

### Analyzing Existing Projects

```bash
cd /path/to/your/project
nora  # Start NORA in project directory

nora> check-project
nora> research-frameworks
```

### Package Management

```
nora> suggest web scraping library
# Returns: beautifulsoup4, scrapy, etc.

nora> install beautifulsoup4
# Researches and installs with confirmation
```

---

## Common Workflows

### Web Application
```
goal Create a Flask web app with user authentication, SQLite database, and REST API endpoints
```

### Data Processing
```
goal Create a Python script to process CSV files, generate statistics, and create visualizations
```

### Automation
```
goal Create a backup script that compresses directories and uploads to cloud storage
```

### CLI Tool
```
goal Create a command-line tool for managing environment variables with add, list, export commands
```

### Machine Learning
```
goal Create an image classifier using PyTorch with data loading, training, and prediction
```

---

## Troubleshooting Guide

### No Files Created

**Check:**
1. Workflow status: `workflows` command
2. Workspace location: `status` command
3. Directory permissions: `ls -la projects/`

### Slow Performance

**Solutions:**
- Use smaller model (3B instead of 7B)
- Enable GPU acceleration
- Increase context size: `LLAMA_CONTEXT_SIZE=4096`

### Import Errors

```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Memory Issues

For large projects:
```bash
# Reduce context size
LLAMA_CONTEXT_SIZE=4096

# Reduce max tokens
LLAMA_MAX_TOKENS=1024
```

---

## Tips & Tricks

### 1. Use Framework Names
```
✓ goal Create a FastAPI REST endpoint
✗ goal Create a REST endpoint (NORA will choose)
```

### 2. Specify Language
```
✓ goal Create a Python web scraper
✗ goal Create a web scraper (defaults to Python)
```

### 3. Include Requirements
```
✓ goal Create a password generator with GUI using tkinter
✗ goal Create a password generator
```

### 4. Request Tests
```
✓ goal Create a calculator with comprehensive unit tests
```

### 5. Specify Complexity
```
✓ goal Create a simple REST API
✓ goal Create a production-ready REST API with error handling and logging
```

---

## Keyboard Shortcuts

In the CLI:
- **Ctrl+C** - Cancel current operation
- **Ctrl+D** - Exit (same as `exit` command)
- **↑/↓** - Command history

---

## Getting Help

1. Run `doctor` command for diagnostics
2. Check `data/swarm.log` for errors
3. See documentation:
   - [SETUP.md](SETUP.md) - Installation details
   - [QUICKSTART.md](QUICKSTART.md) - Getting started
   - [EXAMPLES.md](EXAMPLES.md) - Sample projects
   - [TESTING_GUIDE.md](TESTING_GUIDE.md) - Validation

---

## Quick Reference

```
Starting:
  ./run.sh              Start NORA (recommended)
  python main.py        Manual start

Commands:
  goal <desc>           Build anything
  status                System status
  doctor                Diagnostics
  agents                List agents
  workflows             Show workflows
  suggest <purpose>     Get recommendations
  install <pkg>         Install package
  check-project         Analyze project
  research-frameworks   Auto-research
  help                  Show commands
  exit                  Quit NORA

Examples:
  goal Create a Python calculator
  goal Build a Flask REST API
  suggest Python GUI framework
  install requests
```

---

**Ready to build? Run `./run.sh` and start creating!** 🚀
