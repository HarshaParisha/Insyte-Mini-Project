"""
Insyte AI - Data Manager
Handles SQLite database operations for secure, local-only data storage.
"""

import sqlite3
import json
import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging
import os

class DataManager:
    def __init__(self, db_path: str = "data/database/insyte.db"):
        """
        Initialize the Data Manager with SQLite database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def initialize_database(self) -> bool:
        """
        Create database tables if they don't exist.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create conversations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_input TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                ''')
                
                # Create documents table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        doc_type TEXT DEFAULT 'note',
                        tags TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                ''')
                
                # Create productivity_metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS productivity_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        metric_type TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        description TEXT,
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create voice_sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS voice_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transcription TEXT NOT NULL,
                        confidence_score REAL,
                        duration REAL,
                        language TEXT DEFAULT 'en',
                        audio_path TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(doc_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_date ON productivity_metrics(date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_type ON productivity_metrics(metric_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_voice_created ON voice_sessions(created_at)')
                
                conn.commit()
                
            self.logger.info(f"Database initialized: {self.db_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {str(e)}")
            return False
    
    def save_conversation(self, session_id: str, user_input: str, ai_response: str, 
                         metadata: Dict = None) -> Optional[int]:
        """
        Save a conversation exchange to the database.
        
        Args:
            session_id: Unique session identifier
            user_input: User's message
            ai_response: AI's response
            metadata: Optional metadata dictionary
            
        Returns:
            int: Conversation ID if successful, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO conversations (session_id, user_input, ai_response, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, user_input, ai_response, json.dumps(metadata) if metadata else None))
                
                conversation_id = cursor.lastrowid
                conn.commit()
                
                self.logger.debug(f"Saved conversation {conversation_id}")
                return conversation_id
                
        except Exception as e:
            self.logger.error(f"Failed to save conversation: {str(e)}")
            return None
    
    def save_document(self, title: str, content: str, doc_type: str = "note", 
                     tags: List[str] = None, metadata: Dict = None) -> Optional[int]:
        """
        Save a document to the database.
        
        Args:
            title: Document title
            content: Document content
            doc_type: Type of document ('note', 'task', 'idea', etc.)
            tags: List of tags
            metadata: Optional metadata dictionary
            
        Returns:
            int: Document ID if successful, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                tags_str = json.dumps(tags) if tags else None
                metadata_str = json.dumps(metadata) if metadata else None
                
                cursor.execute('''
                    INSERT INTO documents (title, content, doc_type, tags, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (title, content, doc_type, tags_str, metadata_str))
                
                document_id = cursor.lastrowid
                conn.commit()
                
                self.logger.debug(f"Saved document {document_id}")
                return document_id
                
        except Exception as e:
            self.logger.error(f"Failed to save document: {str(e)}")
            return None
    
    def save_productivity_metric(self, date: str, metric_type: str, metric_value: float,
                               description: str = None, metadata: Dict = None) -> Optional[int]:
        """
        Save a productivity metric to the database.
        
        Args:
            date: Date in YYYY-MM-DD format
            metric_type: Type of metric ('tasks_completed', 'focus_time', etc.)
            metric_value: Numeric value of the metric
            description: Optional description
            metadata: Optional metadata dictionary
            
        Returns:
            int: Metric ID if successful, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO productivity_metrics (date, metric_type, metric_value, description, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (date, metric_type, metric_value, description, json.dumps(metadata) if metadata else None))
                
                metric_id = cursor.lastrowid
                conn.commit()
                
                self.logger.debug(f"Saved productivity metric {metric_id}")
                return metric_id
                
        except Exception as e:
            self.logger.error(f"Failed to save productivity metric: {str(e)}")
            return None
    
    def save_voice_session(self, transcription: str, confidence_score: float = None,
                          duration: float = None, language: str = "en",
                          audio_path: str = None, metadata: Dict = None) -> Optional[int]:
        """
        Save a voice transcription session to the database.
        
        Args:
            transcription: Transcribed text
            confidence_score: Confidence score (0-1)
            duration: Audio duration in seconds
            language: Language code
            audio_path: Path to audio file
            metadata: Optional metadata dictionary
            
        Returns:
            int: Session ID if successful, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO voice_sessions (transcription, confidence_score, duration, 
                                              language, audio_path, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (transcription, confidence_score, duration, language, audio_path,
                      json.dumps(metadata) if metadata else None))
                
                session_id = cursor.lastrowid
                conn.commit()
                
                self.logger.debug(f"Saved voice session {session_id}")
                return session_id
                
        except Exception as e:
            self.logger.error(f"Failed to save voice session: {str(e)}")
            return None
    
    def get_conversations(self, session_id: str = None, limit: int = 100) -> List[Dict]:
        """
        Retrieve conversations from the database.
        
        Args:
            session_id: Optional session ID to filter by
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if session_id:
                    cursor.execute('''
                        SELECT * FROM conversations 
                        WHERE session_id = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (session_id, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM conversations 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (limit,))
                
                rows = cursor.fetchall()
                conversations = []
                
                for row in rows:
                    conv = dict(row)
                    if conv['metadata']:
                        conv['metadata'] = json.loads(conv['metadata'])
                    conversations.append(conv)
                
                return conversations
                
        except Exception as e:
            self.logger.error(f"Failed to get conversations: {str(e)}")
            return []
    
    def get_documents(self, doc_type: str = None, tags: List[str] = None, 
                     limit: int = 100) -> List[Dict]:
        """
        Retrieve documents from the database.
        
        Args:
            doc_type: Optional document type to filter by
            tags: Optional tags to filter by
            limit: Maximum number of documents to return
            
        Returns:
            List of document dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM documents"
                params = []
                conditions = []
                
                if doc_type:
                    conditions.append("doc_type = ?")
                    params.append(doc_type)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY updated_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                documents = []
                
                for row in rows:
                    doc = dict(row)
                    if doc['tags']:
                        doc['tags'] = json.loads(doc['tags'])
                    if doc['metadata']:
                        doc['metadata'] = json.loads(doc['metadata'])
                    
                    # Filter by tags if specified
                    if tags and doc['tags']:
                        if not any(tag in doc['tags'] for tag in tags):
                            continue
                    
                    documents.append(doc)
                
                return documents
                
        except Exception as e:
            self.logger.error(f"Failed to get documents: {str(e)}")
            return []
    
    def get_productivity_metrics(self, start_date: str = None, end_date: str = None,
                               metric_type: str = None) -> List[Dict]:
        """
        Retrieve productivity metrics from the database.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metric_type: Optional metric type to filter by
            
        Returns:
            List of metric dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM productivity_metrics"
                params = []
                conditions = []
                
                if start_date:
                    conditions.append("date >= ?")
                    params.append(start_date)
                
                if end_date:
                    conditions.append("date <= ?")
                    params.append(end_date)
                
                if metric_type:
                    conditions.append("metric_type = ?")
                    params.append(metric_type)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY date DESC, created_at DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                metrics = []
                
                for row in rows:
                    metric = dict(row)
                    if metric['metadata']:
                        metric['metadata'] = json.loads(metric['metadata'])
                    metrics.append(metric)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Failed to get productivity metrics: {str(e)}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Return statistics about the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count records in each table
                tables = ['conversations', 'documents', 'productivity_metrics', 'voice_sessions']
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]
                
                # Database file size
                if os.path.exists(self.db_path):
                    stats['database_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
                else:
                    stats['database_size_mb'] = 0
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {str(e)}")
            return {}
    
    # ==================== PROJECT MANAGEMENT ====================
    
    def create_project_tables(self) -> bool:
        """Create tables for project-based document management."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Projects table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        description TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                ''')
                
                # Project documents table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS project_documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        filename TEXT NOT NULL,
                        original_filename TEXT NOT NULL,
                        file_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        file_size INTEGER,
                        page_count INTEGER,
                        upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                    )
                ''')
                
                # Indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_docs_project ON project_documents(project_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_docs_type ON project_documents(file_type)')
                
                # Document Q&A table (auto-generated questions and answers)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS document_qa (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        document_id INTEGER NOT NULL,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        source TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (document_id) REFERENCES project_documents(id) ON DELETE CASCADE
                    )
                ''')
                
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_qa_document ON document_qa(document_id)')
                
                conn.commit()
                self.logger.info("Project tables created successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create project tables: {str(e)}")
            return False
    
    def create_project(self, name: str, description: str = "") -> Optional[int]:
        """Create a new project."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO projects (name, description)
                    VALUES (?, ?)
                ''', (name, description))
                project_id = cursor.lastrowid
                conn.commit()
                self.logger.info(f"Created project: {name} (ID: {project_id})")
                return project_id
        except sqlite3.IntegrityError:
            self.logger.warning(f"Project already exists: {name}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to create project: {str(e)}")
            return None
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects with document counts."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.id, p.name, p.description, p.created_at, p.updated_at,
                           COUNT(pd.id) as doc_count
                    FROM projects p
                    LEFT JOIN project_documents pd ON p.id = pd.project_id
                    GROUP BY p.id
                    ORDER BY p.updated_at DESC
                ''')
                
                projects = []
                for row in cursor.fetchall():
                    projects.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'created_at': row[3],
                        'updated_at': row[4],
                        'doc_count': row[5]
                    })
                return projects
                
        except Exception as e:
            self.logger.error(f"Failed to get projects: {str(e)}")
            return []
    
    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get project details by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, description, created_at, updated_at
                    FROM projects WHERE id = ?
                ''', (project_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'created_at': row[3],
                        'updated_at': row[4]
                    }
                return None
        except Exception as e:
            self.logger.error(f"Failed to get project: {str(e)}")
            return None
    
    def save_project_document(self, project_id: int, filename: str, 
                             original_filename: str, file_type: str, 
                             content: str, file_size: int = 0, 
                             page_count: int = 0, metadata: Dict = None) -> Optional[int]:
        """Save a document to a project."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO project_documents 
                    (project_id, filename, original_filename, file_type, content, 
                     file_size, page_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (project_id, filename, original_filename, file_type, content, 
                      file_size, page_count, json.dumps(metadata) if metadata else None))
                
                doc_id = cursor.lastrowid
                
                # Update project's updated_at
                cursor.execute('''
                    UPDATE projects SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (project_id,))
                
                conn.commit()
                self.logger.info(f"Saved document to project {project_id}: {original_filename}")
                return doc_id
                
        except Exception as e:
            self.logger.error(f"Failed to save project document: {str(e)}")
            return None
    
    def get_project_documents(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all documents in a project."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, filename, original_filename, file_type, content,
                           file_size, page_count, upload_date, metadata
                    FROM project_documents
                    WHERE project_id = ?
                    ORDER BY upload_date DESC
                ''', (project_id,))
                
                documents = []
                for row in cursor.fetchall():
                    documents.append({
                        'id': row[0],
                        'filename': row[1],
                        'original_filename': row[2],
                        'file_type': row[3],
                        'content': row[4],
                        'file_size': row[5],
                        'page_count': row[6],
                        'upload_date': row[7],
                        'metadata': json.loads(row[8]) if row[8] else {}
                    })
                return documents
                
        except Exception as e:
            self.logger.error(f"Failed to get project documents: {str(e)}")
            return []
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all its documents."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
                conn.commit()
                self.logger.info(f"Deleted project {project_id}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to delete project: {str(e)}")
            return False
    
    def delete_project_document(self, document_id: int) -> bool:
        """Delete a document from a project."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM project_documents WHERE id = ?', (document_id,))
                conn.commit()
                self.logger.info(f"Deleted document {document_id}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to delete document: {str(e)}")
            return False
    
    # ==================== Q&A MANAGEMENT ====================
    
    def save_document_qa_pairs(self, document_id: int, qa_pairs: List[Dict[str, str]]) -> bool:
        """
        Save Q&A pairs for a document.
        
        Args:
            document_id: Document ID
            qa_pairs: List of dicts with 'question', 'answer', 'source' keys
            
        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete existing Q&A for this document
                cursor.execute('DELETE FROM document_qa WHERE document_id = ?', (document_id,))
                
                # Insert new Q&A pairs
                for qa in qa_pairs:
                    cursor.execute('''
                        INSERT INTO document_qa (document_id, question, answer, source)
                        VALUES (?, ?, ?, ?)
                    ''', (document_id, qa['question'], qa['answer'], qa.get('source', '')))
                
                conn.commit()
                self.logger.info(f"Saved {len(qa_pairs)} Q&A pairs for document {document_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save Q&A pairs: {str(e)}")
            return False
    
    def get_project_qa_pairs(self, project_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all Q&A pairs for a project.
        
        Args:
            project_id: Project ID
            limit: Maximum number of Q&A pairs to return
            
        Returns:
            List of Q&A dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT qa.id, qa.question, qa.answer, qa.source, 
                           pd.original_filename, qa.created_at
                    FROM document_qa qa
                    JOIN project_documents pd ON qa.document_id = pd.id
                    WHERE pd.project_id = ?
                    ORDER BY qa.created_at DESC
                    LIMIT ?
                ''', (project_id, limit))
                
                qa_pairs = []
                for row in cursor.fetchall():
                    qa_pairs.append({
                        'id': row[0],
                        'question': row[1],
                        'answer': row[2],
                        'source': row[3],
                        'filename': row[4],
                        'created_at': row[5]
                    })
                return qa_pairs
                
        except Exception as e:
            self.logger.error(f"Failed to get Q&A pairs: {str(e)}")
            return []
    
    def get_document_qa_pairs(self, document_id: int) -> List[Dict[str, str]]:
        """Get Q&A pairs for a specific document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, question, answer, source
                    FROM document_qa
                    WHERE document_id = ?
                    ORDER BY id
                ''', (document_id,))
                
                qa_pairs = []
                for row in cursor.fetchall():
                    qa_pairs.append({
                        'id': row[0],
                        'question': row[1],
                        'answer': row[2],
                        'source': row[3]
                    })
                return qa_pairs
                
        except Exception as e:
            self.logger.error(f"Failed to get document Q&A: {str(e)}")
            return []
