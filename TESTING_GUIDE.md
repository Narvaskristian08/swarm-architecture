# NORA Testing Guide

## Prerequisites

### 1. Install Ollama Model

NORA requires a language model to function. Install one with:

```bash
# Recommended model (7B parameters, good balance)
ollama pull qwen2.5:7b

# Alternative smaller model (faster, less capable)
ollama pull qwen2.5:3b

# Alternative larger model (slower, more capable)
ollama pull qwen2.5:14b
```

Verify installation:
```bash
ollama list
```

You should see the model listed.

### 2. Activate Virtual Environment

```bash
cd /Users/deb/ai-swarm
source venv/bin/activate
```

---

## Running Tests

### Basic Tests (No LLM Required)

These tests validate core functionality without needing a language model:

```bash
python tests/test_basic.py
```

Expected output:
```
============================================================
AI SWARM - Basic Tests
============================================================
...
Tests: 9 passed, 0 failed
============================================================
```

### Workflow Tests (No LLM Required)

These tests validate orchestration logic:

```bash
python tests/test_workflow.py
```

Expected output:
```
============================================================
AI SWARM - Workflow Execution Tests
============================================================
...
Tests: 5 passed, 0 failed
============================================================
```

### End-to-End Test (Requires LLM)

This test executes a complete workflow from goal to file creation:

```bash
python tests/test_e2e_calculator.py
```

Expected output:
```
============================================================
End-to-End Test: Creating Calculator Application
============================================================

📁 Test workspace: /Users/deb/ai-swarm/test_output_e2e

🔌 Connecting to LLM...
✓ Connected to Ollama

🎯 Initializing orchestrator...
✓ Registered 2 agents

🎯 Goal: Create a simple Python calculator with add, subtract, multiply, and divide functions

⚙️  Creating workflow...
✓ Workflow created: [workflow-id]

▶️  Executing workflow...
[LLM execution logs...]

📊 Results:
  Status: completed
  Tasks completed: 3
  Tasks failed: 0

📄 Files created: 2
  ✓ calculator/main.py (XXX bytes)
  ✓ calculator/tests/test_calculator.py (XXX bytes)

📋 Plan Summary:
  Goal: Create a simple Python calculator...
  Tasks: 3

📝 Sample code from main.py:
------------------------------------------------------------
def add(a, b):
    return a + b
...
------------------------------------------------------------

✅ End-to-end test PASSED!
```

This test creates actual files in `test_output_e2e/calculator/`.

---

## Running NORA Interactively

### Start NORA CLI

```bash
python main.py
```

Expected output:
```
Initializing NORA...
Neural Orchestration & Research Assistant

Connecting to Ollama...
✓ Connected to Ollama (available models: 1)
✓ Memory system ready (Vector: True)
✓ Initialized 5 tools
Registering agents...
✓ Registered 8 agents:
  - Planner, Coder, Reviewer
  - Research, Tester, Memory, Reflection, Installer
✓ NORA initialized successfully!
Ready to build applications. Type 'goal <description>' to start.

NORA>
```

### Example Commands

#### 1. Simple Calculator

```
NORA> goal Create a simple Python calculator
```

NORA will:
1. Create a workflow
2. Plan the project (Planner agent)
3. Implement the code (Coder agent)
4. Save files to a `calculator/` directory

#### 2. Todo Application

```
NORA> goal Create a command-line todo application with persistent storage
```

NORA will create a more complex project with multiple files.

#### 3. Check System Status

```
NORA> status
```

Shows registered agents, active workflows, and system health.

#### 4. List Files

```
NORA> ls
```

Lists files in the current workspace.

#### 5. View File

```
NORA> cat calculator/main.py
```

Displays the content of a generated file.

#### 6. Exit

```
NORA> exit
```

---

## Interpreting Results

### Successful Workflow

Look for:
- ✅ Status: `completed`
- ✅ Tasks completed > 0
- ✅ Tasks failed = 0
- ✅ Files created list is non-empty
- ✅ Generated files exist in workspace

### Workflow with Errors

May show:
- ⚠️ Status: `completed_with_errors`
- ⚠️ Some tasks failed
- ⚠️ Partial file creation

Common causes:
- LLM timeout
- Invalid code generation
- File write permissions

### Failed Workflow

Shows:
- ❌ Status: `failed`
- ❌ Error message
- ❌ No files created

Common causes:
- LLM not available
- Planner returned empty task list
- Agent not registered
- Invalid goal format

---

## Troubleshooting

### "Ollama not available"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama
# (Method depends on installation)
ollama serve
```

### "No models found"

```bash
# Install a model
ollama pull qwen2.5:7b

# Verify
ollama list
```

### "Request timed out"

The LLM is taking too long. Either:
1. Use a smaller model (qwen2.5:3b)
2. Increase timeout in `.env`:
   ```
   OLLAMA_TIMEOUT=300
   ```
3. Simplify the goal

### "Planner returned empty task list"

The LLM failed to generate a valid plan. Check:
1. Model is working: `ollama run qwen2.5:7b "Hello"`
2. Goal is clear and specific
3. Ollama logs for errors

### "No agent found for task"

Agent not registered. Check:
```python
# In main.py, ensure all agents are registered:
orchestrator.register_agent(planner)
orchestrator.register_agent(coder)
# etc.
```

### Files Not Created

Check:
1. Workspace directory exists and is writable
2. Check logs for file tool errors
3. Verify `code_blocks` in agent result

---

## Test Goals by Complexity

### Simple (Good for First Test)

```
goal Create a Python calculator
goal Create a greeting function in Python
goal Create a temperature converter
```

### Medium

```
goal Create a command-line todo application
goal Create a simple HTTP API with Flask
goal Create a file backup script
```

### Complex (Phase 2+)

```
goal Create a REST API with authentication
goal Create a web scraper with database storage
goal Create a budget tracking application
```

---

## Expected Behavior

### Phase 1 (Current Implementation)

✅ **What Works:**
- Goal → Plan → Code → Files
- Dependency resolution
- Agent selection
- File creation

❌ **What Doesn't Work Yet:**
- Test execution (Phase 2)
- Code review (Phase 2)
- Automatic bug fixes (Phase 2)
- Iterative improvement (Phase 2)
- Parallel execution (Phase 3)

### After Phase 2 (Future)

Will also support:
- Automatic testing of generated code
- Test failure analysis and fixes
- Code review feedback
- Iterative refinement

---

## Monitoring Execution

### Log Levels

NORA uses Python logging. To see more detail:

```bash
# Set in .env
LOG_LEVEL=DEBUG
```

Or run with:
```bash
python -u main.py 2>&1 | tee nora.log
```

### Key Log Messages

```
INFO:core.orchestrator:Starting workflow execution: [goal]
INFO:core.orchestrator:Requesting plan from Planner...
INFO:agents.planner:Creating plan for goal: [goal]
INFO:core.orchestrator:Plan created with X tasks
INFO:core.orchestrator:Task execution order: ['task_1', 'task_2', ...]
INFO:core.orchestrator:Executing task: task_1 - [description]
INFO:core.orchestrator:Task task_1 completed: success
INFO:tools.tool_manager:Initialized 5 tools
```

---

## Performance Expectations

### With qwen2.5:7b on Apple Silicon

- **Simple goal** (calculator): 30-60 seconds
- **Medium goal** (todo app): 2-4 minutes
- **Complex goal** (API): 5-10 minutes

### Bottlenecks

1. **LLM inference** (80% of time)
   - Planning: 10-30 seconds
   - Code generation per task: 20-60 seconds

2. **File operations** (minimal)
3. **Orchestration logic** (negligible)

### Optimization Tips

1. Use smaller models for faster iteration
2. Break complex goals into multiple workflows
3. Increase parallel execution in Phase 3

---

## Files Generated

### Typical Project Structure

```
project_name/
├── main.py              # Main implementation
├── tests/
│   └── test_project.py  # Test file (if generated)
└── README.md            # Documentation (if generated)
```

### File Naming

NORA infers filenames from:
1. Goal keywords (calculator, todo, api, etc.)
2. Task descriptions (main, tests, etc.)
3. Programming language
4. Task order

Examples:
- `calculator/main.py`
- `todo/tests/test_todo.py`
- `api/api_1.py`

---

## Success Criteria

✅ A successful test should:
1. Complete without errors
2. Create at least 1 file
3. Generate valid Python code
4. Match the goal description
5. Complete in reasonable time (< 5 minutes for simple goals)

---

## Next Steps After Testing

Once basic tests pass:

1. ✅ Run `python tests/test_basic.py`
2. ✅ Run `python tests/test_workflow.py`
3. ✅ Install Ollama model
4. ✅ Run `python tests/test_e2e_calculator.py`
5. ✅ Test interactive CLI with simple goal
6. ✅ Inspect generated files
7. ➡️ Proceed to Phase 2 implementation

---

## Getting Help

### Check Logs

```bash
# Run with logging
python main.py 2>&1 | tee nora.log

# Search for errors
grep ERROR nora.log
```

### Common Issues Document

See `TROUBLESHOOTING.md` for detailed solutions.

### Implementation Details

See `IMPLEMENTATION_REPORT.md` for technical architecture.

---

**Ready to test? Start with:**

```bash
ollama pull qwen2.5:7b
source venv/bin/activate
python tests/test_e2e_calculator.py
```
