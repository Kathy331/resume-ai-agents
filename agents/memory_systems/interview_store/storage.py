# agents/memory_systems/interview_store/storage.py
"""
Core storage operations for interviews

Data is being store in the SQLite database with duplicate detection,
CRUD operations, and interview lifecycle tracking.


"""

from .interview_db import InterviewDB
from .interview_utils import get_first_or_none, create_content_hash
from typing import Dict, Any, Optional
import json

class InterviewStorage(InterviewDB):
    """Core interview storage operations."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.similarity_threshold = config.get("similarity_threshold", 0.8)
        self.date_tolerance_days = config.get("date_tolerance_days", 7)

    async def store_interview(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a new interview with duplicate detection."""
        entities = data["entities"]
        email_id = data.get("email_id") or entities.get("email_id")
        
        # Extract key fields
        candidate = get_first_or_none(entities.get("CANDIDATE", []))
        company = get_first_or_none(entities.get("COMPANY", []))
        role = get_first_or_none(entities.get("ROLE", []))
        interviewer = get_first_or_none(entities.get("INTERVIEWER", []))
        interview_date = get_first_or_none(entities.get("DATE", []))
        interview_time = get_first_or_none(entities.get("TIME", []))
        duration = get_first_or_none(entities.get("DURATION", []))
        location = get_first_or_none(entities.get("LOCATION", []))
        format_type = get_first_or_none(entities.get("FORMAT", []))
        
        # Create content hash for exact duplicate detection
        content_hash = create_content_hash(entities)
        
        # Check for exact duplicates first
        existing_id = self._find_exact_duplicate(content_hash)
        if existing_id:
            return {
                "action": "duplicate_found",
                "interview_id": existing_id,
                "message": "Exact duplicate found"
            }
        
        # Store new interview
        interview_id = self._store_interview_record(
            email_id, candidate, company, role, interviewer,
            interview_date, interview_time, duration, location, format_type,
            entities, content_hash
        )
        
        return {
            "action": "stored",
            "interview_id": interview_id,
            "status": "preparing"
        }

    def _store_interview_record(self, email_id: str, candidate: str, company: str, role: str,
                              interviewer: str, interview_date: str, interview_time: str,
                              duration: str, location: str, format_type: str,
                              entities: Dict, content_hash: str) -> int:
        """Store interview record in database."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO interviews 
                (email_id, candidate_name, company_name, role, interviewer, 
                 interview_date, interview_time, duration, location, format, 
                 status, raw_entities, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email_id, candidate, company, role, interviewer,
                interview_date, interview_time, duration, location, format_type,
                "preparing", json.dumps(entities), content_hash
            ))
            
            return cursor.lastrowid

    def _find_exact_duplicate(self, content_hash: str) -> Optional[int]:
        """Find exact duplicate by content hash."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT id FROM interviews WHERE content_hash = ?", (content_hash,))
            result = cursor.fetchone()
            return result[0] if result else None