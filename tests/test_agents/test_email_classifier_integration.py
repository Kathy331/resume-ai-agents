#!/usr/bin/env python3
"""
Test script to verify EmailClassifierAgent integration
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.append('.')

def test_email_classifier_integration():
    """Test the EmailClassifierAgent integration"""
    
    print("🧪 Testing EmailClassifierAgent Integration")
    print("=" * 50)
    
    # Test 1: Import the classifier
    try:
        from agents.email_classifier.agent import EmailClassifierAgent
        print("✅ 1. EmailClassifierAgent import successful")
    except Exception as e:
        print(f"❌ 1. EmailClassifierAgent import failed: {e}")
        return False
    
    # Test 2: Test the updated classify_emails function
    try:
        from workflows.email_pipeline import classify_emails
        
        # Sample emails for testing
        test_emails = [
            {
                'id': '1',
                'subject': 'Interview Invitation - Software Engineer Position',
                'body': 'We would like to invite you for an interview...',
                'from': 'hr@techcorp.com',
                'to': ['candidate@example.com']
            },
            {
                'id': '2', 
                'subject': 'Meeting with friends',
                'body': 'Hi there, want to grab dinner tonight?',
                'from': 'user@example.com',
                'to': ['friend@example.com']
            },
            {
                'id': '3',
                'subject': 'Newsletter - Weekly Updates',
                'body': 'Here are this week\'s updates...',
                'from': 'newsletter@company.com',
                'to': ['user@example.com']
            }
        ]
        
        # Test classification
        result = classify_emails(test_emails, user_email='user@example.com')
        
        print("✅ 2. classify_emails function works")
        print(f"   - Interview emails: {len(result.get('Interview_invite', []))}")
        print(f"   - Personal emails: {len(result.get('Personal_sent', []))}")
        print(f"   - Other emails: {len(result.get('Others', []))}")
        
    except Exception as e:
        print(f"❌ 2. classify_emails function failed: {e}")
        return False
    
    # Test 3: Test EmailPipeline with new classifier
    try:
        from workflows.email_pipeline import EmailPipeline
        
        pipeline = EmailPipeline()
        print("✅ 3. EmailPipeline initialization successful")
        
        # Test single email classification
        async def test_single_classification():
            result = await pipeline._classify_email(test_emails[0])
            return result
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        classification_result = loop.run_until_complete(test_single_classification())
        
        if classification_result.get('success'):
            print(f"✅ 4. Single email classification successful: {classification_result.get('category')}")
        else:
            print(f"❌ 4. Single email classification failed: {classification_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 3-4. EmailPipeline tests failed: {e}")
        return False
    
    # Test 4: Test workflow runner integration
    try:
        from agents.orchestrator.workflow_runner import WorkflowRunner
        
        runner = WorkflowRunner(enable_notifications=False, log_results=False)
        print("✅ 5. WorkflowRunner with EmailClassifierAgent ready")
        
    except Exception as e:
        print(f"❌ 5. WorkflowRunner integration failed: {e}")
        return False
    
    print("\n🎉 All EmailClassifierAgent integration tests passed!")
    print("📝 The system now uses EmailClassifierAgent instead of temporary rules")
    return True

if __name__ == "__main__":
    success = test_email_classifier_integration()
    if not success:
        sys.exit(1)
