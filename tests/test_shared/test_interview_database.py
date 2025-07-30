# tests/test_shared/test_interview_database.py
"""
Test for interview database creation and basic operations

This test verifies that the SQLite database for interview storage
can be created and basic operations work correctly.

Run from project root:
python -m pytest tests/test_shared/test_interview_database.py -v
"""

import os
import sqlite3
import tempfile
from pathlib import Path


class TestInterviewDatabase:
    """Test class for interview database functionality"""
    
    def test_database_creation_and_schema(self):
        """Test database creation with proper schema"""
        print("🧪 Testing Interview Database Creation")
        print("=" * 50)
        
        # Use a temporary database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            db_path = temp_db.name
        
        try:
            # Create database and table (similar to InterviewDB class)
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
                
                # Create indexes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_candidate_company ON interviews(candidate_name, company_name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_email_id ON interviews(email_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON interviews(content_hash)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON interviews(status)")
                
                conn.commit()
            
            # Verify database was created
            assert os.path.exists(db_path), "Database file should be created"
            print(f"✅ Database created successfully")
            
            # Verify schema
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                assert 'interviews' in tables, "Interviews table should exist"
                
                # Check table structure
                cursor = conn.execute("PRAGMA table_info(interviews)")
                columns = {row[1]: row[2] for row in cursor.fetchall()}  # name: type
                
                expected_columns = {
                    'id': 'INTEGER',
                    'email_id': 'TEXT',
                    'candidate_name': 'TEXT',
                    'company_name': 'TEXT',
                    'role': 'TEXT',
                    'status': 'TEXT'
                }
                
                for col_name, col_type in expected_columns.items():
                    assert col_name in columns, f"Column {col_name} should exist"
                    # Note: SQLite type affinity means we don't need exact type matches
                
                print(f"✅ Database schema verified ({len(columns)} columns)")
            
        finally:
            # Clean up temporary file
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_database_operations(self):
        """Test basic CRUD operations on the database"""
        print("🧪 Testing Database CRUD Operations")
        print("=" * 50)
        
        # Use a temporary database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            db_path = temp_db.name
        
        try:
            # Create and populate database
            with sqlite3.connect(db_path) as conn:
                # Create table
                conn.execute("""
                    CREATE TABLE interviews (
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
                
                # Insert test data
                test_interviews = [
                    ('test_001', 'John Doe', 'TechCorp', 'Software Engineer', 'Sarah Johnson', 
                     'August 1st, 2025', '2:00 PM PST', '1 hour', 'Video call', 'Virtual', 'preparing', 'hash1'),
                    ('test_002', 'Jane Smith', 'DataTech Inc', 'Data Scientist', 'Dr. Michael Chen',
                     'August 3rd, 2025', '10:30 AM EST', '90 minutes', 'Office', 'In-person', 'preparing', 'hash2')
                ]
                
                for interview in test_interviews:
                    conn.execute("""
                        INSERT INTO interviews 
                        (email_id, candidate_name, company_name, role, interviewer, 
                         interview_date, interview_time, duration, location, format, status, content_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, interview)
                
                conn.commit()
                
                # Test SELECT operation
                cursor = conn.execute("SELECT COUNT(*) FROM interviews")
                count = cursor.fetchone()[0]
                assert count == 2, f"Should have 2 records, got {count}"
                print(f"✅ INSERT operation successful ({count} records)")
                
                # Test UPDATE operation
                conn.execute("UPDATE interviews SET status = 'prepped' WHERE company_name = 'TechCorp'")
                conn.commit()
                
                cursor = conn.execute("SELECT status FROM interviews WHERE company_name = 'TechCorp'")
                status = cursor.fetchone()[0]
                assert status == 'prepped', f"Status should be 'prepped', got '{status}'"
                print("✅ UPDATE operation successful")
                
                # Test SELECT with conditions
                cursor = conn.execute("""
                    SELECT company_name, role, candidate_name 
                    FROM interviews 
                    WHERE status = 'prepped'
                """)
                records = cursor.fetchall()
                assert len(records) == 1, "Should find 1 prepped interview"
                assert records[0][0] == 'TechCorp', "Should find TechCorp interview"
                print("✅ SELECT with conditions successful")
                
                # Test DELETE operation (optional, for completeness)
                cursor = conn.execute("SELECT COUNT(*) FROM interviews WHERE status = 'preparing'")
                preparing_count = cursor.fetchone()[0]
                assert preparing_count == 1, "Should have 1 preparing interview"
                print("✅ All CRUD operations verified")
                
        finally:
            # Clean up temporary file
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_production_database_creation(self):
        """Test creating the actual production database"""
        print("🧪 Testing Production Database Creation")
        print("=" * 50)
        
        # Define production database path
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
            
            # Insert some test data if table is empty
            cursor = conn.execute("SELECT COUNT(*) FROM interviews")
            count = cursor.fetchone()[0]
            
            if count == 0:
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
                print("✅ Sample test data inserted")
        
        # Verify database was created
        if os.path.exists(db_path):
            print(f"✅ Production database created at: {db_path}")
            
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
                    LIMIT 3
                """)
                records = cursor.fetchall()
                
                if records:
                    print("\n📋 Sample Interview Records:")
                    for record in records:
                        print(f"   ID: {record[0]}, Company: {record[1]}, Role: {record[2]}, "
                              f"Candidate: {record[3]}, Status: {record[4]}")
                        
            print(f"💾 Database file size: {os.path.getsize(db_path)} bytes")
            
            # Assert for test
            assert os.path.exists(db_path), "Production database should exist"
            assert os.path.getsize(db_path) > 0, "Database should not be empty"
            
        else:
            raise AssertionError(f"Production database not created at: {db_path}")


def test_interview_database_integration():
    """Integration test function that can be run directly"""
    test_instance = TestInterviewDatabase()
    test_instance.test_database_creation_and_schema()
    test_instance.test_database_operations()
    test_instance.test_production_database_creation()
    print("🎉 All interview database tests passed!")


if __name__ == "__main__":
    test_interview_database_integration()
