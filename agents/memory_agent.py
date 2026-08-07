"""
Memory Agent
Manages knowledge storage and retrieval across the swarm.
"""
from typing import Dict, Any, List, Optional
import logging

from core import BaseAgent, PromptTemplate

logger = logging.getLogger(__name__)


class MemoryAgentClass(BaseAgent):
    """
    Memory Agent - Manages swarm knowledge.
    
    Responsibilities:
    1. Store important information
    2. Summarize conversations
    3. Retrieve relevant past knowledge
    4. Prevent duplicate storage
    5. Maintain organized knowledge base
    """
    
    def __init__(self):
        super().__init__(
            agent_id="memory_agent",
            name="Memory Agent",
            description="Manages knowledge storage and retrieval"
        )
        self.capabilities = ["store", "retrieve", "summarize", "organize"]
        self.memory_manager = None
    
    def set_memory_manager(self, memory_manager):
        """Set the memory manager for this agent"""
        self.memory_manager = memory_manager
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a memory task.
        
        Args:
            task: Dictionary containing:
                - type: Task type (store, retrieve, summarize)
                - data: Data to process
                
        Returns:
            Dictionary containing operation result
        """
        task_type = task.get("type", "store")
        
        if task_type == "store":
            return self._store_knowledge(task)
        elif task_type == "retrieve":
            return self._retrieve_knowledge(task)
        elif task_type == "summarize":
            return self._summarize_content(task)
        elif task_type == "organize":
            return self._organize_knowledge(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
    
    def _store_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Store knowledge in memory system"""
        category = task.get("category", "general")
        title = task.get("title", "")
        content = task.get("content", "")
        source = task.get("source", "")
        tags = task.get("tags", [])
        
        if not content:
            return {"status": "error", "message": "No content to store"}
        
        if not self.memory_manager:
            return {"status": "error", "message": "Memory manager not configured"}
        
        self.state.update("working", f"Storing knowledge: {title}")
        logger.info(f"Storing knowledge: {title} (category: {category})")
        
        # Store in memory system
        knowledge_id = self.memory_manager.store_knowledge(
            category=category,
            title=title or "Untitled",
            content=content,
            source=source,
            tags=tags,
            enable_semantic_search=True
        )
        
        self.state.update("done", "Knowledge stored")
        
        return {
            "status": "success",
            "knowledge_id": knowledge_id,
            "category": category,
            "title": title
        }
    
    def _retrieve_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve knowledge from memory system"""
        query = task.get("query", "")
        category = task.get("category")
        limit = task.get("limit", 5)
        
        if not query:
            return {"status": "error", "message": "Query is required"}
        
        if not self.memory_manager:
            return {"status": "error", "message": "Memory manager not configured"}
        
        self.state.update("working", f"Searching knowledge: {query}")
        logger.info(f"Retrieving knowledge for query: {query}")
        
        # Search memory
        results = self.memory_manager.search_knowledge(
            query=query,
            category=category,
            use_semantic=True,
            limit=limit
        )
        
        self.state.update("done", f"Found {len(results)} results")
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    def _summarize_content(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize content for storage"""
        content = task.get("content", "")
        max_length = task.get("max_length", 500)
        
        if not content:
            return {"status": "error", "message": "No content to summarize"}
        
        self.state.update("working", "Summarizing content")
        
        prompt = f"""Summarize the following content in {max_length} words or less:

{content}

Provide a clear, concise summary that captures the key information."""
        
        system_prompt = PromptTemplate.get_system_prompt("memory")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.3)
        
        self.state.update("done", "Summary created")
        
        return {
            "status": "success",
            "original_length": len(content.split()),
            "summary": response.strip(),
            "summary_length": len(response.split())
        }
    
    def _organize_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Organize and categorize knowledge"""
        items = task.get("items", [])
        
        if not items:
            return {"status": "error", "message": "No items to organize"}
        
        self.state.update("working", "Organizing knowledge")
        
        # Build prompt
        items_text = "\n".join([f"- {item}" for item in items])
        
        prompt = f"""Organize these knowledge items into logical categories:

{items_text}

Provide:
1. Suggested categories
2. How items should be grouped
3. Tags for each item
4. Priority/importance ranking

Format as a clear organizational structure."""
        
        system_prompt = PromptTemplate.get_system_prompt("memory")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.5)
        
        self.state.update("done", "Organization complete")
        
        return {
            "status": "success",
            "organization": response,
            "item_count": len(items)
        }
    
    def store(
        self,
        content: str,
        title: str = "",
        category: str = "general",
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Convenience method for storing knowledge"""
        return self.process({
            "type": "store",
            "content": content,
            "title": title,
            "category": category,
            "tags": tags or []
        })
    
    def retrieve(self, query: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Convenience method for retrieving knowledge"""
        return self.process({
            "type": "retrieve",
            "query": query,
            "category": category
        })
