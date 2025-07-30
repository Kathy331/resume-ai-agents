# agents/memory_systems/interview_store/lookup.py
"""
Interview lookup and search operations

Handles querying, filtering, and searching through stored interviews.
Provides duplicate detection and similarity matching functionality.

for examples:
query: {
    "action": "find_similar",
    "entities": {
      "CANDIDATE": ["John Doe"],
      "COMPANY": ["Tech Corp"],
      "ROLE": ["Software Engineer"],
      "DATE": ["2023-10-01"]
    } 
}

response: {
    "similar_interviews": [
      {
        "interview_id": 123,
        "candidate_name": "John Doe",
        "company_name": "Tech Corp",  
        "role": "Software Engineer",
        "interview_date": "2023-10-01",
        "status": "scheduled",
        "similarity_score": 0.85,
        "reasons": ["Candidate: 0.9", "Company: 0.8", "Role: 0.7", "Date proximity"]
      }
    ],
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from difflib import SequenceMatcher

from agents.base_agent import BaseAgent, AgentInput, AgentOutput

from .interview_db import InterviewDB
from .interview_utils import get_first_or_none, parse_date, calculate_similarity
from agents.base_agent import BaseAgent, AgentInput, AgentOutput

class InterviewLookup(InterviewDB, BaseAgent):
    """Agent for looking up and searching interviews."""
    
    def __init__(self, config: Dict[str, Any]):
        InterviewDB.__init__(self, config)
        BaseAgent.__init__(self, config)
        self.similarity_threshold = config.get("similarity_threshold", 0.8)
        self.date_tolerance_days = config.get("date_tolerance_days", 7)


    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate lookup input."""
        action = input_data.data.get("action")
        if action == "find_similar":
            return "entities" in input_data.data
        elif action == "get_by_id":
            return "interview_id" in input_data.data
        elif action == "search":
            return "query_params" in input_data.data
        return False

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Execute lookup operation."""
        try:
            action = input_data.data.get("action")
            
            if action == "find_similar":
                result = await self._find_similar_interviews(input_data.data["entities"])
            elif action == "get_by_id":
                result = await self._get_interview_by_id(input_data.data["interview_id"])
            elif action == "search":
                result = await self._search_interviews(input_data.data["query_params"])
            elif action == "get_history":
                result = await self._get_interview_history(input_data.data.get("query_params", {}))
            else:
                return AgentOutput(success=False, data={}, errors=[f"Unknown action: {action}"])
            
            return AgentOutput(success=True, data=result)
            
        except Exception as e:
            return AgentOutput(success=False, data={}, errors=[str(e)])

    async def _find_similar_interviews(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Find similar interviews based on candidate, company, role, and date."""
        date_str = get_first_or_none(entities.get("DATE", []))
        target_date = parse_date(date_str) if date_str else None
        
        if not (entities.get("CANDIDATE") or entities.get("COMPANY")):
            return {"similar_interviews": [], "count": 0}
        
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM interviews ORDER BY created_at DESC")
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
            
            if similarity_score > 0.5:  # Threshold for similarity
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
        
        return {
            "similar_interviews": similar,
            "count": len(similar)
        }

    async def _get_interview_by_id(self, interview_id: int) -> Dict[str, Any]:
        """Get specific interview by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,))
            interview = cursor.fetchone()
            
            if not interview:
                return {"error": "Interview not found"}
            
            import json
            raw_entities = json.loads(interview["raw_entities"]) if interview["raw_entities"] else {}
            
            return {
                "interview": dict(interview),
                "raw_entities": raw_entities
            }

    async def _search_interviews(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Search interviews with flexible parameters."""
        conditions = []
        params = []
        
        if "candidate" in query_params:
            conditions.append("candidate_name LIKE ?")
            params.append(f"%{query_params['candidate']}%")
            
        if "company" in query_params:
            conditions.append("company_name LIKE ?")
            params.append(f"%{query_params['company']}%")
            
        if "role" in query_params:
            conditions.append("role LIKE ?")
            params.append(f"%{query_params['role']}%")
            
        if "status" in query_params:
            conditions.append("status = ?")
            params.append(query_params["status"])
        
        if "date_from" in query_params:
            conditions.append("interview_date >= ?")
            params.append(query_params["date_from"])
            
        if "date_to" in query_params:
            conditions.append("interview_date <= ?")
            params.append(query_params["date_to"])
        
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
            "count": len(interviews),
            "query_params": query_params
        }

    async def _get_interview_history(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get interview history with optional filtering."""
        limit = query_params.get("limit", 100)
        status_filter = query_params.get("status")
        
        conditions = []
        params = []
        
        if status_filter:
            conditions.append("status = ?")
            params.append(status_filter)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(f"""
                SELECT id, candidate_name, company_name, role, status, 
                       interview_date, created_at, updated_at
                FROM interviews 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ?
            """, params + [limit])
            
            history = [dict(row) for row in cursor.fetchall()]
        
        # Get status distribution
        cursor = conn.execute("SELECT status, COUNT(*) as count FROM interviews GROUP BY status")
        status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}
        
        return {
            "history": history,
            "count": len(history),
            "status_distribution": status_counts
        }

    def _calculate_similarity(self, entities: Dict, interview: Dict, target_date: datetime = None) -> Tuple[float, List[str]]:
        """Calculate similarity between entities and stored interview."""
        score = 0.0
        reasons = []
        
        candidate = self._get_first_or_none(entities.get("CANDIDATE", []))
        company = self._get_first_or_none(entities.get("COMPANY", []))
        role = self._get_first_or_none(entities.get("ROLE", []))
        
        # Candidate similarity (40% weight)
        if candidate and interview.get("candidate_name"):
            sim = self._text_similarity(candidate, interview["candidate_name"])
            if sim > self.similarity_threshold:
                score += 0.4 * sim
                reasons.append(f"Candidate: {sim:.2f}")
        
        # Company similarity (30% weight)
        if company and interview.get("company_name"):
            sim = self._text_similarity(company, interview["company_name"])
            if sim > self.similarity_threshold:
                score += 0.3 * sim
                reasons.append(f"Company: {sim:.2f}")
        
        # Role similarity (20% weight)
        if role and interview.get("role"):
            sim = self._text_similarity(role, interview["role"])
            if sim > self.similarity_threshold:
                score += 0.2 * sim
                reasons.append(f"Role: {sim:.2f}")
        
        # Date proximity (10% weight)
        if target_date and interview.get("interview_date"):
            interview_date = self._parse_date(interview["interview_date"])
            if interview_date and abs((target_date - interview_date).days) <= self.date_tolerance_days:
                score += 0.1
                reasons.append("Date proximity")
        
        return score, reasons

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity."""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string."""
        if not date_str:
            return None
        
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def _get_first_or_none(self, items: List[str]) -> Optional[str]:
        """Get first item from list or None."""
        return items[0] if items else None

