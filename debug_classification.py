#!/usr/bin/env python3
"""Debug script to test email classification"""

import asyncio
from agents.email_classifier.agent import EmailClassifierAgent
from shared.models import AgentInput

def test_classification():
    # Test email that should be classified as interview
    test_email = {
        'id': 'test123',
        'subject': 'Invitation to Interview for Internship Opportunity with JUTEQ',
        'sender': 'recruiter@juteq.com',
        'recipients': ['user@example.com'],
        'body': 'We would like to invite you for an interview for our internship program.',
        'date': '2025-07-30',
        'from': 'recruiter@juteq.com',  # Add both fields
        'to': ['user@example.com']
    }
    
    print("Testing email classification...")
    print(f"Subject: {test_email['subject']}")
    print(f"Body: {test_email['body']}")
    
    # Initialize classifier
    config = {'model': 'gpt-4', 'temperature': 0.7}
    classifier = EmailClassifierAgent(config=config)
    
    # Create input data
    input_data = AgentInput(
        data={"emails": [test_email]},
        metadata={}
    )
    
    # Run classification
    async def run_test():
        result = await classifier.execute(input_data)
        print(f"\nClassification result:")
        print(f"Success: {result.success}")
        print(f"Data: {result.data}")
        
        interview_ids = result.data.get('interview_ids', [])
        is_interview = test_email['id'] in interview_ids
        print(f"Is interview: {is_interview}")
        
        return result
    
    # Run the test
    return asyncio.run(run_test())

if __name__ == "__main__":
    test_classification()
