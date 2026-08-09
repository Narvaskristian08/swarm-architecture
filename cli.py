"""
Command Line Interface for AI Swarm
"""
import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint

console = Console()


class SwarmCLI:
    """Interactive CLI for the AI Swarm"""
    
    def __init__(self, orchestrator, tool_manager=None):
        self.orchestrator = orchestrator
        self.tool_manager = tool_manager
        self.running = False
    
    def show_banner(self):
        """Display welcome banner"""
        banner = """
[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]
[bold cyan]║              N O R A                   ║[/bold cyan]
[bold cyan]║   Neural Orchestration & Research     ║[/bold cyan]
[bold cyan]║           Assistant                   ║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]

[dim]Just describe what you want - NORA builds it![/dim]
[dim]Type 'help' for commands or 'goal <description>' to start[/dim]
        """
        console.print(banner)
    
    def show_help(self):
        """Display help information"""
        help_table = Table(title="Available Commands", show_header=True)
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")
        
        commands = [
            ("goal <description>", "Build anything! Example: 'goal Create a budget tracker app'"),
            ("status", "Show system status and active workflows"),
            ("agents", "List all registered agents"),
            ("workflows", "Show active workflows"),
            ("suggest <purpose>", "Ask AI for framework recommendations"),
            ("install <framework>", "Install a specific framework"),
            ("check-project", "Analyze existing project"),
            ("research-frameworks", "Research frameworks in current project"),
            ("clear", "Clear the screen"),
            ("help", "Show this help message"),
            ("quit / exit", "Exit NORA"),
        ]
        
        for cmd, desc in commands:
            help_table.add_row(cmd, desc)
        
        console.print(help_table)
    
    def show_status(self):
        """Display system status"""
        status = self.orchestrator.get_system_status()
        
        console.print("\n[bold]System Status[/bold]")
        console.print(f"Orchestrator: [green]{status['orchestrator_status']['status']}[/green]")
        console.print(f"Active Workflows: {status['active_workflows']}")
        console.print(f"Queued Messages: {status['queued_messages']}")
    
    def show_agents(self):
        """Display registered agents"""
        agents_table = Table(title="Registered Agents", show_header=True)
        agents_table.add_column("Agent ID", style="cyan")
        agents_table.add_column("Name", style="yellow")
        agents_table.add_column("Status", style="green")
        agents_table.add_column("Capabilities", style="dim")
        
        for agent_id, agent in self.orchestrator.registered_agents.items():
            status = agent.get_status()
            agents_table.add_row(
                agent_id,
                status['name'],
                status['status'],
                ", ".join(status['capabilities'][:3])  # Show first 3
            )
        
        console.print(agents_table)
    
    def show_workflows(self):
        """Display active workflows"""
        if not self.orchestrator.active_workflows:
            console.print("[dim]No active workflows[/dim]")
            return
        
        workflows_table = Table(title="Active Workflows", show_header=True)
        workflows_table.add_column("ID", style="cyan", no_wrap=True)
        workflows_table.add_column("Goal", style="white")
        workflows_table.add_column("Status", style="yellow")
        workflows_table.add_column("Created", style="dim")
        
        for wf_id, workflow in self.orchestrator.active_workflows.items():
            workflows_table.add_row(
                wf_id[:8] + "...",
                workflow.goal[:50] + ("..." if len(workflow.goal) > 50 else ""),
                workflow.status,
                workflow.created_at.strftime("%H:%M:%S")
            )
        
        console.print(workflows_table)
    
    def handle_goal(self, goal: str):
        """Handle a new goal submission"""
        if not goal.strip():
            console.print("[red]Please provide a goal description[/red]")
            return
        
        console.print(f"\n[bold]Processing goal:[/bold] {goal}")
        
        # Create workflow
        workflow_id = self.orchestrator.create_workflow(goal)
        
        # Execute workflow
        with console.status("[bold green]Agents working...", spinner="dots"):
            result = self.orchestrator.execute_workflow(workflow_id)
        
        # Display result
        if result.get("status") == "completed":
            console.print(Panel(
                result.get("message", "Goal processed successfully"),
                title="[green]Success[/green]",
                border_style="green"
            ))
        else:
            console.print(Panel(
                result.get("message", "An error occurred"),
                title="[red]Error[/red]",
                border_style="red"
            ))
    
    def run(self):
        """Main CLI loop"""
        self.running = True
        self.show_banner()
        
        try:
            while self.running:
                try:
                    # Get user input
                    user_input = Prompt.ask("\n[bold cyan]nora>[/bold cyan]")
                    
                    if not user_input.strip():
                        continue
                    
                    # Parse command
                    parts = user_input.strip().split(maxsplit=1)
                    command = parts[0].lower()
                    args = parts[1] if len(parts) > 1 else ""
                    
                    # Handle commands
                    if command in ["quit", "exit"]:
                        if Confirm.ask("Are you sure you want to exit?"):
                            self.running = False
                            console.print("[yellow]Shutting down swarm...[/yellow]")
                            self.orchestrator.shutdown()
                    
                    elif command == "help":
                        self.show_help()
                    
                    elif command == "status":
                        self.show_status()
                    
                    elif command == "agents":
                        self.show_agents()
                    
                    elif command == "workflows":
                        self.show_workflows()
                    
                    elif command == "goal":
                        self.handle_goal(args)
                    
                    elif command == "check-project":
                        self.check_project()
                    
                    elif command == "research-frameworks":
                        self.research_frameworks()
                    
                    elif command.startswith("suggest "):
                        purpose = command[8:].strip()
                        self.suggest_framework(purpose)
                    
                    elif command.startswith("install "):
                        framework = command[8:].strip()
                        self.install_framework(framework)
                    
                    elif command == "clear":
                        console.clear()
                        self.show_banner()
                    
                    else:
                        console.print(f"[red]Unknown command: {command}[/red]")
                        console.print("[dim]Type 'help' for available commands[/dim]")
                
                except KeyboardInterrupt:
                    console.print("\n[yellow]Use 'quit' or 'exit' to leave[/yellow]")
                    continue
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down...[/yellow]")
        finally:
            if self.running:
                console.print("[green]Goodbye![/green]")
    
    def check_project(self):
        """Analyze current project and display frameworks/libraries"""
        if not self.tool_manager:
            console.print("[yellow]Tool manager not available[/yellow]")
            return
        
        console.print("\n[bold cyan]Analyzing project...[/bold cyan]")
        
        with console.status("[bold green]Scanning files...", spinner="dots"):
            result = self.tool_manager.analyze_project()
        
        if result.get("status") != "success":
            console.print(f"[red]Analysis failed: {result.get('error')}[/red]")
            return
        
        # Display results
        console.print(f"\n[bold]Project Analysis[/bold]")
        console.print(f"Path: [dim]{result.get('project_path')}[/dim]\n")
        
        # Project type
        project_type = result.get("project_type", "Unknown")
        console.print(f"[bold]Type:[/bold] {project_type}")
        
        # Languages
        languages = result.get("languages", [])
        if languages:
            console.print(f"[bold]Languages:[/bold] {', '.join(languages)}")
        
        # Package managers
        pkg_managers = result.get("package_managers", [])
        if pkg_managers:
            console.print(f"[bold]Package Managers:[/bold] {', '.join(pkg_managers)}")
        
        # Frameworks
        frameworks = result.get("frameworks", [])
        if frameworks:
            console.print(f"\n[bold green]Frameworks ({len(frameworks)}):[/bold green]")
            for fw in sorted(frameworks):
                console.print(f"  • {fw}")
        
        # Libraries
        libraries = result.get("libraries", [])
        if libraries:
            console.print(f"\n[bold blue]Libraries ({len(libraries)}):[/bold blue]")
            # Show first 20
            for lib in sorted(libraries)[:20]:
                console.print(f"  • {lib}")
            if len(libraries) > 20:
                console.print(f"  [dim]... and {len(libraries) - 20} more[/dim]")
        
        # Config files found
        config_files = result.get("config_files", [])
        if config_files:
            console.print(f"\n[bold]Config Files:[/bold] {', '.join(config_files)}")
        
        # Suggest checking documentation
        if frameworks:
            console.print(f"\n[dim]Tip: Use 'goal Research <framework> documentation' to learn more[/dim]")

    def check_project(self):
        """Analyze and check current project"""
        if not self.tool_manager:
            console.print("[yellow]Tool manager not available[/yellow]")
            return
        
        console.print("\n[bold cyan]Analyzing Project...[/bold cyan]\n")
        
        with console.status("[bold green]Scanning project...", spinner="dots"):
            # Analyze project
            analysis = self.tool_manager.analyze_project()
        
        if analysis.get("status") != "success":
            console.print(f"[red]Analysis failed: {analysis.get('error')}[/red]")
            return
        
        # Display basic info
        console.print(f"[bold]Project Type:[/bold] {analysis.get('project_type', 'Unknown')}")
        console.print(f"[bold]Languages:[/bold] {', '.join(analysis.get('languages', []))}")
        
        # Frameworks
        if analysis.get("frameworks"):
            console.print(f"[bold]Frameworks:[/bold] {', '.join(analysis['frameworks'])}")
        
        # Libraries
        if analysis.get("libraries"):
            lib_count = len(analysis["libraries"])
            console.print(f"[bold]Libraries:[/bold] {lib_count} detected")
            
            # Show first 10
            if lib_count > 0:
                libs = sorted(analysis["libraries"])[:10]
                for lib in libs:
                    console.print(f"  • {lib}")
                if lib_count > 10:
                    console.print(f"  ... and {lib_count - 10} more")
        
        # Check for outdated packages
        console.print("\n[bold cyan]Checking for Updates...[/bold cyan]\n")
        
        with console.status("[bold green]Checking versions...", spinner="dots"):
            # Detect language
            language = None
            if "Python" in analysis.get("languages", []):
                language = "python"
            elif "JavaScript/TypeScript" in analysis.get("languages", []):
                language = "javascript"
            
            if language:
                outdated_result = self.tool_manager.execute_tool(
                    "project",
                    operation="check_outdated",
                    language=language
                )
            else:
                outdated_result = {"status": "error", "error": "Could not detect language"}
        
        if outdated_result.get("status") == "success":
            outdated = outdated_result.get("outdated", [])
            
            if outdated:
                console.print(f"[yellow]⚠ Found {len(outdated)} outdated packages:[/yellow]\n")
                
                # Create table
                table = Table(show_header=True)
                table.add_column("Package", style="cyan")
                table.add_column("Current", style="yellow")
                table.add_column("Latest", style="green")
                
                for pkg in outdated[:15]:  # Show first 15
                    table.add_row(
                        pkg["name"],
                        pkg["current"],
                        pkg["latest"]
                    )
                
                console.print(table)
                
                if len(outdated) > 15:
                    console.print(f"\n[dim]... and {len(outdated) - 15} more[/dim]")
                
                # Suggest update command
                if language == "python":
                    console.print("\n[bold]To update:[/bold]")
                    console.print("  pip install --upgrade <package-name>")
                    console.print("  or: pip install -r requirements.txt --upgrade")
                elif language == "javascript":
                    console.print("\n[bold]To update:[/bold]")
                    console.print("  npm update")
                    console.print("  or: npm install <package-name>@latest")
            else:
                console.print("[green]✓ All packages are up to date![/green]")
        else:
            console.print(f"[yellow]⚠ Could not check for updates: {outdated_result.get('error')}[/yellow]")
            console.print("[dim]Make sure the package manager is installed[/dim]")
        
        console.print()

    
    def research_frameworks(self):
        """Intelligently research detected frameworks"""
        if not self.tool_manager:
            console.print("[yellow]Tool manager not available[/yellow]")
            return
        
        console.print("\n[bold cyan]Intelligent Framework Research[/bold cyan]\n")
        console.print("[dim]Detecting and researching all frameworks automatically...[/dim]\n")
        
        # Run the intelligent research script
        import subprocess
        import sys
        
        script_path = Path(__file__).parent / "examples" / "auto_research_frameworks.py"
        
        if script_path.exists():
            try:
                subprocess.run([sys.executable, str(script_path)], check=True)
            except Exception as e:
                console.print(f"[red]Error running research: {e}[/red]")
        else:
            console.print("[yellow]Research script not found[/yellow]")
            console.print("[dim]Using simplified version...[/dim]\n")
            
            # Simplified inline version
            analysis = self.tool_manager.analyze_project()
            
            if analysis.get("status") == "success":
                libraries = analysis.get("libraries", [])
                
                # Identify important frameworks
                ai_ml_keywords = ['yolo', 'ultralytics', 'tensorflow', 'pytorch', 
                                 'keras', 'opencv', 'transformers']
                
                important = [lib for lib in libraries 
                            if any(kw in lib.lower() for kw in ai_ml_keywords)]
                
                if important:
                    console.print(f"[yellow]Found {len(important)} AI/ML frameworks:[/yellow]")
                    for lib in important:
                        console.print(f"  • {lib}")
                    
                    console.print("\n[bold]To research these:[/bold]")
                    console.print(f"  swarm> goal Research {important[0]} framework and its usage")
                else:
                    console.print("[green]No specialized AI/ML frameworks detected[/green]")
                    console.print(f"[dim]Detected {len(libraries)} general libraries[/dim]")

    
    def suggest_framework(self, purpose: str):
        """AI suggests best framework for a purpose"""
        if not purpose:
            console.print("[yellow]Usage: suggest <what you need>[/yellow]")
            console.print("[dim]Example: suggest object detection in Python[/dim]")
            return
        
        console.print(f"\n[bold cyan]AI Framework Suggestion[/bold cyan]\n")
        console.print(f"[dim]Purpose: {purpose}[/dim]\n")
        
        # Get installer agent
        installer = self.orchestrator.get_agent("installer")
        if not installer:
            console.print("[red]Installer agent not available[/red]")
            return
        
        with console.status("[bold green]Consulting AI...", spinner="dots"):
            result = installer.process({
                "type": "suggest_framework",
                "purpose": purpose,
                "language": "python"  # Default, could be detected
            })
        
        if result.get("status") == "success":
            suggestion = result.get("suggestion", {})
            
            console.print(f"[bold green]Recommended:[/bold green] {suggestion.get('framework', 'Unknown')}\n")
            console.print(f"[bold]Why:[/bold] {suggestion.get('reason', 'No reason provided')}\n")
            
            alternatives = suggestion.get("alternatives", [])
            if alternatives:
                console.print(f"[bold]Alternatives:[/bold] {', '.join(alternatives)}\n")
            
            console.print(f"[bold]Install:[/bold] {suggestion.get('installation', 'See documentation')}")
            console.print(f"[bold]Difficulty:[/bold] {suggestion.get('difficulty', 'Unknown')}")
            
            docs = suggestion.get("documentation")
            if docs:
                console.print(f"[bold]Docs:[/bold] {docs}")
            
            # Offer to install
            framework = suggestion.get('framework')
            if framework:
                console.print(f"\n[dim]To install: swarm> install {framework}[/dim]")
        else:
            console.print(f"[red]Failed to get suggestion: {result.get('message')}[/red]")
    
    def install_framework(self, framework: str):
        """Research and install a framework"""
        if not framework:
            console.print("[yellow]Usage: install <framework-name>[/yellow]")
            console.print("[dim]Example: install ultralytics[/dim]")
            return
        
        console.print(f"\n[bold cyan]Framework Installation: {framework}[/bold cyan]\n")
        
        # Get installer agent
        installer = self.orchestrator.get_agent("installer")
        if not installer:
            console.print("[red]Installer agent not available[/red]")
            return
        
        # Step 1: Research and check
        console.print("[bold]Step 1: Research & Check[/bold]")
        with console.status(f"[bold green]Researching {framework}...", spinner="dots"):
            result = installer.process({
                "type": "research_and_install",
                "framework": framework,
                "language": "python",
                "auto_install": False  # Don't auto-install, ask first
            })
        
        if result.get("status") != "success":
            console.print(f"[red]Error: {result.get('message')}[/red]")
            return
        
        # Show research findings
        steps = result.get("steps", [])
        for step in steps:
            step_name = step.get("step", "")
            if step_name == "research":
                findings = step.get("findings", "")
                console.print(f"\n[green]✓[/green] Research complete")
                console.print(Panel(findings[:300] + "...", title="Key Information", border_style="blue"))
            
            elif step_name == "check_installed":
                is_installed = step.get("installed", False)
                if is_installed:
                    console.print(f"\n[green]✓[/green] {framework} is already installed")
                    return
                else:
                    console.print(f"\n[yellow]•[/yellow] {framework} is not installed")
        
        # Step 2: Confirm installation
        install_cmd = result.get("installation_command", "")
        console.print(f"\n[bold]Step 2: Installation[/bold]")
        console.print(f"[dim]Command: {install_cmd}[/dim]\n")
        
        # Ask for confirmation
        try:
            confirm = console.input(f"[bold yellow]Install {framework}? (yes/no):[/bold yellow] ")
            
            if confirm.lower() in ["yes", "y"]:
                console.print(f"\n[bold green]Installing {framework}...[/bold green]")
                
                # Execute installation
                install_result = installer.process({
                    "type": "install_package",
                    "framework": framework,
                    "language": "python",
                    "confirm": True
                })
                
                if install_result.get("status") == "success":
                    console.print(f"\n[green]✓ Successfully installed {framework}![/green]")
                    console.print(f"[dim]You can now use {framework} in your project[/dim]\n")
                else:
                    console.print(f"\n[red]✗ Installation failed: {install_result.get('message')}[/red]")
                    console.print(f"[dim]Try manually: {install_cmd}[/dim]\n")
            else:
                console.print(f"\n[yellow]Installation cancelled[/yellow]")
                console.print(f"[dim]To install later: {install_cmd}[/dim]\n")
        
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Installation cancelled[/yellow]\n")
