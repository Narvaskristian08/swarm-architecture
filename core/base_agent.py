"""
Base Agent Class
All specialized agents inherit from this base class.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class AgentMessage:
    """Represents a message passed between agents"""
    
    def __init__(
        self,
        sender: str,
        receiver: str,
        content: str,
        message_type: str = "task",
        metadata: Optional[Dict] = None
    ):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.message_type = message_type
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "type": self.message_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class AgentState:
    """Tracks agent execution state"""
    
    def __init__(self):
        self.status = "idle"  # idle, thinking, working, waiting, done, error
        self.current_task = None
        self.history = []
        self.metadata = {}
    
    def update(self, status: str, task: Optional[str] = None, metadata: Optional[Dict] = None):
        self.status = status
        if task:
            self.current_task = task
        if metadata:
            self.metadata.update(metadata)
        self.history.append({
            "status": status,
            "task": task,
            "timestamp": datetime.now().isoformat()
        })


class BaseAgent(ABC):
    """
    Base class for all agents in the swarm.
    Provides common functionality for communication, state management, and execution.
    """
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.state = AgentState()
        self.inbox: List[AgentMessage] = []
        self.outbox: List[AgentMessage] = []
        self.capabilities: List[str] = []
        self.llm_client = None  # Will be set when LLM is needed
        self.conversation_history: List[Dict[str, str]] = []
    
    def receive_message(self, message: AgentMessage):
        """Receive a message from another agent"""
        self.inbox.append(message)
    
    def send_message(self, receiver: str, content: str, message_type: str = "task", metadata: Optional[Dict] = None) -> AgentMessage:
        """Send a message to another agent"""
        message = AgentMessage(
            sender=self.agent_id,
            receiver=receiver,
            content=content,
            message_type=message_type,
            metadata=metadata
        )
        self.outbox.append(message)
        return message
    
    def get_pending_messages(self) -> List[AgentMessage]:
        """Get unprocessed messages"""
        messages = self.inbox.copy()
        self.inbox.clear()
        return messages
    
    def get_outgoing_messages(self) -> List[AgentMessage]:
        """Get messages ready to send"""
        messages = self.outbox.copy()
        self.outbox.clear()
        return messages
    
    @abstractmethod
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task and return results.
        Must be implemented by each agent.
        
        Args:
            task: Dictionary containing task details
            
        Returns:
            Dictionary containing results and status
        """
        pass
    
    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type"""
        return task_type in self.capabilities
    
    def log_action(self, action: str, details: Optional[Dict] = None):
        """Log an agent action"""
        log_entry = {
            "agent": self.agent_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        # This will be extended with actual logging in Phase 4
        return log_entry
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.state.status,
            "current_task": self.state.current_task,
            "pending_messages": len(self.inbox),
            "capabilities": self.capabilities
        }
    
    def reset(self):
        """Reset agent state"""
        self.state = AgentState()
        self.inbox.clear()
        self.outbox.clear()
        self.conversation_history.clear()
    
    def set_llm_client(self, llm_client):
        """Set the LLM client for this agent"""
        self.llm_client = llm_client
        logger.info(f"LLM client configured for {self.name}")
    
    def query_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        use_history: bool = False
    ) -> str:
        """
        Query the LLM with a prompt.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            temperature: Sampling temperature
            use_history: Whether to use conversation history
            
        Returns:
            The LLM's response
        """
        if not self.llm_client:
            logger.warning(f"{self.name} has no LLM client configured")
            return "Error: No LLM client available"
        
        try:
            if use_history:
                # Use chat mode with history
                messages = self.conversation_history.copy()
                messages.append({"role": "user", "content": prompt})
                
                if system_prompt:
                    messages.insert(0, {"role": "system", "content": system_prompt})
                
                result = self.llm_client.chat(messages, temperature=temperature)
                response = result.get("response", "")
                
                # Update history
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": response})
                
                # Keep history manageable
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
            else:
                # Single generation
                result = self.llm_client.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature
                )
                response = result.get("response", "")
            
            return response
        
        except Exception as e:
            logger.error(f"LLM query failed for {self.name}: {e}")
            return f"Error querying LLM: {str(e)}"
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.conversation_history.clear()
