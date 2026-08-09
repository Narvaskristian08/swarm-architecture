"""
Complete AI Swarm Workflow Demo
Shows: Detect → Research → Suggest → Install → Verify
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import InstallerAgent, ResearchAgent
from core import get_llm_client
from memory import get_memory_manager
from tools import get_tool_manager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def demo_complete_workflow():
    """Demonstrate the complete framework workflow"""
    console.print(Panel.fit(
        "[bold green]Complete AI Swarm Framework Workflow[/bold green]\n"
        "[dim]Detection → Research → Suggestion → Installation → Verification[/dim]",
        border_style="green"
    ))
    
    # Initialize systems
    console.print("\n[bold cyan]Initializing Systems...[/bold cyan]")
    
    try:
        llm = get_llm_client()
        tools = get_tool_manager()
        memory = get_memory_manager()
        
        research_agent = ResearchAgent()
        research_agent.set_llm_client(llm)
        research_agent.set_web_tool(tools.get_tool("web"))
        
        installer_agent = InstallerAgent()
        installer_agent.set_llm_client(llm)
        installer_agent.set_terminal_tool(tools.get_tool("terminal"))
        installer_agent.set_web_tool(tools.get_tool("web"))
        
        console.print("[green]✓ All systems ready[/green]\n")
    except Exception as e:
        console.print(f"[red]Initialization failed: {e}[/red]")
        console.print("[dim]Make sure Ollama is running: ollama serve[/dim]\n")
        return
    
    # Scenario: User wants object detection
    console.print("=" * 70)
    console.print("[bold]Scenario:[/bold] Developer needs object detection for a Python project")
    console.print("=" * 70 + "\n")
    
    # Step 1: AI Suggests Framework
    console.print("[bold cyan]Step 1: AI Suggests Best Framework[/bold cyan]\n")
    
    purpose = "object detection in images for a Python computer vision project"
    
    with console.status(f"[bold green]Analyzing requirements and suggesting framework...", spinner="dots"):
        suggestion_result = installer_agent.process({
            "type": "suggest_framework",
            "purpose": purpose,
            "language": "python",
            "context": "Need fast, accurate object detection with pre-trained models"
        })
    
    if suggestion_result.get("status") != "success":
        console.print("[red]Suggestion failed[/red]")
        return
    
    suggestion = suggestion_result.get("suggestion", {})
    framework = suggestion.get("framework", "unknown")
    
    # Display suggestion
    table = Table(title="AI Recommendation", show_header=False, border_style="green")
    table.add_column("Property", style="cyan", width=15)
    table.add_column("Value", style="white")
    
    table.add_row("Framework", f"[bold green]{framework}[/bold green]")
    table.add_row("Reason", suggestion.get("reason", "")[:80])
    table.add_row("Difficulty", suggestion.get("difficulty", "unknown"))
    table.add_row("Install", suggestion.get("installation", ""))
    
    alternatives = suggestion.get("alternatives", [])
    if alternatives:
        table.add_row("Alternatives", ", ".join(alternatives[:3]))
    
    console.print(table)
    console.print()
    
    # Step 2: Research the Framework
    console.print("[bold cyan]Step 2: Research Framework Details[/bold cyan]\n")
    
    with console.status(f"[bold green]Researching {framework}...", spinner="dots"):
        research_result = research_agent.process({
            "type": "research_topic",
            "topic": f"{framework} - features, versions, and usage",
            "context": "Evaluating for object detection project"
        })
    
    if research_result.get("status") == "success":
        findings = research_result.get("findings", {})
        summary = findings.get("summary", findings.get("intro", ""))
        
        if summary:
            console.print(Panel(
                summary[:400] + ("..." if len(summary) > 400 else ""),
                title=f"[green]{framework} Research[/green]",
                border_style="blue"
            ))
            console.print()
            
            # Store in memory
            memory.store_knowledge(
                category="frameworks",
                title=f"{framework} Overview",
                content=summary,
                tags=["ai-suggested", framework.lower(), "object-detection"],
                source="installer_workflow"
            )
            console.print("[green]✓ Stored in memory[/green]\n")
    
    # Step 3: Check if Already Installed
    console.print("[bold cyan]Step 3: Check Installation Status[/bold cyan]\n")
    
    check_result = installer_agent.process({
        "type": "check_installed",
        "framework": framework,
        "language": "python"
    })
    
    is_installed = check_result.get("installed", False)
    version = check_result.get("version")
    
    if is_installed:
        console.print(f"[green]✓ {framework} is already installed[/green]")
        if version:
            console.print(f"[dim]  Version: {version}[/dim]\n")
        console.print("[bold]Workflow Complete![/bold] Framework is ready to use.\n")
        return
    else:
        console.print(f"[yellow]• {framework} is not installed[/yellow]\n")
    
    # Step 4: Installation Workflow
    console.print("[bold cyan]Step 4: Installation[/bold cyan]\n")
    
    console.print("[bold yellow]In Production:[/bold yellow]")
    console.print(f"  The system would now ask for confirmation:")
    console.print(f"  'Install {framework}? (yes/no)'")
    console.print()
    console.print(f"[bold yellow]What Happens Next:[/bold yellow]")
    console.print(f"  1. User confirms installation")
    console.print(f"  2. System runs: pip install {framework}")
    console.print(f"  3. Verifies installation succeeded")
    console.print(f"  4. Shows success message")
    console.print()
    
    # Simulate for demo (don't actually install)
    console.print("[dim]For this demo, we'll simulate the installation...[/dim]\n")
    
    install_cmd = f"pip install {framework}"
    
    console.print(f"[bold]Installation Command:[/bold]")
    console.print(Panel(install_cmd, border_style="green"))
    
    # Step 5: Post-Installation
    console.print("\n[bold cyan]Step 5: Post-Installation[/bold cyan]\n")
    
    console.print("[green]✓ Installation complete![/green]")
    console.print(f"[green]✓ {framework} is now available[/green]\n")
    
    console.print("[bold]Next Steps:[/bold]")
    console.print(f"  1. Import: [dim]from {framework} import ...[/dim]")
    console.print(f"  2. Check docs in memory: [dim]swarm> goal Show me {framework} examples[/dim]")
    console.print(f"  3. Start coding: [dim]swarm> goal Write object detection code with {framework}[/dim]")
    
    # Summary
    console.print("\n" + "=" * 70)
    console.print("[bold green]Workflow Complete![/bold green]")
    console.print("=" * 70 + "\n")
    
    console.print("[bold]What the AI Swarm Did:[/bold]")
    console.print(f"  ✓ Analyzed requirements: '{purpose}'")
    console.print(f"  ✓ Suggested best framework: {framework}")
    console.print(f"  ✓ Researched framework documentation")
    console.print(f"  ✓ Stored knowledge in memory")
    console.print(f"  ✓ Checked installation status")
    console.print(f"  ✓ Prepared installation command")
    console.print(f"  ✓ Ready to install with confirmation\n")
    
    console.print("[bold cyan]Key Features:[/bold cyan]")
    console.print("  • [green]Intelligent Suggestion[/green] - AI picks the best framework")
    console.print("  • [green]Automatic Research[/green] - Fetches latest documentation")
    console.print("  • [green]Knowledge Storage[/green] - Remembers for future use")
    console.print("  • [green]Safe Installation[/green] - Always asks for confirmation")
    console.print("  • [green]Verification[/green] - Checks installation succeeded")
    console.print("  • [green]Adaptive[/green] - Works with ANY framework\n")
    
    console.print("[bold]Real-World Usage:[/bold]")
    console.print("  [cyan]swarm> suggest object detection[/cyan]")
    console.print("  [dim]  AI: I recommend ultralytics (YOLO) because...[/dim]")
    console.print()
    console.print("  [cyan]swarm> install ultralytics[/cyan]")
    console.print("  [dim]  System: Researching... Not installed. Install? (yes/no)[/dim]")
    console.print()
    console.print("  [cyan]swarm> goal Write YOLO object detection code[/cyan]")
    console.print("  [dim]  Coder: Here's the implementation...[/dim]\n")
    
    console.print("[bold green]The swarm handles everything automatically! 🚀[/bold green]\n")


if __name__ == "__main__":
    demo_complete_workflow()
