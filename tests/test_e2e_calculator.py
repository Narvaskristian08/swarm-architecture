"""
End-to-End Test: Calculator Project
Tests the complete workflow from goal to actual file creation.
"""
import sys
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_calculator_creation():
    """Test creating a calculator application end-to-end"""
    print("\n" + "=" * 60)
    print("End-to-End Test: Creating Calculator Application")
    print("=" * 60)
    
    from core import Orchestrator, get_llm_client
    from agents import PlannerAgent, CoderAgent
    from tools import get_tool_manager
    
    # Setup test workspace
    test_workspace = project_root / "test_output_e2e"
    if test_workspace.exists():
        shutil.rmtree(test_workspace)
    test_workspace.mkdir()
    
    print(f"\n📁 Test workspace: {test_workspace}")
    
    try:
        # Initialize LLM client
        print("\n🔌 Connecting to LLM...")
        llm_client = get_llm_client()
        print("✓ Connected to Ollama")
        
        # Create orchestrator with test workspace
        print("\n🎯 Initializing orchestrator...")
        orchestrator = Orchestrator(workspace_root=test_workspace)
        orchestrator.set_llm_client(llm_client)
        
        # Register agents
        planner = PlannerAgent()
        coder = CoderAgent()
        
        planner.set_llm_client(llm_client)
        coder.set_llm_client(llm_client)
        
        orchestrator.register_agent(planner)
        orchestrator.register_agent(coder)
        print(f"✓ Registered {len(orchestrator.registered_agents)} agents")
        
        # Create and execute workflow
        goal = "Create a simple Python calculator with add, subtract, multiply, and divide functions"
        print(f"\n🎯 Goal: {goal}")
        
        print("\n⚙️  Creating workflow...")
        workflow_id = orchestrator.create_workflow(goal)
        print(f"✓ Workflow created: {workflow_id}")
        
        print("\n▶️  Executing workflow...")
        print("-" * 60)
        result = orchestrator.execute_workflow(workflow_id)
        print("-" * 60)
        
        # Check results
        print("\n📊 Results:")
        print(f"  Status: {result.get('status')}")
        print(f"  Tasks completed: {result.get('tasks_completed', 0)}")
        print(f"  Tasks failed: {result.get('tasks_failed', 0)}")
        
        if result.get('files_created'):
            print(f"\n📄 Files created: {len(result['files_created'])}")
            for file in result['files_created']:
                file_path = test_workspace / file
                if file_path.exists():
                    print(f"  ✓ {file} ({file_path.stat().st_size} bytes)")
                else:
                    print(f"  ✗ {file} (not found)")
        
        # Display plan
        if 'plan' in result:
            plan = result['plan']
            print(f"\n📋 Plan Summary:")
            print(f"  Goal: {plan.get('goal', 'N/A')}")
            print(f"  Tasks: {len(plan.get('tasks', []))}")
            for i, task in enumerate(plan.get('tasks', [])[:3], 1):
                print(f"    {i}. {task.get('description', 'N/A')[:60]}")
        
        # Show sample code
        if result.get('files_created'):
            first_file = test_workspace / result['files_created'][0]
            if first_file.exists():
                print(f"\n📝 Sample code from {first_file.name}:")
                print("-" * 60)
                content = first_file.read_text()
                print(content[:400] + ("..." if len(content) > 400 else ""))
                print("-" * 60)
        
        # Verify success
        assert result['status'] in ['completed', 'completed_with_errors'], \
            f"Workflow failed: {result.get('message')}"
        
        assert result.get('tasks_completed', 0) > 0, "No tasks were completed"
        
        print("\n✅ End-to-end test PASSED!")
        print(f"✅ Created calculator application in {test_workspace}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup (optional - comment out to inspect files)
        # if test_workspace.exists():
        #     shutil.rmtree(test_workspace)
        pass


if __name__ == "__main__":
    success = test_calculator_creation()
    sys.exit(0 if success else 1)
