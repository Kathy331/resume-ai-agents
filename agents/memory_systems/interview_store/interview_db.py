# agents/memory_systems/interview_store/interview_db.py
"""
Base class for interview database operations
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any


class InterviewDB:
    """Base class for interview database operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.db_path = config.get("db_path", "agents/memory_systems/interview_store/interviews.db")
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with proper schema."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id TEXT,
                    candidate_name TEXT,
                    company_name TEXT,
                    role TEXT,
                    interviewer TEXT,
                    interview_date TEXT,
                    interview_time TEXT,
                    duration TEXT,
                    location TEXT,
                    format TEXT,
                    status TEXT DEFAULT 'preparing',
                    raw_entities TEXT,
                    content_hash TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_candidate_company ON interviews(candidate_name, company_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_email_id ON interviews(email_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON interviews(content_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON interviews(status)")
            
            # Create history table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interview_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interview_id INTEGER,
                    field_name TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (interview_id) REFERENCES interviews (id)
                )
            """)
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)