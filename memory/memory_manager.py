"""
Memory Manager
Coordinates short-term, long-term, and vector memory systems.
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import uuid

from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .vector_memory import VectorMemory

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Unified memory manager coordinating all memory layers.
    
    Responsibilities:
    1. Manage memory flow between layers
    2. Decide what to store long-term
    3. Handle summarization
    4. Provide unified search interface
    """
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.vector = VectorMemory()
        self.current_session_id: Optional[str] = None
        
        logger.info("Memory manager initialized")
        logger.info(f"Vector memory available: {self.vector.is_available()}")
    
    # ========== Session Management ==========
    
    def start_session(self, goal: str, metadata: Optional[Dict] = None) -> str:
        """Start a new session across all memory layers"""
        session_id = str(uuid.uuid4())
        
        # Initialize short-term memory
        self.short_term.start_session(session_id)
        
        # Create session in long-term memory
        self.long_term.create_session(session_id, goal, metadata)
        
        self.current_session_id = session_id
        logger.info(f"Started session {session_id}")
        
        return session_id
    
    def end_session(self, summary: Optional[str] = None):
        """End current session and persist important data"""
        if not self.current_session_id:
            logger.warning("No active session to end")
            return
        
        # Get short-term content for summarization
        if self.short_term.should_summarize():
            content = self.short_term.get_summarizable_content()
            self._summarize_and_store(content)
        
        # End session in long-term memory
        self.long_term.end_session(self.current_session_id, summary)
        
        logger.info(f"Ended session {self.current_session_id}")
        self.current_session_id = None
    
    # ========== Message Storage ==========
    
    def store_message(
        self,
        sender: str,
        receiver: str,
        content: str,
        message_type: str = "task",
        metadata: Optional[Dict] = None,
        persist: bool = False
    ):
        """
        Store a message in appropriate memory layer(s).
        
        Args:
            persist: If True, also store in long-term memory
        """
        # Always store in short-term
        self.short_term.add_message(sender, receiver, content, message_type, metadata)
        
        # Optionally persist
        if persist:
            self.long_term.store_conversation(
                sender, receiver, content,
                session_id=self.current_session_id,
                message_type=message_type,
                metadata=metadata
            )
    
    def get_recent_messages(self, count: int = 10) -> List[Dict]:
        """Get recent messages from short-term memory"""
        return self.short_term.get_recent_messages(count)
    
    def get_conversation_history(
        self,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get conversation history from long-term memory"""
        return self.long_term.get_conversation_history(session_id, limit)
    
    # ========== Task Management ==========
    
    def create_task(
        self,
        task_id: str,
        description: str,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Create a task in long-term memory"""
        return self.long_term.create_task(
            task_id, description, agent_id,
            session_id=self.current_session_id,
            metadata=metadata
        )
    
    def update_task(self, task_id: str, status: str, result: Optional[str] = None):
        """Update task status"""
        self.long_term.update_task(task_id, status, result)
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task details"""
        return self.long_term.get_task(task_id)
    
    # ========== Knowledge Storage ==========
    
    def store_knowledge(
        self,
        category: str,
        title: str,
        content: str,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        enable_semantic_search: bool = True
    ) -> Optional[int]:
        """
        Store knowledge in both long-term and vector memory.
        
        Returns:
            Knowledge ID from long-term memory
        """
        # Store in long-term (structured)
        knowledge_id = self.long_term.store_knowledge(
            category, title, content, source, tags, metadata
        )
        
        # Store in vector memory for semantic search
        if enable_semantic_search and self.vector.is_available():
            vector_metadata = {
                "knowledge_id": knowledge_id,
                "category": category,
                "title": title,
                "source": source or "unknown",
                "tags": tags or [],
                **(metadata or {})
            }
            self.vector.add(content, vector_metadata, doc_id=f"knowledge_{knowledge_id}")
        
        logger.info(f"Stored knowledge: {title} (category: {category})")
        return knowledge_id
    
    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        use_semantic: bool = True,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search knowledge using both semantic and keyword search.
        
        Returns combined and deduplicated results.
        """
        results = []
        
        # Semantic search (if available and requested)
        if use_semantic and self.vector.is_available():
            filter_metadata = {"category": category} if category else None
            semantic_results = self.vector.search(query, n_results=limit, filter_metadata=filter_metadata)
            results.extend(semantic_results)
        
        # Keyword search from long-term memory
        keyword_results = self.long_term.search_knowledge(query, category, limit)
        
        # Merge results (avoiding duplicates)
        seen_ids = {r.get("knowledge_id") for r in results if "knowledge_id" in r}
        for kr in keyword_results:
            if kr.get("id") not in seen_ids:
                results.append({
                    "knowledge_id": kr["id"],
                    "title": kr["title"],
                    "content": kr["content"],
                    "category": kr["category"],
                    "metadata": kr
                })
        
        return results[:limit]
    
    # ========== Agent History ==========
    
    def log_agent_action(
        self,
        agent_id: str,
        action: str,
        details: Optional[str] = None
    ):
        """Log an agent action"""
        self.long_term.log_agent_action(
            agent_id, action, details,
            session_id=self.current_session_id
        )
    
    def get_agent_history(self, agent_id: str, limit: int = 50) -> List[Dict]:
        """Get agent action history"""
        return self.long_term.get_agent_history(agent_id, limit)
    
    # ========== Context Management ==========
    
    def set_context(self, key: str, value: Any):
        """Set context in short-term memory"""
        self.short_term.set_context(key, value)
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context from short-term memory"""
        return self.short_term.get_context(key, default)
    
    # ========== Summarization ==========
    
    def _summarize_and_store(self, content: Dict[str, Any]):
        """
        Summarize session content and store important information.
        This is a placeholder - Phase 6 will add LLM-based summarization.
        """
        session_id = content.get("session_id")
        messages = content.get("messages", [])
        
        # Simple summarization for now
        summary = f"Session with {len(messages)} messages"
        
        # Store important messages in long-term
        for msg in messages[-10:]:  # Last 10 messages
            self.long_term.store_conversation(
                sender=msg["sender"],
                receiver=msg["receiver"],
                message=msg["content"],
                session_id=session_id,
                message_type=msg["type"],
                metadata=msg.get("metadata")
            )
        
        logger.info(f"Summarized and stored session content for {session_id}")
    
    # ========== Statistics and Utilities ==========
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from all memory layers"""
        return {
            "short_term": self.short_term.get_session_summary(),
            "long_term": self.long_term.get_statistics(),
            "vector": self.vector.get_statistics(),
            "current_session": self.current_session_id
        }
    
    def cleanup(self):
        """Clean up resources"""
        self.short_term.clear()
        self.long_term.close()
        logger.info("Memory manager cleaned up")


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get or create the global memory manager"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
