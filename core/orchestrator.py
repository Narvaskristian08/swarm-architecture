"""
Orchestrator Agent
Coordinates all agents, manages workflow, and routes messages.
"""
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent, AgentMessage
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowState:
    """Tracks the state of a workflow"""
    
    def __init__(self, workflow_id: str, goal: str):
        self.workflow_id = workflow_id
        self.goal = goal
        self.status = "created"  # created, planning, executing, completed, failed
        self.created_at = datetime.now()
        self.completed_at = None
        self.tasks = []
        self.results = {}
        self.agent_assignments = {}
    
    def to_dict(self) -> Dict:
        return {
            "workflow_id": self.workflow_id,
            "goal": self.goal,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tasks": self.tasks,
            "results": self.results
        }


class Orchestrator(BaseAgent):
    """
    Central coordinator for the AI swarm.
    Receives user goals, coordinates agents, and manages workflow execution.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="orchestrator",
            name="Orchestrator",
            description="Coordinates agent collaboration and manages workflows"
        )
        self.capabilities = ["coordinate", "route", "workflow_management"]
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.active_workflows: Dict[str, WorkflowState] = {}
        self.message_queue: List[AgentMessage] = []
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.registered_agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get a registered agent by ID"""
        return self.registered_agents.get(agent_id)
    
    def find_capable_agents(self, task_type: str) -> List[BaseAgent]:
        """Find all agents capable of handling a task type"""
        return [
            agent for agent in self.registered_agents.values()
            if agent.can_handle(task_type)
        ]
    
    def create_workflow(self, goal: str) -> str:
        """Create a new workflow for a user goal"""
        import uuid
        workflow_id = str(uuid.uuid4())
        workflow = WorkflowState(workflow_id, goal)
        self.active_workflows[workflow_id] = workflow
        
        logger.info(f"Created workflow {workflow_id}: {goal}")
        self.log_action("workflow_created", {"workflow_id": workflow_id, "goal": goal})
        
        return workflow_id
    
    def assign_task_to_agent(self, workflow_id: str, agent_id: str, task: Dict) -> bool:
        """Assign a task to a specific agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return False
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            return False
        
        # Send task message to agent
        message = self.send_message(
            receiver=agent_id,
            content=str(task),
            message_type="task",
            metadata={"workflow_id": workflow_id, "task": task}
        )
        
        # Route the message
        self.route_message(message)
        
        # Track assignment
        workflow.agent_assignments[agent_id] = task
        logger.info(f"Assigned task to {agent.name}: {task.get('description', 'No description')}")
        
        return True
    
    def route_message(self, message: AgentMessage):
        """Route a message to the appropriate agent"""
        receiver = self.get_agent(message.receiver)
        if receiver:
            receiver.receive_message(message)
            logger.debug(f"Routed message from {message.sender} to {message.receiver}")
        else:
            logger.warning(f"Cannot route message: receiver {message.receiver} not found")
            self.message_queue.append(message)  # Queue for later
    
    def process_agent_outputs(self):
        """Collect and route messages from all agents"""
        for agent in self.registered_agents.values():
            outgoing = agent.get_outgoing_messages()
            for message in outgoing:
                self.route_message(message)
    
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow by coordinating agents.
        This is a simplified version - Phase 2 will add LLM-based decision making.
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {"status": "error", "message": "Workflow not found"}
        
        workflow.status = "executing"
        self.state.update("working", f"Executing workflow: {workflow.goal}")
        
        logger.info(f"Starting workflow execution: {workflow.goal}")
        
        # Phase 1: Simple execution flow
        # Phase 2 will add intelligent agent selection and coordination
        
        result = {
            "workflow_id": workflow_id,
            "status": "completed",
            "message": "Workflow framework ready. Phase 2 will add LLM-based execution."
        }
        
        workflow.status = "completed"
        workflow.completed_at = datetime.now()
        
        return result
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process orchestrator-level tasks"""
        task_type = task.get("type", "unknown")
        
        if task_type == "create_workflow":
            goal = task.get("goal", "")
            workflow_id = self.create_workflow(goal)
            return {"status": "success", "workflow_id": workflow_id}
        
        elif task_type == "execute_workflow":
            workflow_id = task.get("workflow_id")
            return self.execute_workflow(workflow_id)
        
        elif task_type == "status":
            return self.get_system_status()
        
        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}
    
    def get_system_status(self) -> Dict:
        """Get status of entire swarm system"""
        return {
            "orchestrator_status": self.get_status(),
            "registered_agents": {
                agent_id: agent.get_status()
                for agent_id, agent in self.registered_agents.items()
            },
            "active_workflows": len(self.active_workflows),
            "queued_messages": len(self.message_queue)
        }
    
    def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        logger.info("Shutting down orchestrator...")
        for agent in self.registered_agents.values():
            agent.reset()
        self.active_workflows.clear()
        self.message_queue.clear()
        logger.info("Orchestrator shutdown complete")
