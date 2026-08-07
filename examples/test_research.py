"""
Test Web Research Capabilities
Demonstrates the Research Agent's ability to fetch and process documentation.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_llm_client
from agents import ResearchAgent
from tools import get_tool_manager
from rich.console import Console

console = Console()


def test_web_fetch():
    """Test basic web fetching"""
    console.print("\n[bold cyan]Test 1: Basic Web Fetching[/bold cyan]")
    
    tools = get_tool_manager()
    web_tool = tools.get_tool("web")
    
    if not web_tool.enabled:
        console.print("[yellow]Web research is disabled in config[/yellow]")
        return
    
    # Test fetching a simple page
    result = web_tool.run(
        operation="get_status",
        url="https://python.org"
    )
    
    if result.get("accessible"):
        console.print("[green]✓[/green] Web access working")
        console.print(f"  URL: {result.get('url')}")
        console.print(f"  Status: {result.get('status_code')}")
    else:
        console.print("[red]✗[/red] Web access failed")


def test_documentation_fetch():
    """Test fetching documentation"""
    console.print("\n[bold cyan]Test 2: Documentation Fetching[/bold cyan]")
    
    tools = get_tool_manager()
    web_tool = tools.get_tool("web")
    
    if not web_tool.enabled:
        console.print("[yellow]Skipping - web research disabled[/yellow]")
        return
    
    # Try to fetch Python documentation
    result = web_tool.run(
        operation="search_docs",
        library="python"
    )
    
    if result.get("status") == "success":
        console.print("[green]✓[/green] Documentation fetched successfully")
        console.print(f"  Title: {result.get('title', 'N/A')}")
        console.print(f"  Word count: {result.get('word_count', 0)}")
        console.print(f"  Content preview: {result.get('text', '')[:100]}...")
    else:
        console.print(f"[yellow]⚠[/yellow] Fetch failed: {result.get('error')}")


def test_research_agent():
    """Test Research Agent with LLM"""
    console.print("\n[bold cyan]Test 3: Research Agent (requires Ollama)[/bold cyan]")
    
    try:
        llm = get_llm_client()
        research = ResearchAgent()
        research.set_llm_client(llm)
        
        tools = get_tool_manager()
        research.set_web_tool(tools.get_tool("web"))
        
        # Simple research query
        console.print("  Researching: FastAPI basics...")
        
        result = research.process({
            "type": "check_docs",
            "library": "fastapi",
            "specific_topic": "getting started"
        })
        
        if result.get("status") == "success":
            console.print("[green]✓[/green] Research completed")
            
            doc = result.get("documentation", {})
            console.print(f"\n[bold]Library:[/bold] {result.get('library')}")
            
            # Show sections found
            if doc:
                console.print(f"[bold]Sections found:[/bold] {', '.join(list(doc.keys())[:5])}")
                
                # Show a snippet
                for key in list(doc.keys())[:2]:
                    content = str(doc[key])
                    if content:
                        console.print(f"\n[bold]{key}:[/bold]")
                        console.print(f"  {content[:200]}...")
        else:
            console.print(f"[yellow]⚠[/yellow] Research failed: {result.get('message')}")
    
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] Could not connect to LLM: {e}")
        console.print("  Make sure Ollama is running: ollama serve")


def test_version_check():
    """Test checking library versions"""
    console.print("\n[bold cyan]Test 4: Version Check[/bold cyan]")
    
    try:
        llm = get_llm_client()
        research = ResearchAgent()
        research.set_llm_client(llm)
        
        console.print("  Checking FastAPI version...")
        
        result = research.process({
            "type": "verify_version",
            "library": "fastapi"
        })
        
        if result.get("status") == "success":
            console.print("[green]✓[/green] Version check complete")
            console.print(f"\n{result.get('version_info', '')[:300]}...")
        else:
            console.print("[yellow]⚠[/yellow] Version check failed")
    
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] LLM not available: {e}")


def test_code_examples():
    """Test finding code examples"""
    console.print("\n[bold cyan]Test 5: Code Examples[/bold cyan]")
    
    try:
        llm = get_llm_client()
        research = ResearchAgent()
        research.set_llm_client(llm)
        
        console.print("  Finding examples for: REST API endpoint...")
        
        result = research.process({
            "type": "find_examples",
            "use_case": "Create a simple REST API endpoint",
            "language": "python"
        })
        
        if result.get("status") == "success":
            console.print("[green]✓[/green] Examples found")
            
            examples = result.get("examples", [])
            console.print(f"  Found {len(examples)} code examples")
            
            if examples:
                console.print(f"\n[bold]Example 1:[/bold]")
                console.print(f"```{examples[0].get('language', 'python')}")
                console.print(examples[0].get('code', '')[:200])
                console.print("```")
        else:
            console.print("[yellow]⚠[/yellow] Could not find examples")
    
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] LLM not available: {e}")


def main():
    """Run all tests"""
    console.print("[bold green]Web Research Capabilities Test[/bold green]")
    console.print("=" * 60)
    
    test_web_fetch()
    test_documentation_fetch()
    test_research_agent()
    test_version_check()
    test_code_examples()
    
    console.print("\n" + "=" * 60)
    console.print("[bold]Test Complete![/bold]")
    console.print("\nNote: Some tests require:")
    console.print("  1. Internet connection")
    console.print("  2. Ollama running (ollama serve)")
    console.print("  3. ENABLE_WEB_RESEARCH=true in .env")


if __name__ == "__main__":
    main()
