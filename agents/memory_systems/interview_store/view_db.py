#!/usr/bin/env python3
"""
Database Viewer - Pretty print interview database
Usage: python view_db.py
"""

import sqlite3
import sys
from datetime import datetime
from typing import List, Dict, Any

def format_field(value: str, width: int = 20) -> str:
    """Format a field with proper width and handle None/empty values"""
    if not value or value.strip() == '':
        return f"{'(empty)':<{width}}"
    elif len(value) > width:
        return f"{value[:width-3]}..."
    else:
        return f"{value:<{width}}"

def print_separator(char: str = "=", length: int = 120):
    """Print a separator line"""
    print(char * length)

def view_interviews_table():
    """View interviews table in a nice format"""
    db_path = "agents/memory_systems/interview_store/interviews.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all interviews
        cursor.execute("""
            SELECT id, email_id, candidate_name, company_name, role, 
                   interviewer, interview_date, interview_time, 
                   location, status, created_at 
            FROM interviews 
            ORDER BY created_at DESC
        """)
        
        interviews = cursor.fetchall()
        
        if not interviews:
            print("📭 No interviews found in database")
            return
        
        print(f"📊 INTERVIEW DATABASE - {len(interviews)} RECORDS")
        print_separator()
        
        # Header
        headers = [
            ("ID", 3),
            ("Candidate", 15),
            ("Company", 15),
            ("Role", 15),
            ("Date", 12),
            ("Time", 10),
            ("Location", 12),
            ("Status", 10),
            ("Created", 12)
        ]
        
        header_line = ""
        for header, width in headers:
            header_line += f"{header:<{width}} "
        print(header_line)
        print_separator("-")
        
        # Data rows
        for interview in interviews:
            (id_, email_id, candidate, company, role, interviewer, 
             date, time, location, status, created) = interview
            
            # Format created date
            try:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                created_short = created_dt.strftime('%m/%d %H:%M')
            except:
                created_short = created[:10] if created else ''
            
            # Build row
            row_data = [
                (str(id_), 3),
                (candidate or '(empty)', 15),
                (company or '(empty)', 15),
                (role or '(empty)', 15),
                (date or '', 12),
                (time or '', 10),
                (location or '', 12),
                (status or '', 10),
                (created_short, 12)
            ]
            
            row_line = ""
            for data, width in row_data:
                row_line += format_field(data, width) + " "
            print(row_line)
        
        print_separator()
        
        # Statistics
        real_emails = len([i for i in interviews if not (i[1] or '').startswith('test_')])
        test_emails = len(interviews) - real_emails
        
        statuses = {}
        for interview in interviews:
            status = interview[9] or 'unknown'
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"📈 STATISTICS:")
        print(f"   Real emails: {real_emails}")
        print(f"   Test data: {test_emails}")
        print(f"   By status: {dict(statuses)}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    view_interviews_table()
