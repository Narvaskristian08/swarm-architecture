# AI Swarm Features

Complete feature list for the Local AI Swarm system.

## Core Capabilities

### 🤖 Intelligent Agents (8 Total)

1. **Orchestrator** - Coordinates all agents and workflows
2. **Planner** - Breaks down goals into actionable tasks
3. **Coder** - Generates and modifies code
4. **Reviewer** - Reviews code for quality and security
5. **Research** - Fetches documentation and web content
6. **Tester** - Designs and runs tests
7. **Memory Agent** - Manages knowledge storage
8. **Reflection** - Learns from experience

### 🧠 Memory System (3 Layers)

- **Short-term**: Runtime session state
- **Long-term**: SQLite database for persistent storage
- **Vector**: ChromaDB for semantic search

### 🛠️ Tools (5 Types)

- **File Tool**: Read, write, search files with safety checks
- **Terminal Tool**: Execute commands with dangerous command detection
- **Git Tool**: Version control operations
- **Web Tool**: Scrape documentation and web content
- **Project Analyzer**: Detect frameworks, libraries, and check versions ✨ NEW

## Project Analysis Features ✨

### Framework & Library Detection

**What it does:**
- Automatically scans your project
- Detects programming languages
- Identifies frameworks (Django, Flask, FastAPI, React, Vue, etc.)
- Lists all dependencies
- Recognizes project type

**Supported Package Files:**
- `requirements.txt` (Python/pip)
- `Pipfile` (Python/pipenv)
- `pyproject.toml` (Python/poetry)
- `package.json` (JavaScript/npm)
- `composer.json` (PHP)
- `Gemfile` (Ruby)
- `go.mod` (Go)
- `Cargo.toml` (Rust)
- `pom.xml` (Java/Maven)

**Example Output:**
```
Project Type: Python Web API
Languages: Python
Frameworks: fastapi
Libraries: 47 detected
  • pydantic
  • sqlalchemy
  • alembic
  • requests
  ... (43 more)
```

### Version Checking & Update Detection ✨

**What it does:**
- Checks installed package versions
- Compares with latest available versions
- Identifies outdated dependencies
- Categorizes updates (Major, Minor, Patch)
- Suggests update commands

**How it works:**
```bash
# Via CLI
swarm> check-project

# Or programmatically
tool_manager.execute_tool("project", operation="check_outdated", language="python")
```

**Example Output:**
```
⚠ Found 5 outdated packages:

Package       Current    Latest     Update Needed
──────────────────────────────────────────────────
requests      2.28.0     2.31.0     Minor
pydantic      1.10.2     2.5.0      Major
fastapi       0.95.0     0.104.1    Minor
uvicorn       0.20.0     0.24.0     Minor
sqlalchemy    1.4.48     2.0.23     Major

⚠ Warning: Some packages have major version updates.
Review changelogs before updating.

To update:
  pip install --upgrade <package-name>
  or: pip install -r requirements.txt --upgrade
```

## Web Research Features

### Documentation Fetching

**Pre-configured documentation sources:**
- Python: https://docs.python.org
- NumPy: https://numpy.org/doc
- Pandas: https://pandas.pydata.org/docs
- Django: https://docs.djangoproject.com
- Flask: https://flask.palletsprojects.com
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- And more...

**How to use:**
```python
# Research agent checks docs
research_agent.check_documentation(
    library="fastapi",
    specific_topic="authentication"
)

# Or via web tool directly
web_tool.fetch_documentation("fastapi")
```

### Web Scraping

**Capabilities:**
- Fetch and parse HTML
- Extract clean text content
- Remove scripts, styles, navigation
- Identify main content
- Check URL accessibility

**Example:**
```python
result = web_tool.run(
    operation="fetch_text",
    url="https://example.com/docs"
)

print(result['title'])      # Page title
print(result['text'])       # Clean text content
print(result['word_count']) # Word count
```

## CLI Commands

```bash
# Basic commands
swarm> help              # Show all commands
swarm> status            # System status
swarm> agents            # List agents

# Project analysis (NEW)
swarm> check-project     # Analyze frameworks and check versions

# Goal submission
swarm> goal Create a REST API with authentication

# Management
swarm> workflows         # Active workflows
swarm> clear             # Clear screen
swarm> quit              # Exit
```

## Safety Features

### File Operations
- Workspace restrictions (can't access outside project)
- File size limits (configurable, default 10MB)
- Confirmation for deletions

### Terminal Commands
- Dangerous command detection
- Patterns checked: `rm -rf`, `DROP DATABASE`, etc.
- Requires explicit confirmation
- Command history tracking

### General
- All actions logged
- Sandboxed execution where possible
- Configurable safety levels

## LLM Integration

### Ollama/Qwen
- Local inference (no cloud required)
- Multiple model support
- Automatic fallback handling
- Conversation history management
- Temperature control per agent

### Prompt Engineering
- Specialized system prompts per agent
- Task-specific prompt templates
- Response parsing (JSON, code, lists)
- Context management

## Memory & Learning

### Knowledge Storage
```python
# Store knowledge
memory.store_knowledge(
    category="python",
    title="FastAPI Best Practices",
    content="...",
    tags=["api", "python", "fastapi"]
)

# Retrieve knowledge
results = memory.search_knowledge(
    query="authentication patterns",
    category="security"
)
```

### Session Management
- Track workflows
- Store conversations
- Log agent actions
- Maintain project history

### Vector Search
- Semantic similarity search
- ChromaDB integration
- Automatic embedding
- Category filtering

## Workflow Examples

### 1. Check Project Health
```bash
swarm> check-project
```
→ Scans project, lists dependencies, checks for updates

### 2. Research & Implement
```bash
swarm> goal Research SQLAlchemy async patterns and implement a user model
```
→ Research agent fetches docs → Coder implements → Reviewer checks

### 3. Code Review
```bash
swarm> goal Review the authentication code for security issues
```
→ Reviewer analyzes → Suggests improvements → Documents findings

### 4. Update Dependencies
```bash
swarm> check-project
# See outdated packages
# Then update manually based on recommendations
```

## Configuration

### Environment Variables (.env)

```bash
# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=120

# Memory
MAX_SHORT_TERM_MESSAGES=50
VECTOR_COLLECTION_NAME=swarm_knowledge

# Tools
ENABLE_WEB_RESEARCH=true
ENABLE_GIT_TOOLS=true
MAX_FILE_SIZE_MB=10

# Safety
REQUIRE_CONFIRMATION=true
LOG_LEVEL=INFO
```

## Performance

### System Requirements
- **Minimum**: 4GB RAM, Python 3.9+
- **Recommended**: 8GB+ RAM, SSD
- **Optimal**: 16GB RAM, GPU (optional)

### Response Times
- Project analysis: 1-3 seconds
- Version checking: 5-10 seconds (depends on package manager)
- LLM queries: 2-10 seconds (depends on model size)
- Web scraping: 1-5 seconds (depends on site)

## Extensibility

### Add Custom Agents
```python
from core import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("my_agent", "My Agent", "Does custom work")
        self.capabilities = ["custom_task"]
    
    def process(self, task):
        # Your implementation
        return {"status": "success"}
```

### Add Custom Tools
```python
from tools import BaseTool

class MyTool(BaseTool):
    def execute(self, **kwargs):
        # Your implementation
        return {"status": "success"}
    
    def validate_params(self, **kwargs):
        return True, None
```

## Roadmap

### Current (v1.0)
- ✅ 8 specialized agents
- ✅ 3-layer memory system
- ✅ 5 tool types
- ✅ Project analysis
- ✅ Version checking
- ✅ Web research
- ✅ CLI interface

### Planned (v1.1+)
- 🔄 Web UI
- 🔄 Voice interface (Whisper + TTS)
- 🔄 Distributed workers
- 🔄 Plugin system
- 🔄 GitHub integration
- 🔄 API server mode
- 🔄 Docker containerization
- 🔄 CI/CD integration

## Use Cases

1. **Code Development**: Generate, review, and test code
2. **Project Maintenance**: Check dependencies, update libraries
3. **Documentation Research**: Fetch current docs, best practices
4. **Code Review**: Automated security and quality checks
5. **Learning**: Explore frameworks, understand patterns
6. **Refactoring**: Modernize code with current practices
7. **Testing**: Generate test cases, run test suites
8. **Knowledge Management**: Store and retrieve project knowledge

## Limitations

- Requires Ollama running locally
- Python/JavaScript version checking only
- Static HTML scraping (no JavaScript rendering)
- No cloud API support (by design - fully local)
- Limited to configured documentation sources
- Requires internet for web research

## Getting Help

- **Documentation**: See README.md, SETUP.md, EXAMPLES.md
- **Tests**: Run `python tests/test_basic.py`
- **Demos**: Check `examples/` directory
- **CLI**: Type `help` in the swarm prompt
- **Logs**: Check `data/swarm.log`

## Summary

The AI Swarm provides a complete local AI development assistant that can:
- ✅ Understand your project structure
- ✅ Detect all frameworks and libraries
- ✅ Check for outdated dependencies
- ✅ Research documentation online
- ✅ Generate and review code
- ✅ Run tests and validate functionality
- ✅ Store and retrieve knowledge
- ✅ Learn from experience

All running **100% locally** on your hardware! 🚀
