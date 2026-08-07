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
[bold cyan]║     AI SWARM - Local Architecture     ║[/bold cyan]
[bold cyan]║      Powered by Qwen via Ollama       ║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]

[dim]Type 'help' for available commands[/dim]
        """
        console.print(banner)
    
    def show_help(self):
        """Display help information"""
        help_table = Table(title="Available Commands", show_header=True)
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")
        
        commands = [
            ("goal <description>", "Submit a new goal for the swarm to accomplish"),
            ("status", "Show system status and active workflows"),
            ("agents", "List all registered agents"),
            ("workflows", "Show active workflows"),
            ("check-project", "Analyze current project frameworks and libraries"),
            ("clear", "Clear the screen"),
            ("help", "Show this help message"),
            ("quit / exit", "Exit the swarm system"),
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
                    user_input = Prompt.ask("\n[bold cyan]swarm>[/bold cyan]")
                    
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
                    
                    elif command == "clear":
                        console.clear()
                        self.show_banner()
                    
                    else:
                        console.print(f"[red]Unknown command: {command}[/red]")
                        console.print("[dim]Type 'help' for available commands[/dim]")
    
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
                
                except KeyboardInterrupt:
                    console.print("\n[yellow]Use 'quit' or 'exit' to leave[/yellow]")
                    continue
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")
        
        finally:
            console.print("[green]Goodbye![/green]")
