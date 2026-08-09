"""
Demo: YOLO Framework Research
Shows how the swarm automatically learns about YOLO and similar frameworks
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import ResearchAgent
from core import get_llm_client
from memory import get_memory_manager
from tools import get_tool_manager
from rich.console import Console
from rich.panel import Panel

console = Console()


def demo_yolo_research():
    """Demonstrate automatic YOLO framework research"""
    console.print(Panel.fit(
        "[bold green]YOLO Framework Research Demo[/bold green]\n"
        "[dim]Simulating detection and research of YOLO in a project[/dim]",
        border_style="green"
    ))
    
    # Simulate a project with YOLO
    simulated_project = {
        "libraries": ["ultralytics", "torch", "opencv-python", "numpy", "pillow"],
        "project_type": "Computer Vision Application",
        "language": "Python"
    }
    
    console.print(f"\n[bold cyan]Simulated Project:[/bold cyan]")
    console.print(f"Type: {simulated_project['project_type']}")
    console.print(f"Libraries detected: {', '.join(simulated_project['libraries'])}\n")
    
    # Initialize systems
    try:
        llm = get_llm_client()
        research = ResearchAgent()
        research.set_llm_client(llm)
        
        tools = get_tool_manager()
        research.set_web_tool(tools.get_tool("web"))
        
        memory = get_memory_manager()
        
        llm_available = True
    except Exception as e:
        console.print(f"[yellow]LLM not available: {e}[/yellow]")
        console.print("[dim]This demo requires Ollama to be running[/dim]\n")
        llm_available = False
        return
    
    # Research YOLO
    console.print("[bold cyan]Step 1: Researching Ultralytics (YOLO)[/bold cyan]\n")
    
    with console.status("[bold green]Querying LLM and searching documentation...", spinner="dots"):
        result = research.process({
            "type": "research_topic",
            "topic": "Ultralytics YOLO - what is it, what is it used for, and what are the latest versions?",
            "context": "This is used in a computer vision application with PyTorch"
        })
    
    if result.get("status") == "success":
        findings = result.get("findings", {})
        summary = findings.get("summary", findings.get("intro", "No summary available"))
        
        console.print(Panel(
            summary,
            title="[green]YOLO Research Results[/green]",
            border_style="green"
        ))
        
        # Store in memory
        memory.store_knowledge(
            category="frameworks",
            title="Ultralytics YOLO Overview",
            content=summary,
            tags=["yolo", "computer-vision", "object-detection", "ultralytics"],
            source="auto_research"
        )
        
        console.print("\n[green]✓ Stored in memory for future reference[/green]")
    else:
        console.print("[red]Research failed[/red]")
        return
    
    # Research PyTorch compatibility
    console.print("\n[bold cyan]Step 2: Checking PyTorch Compatibility[/bold cyan]\n")
    
    with console.status("[bold green]Researching PyTorch requirements...", spinner="dots"):
        torch_result = research.process({
            "type": "research_topic",
            "topic": "PyTorch compatibility with Ultralytics YOLO - what versions work together?",
            "context": "Need to ensure proper setup for YOLO object detection"
        })
    
    if torch_result.get("status") == "success":
        torch_findings = torch_result.get("findings", {})
        console.print("[green]✓ PyTorch compatibility researched[/green]")
        console.print(f"[dim]{list(torch_findings.keys())[:3]}[/dim]")
    
    # Get usage examples
    console.print("\n[bold cyan]Step 3: Finding Usage Examples[/bold cyan]\n")
    
    with console.status("[bold green]Finding code examples...", spinner="dots"):
        examples_result = research.process({
            "type": "find_examples",
            "use_case": "Using Ultralytics YOLO for object detection",
            "language": "python"
        })
    
    if examples_result.get("status") == "success":
        examples = examples_result.get("examples", [])
        
        if examples:
            console.print(f"[green]✓ Found {len(examples)} code examples[/green]\n")
            
            console.print("[bold]Example 1: Basic YOLO Usage[/bold]")
            console.print(Panel(
                examples[0].get("code", "No code available")[:400] + "...",
                border_style="blue"
            ))
        else:
            console.print("[yellow]No examples extracted, but general guidance available[/yellow]")
    
    # Retrieve from memory
    console.print("\n[bold cyan]Step 4: Retrieving Stored Knowledge[/bold cyan]\n")
    
    stored = memory.search_knowledge(
        query="YOLO object detection",
        category="frameworks",
        limit=3
    )
    
    if stored:
        console.print(f"[green]✓ Found {len(stored)} related entries in memory[/green]")
        for entry in stored:
            console.print(f"  • {entry.get('title', 'Untitled')}")
    
    # Summary
    console.print("\n" + "=" * 70)
    console.print("[bold green]Research Complete![/bold green]\n")
    
    console.print("[bold]What the Swarm Learned:[/bold]")
    console.print("  ✓ Detected YOLO (ultralytics) in project")
    console.print("  ✓ Researched what YOLO is and its purpose")
    console.print("  ✓ Checked PyTorch compatibility requirements")
    console.print("  ✓ Found usage examples")
    console.print("  ✓ Stored everything in memory for future use\n")
    
    console.print("[bold]Next Steps:[/bold]")
    console.print("  1. Check for updates: swarm> check-project")
    console.print("  2. Get help: swarm> goal How do I train a custom YOLO model?")
    console.print("  3. Review code: swarm> goal Review my YOLO implementation")
    console.print("  4. Test: swarm> goal Create tests for YOLO detection\n")
    
    console.print("[bold cyan]The swarm now understands YOLO![/bold cyan]")
    console.print("[dim]It can help with implementation, debugging, and optimization.[/dim]\n")


if __name__ == "__main__":
    demo_yolo_research()
