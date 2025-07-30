# simple_db_test.py
"""
Simple test to verify database creation without complex agent dependencies
"""

import os
import sqlite3
from pathlib import Path

def test_database_creation_simple():
    """Simple test to create the database directly"""
    print("🧪 Simple Database Creation Test")
    print("=" * 40)
    
    # Define database path
    db_path = "agents/memory_systems/interview_store/interviews.db"
    
    # Create directory if it doesn't exist
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Create database and table
    with sqlite3.connect(db_path) as conn:
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
        
        # Insert some test data
        test_interviews = [
            ('test_001', 'John Doe', 'TechCorp', 'Software Engineer', 'Sarah Johnson', 
             'August 1st, 2025', '2:00 PM PST', '1 hour', 'Video call', 'Virtual', 'preparing'),
            ('test_002', 'Jane Smith', 'DataTech Inc', 'Data Scientist', 'Dr. Michael Chen',
             'August 3rd, 2025', '10:30 AM EST', '90 minutes', 'Office', 'In-person', 'preparing')
        ]
        
        for interview in test_interviews:
            conn.execute("""
                INSERT INTO interviews 
                (email_id, candidate_name, company_name, role, interviewer, 
                 interview_date, interview_time, duration, location, format, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, interview)
        
        conn.commit()
    
    # Verify database was created
    if os.path.exists(db_path):
        print(f"✅ Database created successfully at: {db_path}")
        
        # Check contents
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM interviews")
            count = cursor.fetchone()[0]
            print(f"📊 Database contains {count} interview records")
            
            # Show sample data
            cursor = conn.execute("""
                SELECT id, company_name, role, candidate_name, status, created_at 
                FROM interviews 
                ORDER BY created_at DESC
            """)
            records = cursor.fetchall()
            
            print("\n📋 Interview Records:")
            for record in records:
                print(f"   ID: {record[0]}, Company: {record[1]}, Role: {record[2]}, "
                      f"Candidate: {record[3]}, Status: {record[4]}")
                      
        print(f"\n💾 Database file size: {os.path.getsize(db_path)} bytes")
    else:
        print(f"❌ Database not found at: {db_path}")
    
    print("\n" + "=" * 40)
    print("✅ Simple database test completed!")

if __name__ == "__main__":
    test_database_creation_simple()
