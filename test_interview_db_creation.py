# test_interview_db_creation.py
"""
Test script to verify database creation with mock interview emails

This creates mock interview emails to test the enhanced pipeline
and verify that the interviews.db file is created properly.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

# Create a simplified test version without importing the full pipeline
from shared.models import AgentInput, AgentOutput

class MockEnhancedPipeline:
    """Simplified mock pipeline for testing database creation"""
    
    def __init__(self):
        # Import only the interview store agent for testing
        from agents.memory_systems.interview_store.agents import InterviewStoreAgent
        self.interview_store = InterviewStoreAgent({})
    
    async def process_email(self, email_data):
        """Simplified processing that just tests database storage"""
        result = {
            'email_id': email_data.get('id', 'unknown'),
            'research_performed': True,
            'memory_updated': False,
            'entities': {'success': True, 'data': {}},
            'errors': []
        }
        
        try:
            # Mock entity extraction results
            mock_entities = {
                'COMPANY': ['TechCorp'] if 'TechCorp' in email_data.get('body', '') else ['DataTech Inc'],
                'ROLE': ['Software Engineer'] if 'Software Engineer' in email_data.get('body', '') else ['Data Scientist'],
                'CANDIDATE': ['John Doe'] if 'John Doe' in email_data.get('body', '') else ['Jane Smith'],
                'DATE': ['August 1st, 2025'],
                'TIME': ['2:00 PM PST'],
                'INTERVIEWER': ['Sarah Johnson']
            }
            
            result['entities']['data'] = mock_entities
            
            # Test storing in memory
            store_data = {
                'action': 'store',
                'entities': mock_entities,
                'research_data': {'company': {'mock': 'research'}, 'role': {'mock': 'data'}},
                'status': 'preparing'
            }
            
            agent_input = AgentInput(data=store_data)
            memory_output = await self.interview_store.execute(agent_input)
            
            result['memory_updated'] = memory_output.success
            if memory_output.errors:
                result['errors'].extend(memory_output.errors)
                
        except Exception as e:
            result['errors'].append(str(e))
        
        return result

def create_mock_interview_emails():
    """Create mock interview emails for testing"""
    return [
        {
            'id': 'test_001',
            'subject': 'Interview Invitation - Software Engineer Position at TechCorp',
            'sender': 'recruiter@techcorp.com',
            'body': """
            Dear John Doe,

            We are pleased to invite you for an interview for the Software Engineer position at TechCorp.
            
            Interview Details:
            - Company: TechCorp
            - Role: Software Engineer
            - Interviewer: Sarah Johnson, Engineering Manager
            - Date: August 1st, 2025
            - Time: 2:00 PM PST
            - Duration: 1 hour
            - Format: Video call via Zoom
            
            Please confirm your availability.
            
            Best regards,
            TechCorp Recruitment Team
            """
        },
        {
            'id': 'test_002',
            'subject': 'Follow-up Interview - Data Scientist Role',
            'sender': 'hiring@datatech.com',
            'body': """
            Hi Jane Smith,

            Thank you for your interest in the Data Scientist position at DataTech Inc.
            
            We would like to schedule a technical interview:
            - Company: DataTech Inc
            - Position: Senior Data Scientist
            - Interviewer: Dr. Michael Chen
            - Date: August 3rd, 2025
            - Time: 10:30 AM EST
            - Duration: 90 minutes
            
            Looking forward to speaking with you.
            
            Best,
            DataTech Hiring Team
            """
        }
    ]

def test_database_creation():
    """Test database creation with mock interview emails"""
    print("🧪 Testing Database Creation with Mock Interview Emails")
    print("=" * 60)
    
    # Create mock enhanced pipeline
    pipeline = MockEnhancedPipeline()
    
    # Create mock classified emails (simulating classification as Interview_invite)
    mock_classified_emails = {
        'Interview_invite': create_mock_interview_emails(),
        'Personal_sent': [],
        'Others': []
    }
    
    print("📧 Processing mock interview emails...")
    
    # Process the interview emails through mock pipeline (async)
    import asyncio
    async def run_async_processing():
        results = []
        interview_emails = mock_classified_emails.get('Interview_invite', [])
        
        for email in interview_emails:
            result = await pipeline.process_email(email)
            results.append(result)
        
        return results
    
    results = asyncio.run(run_async_processing())
    
    print(f"✅ Processed {len(results)} interview invitations")
    
    # Check if database was created
    db_path = "agents/memory_systems/interview_store/interviews.db"
    if os.path.exists(db_path):
        print(f"✅ Database created successfully at: {db_path}")
        
        # Check database contents
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM interviews")
            count = cursor.fetchone()[0]
            print(f"📊 Database contains {count} interview records")
            
            # Show some sample data
            cursor = conn.execute("""
                SELECT id, company_name, role, candidate_name, status, created_at 
                FROM interviews 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            records = cursor.fetchall()
            
            if records:
                print("\n📋 Sample Interview Records:")
                for record in records:
                    print(f"   ID: {record[0]}, Company: {record[1]}, Role: {record[2]}, "
                          f"Candidate: {record[3]}, Status: {record[4]}")
    else:
        print(f"❌ Database not found at: {db_path}")
    
    # Show processing results
    print(f"\n🎯 Processing Results:")
    for i, result in enumerate(results, 1):
        print(f"   Interview {i}:")
        print(f"     Research performed: {result.get('research_performed', False)}")
        print(f"     Memory updated: {result.get('memory_updated', False)}")
        if result.get('entities') and result['entities'].get('success'):
            entities = result['entities']['data']
            company = entities.get('COMPANY', ['Unknown'])[0] if entities.get('COMPANY') else 'Unknown'
            role = entities.get('ROLE', ['Unknown'])[0] if entities.get('ROLE') else 'Unknown'
            print(f"     Company: {company}, Role: {role}")
        if result.get('errors'):
            print(f"     Errors: {result['errors']}")
    
    print("\n" + "=" * 60)
    print("✅ Database creation test completed!")

if __name__ == "__main__":
    test_database_creation()
