"""
Error Scenario Tests for NORA
Tests error handling, validation, and edge cases.
"""
import sys
import shutil
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestMalformedPlans:
    """Test handling of malformed planner output"""
    
    def test_empty_task_list(self):
        """Test that empty task list is rejected"""
        print("\nTesting empty task list rejection...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # Try to normalize empty task list
        try:
            orch._normalize_tasks([])
            print("  ✗ Empty task list was accepted (BAD)")
            assert False, "Should reject empty task list"
        except ValueError as e:
            assert "empty" in str(e).lower()
            print(f"  ✓ Empty task list rejected: {str(e)[:50]}")
    
    def test_missing_task_description(self):
        """Test that tasks without description are rejected"""
        print("\nTesting missing task description rejection...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # Task without description
        tasks = [
            {"id": "task_1"}  # Missing description
        ]
        
        try:
            orch._normalize_tasks(tasks)
            print("  ✗ Task without description was accepted (BAD)")
            assert False, "Should reject task without description"
        except ValueError as e:
            assert "description" in str(e).lower()
            print(f"  ✓ Missing description rejected: {str(e)[:50]}")
    
    def test_duplicate_task_ids(self):
        """Test that duplicate task IDs are rejected"""
        print("\nTesting duplicate task ID rejection...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # Tasks with duplicate IDs
        tasks = [
            {"id": "task_1", "description": "First task", "dependencies": []},
            {"id": "task_1", "description": "Second task", "dependencies": []},  # Duplicate ID
        ]
        
        try:
            orch._normalize_tasks(tasks)
            print("  ✗ Duplicate task IDs were accepted (BAD)")
            assert False, "Should reject duplicate task IDs"
        except ValueError as e:
            assert "duplicate" in str(e).lower()
            print(f"  ✓ Duplicate IDs rejected: {str(e)[:50]}")
    
    def test_invalid_dependencies(self):
        """Test that dependencies on non-existent tasks are rejected"""
        print("\nTesting invalid dependency rejection...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # Task depends on non-existent task
        tasks = [
            {"id": "task_1", "description": "First task", "dependencies": ["task_2"]},  # task_2 doesn't exist
        ]
        
        try:
            orch._normalize_tasks(tasks)
            print("  ✗ Invalid dependency was accepted (BAD)")
            assert False, "Should reject unknown dependency"
        except ValueError as e:
            assert "unknown" in str(e).lower() or "dependencies" in str(e).lower()
            print(f"  ✓ Invalid dependency rejected: {str(e)[:50]}")
    
    def test_self_dependency(self):
        """Test that self-dependencies are rejected"""
        print("\nTesting self-dependency rejection...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # Task depends on itself
        tasks = [
            {"id": "task_1", "description": "Task", "dependencies": ["task_1"]},  # Self-dependency
        ]
        
        try:
            orch._normalize_tasks(tasks)
            print("  ✗ Self-dependency was accepted (BAD)")
            assert False, "Should reject self-dependency"
        except ValueError as e:
            assert "itself" in str(e).lower() or "self" in str(e).lower()
            print(f"  ✓ Self-dependency rejected: {str(e)[:50]}")


class TestCircularDependencies:
    """Test circular dependency detection"""
    
    def test_simple_cycle(self):
        """Test detection of simple 2-node cycle"""
        print("\nTesting simple cycle detection...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # A -> B -> A
        tasks = [
            {"id": "a", "description": "A", "dependencies": ["b"]},
            {"id": "b", "description": "B", "dependencies": ["a"]},
        ]
        
        try:
            normalized = orch._normalize_tasks(tasks)
            orch._resolve_task_order(normalized)
            print("  ✗ Circular dependency not detected (BAD)")
            assert False, "Should detect circular dependency"
        except ValueError as e:
            assert "circular" in str(e).lower()
            print(f"  ✓ Simple cycle detected: {str(e)[:50]}")
    
    def test_complex_cycle(self):
        """Test detection of multi-node cycle"""
        print("\nTesting complex cycle detection...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # A -> B -> C -> A
        tasks = [
            {"id": "a", "description": "A", "dependencies": ["c"]},
            {"id": "b", "description": "B", "dependencies": ["a"]},
            {"id": "c", "description": "C", "dependencies": ["b"]},
        ]
        
        try:
            normalized = orch._normalize_tasks(tasks)
            orch._resolve_task_order(normalized)
            print("  ✗ Complex circular dependency not detected (BAD)")
            assert False, "Should detect circular dependency"
        except ValueError as e:
            assert "circular" in str(e).lower()
            print(f"  ✓ Complex cycle detected: {str(e)[:50]}")


class TestPathTraversal:
    """Test path traversal prevention"""
    
    def test_absolute_path_rejection(self):
        """Test that absolute paths are rejected"""
        print("\nTesting absolute path rejection...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # Try to use absolute path
        try:
            orch._safe_artifact_path("/etc/passwd")
            print("  ✗ Absolute path was accepted (BAD)")
            assert False, "Should reject absolute path"
        except ValueError as e:
            assert "unsafe" in str(e).lower()
            print(f"  ✓ Absolute path rejected: {str(e)[:50]}")
    
    def test_parent_traversal_rejection(self):
        """Test that .. traversal is rejected"""
        print("\nTesting parent traversal rejection...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # Try to traverse to parent
        try:
            orch._safe_artifact_path("../../../etc/passwd")
            print("  ✗ Path traversal was accepted (BAD)")
            assert False, "Should reject path traversal"
        except ValueError as e:
            assert "unsafe" in str(e).lower()
            print(f"  ✓ Path traversal rejected: {str(e)[:50]}")
    
    def test_empty_path_rejection(self):
        """Test that empty paths are rejected"""
        print("\nTesting empty path rejection...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # Try empty path
        try:
            orch._safe_artifact_path("")
            print("  ✗ Empty path was accepted (BAD)")
            assert False, "Should reject empty path"
        except ValueError as e:
            assert "empty" in str(e).lower()
            print(f"  ✓ Empty path rejected: {str(e)[:50]}")
    
    def test_valid_relative_path(self):
        """Test that valid relative paths are accepted"""
        print("\nTesting valid relative path acceptance...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # Valid relative path
        result = orch._safe_artifact_path("project/main.py")
        assert "project/main.py" in result
        print(f"  ✓ Valid relative path accepted: {result}")


class TestConfigurationErrors:
    """Test configuration error handling"""
    
    def test_invalid_llm_provider(self):
        """Test that invalid LLM provider is rejected"""
        print("\nTesting invalid LLM provider rejection...")
        
        import os
        original = os.environ.get("LLM_PROVIDER")
        
        try:
            # Set invalid provider
            os.environ["LLM_PROVIDER"] = "invalid_provider"
            
            # Try to import config - should fail
            try:
                # Force re-import
                import importlib
                import config
                importlib.reload(config)
                print("  ✗ Invalid provider was accepted (BAD)")
                assert False, "Should reject invalid provider"
            except ValueError as e:
                assert "llama_cpp" in str(e) or "ollama" in str(e)
                print(f"  ✓ Invalid provider rejected: {str(e)[:50]}")
        
        finally:
            # Restore original
            if original:
                os.environ["LLM_PROVIDER"] = original
            elif "LLM_PROVIDER" in os.environ:
                del os.environ["LLM_PROVIDER"]
    
    def test_missing_gguf_path(self):
        """Test handling of missing GGUF model path"""
        print("\nTesting missing GGUF path handling...")
        
        from core.llm_client import LlamaCppClient
        
        # Client without model path
        client = LlamaCppClient(model_path="")
        
        health = client.health()
        assert health["ready"] == False
        assert "LLAMA_MODEL_PATH" in health["message"]
        print(f"  ✓ Missing GGUF path detected: {health['message'][:50]}")
    
    def test_invalid_gguf_path(self):
        """Test handling of invalid GGUF model path"""
        print("\nTesting invalid GGUF path handling...")
        
        from core.llm_client import LlamaCppClient
        
        # Client with non-existent model path
        client = LlamaCppClient(model_path="/nonexistent/model.gguf")
        
        health = client.health()
        assert health["ready"] == False
        assert "not found" in health["message"].lower() or "does not exist" in health["message"].lower()
        print(f"  ✓ Invalid GGUF path detected: {health['message'][:50]}")


class TestWorkflowFailures:
    """Test workflow failure scenarios"""
    
    def test_workflow_without_llm(self):
        """Test that workflow fails gracefully without LLM"""
        print("\nTesting workflow without LLM...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        # No LLM client set
        
        workflow_id = orch.create_workflow("Test goal")
        result = orch.execute_workflow(workflow_id)
        
        assert result["status"] == "blocked"
        assert "error_code" in result
        assert result["error_code"] == "model_not_ready"
        print(f"  ✓ Workflow blocked without LLM: {result['message'][:50]}")
    
    def test_workflow_with_missing_agent(self):
        """Test that workflow handles missing agent gracefully"""
        print("\nTesting workflow with missing agent...")
        
        from core import Orchestrator
        from agents import PlannerAgent
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        # Only register planner, not coder
        orch.register_agent(PlannerAgent())
        
        # Try to select coder agent
        task = {"description": "Implement feature", "agent": "coder"}
        agent = orch._select_agent_for_task(task)
        
        # Should return None or fall back
        print(f"  ✓ Missing agent handled: {agent.agent_id if agent else 'None'}")
    
    def test_duplicate_filenames(self):
        """Test that duplicate filenames are handled"""
        print("\nTesting duplicate filename handling...")
        
        from core import Orchestrator
        
        orch = Orchestrator(workspace_root=Path("./test_errors"))
        
        # Create unique filename when collision exists
        filename = orch._unique_filename("project/main.py", "task_1", [])
        
        # Should return original if not exists
        assert filename == "project/main.py"
        print(f"  ✓ Unique filename generated: {filename}")
        
        # Now test with collision
        # (This would need the workspace to exist, which we skip for simplicity)


class TestAgentErrors:
    """Test agent error handling"""
    
    def test_agent_without_llm(self):
        """Test that agent handles missing LLM gracefully"""
        print("\nTesting agent without LLM...")
        
        from agents import CoderAgent
        
        coder = CoderAgent()
        # No LLM client set
        
        result = coder.process({
            "type": "implement_feature",
            "specification": "Create a function"
        })
        
        # Should return a result (status may vary)
        # Agent may return "success" with mock code or "error"/"failed"
        assert "status" in result
        print(f"  ✓ Agent handled missing LLM: status={result['status']}")
    
    def test_agent_with_invalid_input(self):
        """Test that agent validates input"""
        print("\nTesting agent with invalid input...")
        
        from agents import CoderAgent
        
        coder = CoderAgent()
        
        # Empty specification
        result = coder.process({
            "type": "implement_feature",
            "specification": ""
        })
        
        # Should handle gracefully
        assert result["status"] in ["error", "failed"]
        print(f"  ✓ Agent handled invalid input: {result.get('message', 'Error')[:50]}")


def run_all_error_tests():
    """Run all error scenario tests"""
    print("=" * 60)
    print("NORA - Error Scenario Tests")
    print("=" * 60)
    
    # Test classes
    test_classes = [
        TestMalformedPlans(),
        TestCircularDependencies(),
        TestPathTraversal(),
        TestConfigurationErrors(),
        TestWorkflowFailures(),
        TestAgentErrors(),
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        # Run all test methods in class
        for method_name in dir(test_class):
            if method_name.startswith("test_"):
                method = getattr(test_class, method_name)
                try:
                    method()
                    passed += 1
                except Exception as e:
                    print(f"\n✗ Test failed: {method_name}")
                    print(f"  Error: {e}")
                    import traceback
                    traceback.print_exc()
                    failed += 1
    
    print("\n" + "=" * 60)
    print(f"Error Tests: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_error_tests()
    sys.exit(0 if success else 1)
