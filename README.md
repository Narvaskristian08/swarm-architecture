# Local AI Swarm Architecture

A modular, lightweight AI agent swarm system that runs entirely on local hardware using Ollama/Qwen.

## System Overview

This system implements a multi-agent architecture where specialized agents collaborate to:
- Break down complex goals into actionable tasks
- Research current information
- Write and test code
- Review outputs
- Learn from experience
- Store and retrieve knowledge

## Hardware Requirements

- **Primary**: Apple Silicon M1 Mac (or similar)
- **Optional**: Low-power secondary machine for distributed workloads
- **Memory**: Optimized for low RAM usage (8GB+ recommended)
- **Storage**: Minimal (SQLite + ChromaDB, ~100MB for databases)

## Architecture

```
User Request
     │
     v
Orchestrator ──> Manages workflow and agent communication
     │
     v
Planner ──────> Breaks goals into tasks
     │
     ├──> Research Agent ──> Gathers current information
     ├──> Coder Agent ─────> Writes code
     │         │
     │         v
     │    Tester Agent ───> Validates functionality
     │         │
     │         v
     │    Reviewer Agent ─> Checks quality
     │         │
     │         v
     └──> Memory Agent ───> Stores knowledge
               │
               v
     Reflection Agent ──> Learns from experience
```

## Agent Responsibilities

| Agent | Purpose |
|-------|---------|
| **Orchestrator** | Coordinates all agents, manages workflow |
| **Planner** | Converts goals into executable plans |
| **Research** | Retrieves current documentation and information |
| **Coder** | Generates and modifies code |
| **Tester** | Runs tests and validates builds |
| **Reviewer** | Code review, security, and quality checks |
| **Memory** | Stores and retrieves knowledge |
| **Reflection** | Analyzes outcomes and improves processes |

## Memory System

### Three-Layer Memory

1. **Short-term** (Runtime): Current task state and agent messages
2. **Long-term** (SQLite): Tasks, conversations, project history
3. **Vector** (ChromaDB): Documentation, code patterns, solutions

## Technology Stack

- **LLM**: Qwen via Ollama (local inference)
- **Language**: Python 3.9+
- **Databases**: SQLite (structured) + ChromaDB (vector)
- **Interface**: CLI (current), Web UI (future)
- **Voice**: Whisper + TTS (Phase 7 - future)

## Installation

### 1. Install Ollama

Visit [https://ollama.ai](https://ollama.ai) and install Ollama for your platform.

### 2. Pull Qwen Model

```bash
ollama pull qwen2.5:7b
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your preferences
```

### 5. Run the Swarm

```bash
python main.py
```

## Quick Start

Once the swarm is running:

```bash
# Submit a goal
swarm> goal Create a simple calculator function in Python

# Check system status
swarm> status

# List active agents
swarm> agents

# View workflows
swarm> workflows

# **Check project frameworks and libraries**
swarm> check-project

# Get help
swarm> help
```

## Project Structure

```
ai-swarm/
├── agents/              # Agent implementations
│   ├── planner.py      # Task planning
│   ├── coder.py        # Code generation
│   ├── reviewer.py     # Code review
│   ├── research.py     # Web research
│   ├── tester.py       # Testing
│   ├── memory_agent.py # Knowledge management
│   └── reflection.py   # Learning & improvement
├── core/               # Core framework
│   ├── base_agent.py   # Base agent class
│   ├── orchestrator.py # Agent coordinator
│   ├── llm_client.py   # Ollama integration
│   └── response_parser.py # LLM response parsing
├── memory/             # Memory systems
│   ├── short_term.py   # Runtime memory
│   ├── long_term.py    # SQLite storage
│   ├── vector_memory.py # ChromaDB
│   └── memory_manager.py # Unified coordinator
├── tools/              # Agent tools
│   ├── file_tool.py    # File operations
│   ├── terminal_tool.py # Command execution
│   ├── git_tool.py     # Version control
│   ├── web_tool.py     # Web research
│   └── tool_manager.py # Tool coordinator
├── config/             # Configuration
├── data/               # Databases (auto-created)
├── cli.py              # Command-line interface
└── main.py             # Entry point
```

## Configuration

Edit `.env` to customize:

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=120

# Memory Configuration
MAX_SHORT_TERM_MESSAGES=50
VECTOR_COLLECTION_NAME=swarm_knowledge

# Tool Configuration
ENABLE_WEB_RESEARCH=true
ENABLE_GIT_TOOLS=true
MAX_FILE_SIZE_MB=10

# Safety Settings
REQUIRE_CONFIRMATION=true
LOG_LEVEL=INFO
```

## Features

### ✅ Implemented (Phases 1-6)

- Core agent framework
- Ollama/Qwen integration
- 7 specialized agents
- Three-layer memory system
- File, terminal, git, web, and project analysis tools
- **Automatic framework/library detection**
- Safety features and command validation
- CLI interface

### 🚧 Future Enhancements (Phase 7+)

- Voice interface (Whisper + TTS)
- Web UI
- Distributed worker support
- Enhanced workflow visualization
- More specialized agents
- Advanced orchestration patterns

## Safety Features

- Dangerous command confirmation required
- File operation safeguards
- Action logging
- Sandboxed execution (where possible)
- Size limits on file operations
- Workspace restrictions

## Usage Examples

### Example 1: Simple Code Generation

```bash
swarm> goal Write a Python function to calculate fibonacci numbers
```

The swarm will:
1. Planner creates task breakdown
2. Coder writes the function
3. Reviewer checks code quality
4. Tester designs test cases
5. Memory stores the solution

### Example 2: Research and Implement

```bash
swarm> goal Create a REST API endpoint using FastAPI
```

The swarm will:
1. Research agent checks FastAPI documentation
2. Planner creates implementation plan
3. Coder implements the endpoint
4. Reviewer checks security and best practices
5. Tester validates functionality

### Example 3: Analyze Project Dependencies

```bash
# The swarm can automatically detect what frameworks/libraries you're using
swarm> check-project
```

Output:
```
Project Type: Python Application
Languages: Python
Frameworks: fastapi, django
Libraries: 45 found
  • beautifulsoup4
  • chromadb
  • fastapi
  • ollama
  • pandas
  ... and 40 more

Tip: Use 'goal Research <framework> documentation' to learn more
```

Then research automatically:
```bash
swarm> goal Research the frameworks in this project and check for updates
```

The swarm will:
1. Detect FastAPI and Django in your project
2. Research current versions and best practices
3. Compare with what you're using
4. Suggest improvements or updates

```bash
swarm> goal Review the code in src/utils.py for security issues
```

The swarm will:
1. Research agent checks for known vulnerabilities
2. Reviewer performs comprehensive analysis
3. Tester suggests test cases
4. Reflection provides improvement suggestions

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### ChromaDB Issues

If vector memory is unavailable:
```bash
pip install chromadb
```

The system will work without ChromaDB, but semantic search will be disabled.

### Memory Database

The SQLite database is created automatically at `data/swarm.db`. To reset:

```bash
rm data/swarm.db
python main.py
```

## Development

### Adding a New Agent

1. Create agent file in `agents/` directory
2. Inherit from `BaseAgent`
3. Implement `process()` method
4. Add to `agents/__init__.py`
5. Register in `main.py`

### Adding a New Tool

1. Create tool file in `tools/` directory
2. Inherit from `BaseTool`
3. Implement `execute()` and `validate_params()`
4. Add to `tools/__init__.py`
5. Register in `tool_manager.py`

## Contributing

This is a modular system designed for extension:
- Add new agents for specialized tasks
- Create custom tools for your workflow
- Extend memory systems
- Improve orchestration logic

## Performance

- **Startup**: ~2-3 seconds
- **LLM Response**: 2-10 seconds (depends on model and complexity)
- **Memory Operations**: <100ms
- **Tool Execution**: Varies by operation

## License

MIT

## Acknowledgments

- Ollama for local LLM inference
- Qwen for the language model
- ChromaDB for vector storage
- Rich for beautiful CLI output
# swarm-architecture
