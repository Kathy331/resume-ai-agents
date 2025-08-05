# agents/memory_systems/shared_memory.py
"""
Shared Memory System - Wrapper for interview storage and retrieval
"""

import sqlite3
import json
from typing import Dict, Any, List


class SharedMemorySystem:
    """
    Simplified wrapper class for the interview storage system to provide 
    a direct database interface for the workflow runner.
    """
    
    def __init__(self):
        self.db_path = "agents/memory_systems/interview_store/interviews.db"
    
    def get_all_interviews(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Get all interviews from the database
        
        Args:
            max_results: Maximum number of interviews to return
            
        Returns:
            List of interview dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT id, candidate_name, company_name, role, interviewer, interview_date, 
                           interview_time, duration, status, raw_entities,
                           created_at, updated_at
                    FROM interviews 
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                
                cursor = conn.execute(query, (max_results,))
                rows = cursor.fetchall()
                
                interviews = []
                for row in rows:
                    # Parse entities JSON if available
                    entities = {}
                    if row[9]:  # raw_entities column
                        try:
                            entities = json.loads(row[9])
                        except json.JSONDecodeError:
                            entities = {}
                    
                    interview_dict = {
                        'id': row[0],
                        'candidate_name': row[1],
                        'company': row[2],
                        'role': row[3],
                        'interviewer': row[4],
                        'interview_date': row[5],
                        'interview_time': row[6],
                        'duration': row[7],
                        'status': row[8] or 'preparing',
                        'raw_entities': row[9],
                        'entities': entities,
                        'created_at': row[10],
                        'updated_at': row[11]
                    }
                    interviews.append(interview_dict)
                
                return interviews
                
        except Exception as e:
            print(f"⚠️ Error getting interviews from memory: {str(e)}")
            return []
    
    def update_interview_status(self, interview_id: str, status: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Update the status of an interview
        
        Args:
            interview_id: ID of the interview to update
            status: New status to set
            metadata: Additional metadata to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Update the interview status
                conn.execute(
                    "UPDATE interviews SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (status, int(interview_id))
                )
                
                # If metadata provided, you could store it in a separate field or table
                # For now, we'll just update the status
                
                return True
                
        except Exception as e:
            print(f"⚠️ Error updating interview status: {str(e)}")
            return False
    
    def get_unprepped_interviews(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get interviews that haven't been prepped yet
        
        Args:
            max_results: Maximum number of interviews to return
            
        Returns:
            List of unprepped interview dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get interviews that are not prepped, completed, cancelled, or archived
                exclude_statuses = ['prepped', 'completed', 'cancelled', 'archived']
                status_placeholders = ','.join(['?' for _ in exclude_statuses])
                
                query = f"""
                    SELECT id, candidate_name, company_name, role, interviewer, interview_date, 
                           interview_time, duration, status, raw_entities,
                           created_at, updated_at
                    FROM interviews 
                    WHERE status NOT IN ({status_placeholders})
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                
                params = exclude_statuses + [max_results]
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                interviews = []
                for row in rows:
                    # Parse entities JSON if available
                    entities = {}
                    if row[9]:  # raw_entities column
                        try:
                            entities = json.loads(row[9])
                        except json.JSONDecodeError:
                            entities = {}
                    
                    interview_dict = {
                        'id': row[0],
                        'candidate_name': row[1],
                        'company': row[2],
                        'role': row[3],
                        'interviewer': row[4],
                        'interview_date': row[5],
                        'interview_time': row[6],
                        'duration': row[7],
                        'status': row[8] or 'preparing',
                        'raw_entities': row[9],
                        'entities': entities,
                        'created_at': row[10],
                        'updated_at': row[11]
                    }
                    interviews.append(interview_dict)
                
                return interviews
                
        except Exception as e:
            print(f"⚠️ Error getting unprepped interviews: {str(e)}")
            return []
