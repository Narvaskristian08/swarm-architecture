"""
Check Project Frameworks and Libraries
Demonstrates automatic detection of project dependencies.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import get_tool_manager
from agents import ResearchAgent
from core import get_llm_client
from rich.console import Console
from rich.panel import Panel

console = Console()


def check_current_project():
    """Analyze the current AI Swarm project"""
    console.print("[bold cyan]Checking Current Project[/bold cyan]\n")
    
    tools = get_tool_manager()
    
    # Analyze the project
    result = tools.analyze_project()
    
    if result.get("status") != "success":
        console.print(f"[red]Error: {result.get('error')}[/red]")
        return None
    
    # Display summary
    console.print(Panel(
        f"""[bold]Project Type:[/bold] {result.get('project_type')}
[bold]Languages:[/bold] {', '.join(result.get('languages', []))}
[bold]Frameworks:[/bold] {', '.join(result.get('frameworks', [])) or 'None detected'}
[bold]Libraries:[/bold] {len(result.get('libraries', []))} found
[bold]Package Managers:[/bold] {', '.join(result.get('package_managers', []))}""",
        title="Project Analysis",
        border_style="green"
    ))
    
    return result


def research_frameworks(analysis, llm_available=True):
    """Research the detected frameworks"""
    frameworks = analysis.get("frameworks", [])
    
    if not frameworks:
        console.print("\n[yellow]No frameworks detected to research[/yellow]")
        return
    
    console.print(f"\n[bold cyan]Researching Frameworks[/bold cyan]")
    
    if not llm_available:
        console.print("[yellow]LLM not available - skipping research[/yellow]")
        return
    
    try:
        llm = get_llm_client()
        research = ResearchAgent()
        research.set_llm_client(llm)
        
        # Research first framework
        framework = list(frameworks)[0]
        console.print(f"\nResearching: [bold]{framework}[/bold]...")
        
        result = research.process({
            "type": "check_docs",
            "library": framework
        })
        
        if result.get("status") == "success":
            console.print("[green]✓[/green] Research complete\n")
            
            doc = result.get("documentation", {})
            
            # Show key sections
            for section_name in ["summary", "key_information", "installation"]:
                if section_name in doc:
                    content = str(doc[section_name])
                    if content:
                        console.print(f"[bold]{section_name.replace('_', ' ').title()}:[/bold]")
                        console.print(f"{content[:300]}...\n")
        else:
            console.print(f"[yellow]Research unavailable[/yellow]")
    
    except Exception as e:
        console.print(f"[yellow]Could not research: {e}[/yellow]")


def check_specific_libraries(libraries_to_check):
    """Check if specific libraries are used"""
    console.print(f"\n[bold cyan]Checking for Specific Libraries[/bold cyan]")
    
    tools = get_tool_manager()
    result = tools.analyze_project()
    
    if result.get("status") != "success":
        return
    
    found_libraries = set(result.get("libraries", []))
    
    for lib in libraries_to_check:
        if lib.lower() in found_libraries:
            console.print(f"[green]✓[/green] {lib} - Found")
        else:
            console.print(f"[dim]✗[/dim] {lib} - Not found")


def generate_research_plan(analysis):
    """Generate a plan to research all frameworks"""
    frameworks = analysis.get("frameworks", [])
    libraries = analysis.get("libraries", [])
    
    console.print("\n[bold cyan]Research Plan[/bold cyan]")
    
    if frameworks:
        console.print("\n[bold]Frameworks to research:[/bold]")
        for fw in sorted(frameworks):
            console.print(f"  1. {fw} - Check latest version and best practices")
    
    # Suggest researching key libraries
    key_libraries = [lib for lib in libraries if lib in [
        'requests', 'pandas', 'numpy', 'sqlalchemy', 'pydantic',
        'fastapi', 'django', 'flask', 'pytest', 'chromadb'
    ]]
    
    if key_libraries:
        console.print("\n[bold]Key libraries to research:[/bold]")
        for lib in sorted(key_libraries)[:5]:
            console.print(f"  2. {lib} - Verify usage and latest patterns")
    
    console.print("\n[dim]Use the swarm to research: 'goal Research <library> documentation'[/dim]")


def main():
    """Main demo function"""
    console.print("[bold green]Project Framework & Library Checker[/bold green]")
    console.print("=" * 60)
    
    # 1. Check current project
    analysis = check_current_project()
    
    if not analysis:
        return
    
    # 2. Show detailed breakdown
    console.print("\n[bold]Detailed Breakdown:[/bold]")
    
    details = analysis.get("details", {})
    for filename, info in details.items():
        libs = info.get("libraries", set())
        if libs:
            console.print(f"\n[cyan]{filename}:[/cyan]")
            console.print(f"  Language: {info.get('language', 'Unknown')}")
            console.print(f"  Libraries: {len(libs)}")
            
            # Show first few
            for lib in sorted(libs)[:5]:
                console.print(f"    • {lib}")
            if len(libs) > 5:
                console.print(f"    [dim]... and {len(libs) - 5} more[/dim]")
    
    # 3. Research frameworks (if LLM available)
    try:
        research_frameworks(analysis, llm_available=True)
    except:
        console.print("\n[yellow]Skipping framework research (LLM not available)[/yellow]")
    
    # 4. Check for specific libraries
    check_specific_libraries([
        "ollama",
        "chromadb",
        "fastapi",
        "requests",
        "beautifulsoup4"
    ])
    
    # 5. Generate research plan
    generate_research_plan(analysis)
    
    console.print("\n" + "=" * 60)
    console.print("[bold green]Analysis Complete![/bold green]")


if __name__ == "__main__":
    main()
