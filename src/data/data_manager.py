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
