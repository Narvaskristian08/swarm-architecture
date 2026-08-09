"""
Vector Memory using ChromaDB
Stores embeddings for semantic search: documentation, code, solutions, lessons.
"""
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not installed. Vector memory will be disabled.")

from config import VECTOR_DB_PATH, VECTOR_COLLECTION_NAME

logger = logging.getLogger(__name__)


class VectorMemory:
    """
    Vector memory using ChromaDB.
    Enables semantic search over stored knowledge.
    """
    
    def __init__(self, persist_directory: Path = VECTOR_DB_PATH):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available. Vector memory disabled.")
            return
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client"""
        try:
            # Create persist directory
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            # Initialize client
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=VECTOR_COLLECTION_NAME,
                metadata={"description": "AI Swarm knowledge base"}
            )
            
            logger.info(f"Vector memory initialized at {self.persist_directory}")
            logger.info(f"Collection '{VECTOR_COLLECTION_NAME}' has {self.collection.count()} items")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector memory: {e}")
            self.client = None
            self.collection = None
    
    def is_available(self) -> bool:
        """Check if vector memory is available"""
        return CHROMADB_AVAILABLE and self.client is not None and self.collection is not None
    
    def add(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Add content to vector memory.
        
        Args:
            content: Text content to store
            metadata: Metadata (category, source, tags, etc.)
            doc_id: Optional document ID (generated if not provided)
            
        Returns:
            Document ID or None if failed
        """
        if not self.is_available():
            logger.warning("Vector memory not available")
            return None
        
        try:
            # Generate ID if not provided
            if not doc_id:
                import uuid
                doc_id = str(uuid.uuid4())
            
            # Add to collection
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.debug(f"Added document {doc_id} to vector memory")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add to vector memory: {e}")
            return None
    
    def add_batch(
        self,
        contents: List[str],
        metadatas: List[Dict[str, Any]],
        doc_ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add multiple documents at once.
        
        Returns:
            List of document IDs
        """
        if not self.is_available():
            logger.warning("Vector memory not available")
            return []
        
        try:
            # Generate IDs if not provided
            if not doc_ids:
                import uuid
                doc_ids = [str(uuid.uuid4()) for _ in contents]
            
            # Add batch
            self.collection.add(
                documents=contents,
                metadatas=metadatas,
                ids=doc_ids
            )
            
            logger.info(f"Added {len(contents)} documents to vector memory")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add batch to vector memory: {e}")
            return []
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in vector memory.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of results with content, metadata, and distance
        """
        if not self.is_available():
            logger.warning("Vector memory not available")
            return []
        
        try:
            # Build query
            query_kwargs = {
                "query_texts": [query],
                "n_results": n_results
            }
            
            if filter_metadata:
                query_kwargs["where"] = filter_metadata
            
            # Search
            results = self.collection.query(**query_kwargs)
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
            
            logger.debug(f"Found {len(formatted_results)} results for query: {query[:50]}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        if not self.is_available():
            return None
        
        try:
            result = self.collection.get(ids=[doc_id])
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    def update(
        self,
        doc_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a document"""
        if not self.is_available():
            return False
        
        try:
            update_kwargs = {"ids": [doc_id]}
            
            if content:
                update_kwargs["documents"] = [content]
            if metadata:
                update_kwargs["metadatas"] = [metadata]
            
            self.collection.update(**update_kwargs)
            logger.debug(f"Updated document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            return False
    
    def delete(self, doc_id: str) -> bool:
        """Delete a document"""
        if not self.is_available():
            return False
        
        try:
            self.collection.delete(ids=[doc_id])
            logger.debug(f"Deleted document {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def delete_by_filter(self, filter_metadata: Dict[str, Any]) -> int:
        """Delete documents matching filter"""
        if not self.is_available():
            return 0
        
        try:
            # First, get matching IDs
            results = self.collection.get(where=filter_metadata)
            ids_to_delete = results["ids"]
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} documents")
                return len(ids_to_delete)
            
            return 0
        except Exception as e:
            logger.error(f"Failed to delete by filter: {e}")
            return 0
    
    def get_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get documents by category"""
        if not self.is_available():
            return []
        
        try:
            results = self.collection.get(
                where={"category": category},
                limit=limit
            )
            
            formatted_results = []
            for i in range(len(results["ids"])):
                formatted_results.append({
                    "id": results["ids"][i],
                    "content": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Failed to get by category: {e}")
            return []
    
    def count(self) -> int:
        """Get total number of documents"""
        if not self.is_available():
            return 0
        return self.collection.count()
    
    def clear(self) -> bool:
        """Clear all documents (use with caution!)"""
        if not self.is_available():
            return False
        
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=VECTOR_COLLECTION_NAME)
            self.collection = self.client.create_collection(
                name=VECTOR_COLLECTION_NAME,
                metadata={"description": "AI Swarm knowledge base"}
            )
            logger.warning("Vector memory cleared!")
            return True
        except Exception as e:
            logger.error(f"Failed to clear vector memory: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector memory statistics"""
        if not self.is_available():
            return {"available": False}
        
        try:
            # Get sample of documents to analyze categories
            sample = self.collection.get(limit=1000)
            categories = {}
            
            for metadata in sample["metadatas"]:
                category = metadata.get("category", "unknown")
                categories[category] = categories.get(category, 0) + 1
            
            return {
                "available": True,
                "total_documents": self.count(),
                "categories": categories,
                "collection_name": VECTOR_COLLECTION_NAME
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"available": True, "error": str(e)}