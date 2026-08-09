"""
Demo: Project Analysis and Version Checking
Shows how the swarm can detect frameworks, libraries, and check for updates.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import get_tool_manager
from rich.console import Console
from rich.table import Table

console = Console()


def demo_project_analysis():
    """Demonstrate project analysis"""
    console.print("[bold green]AI Swarm - Project Analysis Demo[/bold green]")
    console.print("=" * 60)
    
    # Get tool manager
    tool_manager = get_tool_manager()
    
    # 1. Analyze project
    console.print("\n[bold cyan]Step 1: Analyzing Project Structure[/bold cyan]\n")
    
    analysis = tool_manager.analyze_project()
    
    if analysis.get("status") == "success":
        console.print(f"✓ Project Type: [green]{analysis.get('project_type')}[/green]")
        console.print(f"✓ Languages: [cyan]{', '.join(analysis.get('languages', []))}[/cyan]")
        
        if analysis.get("frameworks"):
            console.print(f"✓ Frameworks detected: [yellow]{', '.join(analysis['frameworks'])}[/yellow]")
        
        if analysis.get("libraries"):
            console.print(f"✓ Libraries found: [blue]{len(analysis['libraries'])}[/blue]")
            
            # Show some libraries
            libs = sorted(analysis['libraries'])[:15]
            console.print("\n[bold]Top Libraries:[/bold]")
            for i, lib in enumerate(libs, 1):
                console.print(f"  {i}. {lib}")
        
        if analysis.get("config_files"):
            console.print(f"\n✓ Configuration files: {', '.join(analysis['config_files'])}")
    else:
        console.print(f"[red]✗ Analysis failed: {analysis.get('error')}[/red]")
        return
    
    # 2. Check for outdated packages
    console.print("\n[bold cyan]Step 2: Checking for Outdated Packages[/bold cyan]\n")
    
    # Determine language
    language = None
    if "Python" in analysis.get("languages", []):
        language = "python"
        console.print("Detected Python project, checking pip packages...")
    elif "JavaScript/TypeScript" in analysis.get("languages", []):
        language = "javascript"
        console.print("Detected JavaScript project, checking npm packages...")
    
    if language:
        outdated_result = tool_manager.execute_tool(
            "project",
            operation="check_outdated",
            language=language
        )
        
        if outdated_result.get("status") == "success":
            outdated = outdated_result.get("outdated", [])
            
            if outdated:
                console.print(f"\n[yellow]⚠ Found {len(outdated)} outdated packages![/yellow]\n")
                
                # Create table
                table = Table(title="Outdated Packages", show_header=True)
                table.add_column("Package", style="cyan", no_wrap=True)
                table.add_column("Current Version", style="yellow")
                table.add_column("Latest Version", style="green")
                table.add_column("Update Needed", style="red")
                
                for pkg in outdated[:10]:  # Show first 10
                    current = pkg.get("current", "unknown")
                    latest = pkg.get("latest", "unknown")
                    
                    # Calculate update type
                    try:
                        if current and latest:
                            curr_parts = current.split('.')
                            lat_parts = latest.split('.')
                            
                            if len(curr_parts) >= 2 and len(lat_parts) >= 2:
                                if curr_parts[0] != lat_parts[0]:
                                    update_type = "Major"
                                elif curr_parts[1] != lat_parts[1]:
                                    update_type = "Minor"
                                else:
                                    update_type = "Patch"
                            else:
                                update_type = "Yes"
                    except:
                        update_type = "Yes"
                    
                    table.add_row(
                        pkg["name"],
                        current,
                        latest,
                        update_type
                    )
                
                console.print(table)
                
                if len(outdated) > 10:
                    console.print(f"\n[dim]... and {len(outdated) - 10} more packages need updates[/dim]")
                
                # Show update commands
                console.print("\n[bold]Recommended Actions:[/bold]")
                if language == "python":
                    console.print("\n1. Update all packages:")
                    console.print("   [cyan]pip install -r requirements.txt --upgrade[/cyan]")
                    console.print("\n2. Update specific package:")
                    console.print(f"   [cyan]pip install --upgrade {outdated[0]['name']}[/cyan]")
                    console.print("\n3. Check specific package info:")
                    console.print(f"   [cyan]pip show {outdated[0]['name']}[/cyan]")
                elif language == "javascript":
                    console.print("\n1. Update all packages:")
                    console.print("   [cyan]npm update[/cyan]")
                    console.print("\n2. Update to latest:")
                    console.print(f"   [cyan]npm install {outdated[0]['name']}@latest[/cyan]")
                
                # Security warning
                major_updates = [p for p in outdated if 'Major' in str(p)]
                if major_updates:
                    console.print("\n[bold red]⚠ Warning:[/bold red] Some packages have major version updates.")
                    console.print("[dim]Review changelogs before updating to avoid breaking changes.[/dim]")
            
            else:
                console.print("[green]✓ All packages are up to date![/green]")
                console.print("[dim]Your dependencies are current.[/dim]")
        else:
            error_msg = outdated_result.get('error', 'Unknown error')
            console.print(f"[yellow]⚠ Could not check for updates: {error_msg}[/yellow]")
            
            if "not found" in error_msg.lower():
                console.print(f"\n[dim]Make sure {language} package manager is installed:[/dim]")
                if language == "python":
                    console.print("  pip install --upgrade pip")
                elif language == "javascript":
                    console.print("  npm install -g npm")
    else:
        console.print("[yellow]Could not determine project language[/yellow]")
    
    # 3. Summary
    console.print("\n" + "=" * 60)
    console.print("[bold]Summary[/bold]")
    console.print(f"✓ Analyzed project structure")
    console.print(f"✓ Detected {len(analysis.get('libraries', []))} libraries")
    
    if language and outdated_result.get("status") == "success":
        outdated_count = len(outdated_result.get("outdated", []))
        if outdated_count > 0:
            console.print(f"⚠ Found {outdated_count} outdated packages")
        else:
            console.print("✓ All packages up to date")
    
    console.print("=" * 60)
    console.print("\n[bold green]Demo Complete![/bold green]")
    console.print("\nThis swarm can:")
    console.print("  • Detect frameworks and libraries in your project")
    console.print("  • Check which packages are outdated")
    console.print("  • Suggest update commands")
    console.print("  • Research documentation for any library")
    console.print("  • Help you update and maintain your codebase\n")


if __name__ == "__main__":
    demo_project_analysis()
