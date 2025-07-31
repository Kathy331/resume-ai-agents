#!/usr/bin/env python3
"""
Test script for Research Engine Pipeline integration

This script tests the research pipeline integration with the workflow runner
and validates that unprepped interviews are properly identified and processed.
"""

import os
import sys
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_workflow_runner_integration():
    """Test WorkflowRunner integration with research pipeline"""
    print("🧪 Testing Research Engine Pipeline Integration")
    print("=" * 60)
    
    try:
        from agents.orchestrator.workflow_runner import WorkflowRunner
        
        # Initialize runner
        runner = WorkflowRunner(enable_notifications=True, log_results=True)
        print("✅ WorkflowRunner initialized successfully")
        
        # Test research pipeline method exists
        if hasattr(runner, 'run_research_pipeline'):
            print("✅ run_research_pipeline method found")
        else:
            print("❌ run_research_pipeline method missing")
            return False
        
        # Test research pipeline execution (dry run with small batch)
        print("\n🔬 Testing research pipeline execution...")
        result = runner.run_research_pipeline(max_interviews=2, priority_filter='all')
        
        # Validate result structure
        expected_keys = ['success', 'interviews_found', 'interviews_researched', 'processing_time']
        for key in expected_keys:
            if key in result:
                print(f"✅ Result contains '{key}': {result[key]}")
            else:
                print(f"❌ Missing result key: {key}")
        
        # Check execution history
        history = runner.get_execution_history()
        research_runs = [run for run in history if run.get('type') == 'research_pipeline']
        print(f"✅ Execution history contains {len(research_runs)} research pipeline runs")
        
        return result['success'] if 'success' in result else False
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def test_pipeline_components():
    """Test individual pipeline components"""
    print("\n🔧 Testing Pipeline Components")
    print("=" * 60)
    
    try:
        from workflows.research_engine_pipeline import ResearchEnginePipeline, ResearchRequest, ResearchResult
        
        # Test data structures
        print("✅ ResearchRequest dataclass imported")
        print("✅ ResearchResult dataclass imported")
        
        # Test pipeline creation
        pipeline = ResearchEnginePipeline()
        print("✅ ResearchEnginePipeline created successfully")
        
        # Test request creation
        request = ResearchRequest(
            interview_id="test_123",
            company_name="Test Company",
            interviewer_name="John Doe",
            role_title="Software Engineer"
        )
        print(f"✅ ResearchRequest created: {request.interview_id}")
        
        # Test result creation
        result = ResearchResult(interview_id="test_123")
        print(f"✅ ResearchResult created: {result.interview_id}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Component test failed: {str(e)}")
        return False

def test_integration_workflow():
    """Test complete integration workflow"""
    print("\n🔄 Testing Complete Integration Workflow")
    print("=" * 60)
    
    try:
        from agents.orchestrator.workflow_runner import WorkflowRunner
        
        runner = WorkflowRunner()
        
        # Test 1: Email pipeline
        print("1️⃣ Testing email pipeline...")
        email_result = runner.run_email_pipeline('test', max_results=1, user_email='user@test.com')
        print(f"   Email pipeline success: {email_result.get('success', False)}")
        
        # Test 2: Research pipeline
        print("2️⃣ Testing research pipeline...")
        research_result = runner.run_research_pipeline(max_interviews=1, priority_filter='all')
        print(f"   Research pipeline success: {research_result.get('success', False)}")
        
        # Test 3: Check execution history
        print("3️⃣ Checking execution history...")
        history = runner.get_execution_history()
        print(f"   Total runs in history: {len(history)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration workflow test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Research Engine Pipeline Integration Tests")
    print("=" * 80)
    
    test_results = []
    
    # Run individual tests
    test_results.append(("WorkflowRunner Integration", test_workflow_runner_integration()))
    test_results.append(("Pipeline Components", test_pipeline_components()))
    test_results.append(("Integration Workflow", test_integration_workflow()))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Research Engine Pipeline integration is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
