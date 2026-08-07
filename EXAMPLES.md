# AI Swarm Usage Examples

Complete examples showing how to use the AI Swarm system.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Agent Examples](#agent-examples)
3. [Tool Examples](#tool-examples)
4. [Memory Examples](#memory-examples)
5. [Workflow Examples](#workflow-examples)

## Basic Usage

### Starting the Swarm

```bash
python main.py
```

### CLI Commands

```bash
# Get help
swarm> help

# Check system status
swarm> status

# List all agents
swarm> agents

# View active workflows
swarm> workflows

# Submit a goal
swarm> goal <your goal here>

# Clear screen
swarm> clear

# Exit
swarm> quit
```

## Agent Examples

### Example 1: Using the Planner Agent

```python
from agents import PlannerAgent
from core import get_llm_client

# Create and configure agent
planner = PlannerAgent()
planner.set_llm_client(get_llm_client())

# Create a plan
result = planner.create_quick_plan("Build a REST API for a todo list")

print("Plan:", result["plan"])
```

### Example 2: Using the Coder Agent

```python
from agents import CoderAgent
from core import get_llm_client

# Create and configure agent
coder = CoderAgent()
coder.set_llm_client(get_llm_client())

# Generate code
result = coder.write_code(
    specification="Create a function that validates email addresses",
    language="python"
)

for block in result["code_blocks"]:
    print(f"Language: {block['language']}")
    print(f"Code:\n{block['code']}")
```

### Example 3: Using the Reviewer Agent

```python
from agents import ReviewerAgent
from core import get_llm_client

# Create and configure agent
reviewer = ReviewerAgent()
reviewer.set_llm_client(get_llm_client())

code = """
def divide(a, b):
    return a / b
"""

# Review code
result = reviewer.review(code, language="python")

review = result["review"]
print("Issues:", review["issues"])
print("Suggestions:", review["suggestions"])
print("Recommendation:", review["recommendation"])
```

### Example 4: Using the Research Agent

```python
from agents import ResearchAgent
from core import get_llm_client

# Create and configure agent
research = ResearchAgent()
research.set_llm_client(get_llm_client())

# Research a topic
result = research.research(
    topic="Best practices for FastAPI authentication",
    context="Building a production API"
)

print("Findings:", result["findings"])
```

### Example 5: Using the Tester Agent

```python
from agents import TesterAgent
from core import get_llm_client

# Create and configure agent
tester = TesterAgent()
tester.set_llm_client(get_llm_client())

code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

# Design tests
result = tester.test(code, language="python")

print("Test Cases:", result["test_cases"])
```

## Tool Examples

### Example 6: Analyze Project Frameworks and Libraries

```python
from tools import get_tool_manager

tools = get_tool_manager()

# Analyze current project
result = tools.analyze_project()

if result["status"] == "success":
    print(f"Project Type: {result['project_type']}")
    print(f"Languages: {', '.join(result['languages'])}")
    print(f"Frameworks: {', '.join(result['frameworks'])}")
    print(f"Libraries: {len(result['libraries'])} found")
    
    # Show libraries
    for lib in sorted(result['libraries'])[:10]:
        print(f"  • {lib}")
```

**Via CLI:**
```bash
swarm> check-project
```

This will automatically detect:
- Languages (Python, JavaScript, etc.)
- Frameworks (FastAPI, Django, React, etc.)
- Libraries from requirements.txt, package.json, etc.
- Package managers (pip, npm, composer, etc.)

### Example 7: Using File Tool

```python
from tools import get_tool_manager

tools = get_tool_manager()

# Read a file
result = tools.read_file("README.md")
if result["status"] == "success":
    print(result["content"][:100])

# Write a file
result = tools.write_file(
    "output/test.py",
    content="print('Hello, World!')"
)

# Search files
result = tools.search_files(
    search_term="TODO",
    directory="src"
)
print(f"Found in {result['files_found']} files")
```

### Example 8: Using Terminal Tool

```python
from tools import get_tool_manager

tools = get_tool_manager()

# Run a command
result = tools.run_command("python --version")

if result["status"] == "success":
    print("Python version:", result["stdout"])

# Run tests (example)
result = tools.run_command("pytest tests/")
print("Tests passed:", result["return_code"] == 0)
```

### Example 9: Using Git Tool

```python
from tools import get_tool_manager

tools = get_tool_manager()

# Check git status
result = tools.execute_tool("git", operation="status")
print(result["output"])

# Make a commit
result = tools.git_commit(
    message="Add new feature",
    files="src/feature.py"
)

# View log
result = tools.execute_tool("git", operation="log", limit=5)
print(result["output"])
```

### Example 10: Using Web Tool

```python
from tools import get_tool_manager

tools = get_tool_manager()

# Fetch a web page
result = tools.fetch_url("https://docs.python.org")

if result["status"] == "success":
    print("Title:", result["title"])
    print("Word count:", result["word_count"])

# Check if URL is accessible
result = tools.execute_tool(
    "web",
    operation="get_status",
    url="https://example.com"
)
print("Accessible:", result["accessible"])
```

## Memory Examples

### Example 11: Storing Knowledge

```python
from memory import get_memory_manager

memory = get_memory_manager()

# Store knowledge
knowledge_id = memory.store_knowledge(
    category="python",
    title="List Comprehension Best Practices",
    content="Use list comprehensions for simple transformations...",
    tags=["python", "best-practices", "lists"]
)

print(f"Stored with ID: {knowledge_id}")
```

### Example 12: Retrieving Knowledge

```python
from memory import get_memory_manager

memory = get_memory_manager()

# Search knowledge
results = memory.search_knowledge(
    query="authentication",
    category="security",
    limit=5
)

for result in results:
    print(f"Title: {result['title']}")
    print(f"Content: {result['content'][:100]}...")
```

### Example 13: Session Management

```python
from memory import get_memory_manager

memory = get_memory_manager()

# Start a session
session_id = memory.start_session(
    goal="Build a calculator app",
    metadata={"project": "calculator", "priority": "high"}
)

# Store messages
memory.store_message(
    sender="user",
    receiver="planner",
    content="Please create a plan",
    persist=True
)

# End session
memory.end_session(summary="Successfully planned calculator app")
```

## Workflow Examples

### Example 14: Complete Workflow - Code Generation

```python
from core import get_llm_client
from agents import PlannerAgent, CoderAgent, ReviewerAgent
from memory import get_memory_manager

# Initialize
llm = get_llm_client()
memory = get_memory_manager()

# Start session
session_id = memory.start_session("Create a calculator function")

# 1. Plan
planner = PlannerAgent()
planner.set_llm_client(llm)

plan_result = planner.create_quick_plan(
    "Create a Python calculator function with add, subtract, multiply, divide"
)

# 2. Code
coder = CoderAgent()
coder.set_llm_client(llm)

code_result = coder.write_code(
    specification=plan_result["plan"]["summary"],
    language="python"
)

# 3. Review
reviewer = ReviewerAgent()
reviewer.set_llm_client(llm)

if code_result["code_blocks"]:
    code = code_result["code_blocks"][0]["code"]
    
    review_result = reviewer.review(code, language="python")
    
    # Store in memory
    memory.store_knowledge(
        category="code",
        title="Calculator Function",
        content=code,
        tags=["python", "calculator", "math"]
    )

# End session
memory.end_session("Calculator function created and reviewed")

print("Workflow complete!")
```

### Example 14: Research and Implement

```python
from core import get_llm_client
from agents import ResearchAgent, CoderAgent
from tools import get_tool_manager

# Initialize
llm = get_llm_client()
tools = get_tool_manager()

# 1. Research
research = ResearchAgent()
research.set_llm_client(llm)
research.set_web_tool(tools.get_tool("web"))

research_result = research.research(
    topic="FastAPI dependency injection best practices"
)

# 2. Implement based on research
coder = CoderAgent()
coder.set_llm_client(llm)

code_result = coder.write_code(
    specification="Implement FastAPI dependency injection",
    context=str(research_result["findings"]),
    language="python"
)

# 3. Save to file
if code_result["code_blocks"]:
    code = code_result["code_blocks"][0]["code"]
    tools.write_file("api/dependencies.py", code)
    
    print("Implementation saved to api/dependencies.py")
```

### Example 15: Test-Driven Development

```python
from core import get_llm_client
from agents import TesterAgent, CoderAgent, ReviewerAgent

# Initialize
llm = get_llm_client()

# 1. Design tests first
tester = TesterAgent()
tester.set_llm_client(llm)

test_result = tester.process({
    "type": "generate_test_code",
    "code": "# Placeholder for user authentication function",
    "language": "python",
    "test_framework": "pytest"
})

# 2. Implement code to pass tests
coder = CoderAgent()
coder.set_llm_client(llm)

if test_result["test_code"]:
    test_requirements = test_result["test_code"][0]["code"]
    
    code_result = coder.write_code(
        specification="Implement user authentication",
        context=f"Must pass these tests:\n{test_requirements}",
        language="python"
    )

# 3. Review implementation
reviewer = ReviewerAgent()
reviewer.set_llm_client(llm)

if code_result["code_blocks"]:
    review_result = reviewer.review(
        code_result["code_blocks"][0]["code"],
        language="python"
    )
    
    print("Review:", review_result["review"]["recommendation"])
```

## Advanced Examples

### Example 16: Custom Agent Workflow

```python
from core import Orchestrator, get_llm_client
from agents import *
from memory import get_memory_manager

# Create custom orchestration
orchestrator = Orchestrator()
llm = get_llm_client()
memory = get_memory_manager()

# Register all agents
agents = [
    PlannerAgent(),
    ResearchAgent(),
    CoderAgent(),
    TesterAgent(),
    ReviewerAgent(),
    ReflectionAgent()
]

for agent in agents:
    agent.set_llm_client(llm)
    orchestrator.register_agent(agent)

# Create workflow
session_id = memory.start_session("Build travel app feature")

workflow_id = orchestrator.create_workflow(
    "Add payment integration to travel app"
)

# Execute in sequence
orchestrator.assign_task_to_agent(
    workflow_id,
    "research",
    {"type": "research_topic", "topic": "Payment gateway integration"}
)

orchestrator.assign_task_to_agent(
    workflow_id,
    "planner",
    {"type": "create_plan", "goal": "Integrate payment gateway"}
)

# Process outputs
orchestrator.process_agent_outputs()

print("Workflow status:", orchestrator.active_workflows[workflow_id].status)
```

### Example 17: Learning from Experience

```python
from core import get_llm_client
from agents import ReflectionAgent
from memory import get_memory_manager

# Initialize
llm = get_llm_client()
memory = get_memory_manager()

reflection = ReflectionAgent()
reflection.set_llm_client(llm)

# Analyze a completed workflow
workflow_data = {
    "tasks": ["plan", "research", "code", "test", "review"],
    "duration": "15 minutes",
    "agents": ["planner", "research", "coder", "tester", "reviewer"]
}

result = reflection.process({
    "type": "analyze_workflow",
    "workflow_data": workflow_data,
    "goal": "Create REST API",
    "outcome": "Success - API created and tested"
})

# Extract lessons
lessons_result = reflection.process({
    "type": "extract_lessons",
    "experience": result["analysis"]["raw_response"]
})

# Store lessons for future use
memory.store_knowledge(
    category="lessons",
    title="REST API Development Lessons",
    content=str(lessons_result["lessons"]),
    tags=["workflow", "api", "lessons-learned"]
)

print("Lessons learned:", lessons_result["lessons"])
```

## Tips and Best Practices

1. **Always check result status**: `if result["status"] == "success"`
2. **Handle errors gracefully**: Wrap in try-except blocks
3. **Use memory to store important findings**: Help agents learn
4. **Leverage tool manager**: Centralized tool access
5. **Chain agents for complex tasks**: Research → Plan → Code → Test → Review
6. **Use reflection agent**: Learn from successes and failures
7. **Configure timeouts appropriately**: Longer for complex tasks
8. **Save important outputs**: To files or memory system

## Next Steps

- Explore the [README.md](README.md) for architecture details
- Check [SETUP.md](SETUP.md) for installation help
- Create your own custom workflows
- Add custom agents for specialized tasks
