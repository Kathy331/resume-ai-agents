#!/usr/bin/env python3
"""Debug script to test entity extraction"""

import asyncio
from agents.entity_extractor.agent import EntityExtractor
from shared.models import AgentInput

def test_entity_extraction():
    # Test email with clear entities
    email_text = """Subject: Invitation to Interview for Internship Opportunity with JUTEQ

From: recruiter@juteq.com

We would like to invite you for an interview for our Software Engineer internship program at JUTEQ. 
The interview will be conducted by John Smith, our Lead Developer.

Please let us know your availability for next week.

Best regards,
HR Team
JUTEQ Technologies"""
    
    print("Testing entity extraction...")
    print(f"Email text:\n{email_text}\n")
    
    # Initialize entity extractor
    config = {'model': 'gpt-4', 'temperature': 0.7}
    extractor = EntityExtractor(config=config)
    
    # Create input data
    input_data = AgentInput(
        data={"text": email_text, "email_id": "test123"},
        metadata={}
    )
    
    # Run entity extraction
    async def run_test():
        result = await extractor.execute(input_data)
        print(f"Entity extraction result:")
        print(f"Success: {result.success}")
        print(f"Data: {result.data}")
        print(f"Errors: {result.errors}")
        
        return result
    
    # Run the test
    return asyncio.run(run_test())

if __name__ == "__main__":
    test_entity_extraction()
