"""
Intelligent Framework Research
Automatically detects and researches ANY framework (YOLO, TensorFlow, etc.)
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import get_tool_manager
from agents import ResearchAgent
from core import get_llm_client
from memory import get_memory_manager
from rich.console import Console
from rich.table import Table

console = Console()


def auto_research_project():
    """
    Intelligent workflow:
    1. Detect all frameworks/libraries in project
    2. Research unknown ones automatically
    3. Store findings in memory
    4. Provide recommendations
    """
    console.print("[bold green]Intelligent Framework Research System[/bold green]")
    console.print("=" * 70)
    console.print("[dim]Automatically detecting and researching all frameworks...[/dim]\n")
    
    # Initialize systems
    tool_manager = get_tool_manager()
    memory = get_memory_manager()
    
    try:
        llm = get_llm_client()
        research_agent = ResearchAgent()
        research_agent.set_llm_client(llm)
        research_agent.set_web_tool(tool_manager.get_tool("web"))
        llm_available = True
    except:
        console.print("[yellow]LLM not available, will show detection only[/yellow]\n")
        llm_available = False
    
    # Step 1: Analyze project
    console.print("[bold cyan]Step 1: Analyzing Project[/bold cyan]\n")
    
    analysis = tool_manager.analyze_project()
    
    if analysis.get("status") != "success":
        console.print(f"[red]Failed to analyze project: {analysis.get('error')}[/red]")
        return
    
    # Display findings
    console.print(f"✓ Project Type: [green]{analysis.get('project_type')}[/green]")
    console.print(f"✓ Languages: {', '.join(analysis.get('languages', []))}")
    
    libraries = sorted(analysis.get("libraries", []))
    frameworks = sorted(analysis.get("frameworks", []))
    
    console.print(f"✓ Detected {len(libraries)} libraries")
    console.print(f"✓ Detected {len(frameworks)} frameworks\n")
    
    # Step 2: Identify important/unknown frameworks
    console.print("[bold cyan]Step 2: Identifying Key Frameworks[/bold cyan]\n")
    
    # Priority frameworks (AI/ML, Computer Vision, Deep Learning)
    priority_keywords = [
        'yolo', 'ultralytics', 'tensorflow', 'pytorch', 'keras',
        'opencv', 'cv2', 'transformers', 'huggingface',
        'scikit-learn', 'sklearn', 'pandas', 'numpy',
        'fastapi', 'flask', 'django', 'react', 'vue',
        'flutter', 'react-native'
    ]
    
    important_libs = []
    for lib in libraries:
        lib_lower = lib.lower()
        for keyword in priority_keywords:
            if keyword in lib_lower:
                important_libs.append(lib)
                break
    
    if important_libs:
        console.print(f"[yellow]Found {len(important_libs)} important frameworks:[/yellow]")
        for lib in important_libs[:10]:
            console.print(f"  • {lib}")
        if len(important_libs) > 10:
            console.print(f"  ... and {len(important_libs) - 10} more")
    else:
        # Just take first few libraries
        important_libs = libraries[:5]
        console.print(f"[blue]Analyzing top {len(important_libs)} libraries:[/blue]")
        for lib in important_libs:
            console.print(f"  • {lib}")
    
    console.print()
    
    # Step 3: Research each framework
    if llm_available and important_libs:
        console.print("[bold cyan]Step 3: Researching Frameworks (AI-Powered)[/bold cyan]\n")
        
        research_table = Table(title="Framework Research Results", show_header=True)
        research_table.add_column("Framework", style="cyan")
        research_table.add_column("Type/Purpose", style="yellow")
        research_table.add_column("Status", style="green")
        
        for i, lib in enumerate(important_libs[:5], 1):  # Research top 5
            console.print(f"[dim]Researching {i}/{min(5, len(important_libs))}: {lib}...[/dim]")
            
            try:
                # Use research agent to learn about the library
                result = research_agent.process({
                    "type": "research_topic",
                    "topic": f"What is {lib}? What is it used for? Latest version and key features.",
                    "context": f"This is a library found in a {analysis.get('project_type')} project"
                })
                
                if result.get("status") == "success":
                    findings = result.get("findings", {})
                    summary = findings.get("summary", findings.get("intro", ""))
                    
                    # Extract key info
                    purpose = "Unknown"
                    if summary:
                        # Get first sentence
                        first_sentence = summary.split('.')[0] if '.' in summary else summary[:100]
                        purpose = first_sentence[:60] + "..." if len(first_sentence) > 60 else first_sentence
                    
                    research_table.add_row(lib, purpose, "✓ Researched")
                    
                    # Store in memory for future use
                    memory.store_knowledge(
                        category="frameworks",
                        title=f"{lib} Framework Overview",
                        content=f"Library: {lib}\n\n{summary}",
                        tags=["framework", lib.lower(), "auto-discovered"],
                        source="auto_research"
                    )
                else:
                    research_table.add_row(lib, "Research failed", "✗ Error")
            
            except Exception as e:
                research_table.add_row(lib, str(e)[:40], "✗ Error")
        
        console.print(research_table)
        console.print(f"\n[green]✓ Stored research in memory for future reference[/green]\n")
    
    elif important_libs:
        console.print("[bold cyan]Step 3: Framework Information (Manual)[/bold cyan]\n")
        console.print("[yellow]LLM not available. Here's what we can determine:[/yellow]\n")
        
        info_table = Table(show_header=True)
        info_table.add_column("Framework", style="cyan")
        info_table.add_column("Likely Purpose", style="yellow")
        info_table.add_column("Research Links", style="blue")
        
        for lib in important_libs[:10]:
            lib_lower = lib.lower()
            
            # Make educated guesses
            if 'yolo' in lib_lower or 'ultralytics' in lib_lower:
                purpose = "Computer Vision / Object Detection"
            elif 'tensorflow' in lib_lower or 'pytorch' in lib_lower:
                purpose = "Deep Learning Framework"
            elif 'opencv' in lib_lower or 'cv2' in lib_lower:
                purpose = "Computer Vision"
            elif 'transformers' in lib_lower:
                purpose = "NLP / Language Models"
            elif 'pandas' in lib_lower or 'numpy' in lib_lower:
                purpose = "Data Science / Analysis"
            elif 'fastapi' in lib_lower or 'flask' in lib_lower:
                purpose = "Web Framework / API"
            elif 'react' in lib_lower or 'vue' in lib_lower:
                purpose = "Frontend Framework"
            else:
                purpose = "Unknown - Needs Research"
            
            links = f"PyPI, GitHub"
            info_table.add_row(lib, purpose, links)
        
        console.print(info_table)
        console.print("\n[dim]Start Ollama to enable automatic research[/dim]\n")
    
    # Step 4: Provide recommendations
    console.print("[bold cyan]Step 4: Recommendations[/bold cyan]\n")
    
    # Check for common AI/ML frameworks
    ai_frameworks = [lib for lib in libraries if any(x in lib.lower() for x in 
                    ['yolo', 'tensorflow', 'pytorch', 'keras', 'sklearn'])]
    
    if ai_frameworks:
        console.print("[yellow]AI/ML Project Detected![/yellow]")
        console.print(f"Frameworks: {', '.join(ai_frameworks[:5])}\n")
        console.print("Recommendations:")
        console.print("  1. Ensure CUDA/GPU drivers are up to date (if using GPU)")
        console.print("  2. Check model compatibility with framework versions")
        console.print("  3. Monitor model versions and datasets")
        console.print("  4. Use virtual environments to avoid conflicts")
    
    # Check for web frameworks
    web_frameworks = [lib for lib in libraries if any(x in lib.lower() for x in 
                     ['fastapi', 'flask', 'django', 'express'])]
    
    if web_frameworks:
        console.print("\n[blue]Web Framework Detected![/blue]")
        console.print(f"Frameworks: {', '.join(web_frameworks)}\n")
        console.print("Recommendations:")
        console.print("  1. Keep security patches up to date")
        console.print("  2. Review authentication/authorization code")
        console.print("  3. Check for deprecated APIs")
        console.print("  4. Monitor for breaking changes")
    
    # General recommendation
    console.print("\n[bold]General Recommendations:[/bold]")
    console.print(f"  • Found {len(libraries)} total dependencies")
    console.print("  • Run 'swarm> check-project' to check for updates")
    console.print("  • Review major version changes before upgrading")
    console.print("  • Store important framework docs in swarm memory")
    
    console.print("\n" + "=" * 70)
    console.print("[bold green]Analysis Complete![/bold green]\n")
    
    console.print("[bold]What This System Can Do:[/bold]")
    console.print("  ✓ Detect ANY framework (YOLO, TensorFlow, Flutter, etc.)")
    console.print("  ✓ Automatically research unknown frameworks")
    console.print("  ✓ Store knowledge for future reference")
    console.print("  ✓ Provide intelligent recommendations")
    console.print("  ✓ Check for updates and compatibility")
    console.print("\n[dim]The swarm learns and adapts to YOUR project![/dim]\n")


if __name__ == "__main__":
    auto_research_project()
