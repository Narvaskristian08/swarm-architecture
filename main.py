#!/usr/bin/env python3
"""
AI Swarm - Main Entry Point
Phase 1: Basic structure with orchestrator
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import Orchestrator, get_llm_client
from agents import (
    PlannerAgent, CoderAgent, ReviewerAgent,
    ResearchAgent, TesterAgent, MemoryAgentClass, ReflectionAgent, InstallerAgent
)
from memory import get_memory_manager
from tools import get_tool_manager
from cli import SwarmCLI
from rich.console import Console

console = Console()


def setup_environment():
    """Initialize environment and directories"""
    # Create data directory if it doesn't exist
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Load environment variables
    from dotenv import load_dotenv
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        console.print("[yellow]Warning: .env file not found. Using defaults.[/yellow]")
        console.print("[dim]Copy .env.example to .env to customize configuration[/dim]\n")


def initialize_swarm() -> Orchestrator:
    """Initialize the NORA system"""
    console.print("[bold green]Initializing NORA...[/bold green]")
    console.print("[dim]Neural Orchestration & Research Assistant[/dim]\n")
    
    # Initialize LLM client
    console.print("[dim]Connecting to Ollama...[/dim]")
    try:
        llm_client = get_llm_client()
        models = llm_client.list_models()
        if models:
            console.print(f"[green]✓[/green] Connected to Ollama (available models: {len(models)})")
        else:
            console.print("[yellow]⚠[/yellow] Ollama connected but no models found")
            console.print("[dim]  Run: ollama pull qwen2.5:7b[/dim]")
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] Could not connect to Ollama: {e}")
        console.print("[dim]  Make sure Ollama is running: https://ollama.ai[/dim]")
        llm_client = None
    
    # Initialize memory system
    console.print("[dim]Initializing memory system...[/dim]")
    memory_manager = get_memory_manager()
    mem_stats = memory_manager.get_statistics()
    console.print(f"[green]✓[/green] Memory system ready (Vector: {mem_stats['vector']['available']})")
    
    # Initialize tools
    console.print("[dim]Initializing tools...[/dim]")
    tool_manager = get_tool_manager()
    tools_list = tool_manager.list_tools()
    console.print(f"[green]✓[/green] Initialized {len(tools_list)} tools")
    
    # Create orchestrator
    orchestrator = Orchestrator()
    if llm_client:
        orchestrator.set_llm_client(llm_client)
    
    # Register all agents
    console.print("[dim]Registering agents...[/dim]")
    
    # Core agents
    planner = PlannerAgent()
    coder = CoderAgent()
    reviewer = ReviewerAgent()
    
    # Additional agents
    research = ResearchAgent()
    tester = TesterAgent()
    memory_agent = MemoryAgentClass()
    reflection = ReflectionAgent()
    installer = InstallerAgent()
    
    # Configure LLM for all agents
    agents = [planner, coder, reviewer, research, tester, memory_agent, reflection, installer]
    if llm_client:
        for agent in agents:
            agent.set_llm_client(llm_client)
    
    # Configure agent-specific tools
    research.set_web_tool(tool_manager.get_tool("web"))
    tester.set_terminal_tool(tool_manager.get_tool("terminal"))
    installer.set_terminal_tool(tool_manager.get_tool("terminal"))
    installer.set_web_tool(tool_manager.get_tool("web"))
    memory_agent.set_memory_manager(memory_manager)
    
    # Register all agents with orchestrator
    for agent in agents:
        orchestrator.register_agent(agent)
    
    console.print(f"[green]✓[/green] Registered {len(agents)} agents:")
    console.print("[dim]  - Planner, Coder, Reviewer")
    console.print("[dim]  - Research, Tester, Memory, Reflection, Installer[/dim]")
    
    console.print("[green]✓[/green] NORA initialized successfully!")
    console.print("[dim]Ready to build applications. Type 'goal <description>' to start.[/dim]\n")
    
    return orchestrator


def main():
    """Main entry point"""
    try:
        # Setup
        setup_environment()
        
        # Initialize system
        orchestrator = initialize_swarm()
        
        # Get tool manager
        tool_manager = get_tool_manager()
        
        # Start CLI
        cli = SwarmCLI(orchestrator, tool_manager=tool_manager)
        cli.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
