# agents/memory_systems/interview_store/storage.py
"""
Core storage operations for interviews

Data is being store in the SQLite database with duplicate detection,
CRUD operations, and interview lifecycle tracking.
"""

import json
import logging
from typing import Dict, Any, Optional
from shared.models import EntityExtractionResult, InterviewData

from .interview_db import InterviewDB
from .interview_utils import (
    get_first_or_none, 
    create_content_hash, 
    entities_to_extraction_result,
    extraction_result_to_interview_data
)

logger = logging.getLogger(__name__)
from shared.models import EntityExtractionResult, InterviewData
from typing import Dict, Any, Optional, Union
import json

class InterviewStorage(InterviewDB):
    """Core interview storage operations."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.similarity_threshold = config.get("similarity_threshold", 0.8)
        self.date_tolerance_days = config.get("date_tolerance_days", 7)

    def store_interview(self, email_id: str, entities: EntityExtractionResult, 
                       interview_data: InterviewData) -> Dict[str, Any]:
        """Store interview with intelligent duplicate detection."""
        logger.info(f"Storing interview for email {email_id}")
        
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
            email_id, interview_data.candidate_name, interview_data.company_name, 
            interview_data.role, interview_data.interviewer,
            interview_data.interview_date, interview_data.interview_time, 
            interview_data.duration, interview_data.location, interview_data.format,
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
                              entities: EntityExtractionResult, content_hash: str) -> int:
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
                "preparing", json.dumps(entities.dict()), content_hash
            ))
            
            return cursor.lastrowid

    def _find_exact_duplicate(self, content_hash: str) -> Optional[int]:
        """Find exact duplicate by content hash."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT id FROM interviews WHERE content_hash = ?", (content_hash,))
            result = cursor.fetchone()
            return result[0] if result else None