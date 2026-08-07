"""
Short-Term Memory
Manages current session state and recent interactions.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """
    Short-term memory for current session.
    Stores recent messages, task state, and agent interactions.
    """
    
    def __init__(self, max_messages: int = 50):
        self.max_messages = max_messages
        self.messages: deque = deque(maxlen=max_messages)
        self.current_session_id: Optional[str] = None
        self.session_start: Optional[datetime] = None
        self.context: Dict[str, Any] = {}
        self.agent_states: Dict[str, Dict] = {}
    
    def start_session(self, session_id: str):
        """Start a new session"""
        self.current_session_id = session_id
        self.session_start = datetime.now()
        self.messages.clear()
        self.context.clear()
        self.agent_states.clear()
        logger.info(f"Started new session: {session_id}")
    
    def add_message(
        self,
        sender: str,
        receiver: str,
        content: str,
        message_type: str = "task",
        metadata: Optional[Dict] = None
    ):
        """Add a message to short-term memory"""
        message = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "receiver": receiver,
            "content": content,
            "type": message_type,
            "metadata": metadata or {}
        }
        self.messages.append(message)
    
    def get_recent_messages(self, count: int = 10) -> List[Dict]:
        """Get the most recent messages"""
        return list(self.messages)[-count:]
    
    def get_messages_by_agent(self, agent_id: str, count: int = 10) -> List[Dict]:
        """Get recent messages involving a specific agent"""
        agent_messages = [
            msg for msg in self.messages
            if msg["sender"] == agent_id or msg["receiver"] == agent_id
        ]
        return agent_messages[-count:]
    
    def get_conversation(self, agent1: str, agent2: str) -> List[Dict]:
        """Get conversation between two agents"""
        return [
            msg for msg in self.messages
            if (msg["sender"] == agent1 and msg["receiver"] == agent2) or
               (msg["sender"] == agent2 and msg["receiver"] == agent1)
        ]
    
    def set_context(self, key: str, value: Any):
        """Store context information"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Retrieve context information"""
        return self.context.get(key, default)
    
    def update_agent_state(self, agent_id: str, state: Dict):
        """Update agent state"""
        self.agent_states[agent_id] = {
            "state": state,
            "updated_at": datetime.now().isoformat()
        }
    
    def get_agent_state(self, agent_id: str) -> Optional[Dict]:
        """Get agent state"""
        return self.agent_states.get(agent_id)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        duration = None
        if self.session_start:
            duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            "session_id": self.current_session_id,
            "started_at": self.session_start.isoformat() if self.session_start else None,
            "duration_seconds": duration,
            "message_count": len(self.messages),
            "active_agents": len(self.agent_states),
            "context_keys": list(self.context.keys())
        }
    
    def clear(self):
        """Clear all short-term memory"""
        self.messages.clear()
        self.context.clear()
        self.agent_states.clear()
        logger.info("Short-term memory cleared")
    
    def should_summarize(self) -> bool:
        """Check if memory should be summarized and stored"""
        # Summarize when approaching capacity
        return len(self.messages) >= self.max_messages * 0.8
    
    def get_summarizable_content(self) -> Dict[str, Any]:
        """Get content ready for summarization"""
        return {
            "session_id": self.current_session_id,
            "messages": list(self.messages),
            "context": self.context.copy(),
            "agent_states": self.agent_states.copy(),
            "summary": self.get_session_summary()
        }
