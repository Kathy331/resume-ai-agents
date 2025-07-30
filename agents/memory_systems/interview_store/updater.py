# agents/memory_systems/interview_store/updater.py

"""
Interview update operations

features:
- Update interview status: preparing, prepped, scheduled, completed, cancelled
- Track changes in interview records
- Maintain history of changes
"""

import sqlite3
from datetime import datetime
from typing import Dict, Any
from .interview_db import InterviewDB


class InterviewUpdater(InterviewDB):
    """Update operations for interview records."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._init_history_table()

    def _init_history_table(self):
        """Initialize history tracking table."""
        with self.get_connection() as conn:
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

    async def update_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update interview status and track changes."""
        interview_id = data.get("interview_id")
        new_status = data.get("status")

        valid_statuses = {"preparing", "prepped", "scheduled", "completed", "cancelled"}
        if new_status not in valid_statuses:
            return {"error": f"Invalid status: {new_status}"}

        with self.get_connection() as conn:
            cursor = conn.execute("SELECT status FROM interviews WHERE id = ?", (interview_id,))
            row = cursor.fetchone()

            if not row:
                return {"error": "Interview not found"}

            old_status = row[0]
            conn.execute("""
                UPDATE interviews 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_status, interview_id))

            self._record_change(conn, interview_id, "status", old_status, new_status)

        return {
            "action": "status_updated",
            "interview_id": interview_id,
            "old_status": old_status,
            "new_status": new_status,
            "updated_at": datetime.now().isoformat()
        }

    def _record_change(
        self, conn: sqlite3.Connection,
        interview_id: int,
        field: str,
        old_value: str,
        new_value: str
    ):
        """Record a change in the history table."""
        conn.execute("""
            INSERT INTO interview_history (interview_id, field_name, old_value, new_value)
            VALUES (?, ?, ?, ?)
        """, (interview_id, field, old_value, new_value))
