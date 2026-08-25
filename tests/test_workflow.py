"""
Workflow Execution Test
Tests the core orchestration workflow implementation.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_workflow_creation_and_execution():
    """Test creating and executing a simple workflow"""
    print("\nTesting workflow creation and execution...")
    
    from core import Orchestrator, get_llm_client
    from agents import PlannerAgent, CoderAgent
    
    # Create orchestrator
    orchestrator = Orchestrator(workspace_root=Path.cwd() / "test_output")
    
    # Set up LLM client
    try:
        llm_client = get_llm_client()
        orchestrator.set_llm_client(llm_client)
    except Exception as e:
        print(f"  ⚠ Skipping: LLM not available ({e})")
        return
    
    # Register agents
    planner = PlannerAgent()
    coder = CoderAgent()
    
    planner.set_llm_client(llm_client)
    coder.set_llm_client(llm_client)
    
    orchestrator.register_agent(planner)
    orchestrator.register_agent(coder)
    
    # Create workflow
    workflow_id = orchestrator.create_workflow("Create a simple Python calculator")
    assert workflow_id is not None
    
    # Verify workflow created
    workflow = orchestrator.active_workflows.get(workflow_id)
    assert workflow is not None
    assert workflow.status == "created"
    assert workflow.goal == "Create a simple Python calculator"
    
    print(f"  ✓ Created workflow: {workflow_id}")
    print(f"  ✓ Goal: {workflow.goal}")
    print("  ✓ Workflow test passed")


def test_task_ordering():
    """Test task dependency resolution"""
    print("\nTesting task dependency resolution...")
    
    from core import Orchestrator
    
    orchestrator = Orchestrator()
    
    # Create tasks with dependencies
    tasks = [
        {"id": "task_3", "description": "Task 3", "dependencies": ["task_1", "task_2"]},
        {"id": "task_1", "description": "Task 1", "dependencies": []},
        {"id": "task_2", "description": "Task 2", "dependencies": ["task_1"]},
    ]
    
    # Resolve order
    ordered = orchestrator._resolve_task_order(tasks)
    
    # Verify order
    assert len(ordered) == 3
    assert ordered[0]["id"] == "task_1"  # No dependencies, first
    assert ordered[1]["id"] == "task_2"  # Depends on task_1
    assert ordered[2]["id"] == "task_3"  # Depends on both
    
    print(f"  ✓ Task order: {[t['id'] for t in ordered]}")
    print("  ✓ Dependency resolution working correctly")


def test_agent_selection():
    """Test agent selection for different task types"""
    print("\nTesting agent selection...")
    
    from core import Orchestrator
    from agents import PlannerAgent, CoderAgent, TesterAgent, ReviewerAgent
    
    orchestrator = Orchestrator()
    
    # Register agents
    orchestrator.register_agent(PlannerAgent())
    orchestrator.register_agent(CoderAgent())
    orchestrator.register_agent(TesterAgent())
    orchestrator.register_agent(ReviewerAgent())
    
    # Test different task types
    test_cases = [
        ({"description": "Plan the project architecture", "agent": "planner"}, "planner"),
        ({"description": "Implement the feature", "agent": "coder"}, "coder"),
        ({"description": "Write unit tests", "agent": "tester"}, "tester"),
        ({"description": "Review the code", "agent": "reviewer"}, "reviewer"),
        ({"description": "Create a function"}, "coder"),  # Default based on keywords
    ]
    
    for task, expected_agent in test_cases:
        agent = orchestrator._select_agent_for_task(task)
        assert agent is not None, f"No agent selected for: {task}"
        assert agent.agent_id == expected_agent, f"Wrong agent: {agent.agent_id} != {expected_agent}"
    
    print("  ✓ Agent selection working correctly")


def test_filename_inference():
    """Test filename inference from goal and task"""
    print("\nTesting filename inference...")
    
    from core import Orchestrator
    
    orchestrator = Orchestrator()
    
    # Test different scenarios
    test_cases = [
        ("Create a calculator", "Implement main logic", "python", 0, "calculator/main.py"),
        ("Create a calculator", "Write tests", "python", 0, "calculator/tests/test_calculator.py"),
        ("Build a todo app", "Implement main", "python", 0, "todo/main.py"),
        ("Create an API", "Write endpoint", "python", 1, "api/api_1.py"),
    ]
    
    for goal, task_desc, language, index, expected_pattern in test_cases:
        filename = orchestrator._infer_filename(goal, task_desc, language, index)
        assert expected_pattern in filename, f"Filename {filename} doesn't match pattern {expected_pattern}"
    
    print("  ✓ Filename inference working correctly")


def test_context_building():
    """Test building context from task dependencies"""
    print("\nTesting context building...")
    
    from core import Orchestrator
    
    orchestrator = Orchestrator()
    
    # Create mock results
    results = {
        "task_1": {
            "status": "success",
            "code_blocks": [
                {"language": "python", "code": "def add(a, b):\n    return a + b"}
            ]
        },
        "task_2": {
            "status": "success",
            "plan": {
                "summary": "Create a calculator with basic operations"
            }
        },
        "task_3": {
            "status": "failed",
            "error": "Could not connect to database"
        }
    }
    
    # Test context building
    task_with_deps = {
        "id": "task_4",
        "description": "Final integration",
        "dependencies": ["task_1", "task_2", "task_3"]
    }
    
    context = orchestrator._build_task_context(task_with_deps, results)
    
    # Verify context includes relevant info
    assert "task_1" in context
    assert "def add" in context
    assert "task_2" in context
    assert "calculator" in context.lower()
    assert "task_3" in context
    assert "failed" in context
    
    print("  ✓ Context building working correctly")


def run_all_tests():
    """Run all workflow tests"""
    print("=" * 60)
    print("AI SWARM - Workflow Execution Tests")
    print("=" * 60)
    
    tests = [
        test_task_ordering,
        test_agent_selection,
        test_filename_inference,
        test_context_building,
        test_workflow_creation_and_execution,  # Run last as it needs LLM
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test failed: {test.__name__}")
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
