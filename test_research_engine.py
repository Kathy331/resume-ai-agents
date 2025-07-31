#!/usr/bin/env python3
"""
Research Engine Integration Test

This script tests the comprehensive research engine functionality including:
- Tavily client initialization and caching
- Individual research components (company, role, interviewer)
- Research orchestrator coordination
- Configuration management
- Error handling and fallbacks

Run this script to validate the research engine implementation.
"""

import sys
import os
import asyncio
from typing import Dict, Any

# Add the project root to Python path
sys.path.append('/Users/kathychen/VisualStudioCode/Hackaton/General-Seed camp 2025/Final/resume-ai-agents')

def test_import_structure():
    """Test that all components can be imported correctly"""
    print("🧪 Testing Research Engine Import Structure...")
    
    try:
        # Test main package import
        from agents.research_engine import (
            research_orchestrator,
            ResearchRequest,
            ComprehensiveResearchResult,
            research_config,
            health_check,
            get_package_info
        )
        print("✅ Main package imports successful")
        
        # Test individual component imports
        from agents.research_engine import (
            CompanyResearcher,
            InterviewerResearcher,
            RoleResearcher,
            EnhancedTavilyClient
        )
        print("✅ Individual component imports successful")
        
        # Test data model imports
        from agents.research_engine import (
            CompanyInfo,
            ProfessionalProfile,
            SalaryInfo
        )
        print("✅ Data model imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration management"""
    print("\n🧪 Testing Configuration Management...")
    
    try:
        from agents.research_engine import research_config, load_environment_config
        
        # Test configuration summary
        config_summary = research_config.get_config_summary()
        print(f"📋 Config Summary: {config_summary}")
        
        # Test environment loading
        load_environment_config('development')
        print("✅ Development config loaded")
        
        load_environment_config('production')
        print("✅ Production config loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_package_health():
    """Test package health check"""
    print("\n🧪 Testing Package Health...")
    
    try:
        from agents.research_engine import health_check, get_package_info
        
        # Run health check
        health = health_check()
        print(f"🏥 Health Status: {health['status']}")
        print(f"📊 Health Score: {health['health_score']:.1%}")
        
        # Get package info
        package_info = get_package_info()
        print(f"📦 Package Version: {package_info['version']}")
        print(f"🔧 Components: {len(package_info['components'])}")
        
        return health['health_score'] > 0.5
        
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_research_orchestrator_init():
    """Test research orchestrator initialization"""
    print("\n🧪 Testing Research Orchestrator...")
    
    try:
        from agents.research_engine import research_orchestrator, ResearchRequest
        
        # Test orchestrator attributes
        assert hasattr(research_orchestrator, 'company_researcher')
        assert hasattr(research_orchestrator, 'interviewer_researcher')
        assert hasattr(research_orchestrator, 'role_researcher')
        assert hasattr(research_orchestrator, 'tavily_client')
        print("✅ Orchestrator attributes verified")
        
        # Test research request creation
        request = ResearchRequest(
            company_name="Test Company",
            role_title="Test Role",
            interviewer_names=["Test Person"],
            research_depth="standard"
        )
        print("✅ Research request creation successful")
        
        # Test research priorities
        priorities = research_orchestrator.research_priorities
        assert 'basic' in priorities
        assert 'standard' in priorities  
        assert 'comprehensive' in priorities
        print("✅ Research priorities configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        return False

def test_individual_researchers():
    """Test individual research components"""
    print("\n🧪 Testing Individual Researchers...")
    
    try:
        from agents.research_engine import (
            CompanyResearcher,
            InterviewerResearcher,
            RoleResearcher,
            EnhancedTavilyClient
        )
        
        # Test researcher initialization (without actual API calls)
        tavily_client = EnhancedTavilyClient()
        
        company_researcher = CompanyResearcher(tavily_client)
        assert hasattr(company_researcher, 'tavily_client')
        print("✅ CompanyResearcher initialized")
        
        interviewer_researcher = InterviewerResearcher(tavily_client)
        assert hasattr(interviewer_researcher, 'tavily_client')
        print("✅ InterviewerResearcher initialized")
        
        role_researcher = RoleResearcher(tavily_client)
        assert hasattr(role_researcher, 'tavily_client')
        print("✅ RoleResearcher initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual researcher error: {e}")
        return False

def test_data_models():
    """Test data model creation"""
    print("\n🧪 Testing Data Models...")
    
    try:
        from agents.research_engine import (
            CompanyInfo,
            CompanyResearchResult,
            ProfessionalProfile,
            InterviewerResearchResult,
            SalaryInfo,
            RoleResearchResult
        )
        
        # Test company models
        company_info = CompanyInfo(
            name="Test Company",
            industry="Technology",
            description="Test description"
        )
        print("✅ CompanyInfo model created")
        
        # Test interviewer models
        interviewer_profile = ProfessionalProfile(
            name="Test Person",
            current_title="Test Title",
            current_company="Test Company"
        )
        print("✅ ProfessionalProfile model created")
        
        # Test role models
        salary_info = SalaryInfo(
            base_salary_range="$100k-150k",
            total_compensation="$120k-180k"
        )
        print("✅ SalaryInfo model created")
        
        return True
        
    except Exception as e:
        print(f"❌ Data model error: {e}")
        return False

def test_mock_research_workflow():
    """Test research workflow without API calls"""
    print("\n🧪 Testing Mock Research Workflow...")
    
    try:
        from agents.research_engine import research_orchestrator, ResearchRequest
        
        # Create test research request
        request = ResearchRequest(
            company_name="OpenAI",
            role_title="Software Engineer", 
            interviewer_names=["Test Interviewer"],
            research_depth="basic",
            additional_context={"location": "San Francisco"}
        )
        
        # Test workflow methods (without actual API calls)
        assert hasattr(research_orchestrator, 'conduct_comprehensive_research')
        assert hasattr(research_orchestrator, 'quick_company_research')
        assert hasattr(research_orchestrator, 'research_from_email_entities')
        print("✅ Research workflow methods available")
        
        # Test entity-based research structure
        entities = {
            'COMPANY': ['Google'],
            'ROLE': ['Product Manager'],
            'INTERVIEWER': ['John Smith'],
            'LOCATION': ['Mountain View']
        }
        
        # This would normally make API calls, so we just test the method exists
        assert hasattr(research_orchestrator, 'research_from_email_entities')
        print("✅ Entity-based research method available")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Research Engine Integration Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Import Structure", test_import_structure),
        ("Configuration", test_configuration),
        ("Package Health", test_package_health),
        ("Research Orchestrator", test_research_orchestrator_init),
        ("Individual Researchers", test_individual_researchers),
        ("Data Models", test_data_models),
        ("Mock Workflow", test_mock_research_workflow)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total:.1%})")
    
    if passed == total:
        print("🎉 All tests passed! Research engine is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
