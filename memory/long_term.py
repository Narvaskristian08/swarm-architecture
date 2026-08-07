"""
Long-Term Memory using SQLite
Stores structured data: tasks, conversations, projects, agent history.
"""
import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging

from config import DB_PATH

logger = logging.getLogger(__name__)


class LongTermMemory:
    """
    Long-term memory using SQLite.
    Stores persistent structured data.
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
        cursor = self.conn.cursor()
        
        # Sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            goal TEXT,
            status TEXT,
            summary TEXT,
            metadata TEXT
        )
        """)
        
        # Tasks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            description TEXT NOT NULL,
            agent_id TEXT,
            status TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            result TEXT,
            metadata TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
        """)
        
        # Conversations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            message TEXT NOT NULL,
            message_type TEXT,
            metadata TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
        """)
        
        # Projects table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            status TEXT,
            metadata TEXT
        )
        """)
        
        # Agent history table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            session_id TEXT,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
        """)
        
        # Knowledge base table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            tags TEXT,
            metadata TEXT
        )
        """)
        
        self.conn.commit()
        logger.info(f"Long-term memory initialized at {self.db_path}")
    
    # ========== Session Methods ==========
    
    def create_session(self, session_id: str, goal: str, metadata: Optional[Dict] = None) -> bool:
        """Create a new session"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO sessions (id, started_at, goal, status, metadata)
            VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                datetime.now().isoformat(),
                goal,
                "active",
                json.dumps(metadata or {})
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Session {session_id} already exists")
            return False
    
    def end_session(self, session_id: str, summary: Optional[str] = None):
        """End a session"""
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE sessions
        SET ended_at = ?, status = ?, summary = ?
        WHERE id = ?
        """, (datetime.now().isoformat(), "completed", summary, session_id))
        self.conn.commit()
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session details"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_recent_sessions(self, count: int = 10) -> List[Dict]:
        """Get recent sessions"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM sessions
        ORDER BY started_at DESC
        LIMIT ?
        """, (count,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== Task Methods ==========
    
    def create_task(
        self,
        task_id: str,
        description: str,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Create a new task"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO tasks (id, session_id, description, agent_id, status, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                session_id,
                description,
                agent_id,
                "pending",
                datetime.now().isoformat(),
                json.dumps(metadata or {})
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Task {task_id} already exists")
            return False
    
    def update_task(self, task_id: str, status: str, result: Optional[str] = None):
        """Update task status"""
        cursor = self.conn.cursor()
        completed_at = datetime.now().isoformat() if status == "completed" else None
        cursor.execute("""
        UPDATE tasks
        SET status = ?, result = ?, completed_at = ?
        WHERE id = ?
        """, (status, result, completed_at, task_id))
        self.conn.commit()
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task details"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_tasks_by_session(self, session_id: str) -> List[Dict]:
        """Get all tasks for a session"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE session_id = ?", (session_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== Conversation Methods ==========
    
    def store_conversation(
        self,
        sender: str,
        receiver: str,
        message: str,
        session_id: Optional[str] = None,
        message_type: str = "task",
        metadata: Optional[Dict] = None
    ):
        """Store a conversation message"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO conversations (session_id, timestamp, sender, receiver, message, message_type, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            datetime.now().isoformat(),
            sender,
            receiver,
            message,
            message_type,
            json.dumps(metadata or {})
        ))
        self.conn.commit()
    
    def get_conversation_history(
        self,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get conversation history"""
        cursor = self.conn.cursor()
        if session_id:
            cursor.execute("""
            SELECT * FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """, (session_id, limit))
        else:
            cursor.execute("""
            SELECT * FROM conversations
            ORDER BY timestamp DESC
            LIMIT ?
            """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== Project Methods ==========
    
    def create_project(
        self,
        project_id: str,
        name: str,
        description: str = "",
        metadata: Optional[Dict] = None
    ) -> bool:
        """Create a new project"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO projects (id, name, description, created_at, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                name,
                description,
                datetime.now().isoformat(),
                "active",
                json.dumps(metadata or {})
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Project {project_id} already exists")
            return False
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project details"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def list_projects(self, status: Optional[str] = None) -> List[Dict]:
        """List all projects"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * FROM projects WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT * FROM projects")
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== Agent History Methods ==========
    
    def log_agent_action(
        self,
        agent_id: str,
        action: str,
        details: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Log an agent action"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO agent_history (agent_id, session_id, action, timestamp, details)
        VALUES (?, ?, ?, ?, ?)
        """, (agent_id, session_id, action, datetime.now().isoformat(), details))
        self.conn.commit()
    
    def get_agent_history(self, agent_id: str, limit: int = 50) -> List[Dict]:
        """Get agent action history"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM agent_history
        WHERE agent_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (agent_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== Knowledge Methods ==========
    
    def store_knowledge(
        self,
        category: str,
        title: str,
        content: str,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """Store knowledge item"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO knowledge (category, title, content, source, created_at, tags, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            category,
            title,
            content,
            source,
            datetime.now().isoformat(),
            json.dumps(tags or []),
            json.dumps(metadata or {})
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Search knowledge base"""
        cursor = self.conn.cursor()
        if category:
            cursor.execute("""
            SELECT * FROM knowledge
            WHERE category = ? AND (title LIKE ? OR content LIKE ?)
            ORDER BY created_at DESC
            LIMIT ?
            """, (category, f"%{query}%", f"%{query}%", limit))
        else:
            cursor.execute("""
            SELECT * FROM knowledge
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_knowledge_by_category(self, category: str, limit: int = 20) -> List[Dict]:
        """Get knowledge by category"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM knowledge
        WHERE category = ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (category, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== Utility Methods ==========
    
    def get_statistics(self) -> Dict[str, int]:
        """Get memory statistics"""
        cursor = self.conn.cursor()
        stats = {}
        
        for table in ["sessions", "tasks", "conversations", "projects", "agent_history", "knowledge"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Long-term memory connection closed")
