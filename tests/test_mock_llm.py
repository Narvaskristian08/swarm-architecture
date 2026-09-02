"""
Comprehensive Mock LLM Tests
Tests the complete NORA workflow with simulated LLM responses.
No actual LLM model required.
"""
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class MockLLMClient:
    """Mock LLM client that returns predetermined responses"""
    
    def __init__(self):
        self.provider = "mock"
        self.call_count = 0
        self.responses = self._setup_responses()
    
    def _setup_responses(self) -> Dict[str, Any]:
        """Setup predetermined responses for different scenarios"""
        return {
            "planner_calculator": {
                "status": "success",
                "plan": {
                    "goal": "Create a simple Python calculator",
                    "tasks": [
                        {
                            "id": "task_1",
                            "description": "Implement calculator functions",
                            "dependencies": [],
                            "agent": "coder",
                            "language": "python"
                        },
                        {
                            "id": "task_2", 
                            "description": "Create unit tests",
                            "dependencies": ["task_1"],
                            "agent": "tester",
                            "language": "python"
                        }
                    ]
                }
            },
            "coder_calculator": {
                "status": "success",
                "code_blocks": [
                    {
                        "language": "python",
                        "code": """def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
""",
                        "path": "calculator/main.py"
                    }
                ]
            },
            "tester_calculator": {
                "status": "success",
                "test_code": [
                    {
                        "language": "python",
                        "code": """import pytest
from calculator.main import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    
def test_multiply():
    assert multiply(3, 4) == 12
    
def test_divide():
    assert divide(10, 2) == 5
    with pytest.raises(ValueError):
        divide(1, 0)
""",
                        "path": "calculator/tests/test_calculator.py"
                    }
                ]
            },
            "reviewer_code": {
                "status": "success",
                "review": {
                    "issues": [],
                    "positive_aspects": ["Clean code", "Good error handling"],
                    "suggestions": ["Add docstrings"],
                    "recommendation": "approve"
                }
            }
        }
    
    def health(self) -> Dict[str, Any]:
        return {
            "provider": "mock",
            "ready": True,
            "runtime_available": True,
            "model": "mock-model",
            "message": "Mock LLM is ready"
        }
    
    @property
    def model_identifier(self) -> str:
        return "mock-model"
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate mock response based on prompt content"""
        self.call_count += 1
        
        # Return the raw response dict - agents will parse it
        # Determine response type from prompt
        if "plan" in prompt.lower() or "task" in prompt.lower():
            # Return raw response that planner expects
            return {
                "response": """{
    "goal": "Create a simple Python calculator",
    "tasks": [
        {
            "id": "task_1",
            "description": "Implement calculator functions",
            "dependencies": [],
            "agent": "coder",
            "language": "python"
        },
        {
            "id": "task_2",
            "description": "Create unit tests",
            "dependencies": ["task_1"],
            "agent": "tester",
            "language": "python"
        }
    ]
}"""
            }
        elif "implement" in prompt.lower() or "code" in prompt.lower():
            return {
                "response": """```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```"""
            }
        elif "test" in prompt.lower():
            return {
                "response": """```python
import pytest

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2
```"""
            }
        elif "review" in prompt.lower():
            return {
                "response": """## Issues Found
None

## Positive Aspects
- Clean code
- Good error handling

## Overall Assessment
Approve"""
            }
        else:
            return {"response": "Mock response"}
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Mock chat interface"""
        return self.generate(messages[-1]["content"] if messages else "")


def test_mock_llm_client():
    """Test that mock LLM client works correctly"""
    print("\nTesting mock LLM client...")
    
    client = MockLLMClient()
    
    # Test health
    health = client.health()
    assert health["ready"] == True
    assert health["provider"] == "mock"
    print("  ✓ Mock LLM health check works")
    
    # Test generate - returns response with "response" key
    response = client.generate("Create a plan for a calculator")
    assert "response" in response
    print("  ✓ Mock LLM generate works")
    
    # Test model identifier
    assert client.model_identifier == "mock-model"
    print("  ✓ Mock LLM model identifier works")


def test_planner_with_mock_llm():
    """Test planner agent with mock LLM"""
    print("\nTesting planner agent with mock LLM...")
    
    from core import Orchestrator
    from agents import PlannerAgent
    
    # Setup
    client = MockLLMClient()
    planner = PlannerAgent()
    planner.set_llm_client(client)
    
    # Test planning
    result = planner.process({
        "type": "create_plan",
        "goal": "Create a simple Python calculator"
    })
    
    assert result["status"] == "success"
    assert "plan" in result
    assert len(result["plan"]["tasks"]) > 0
    print(f"  ✓ Planner created plan with {len(result['plan']['tasks'])} tasks")


def test_coder_with_mock_llm():
    """Test coder agent with mock LLM"""
    print("\nTesting coder agent with mock LLM...")
    
    from agents import CoderAgent
    
    # Setup
    client = MockLLMClient()
    coder = CoderAgent()
    coder.set_llm_client(client)
    
    # Test code generation
    result = coder.process({
        "type": "implement_feature",
        "specification": "Implement calculator functions",
        "language": "python"
    })
    
    assert result["status"] == "success"
    assert "code_blocks" in result
    assert len(result["code_blocks"]) > 0
    print(f"  ✓ Coder generated {len(result['code_blocks'])} code blocks")
    
    # Check code content
    code = result["code_blocks"][0]["code"]
    assert "def " in code
    print("  ✓ Code contains function definitions")


def test_tester_with_mock_llm():
    """Test tester agent with mock LLM"""
    print("\nTesting tester agent with mock LLM...")
    
    from agents import TesterAgent
    
    # Setup
    client = MockLLMClient()
    tester = TesterAgent()
    tester.set_llm_client(client)
    
    # Test test generation
    result = tester.process({
        "type": "generate_test_code",
        "code": "def add(a, b): return a + b",
        "language": "python",
        "test_framework": "pytest"
    })
    
    assert result["status"] == "success"
    assert "test_code" in result or "code_blocks" in result
    print("  ✓ Tester generated test code")


def test_reviewer_with_mock_llm():
    """Test reviewer agent with mock LLM"""
    print("\nTesting reviewer agent with mock LLM...")
    
    from agents import ReviewerAgent
    
    # Setup
    client = MockLLMClient()
    reviewer = ReviewerAgent()
    reviewer.set_llm_client(client)
    
    # Test code review
    result = reviewer.process({
        "type": "review_code",
        "code": "def add(a, b): return a + b",
        "language": "python"
    })
    
    assert result["status"] == "success"
    assert "review" in result
    print("  ✓ Reviewer analyzed code")


def test_full_workflow_with_mock_llm():
    """Test complete workflow execution with mock LLM"""
    print("\nTesting full workflow with mock LLM...")
    
    from core import Orchestrator
    from agents import PlannerAgent, CoderAgent, TesterAgent, ReviewerAgent
    from tools import get_tool_manager
    
    # Setup test workspace
    test_workspace = project_root / "test_mock_workflow"
    if test_workspace.exists():
        shutil.rmtree(test_workspace)
    test_workspace.mkdir()
    
    try:
        # Setup mock LLM
        client = MockLLMClient()
        
        # Create orchestrator
        orchestrator = Orchestrator(workspace_root=test_workspace)
        orchestrator.set_llm_client(client)
        
        # Register agents with mock LLM
        planner = PlannerAgent()
        coder = CoderAgent()
        tester = TesterAgent()
        reviewer = ReviewerAgent()
        
        for agent in [planner, coder, tester, reviewer]:
            agent.set_llm_client(client)
            orchestrator.register_agent(agent)
        
        print(f"  ✓ Registered {len(orchestrator.registered_agents)} agents")
        
        # Create workflow
        goal = "Create a simple Python calculator"
        workflow_id = orchestrator.create_workflow(goal)
        print(f"  ✓ Created workflow: {workflow_id[:8]}...")
        
        # Execute workflow (with mock LLM)
        with patch('core.llm_client.get_llm_client', return_value=client):
            result = orchestrator.execute_workflow(workflow_id)
        
        # Verify result
        assert result["status"] in ["completed", "completed_with_errors", "blocked"]
        print(f"  ✓ Workflow finished with status: {result['status']}")
        
        # Check tasks were processed
        if result.get("tasks_completed", 0) > 0:
            print(f"  ✓ Completed {result['tasks_completed']} tasks")
        
        # Check files were created (if workflow succeeded)
        if result.get("files_created"):
            print(f"  ✓ Created {len(result['files_created'])} files")
            for file in result["files_created"][:3]:
                file_path = test_workspace / file
                if file_path.exists():
                    print(f"    - {file} ({file_path.stat().st_size} bytes)")
        
        return True
        
    finally:
        # Cleanup
        if test_workspace.exists():
            shutil.rmtree(test_workspace)


def test_orchestrator_without_llm():
    """Test that orchestrator handles missing LLM gracefully"""
    print("\nTesting orchestrator without LLM...")
    
    from core import Orchestrator
    
    # Create orchestrator without LLM
    orchestrator = Orchestrator(workspace_root=Path("./test_no_llm"))
    
    # Create workflow
    workflow_id = orchestrator.create_workflow("Test goal")
    
    # Execute should fail gracefully
    result = orchestrator.execute_workflow(workflow_id)
    
    assert result["status"] in ["blocked", "failed"]
    assert "error_code" in result or "message" in result
    print(f"  ✓ Orchestrator handled missing LLM: {result['status']}")


def test_agent_capability_matching():
    """Test that agents are correctly matched to tasks"""
    print("\nTesting agent capability matching...")
    
    from core import Orchestrator
    from agents import PlannerAgent, CoderAgent, TesterAgent, ReviewerAgent, ResearchAgent
    
    # Setup
    orchestrator = Orchestrator()
    
    for AgentClass in [PlannerAgent, CoderAgent, TesterAgent, ReviewerAgent, ResearchAgent]:
        agent = AgentClass()
        orchestrator.register_agent(agent)
    
    # Test task matching
    test_cases = [
        ({"description": "Plan the project architecture", "agent": "planner"}, "planner"),
        ({"description": "Implement the feature", "agent": "coder"}, "coder"),
        ({"description": "Write unit tests", "agent": "tester"}, "tester"),
        ({"description": "Review the code", "agent": "reviewer"}, "reviewer"),
        ({"description": "Research best frameworks"}, "research"),  # Should match research agent
    ]
    
    for task, expected_agent in test_cases:
        agent = orchestrator._select_agent_for_task(task)
        assert agent is not None, f"No agent selected for: {task['description']}"
        assert agent.agent_id == expected_agent, f"Wrong agent: {agent.agent_id} != {expected_agent}"
    
    print(f"  ✓ Agent matching works for {len(test_cases)} test cases")


def test_workspace_isolation():
    """Test that generated files go to correct workspace"""
    print("\nTesting workspace isolation...")
    
    from core import Orchestrator
    
    # Create two different workspaces
    workspace1 = project_root / "test_workspace_1"
    workspace2 = project_root / "test_workspace_2"
    
    for ws in [workspace1, workspace2]:
        if ws.exists():
            shutil.rmtree(ws)
        ws.mkdir()
    
    try:
        # Create orchestrators with different workspaces
        orch1 = Orchestrator(workspace_root=workspace1)
        orch2 = Orchestrator(workspace_root=workspace2)
        
        # Verify workspace roots
        assert orch1.workspace_root == workspace1.resolve()
        assert orch2.workspace_root == workspace2.resolve()
        
        print("  ✓ Different workspaces are isolated")
        
        # Test path safety
        safe_path = orch1._safe_artifact_path("project/main.py")
        assert "project/main.py" in safe_path
        print("  ✓ Safe paths are accepted")
        
        # Test unsafe path rejection
        try:
            unsafe = orch1._safe_artifact_path("../../../etc/passwd")
            print("  ✗ Unsafe path was accepted (BAD)")
            assert False, "Should have rejected path traversal"
        except ValueError:
            print("  ✓ Path traversal is blocked")
        
    finally:
        # Cleanup
        for ws in [workspace1, workspace2]:
            if ws.exists():
                shutil.rmtree(ws)


def test_dependency_resolution():
    """Test task dependency resolution"""
    print("\nTesting dependency resolution...")
    
    from core import Orchestrator
    
    orchestrator = Orchestrator()
    
    # Test linear dependencies
    tasks = [
        {"id": "a", "description": "Task A", "dependencies": []},
        {"id": "b", "description": "Task B", "dependencies": ["a"]},
        {"id": "c", "description": "Task C", "dependencies": ["b"]},
    ]
    
    ordered = orchestrator._resolve_task_order(tasks)
    assert [t["id"] for t in ordered] == ["a", "b", "c"]
    print("  ✓ Linear dependencies resolved correctly")
    
    # Test diamond dependencies
    tasks = [
        {"id": "a", "description": "Task A", "dependencies": []},
        {"id": "b", "description": "Task B", "dependencies": ["a"]},
        {"id": "c", "description": "Task C", "dependencies": ["a"]},
        {"id": "d", "description": "Task D", "dependencies": ["b", "c"]},
    ]
    
    ordered = orchestrator._resolve_task_order(tasks)
    ids = [t["id"] for t in ordered]
    assert ids.index("a") < ids.index("b")
    assert ids.index("a") < ids.index("c")
    assert ids.index("b") < ids.index("d")
    assert ids.index("c") < ids.index("d")
    print("  ✓ Diamond dependencies resolved correctly")
    
    # Test circular dependency detection
    tasks = [
        {"id": "a", "description": "Task A", "dependencies": ["b"]},
        {"id": "b", "description": "Task B", "dependencies": ["a"]},
    ]
    
    try:
        orchestrator._resolve_task_order(tasks)
        print("  ✗ Circular dependency not detected (BAD)")
        assert False, "Should have detected circular dependency"
    except ValueError:
        print("  ✓ Circular dependencies detected")


def run_all_tests():
    """Run all mock LLM tests"""
    print("=" * 60)
    print("NORA - Mock LLM Workflow Tests")
    print("=" * 60)
    
    tests = [
        test_mock_llm_client,
        test_planner_with_mock_llm,
        test_coder_with_mock_llm,
        test_tester_with_mock_llm,
        test_reviewer_with_mock_llm,
        test_full_workflow_with_mock_llm,
        test_orchestrator_without_llm,
        test_agent_capability_matching,
        test_workspace_isolation,
        test_dependency_resolution,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Tests: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
