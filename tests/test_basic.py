"""
Basic Tests for AI Swarm
Tests core functionality without requiring Ollama to be running.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    # Core
    from core import BaseAgent, Orchestrator, get_llm_client
    from core import PromptTemplate, ResponseParser
    
    # Agents
    from agents import (
        PlannerAgent, CoderAgent, ReviewerAgent,
        ResearchAgent, TesterAgent, MemoryAgentClass, ReflectionAgent
    )
    
    # Memory
    from memory import (
        ShortTermMemory, LongTermMemory, VectorMemory,
        MemoryManager, get_memory_manager
    )
    
    # Tools
    from tools import (
        FileTool, TerminalTool, GitTool, WebTool,
        ToolManager, get_tool_manager
    )
    
    print(" All imports successful")


def test_agent_creation():
    """Test agent instantiation"""
    print("\nTesting agent creation...")
    
    from agents import (
        PlannerAgent, CoderAgent, ReviewerAgent,
        ResearchAgent, TesterAgent, MemoryAgentClass, ReflectionAgent
    )
    
    agents = [
        PlannerAgent(),
        CoderAgent(),
        ReviewerAgent(),
        ResearchAgent(),
        TesterAgent(),
        MemoryAgentClass(),
        ReflectionAgent()
    ]
    
    for agent in agents:
        assert agent.agent_id is not None
        assert agent.name is not None
        assert len(agent.capabilities) > 0
    
    print(f" Created {len(agents)} agents successfully")


def test_orchestrator():
    """Test orchestrator functionality"""
    print("\nTesting orchestrator...")
    
    from core import Orchestrator
    from agents import PlannerAgent, CoderAgent
    
    orchestrator = Orchestrator()
    
    # Register agents
    planner = PlannerAgent()
    coder = CoderAgent()
    
    orchestrator.register_agent(planner)
    orchestrator.register_agent(coder)
    
    # Check registration
    assert len(orchestrator.registered_agents) == 2
    assert orchestrator.get_agent("planner") is not None
    assert orchestrator.get_agent("coder") is not None
    
    # Test status
    status = orchestrator.get_system_status()
    assert "orchestrator_status" in status
    assert len(status["registered_agents"]) == 2
    
    print(" Orchestrator working correctly")


def test_memory_system():
    """Test memory initialization"""
    print("\nTesting memory system...")
    
    from memory import ShortTermMemory, get_memory_manager
    
    # Test short-term memory
    stm = ShortTermMemory()
    stm.start_session("test-session")
    stm.add_message("agent1", "agent2", "test message")
    
    messages = stm.get_recent_messages(5)
    assert len(messages) == 1
    assert messages[0]["content"] == "test message"
    
    # Test memory manager
    mm = get_memory_manager()
    stats = mm.get_statistics()
    assert "short_term" in stats
    assert "long_term" in stats
    assert "vector" in stats
    
    print(" Memory system initialized")


def test_tool_system():
    """Test tool initialization"""
    print("\nTesting tool system...")
    
    from tools import get_tool_manager
    
    tm = get_tool_manager()
    tools = tm.list_tools()
    
    assert len(tools) > 0
    
    # Test file tool
    file_tool = tm.get_tool("file")
    assert file_tool is not None
    assert file_tool.enabled
    
    # Test terminal tool
    terminal_tool = tm.get_tool("terminal")
    assert terminal_tool is not None
    
    print(f" Tool system has {len(tools)} tools")


def test_response_parser():
    """Test response parsing utilities"""
    print("\nTesting response parser...")
    
    from core import ResponseParser
    
    # Test JSON extraction
    text_with_json = 'Here is data: ```json\n{"key": "value"}\n```'
    result = ResponseParser.extract_json(text_with_json)
    assert result == {"key": "value"}
    
    # Test code block extraction
    text_with_code = '```python\nprint("hello")\n```'
    blocks = ResponseParser.extract_code_blocks(text_with_code)
    assert len(blocks) == 1
    assert blocks[0]["language"] == "python"
    
    # Test list extraction
    text_with_list = "1. First\n2. Second\n3. Third"
    items = ResponseParser.extract_list(text_with_list)
    assert len(items) == 3
    
    print("Response parser working correctly")


def test_prompt_templates():
    """Test prompt template system"""
    print("\nTesting prompt templates...")
    
    from core import PromptTemplate
    
    # Test system prompts
    planner_prompt = PromptTemplate.get_system_prompt("planner")
    assert len(planner_prompt) > 0
    assert "planner" in planner_prompt.lower()
    
    coder_prompt = PromptTemplate.get_system_prompt("coder")
    assert len(coder_prompt) > 0
    assert "code" in coder_prompt.lower()
    
    # Test task prompt formatting
    task = {"description": "Test task", "requirements": "Must work"}
    prompt = PromptTemplate.format_task_prompt("coder", task)
    assert "Test task" in prompt
    assert "Must work" in prompt
    
    print("Prompt templates working correctly")


def test_file_tool_validation():
    """Test file tool parameter validation"""
    print("\nTesting file tool validation...")
    
    from tools import FileTool
    from pathlib import Path
    
    tool = FileTool(workspace_root=Path.cwd())
    
    # Test validation
    valid, error = tool.validate_params(operation="read", file_path="test.txt")
    assert valid
    
    # Test missing operation
    valid, error = tool.validate_params(operation="")
    assert not valid
    
    # Test missing file_path
    valid, error = tool.validate_params(operation="read")
    assert not valid
    
    print(" File tool validation working")


def test_agent_capabilities():
    """Test agent capability system"""
    print("\nTesting agent capabilities...")
    
    from agents import PlannerAgent, CoderAgent, ReviewerAgent
    
    planner = PlannerAgent()
    assert planner.can_handle("planning")
    assert not planner.can_handle("unknown_capability")
    
    coder = CoderAgent()
    assert coder.can_handle("code_generation")
    
    reviewer = ReviewerAgent()
    assert reviewer.can_handle("code_review")
    
    print("Agent capabilities working correctly")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("AI SWARM - Basic Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_agent_creation,
        test_orchestrator,
        test_memory_system,
        test_tool_system,
        test_response_parser,
        test_prompt_templates,
        test_file_tool_validation,
        test_agent_capabilities,
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
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Tests: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
