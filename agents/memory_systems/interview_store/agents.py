# agents/memory_systems/interview_store/agents.py
"""
Interview Store Agent

This agent manages SQLite storage for interview data extracted by the Entity Extractor.
It provides CRUD operations, duplicate detection, and interview lifecycle tracking.

Features:
- SQLite database storage with proper schema
- Duplicate detection based on candidate, company, role, and date similarity
- Interview lifecycle tracking (preparing -> prepped)
- Memory retrieval and historical tracking
- Fuzzy matching for deduplication

Input:
- AgentInput with a `data` dictionary containing:
    - "action": (str) One of: "store", "query", "update_status", "get_duplicates", "get_history"
    - "entities": (dict) Extracted entities from Entity Extractor (for store action)
    - "email_id": (str) Optional email identifier
    - "interview_id": (int) Interview ID (for update/query actions)
    - "status": (str) New status (for update_status action) --> ("preparing", "prepped", "scheduled", "completed", "cancelled")
    - "query_params": (dict) Parameters for querying (candidate, company, role, etc.)

Output:
- AgentOutput with:
    - success: (bool) Whether operation succeeded
    - data: (dict) Results based on action type
    - errors: (list) Error messages if any
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from difflib import SequenceMatcher
import re

from shared.models import AgentInput, AgentOutput, EntityExtractionResult, InterviewData
from agents.base_agent import BaseAgent
from .interview_db import InterviewDB
from .interview_utils import get_first_or_none, create_content_hash, calculate_similarity, parse_date


class InterviewStore(InterviewDB, BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        InterviewDB.__init__(self, config)
        BaseAgent.__init__(self, config)
        self.similarity_threshold = config.get("similarity_threshold", 0.8)
        self.date_tolerance_days = config.get("date_tolerance_days", 7)

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
                    content_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_candidate_company 
                ON interviews(candidate_name, company_name)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_email_id 
                ON interviews(email_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_hash 
                ON interviews(content_hash)
            """)

    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate input data based on action type."""
        action = input_data.data.get("action")
        if not action:
            return False
            
        if action == "store":
            return "entities" in input_data.data
        elif action in ["update_status", "query"]:
            return "interview_id" in input_data.data
        elif action == "get_duplicates":
            return "entities" in input_data.data
        elif action in ["get_history", "query_similar", "get_unprepped"]:
            return "query_params" in input_data.data or action == "get_unprepped"
            
        return True

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Execute the requested action."""
        try:
            action = input_data.data.get("action")
            
            if action == "store":
                result = await self._store_interview(input_data.data)
            elif action == "query":
                result = await self._query_interview(input_data.data)
            elif action == "update_status":
                result = await self._update_status(input_data.data)
            elif action == "get_duplicates":
                result = await self._get_duplicates(input_data.data)
            elif action == "get_history":
                result = await self._get_history(input_data.data)
            elif action == "query_similar":
                result = await self._query_similar(input_data.data)
            elif action == "get_unprepped":
                result = await self._get_unprepped_interviews(input_data.data)
            else:
                return AgentOutput(
                    success=False,
                    data={},
                    metadata={"action": action, "timestamp": datetime.now().isoformat()},
                    errors=[f"Unknown action: {action}"]
                )
                
            return AgentOutput(
                success=True,
                data=result,
                metadata={"action": action, "timestamp": datetime.now().isoformat()},
                errors=None
            )
            
        except Exception as e:
            return AgentOutput(
                success=False,
                data={},
                metadata={"action": input_data.data.get("action", "unknown"), "timestamp": datetime.now().isoformat()},
                errors=[str(e)]
            )

    async def _store_interview(self, data: Dict[str, Any]) -> Dict[str, Any]:
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
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id FROM interviews WHERE content_hash = ?",
                (content_hash,)
            )
            exact_duplicate = cursor.fetchone()
            
            if exact_duplicate:
                return {
                    "action": "duplicate_found",
                    "interview_id": exact_duplicate[0],
                    "message": "Exact duplicate found, not storing"
                }
        
        # Check for similar interviews
        duplicates = await self._find_similar_interviews(entities)
        
        if duplicates:
            # Check if we should update existing records with missing information
            updated_any = False
            for similar_interview in duplicates:
                interview_id = similar_interview['interview_id']
                updates_needed = []
                update_values = []
                
                # Check what information is missing and can be updated
                if not similar_interview.get('interviewer') and interviewer:
                    updates_needed.append("interviewer = ?")
                    update_values.append(interviewer)
                
                if not similar_interview.get('role') and role:
                    updates_needed.append("role = ?")
                    update_values.append(role)
                
                # Add other fields that might be missing
                if updates_needed:
                    update_query = f"""
                        UPDATE interviews 
                        SET {', '.join(updates_needed)}, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """
                    update_values.append(interview_id)
                    
                    with self.get_connection() as conn:
                        conn.execute(update_query, update_values)
                    
                    updated_any = True
                    print(f"✅ Updated interview {interview_id} with missing information: {', '.join([u.split(' = ')[0] for u in updates_needed])}")
            
            if updated_any:
                return {
                    "action": "similar_found_and_updated",
                    "similar_interviews": duplicates,
                    "message": f"Found {len(duplicates)} similar interview(s) and updated missing information"
                }
            else:
                return {
                    "action": "similar_found",
                    "similar_interviews": duplicates,
                    "message": f"Found {len(duplicates)} similar interview(s)"
                }
        
        # Store new interview
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
            
            interview_id = cursor.lastrowid
            
        return {
            "action": "stored",
            "interview_id": interview_id,
            "status": "preparing",
            "message": "Interview stored successfully"
        }

    async def _find_similar_interviews(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar interviews based on candidate, company, role, and date."""
        date_str = get_first_or_none(entities.get("DATE", []))
        target_date = parse_date(date_str) if date_str else None
        
        if not (entities.get("CANDIDATE") or entities.get("COMPANY")):
            return []
        
        # Get potential matches
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM interviews 
                WHERE candidate_name IS NOT NULL OR company_name IS NOT NULL
                ORDER BY created_at DESC
            """)
            all_interviews = cursor.fetchall()
        
        similar = []
        
        for interview in all_interviews:
            similarity_score, reasons = calculate_similarity(
                entities, 
                dict(interview), 
                self.similarity_threshold,
                self.date_tolerance_days,
                target_date
            )
            
            # Consider it similar if score > 0.5
            if similarity_score > 0.5:
                similar.append({
                    "interview_id": interview["id"],
                    "candidate_name": interview["candidate_name"],
                    "company_name": interview["company_name"],
                    "role": interview["role"],
                    "interview_date": interview["interview_date"],
                    "status": interview["status"],
                    "similarity_score": similarity_score,
                    "reasons": reasons
                })
        
        return similar

    async def _update_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update interview status (preparing -> prepped)."""
        interview_id = data["interview_id"]
        new_status = data.get("status", "prepped")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE interviews 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_status, interview_id))
            
            if cursor.rowcount == 0:
                return {"error": "Interview not found"}
        
        return {
            "action": "status_updated",
            "interview_id": interview_id,
            "new_status": new_status
        }

    async def _query_interview(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Query specific interview by ID."""
        interview_id = data["interview_id"]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,))
            interview = cursor.fetchone()
            
            if not interview:
                return {"error": "Interview not found"}
            
            # Parse raw entities
            raw_entities = json.loads(interview["raw_entities"]) if interview["raw_entities"] else {}
            
            return {
                "interview": dict(interview),
                "raw_entities": raw_entities
            }

    async def _get_duplicates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get potential duplicates for given entities."""
        entities = data["entities"]
        duplicates = await self._find_similar_interviews(entities)
        
        return {
            "duplicates": duplicates,
            "count": len(duplicates)
        }

    async def _get_history(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get interview history based on query parameters."""
        query_params = data["query_params"]
        
        conditions = []
        params = []
        
        if "candidate" in query_params:
            conditions.append("candidate_name LIKE ?")
            params.append(f"%{query_params['candidate']}%")
            
        if "company" in query_params:
            conditions.append("company_name LIKE ?")
            params.append(f"%{query_params['company']}%")
            
        if "status" in query_params:
            conditions.append("status = ?")
            params.append(query_params["status"])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        limit = query_params.get("limit", 50)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(f"""
                SELECT * FROM interviews 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ?
            """, params + [limit])
            
            interviews = [dict(row) for row in cursor.fetchall()]
        
        return {
            "interviews": interviews,
            "count": len(interviews)
        }

    def _get_first_or_none(self, items: List[str]) -> Optional[str]:
        """Get first item from list or None if empty."""
        return items[0] if items else None

    def _create_content_hash(self, entities: Dict[str, Any]) -> str:
        """Create hash for exact duplicate detection."""
        # Sort keys for consistent hashing
        content = json.dumps(entities, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using SequenceMatcher."""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
            
        # Common date formats
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", 
            "%B %d, %Y", "%b %d, %Y", "%Y-%m-%d %H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    async def _get_unprepped_interviews(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get interviews that need research (status != 'prepped')"""
        try:
            max_results = data.get('max_results', 10)
            priority_filter = data.get('priority_filter', 'all')
            exclude_statuses = data.get('exclude_statuses', ['prepped', 'completed', 'archived'])
            
            # Build WHERE clause for status filtering
            status_placeholders = ','.join(['?' for _ in exclude_statuses])
            where_clause = f"status NOT IN ({status_placeholders})"
            
            # Build query parameters
            query_params = list(exclude_statuses)
            
            # Add priority filter if specified
            if priority_filter != 'all':
                where_clause += " AND priority = ?"
                query_params.append(priority_filter)
            
            # Execute query using the connection from parent class
            with self.get_connection() as conn:
                query = f"""
                    SELECT id, candidate_name, company_name, role, interviewer, interview_date, 
                           interview_time, duration, status, raw_entities,
                           created_at, updated_at
                    FROM interviews 
                    WHERE {where_clause}
                    ORDER BY 
                        created_at DESC
                    LIMIT ?
                """
                query_params.append(max_results)
                
                cursor = conn.execute(query, query_params)
                rows = cursor.fetchall()
            
            # Convert rows to interview dictionaries
            interviews = []
            for row in rows:
                # Parse entities JSON if available
                entities = {}
                if row[9]:  # raw_entities column
                    try:
                        entities = json.loads(row[9])
                    except json.JSONDecodeError:
                        entities = {}
                
                # Merge database column information into entities if missing
                # This ensures that updated database fields are available in entities
                if row[2] and not entities.get('COMPANY'):  # company_name
                    entities['COMPANY'] = [row[2]]
                if row[3] and not entities.get('ROLE'):  # role
                    entities['ROLE'] = [row[3]]
                if row[4] and not entities.get('INTERVIEWER'):  # interviewer
                    entities['INTERVIEWER'] = [row[4]]
                
                interview_dict = {
                    'id': row[0],
                    'candidate': row[1],
                    'company': row[2],
                    'role': row[3],
                    'interviewer': row[4],
                    'interview_date': row[5],
                    'interview_time': row[6],
                    'duration': row[7],
                    'status': row[8] or 'preparing',
                    'priority': 'normal',  # Default priority since it's not in current schema
                    'entities': entities,  # Now includes updated database information
                    'email_subject': f"Interview with {row[2] or 'Company'}" if row[2] else "Interview Invitation",
                    'created_at': row[10],
                    'updated_at': row[11]
                }
                interviews.append(interview_dict)
            
            return {
                'interviews': interviews,
                'count': len(interviews),
                'max_results': max_results,
                'priority_filter': priority_filter,
                'excluded_statuses': exclude_statuses
            }
            
        except Exception as e:
            raise Exception(f"Failed to get unprepped interviews: {str(e)}")