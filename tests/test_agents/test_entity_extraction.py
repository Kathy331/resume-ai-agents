#!/usr/bin/env python3
"""
Entity Extraction Test Suite

Tests for improved entity extraction including:
- Candidate name extraction (without greetings)
- Company name extraction (avoiding platform tools)
- Complete pipeline integration tests

Usage:
    python tests/test_agents/test_entity_extraction.py
"""

import asyncio
import sys
import os
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from agents.entity_extractor.agent import EntityExtractor
from workflows.enhanced_email_pipeline import EnhancedEmailPipeline
from shared.models import AgentInput


def print_header(title: str, char: str = "=", width: int = 60):
    """Print a formatted header"""
    print(f"\n{char * width}")
    print(f"🧪 {title}")
    print(f"{char * width}")


def print_subheader(title: str, char: str = "-", width: int = 40):
    """Print a formatted subheader"""
    print(f"\n{char * width}")
    print(f"📋 {title}")
    print(f"{char * width}")


def print_test_result(test_name: str, expected: List[str], actual: List[str], success: bool = True):
    """Print formatted test result"""
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    print(f"   Expected: {expected}")
    print(f"   Actual:   {actual}")
    if expected == actual:
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL")
    print()


async def test_candidate_extraction():
    """Test candidate name extraction without greetings"""
    print_header("CANDIDATE EXTRACTION TESTS")
    
    extractor = EntityExtractor({})
    
    test_cases = [
        {
            'name': 'Hello Seedling (should extract: Seedling)',
            'text': 'Hello Seedling, we are excited to invite you for an interview.',
            'expected_candidates': ['Seedling']
        },
        {
            'name': 'Hi Calamari (should extract: Calamari)',
            'text': 'Hi Calamari, invitation for internship opportunity.',
            'expected_candidates': ['Calamari']
        },
        {
            'name': 'Dear John (should extract: John)',
            'text': 'Dear John, your interview is scheduled for tomorrow.',
            'expected_candidates': ['John']
        },
        {
            'name': 'Hi Engineering (should extract: nothing)',
            'text': 'Hi Engineering, this should not match as it\'s a department.',
            'expected_candidates': []
        },
        {
            'name': 'Hello Team (should extract: nothing)',
            'text': 'Hello Team, this should not match as it\'s generic.',
            'expected_candidates': []
        },
        {
            'name': 'Hey Alex (should extract: Alex)',
            'text': 'Hey Alex, looking forward to our conversation.',
            'expected_candidates': ['Alex']
        },
        {
            'name': 'Real JUTEQ email (should extract: Calamari)',
            'text': '''Hi Calamari,

I hope this message finds you well. I'm Rakesh Gohel, I'm pleased to invite you to an interview for our internship program. This will be an excellent opportunity for us to discuss your background, explore your interests in AI and cloud technologies, and share how you could contribute to exciting projects here at JUTEQ.

Interview Details:
Date Options: Tuesday, August 6 or Wednesday, August 7
Time: Flexible between 10:00 a.m. and 4:00 p.m. (ET)
Duration: 30 minutes
Format: Virtual via Zoom (link to be provided after scheduling)

Our discussion will focus on your technical skills, problem-solving approach, and how you envision leveraging AI and cloud-native platforms in real-world solutions.

Please reply with your preferred date and time slot by end of day Friday, August 2, so we can confirm the schedule.

Looking forward to learning more about your passion and ambitions in technology.

Best regards,
Rakesh Gohel
Founder & CEO, JUTEQ''',
            'expected_candidates': ['Calamari']
        }
    ]
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 Test {i}: {test_case['name']}")
        
        agent_input = AgentInput(data={'text': test_case['text']})
        result = await extractor.execute(agent_input)
        
        if result.success:
            actual_candidates = result.data.get('CANDIDATE', [])
            expected_candidates = test_case['expected_candidates']
            
            success = actual_candidates == expected_candidates
            results.append(success)
            
            print(f"   Text: \"{test_case['text'][:50]}...\"")
            print(f"   Expected: {expected_candidates}")
            print(f"   Actual:   {actual_candidates}")
            print(f"   Result:   {'✅ PASS' if success else '❌ FAIL'}")
        else:
            print(f"   ❌ ERROR: {result.errors}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"📊 CANDIDATE EXTRACTION SUMMARY: {passed}/{total} tests passed")
    return results


async def test_company_extraction():
    """Test company name extraction avoiding platform tools"""
    print_header("COMPANY EXTRACTION TESTS")
    
    extractor = EntityExtractor({})
    
    test_cases = [
        {
            'name': 'PixelWave company (should extract: PixelWave)',
            'text': 'Interview for Frontend Engineer at PixelWave scheduled via Zoom.',
            'expected_companies': ['PixelWave']
        },
        {
            'name': 'SEEDS company with Google Meet (should extract: SEEDS)',
            'text': 'Interview with Google Meet for internship at SEEDS company.',
            'expected_companies': ['SEEDS']
        },
        {
            'name': 'JUTEQ opportunity (should extract: JUTEQ)',
            'text': 'Invitation for internship opportunity with JUTEQ.',
            'expected_companies': ['JUTEQ']
        },
        {
            'name': 'Only Zoom platform (should extract: nothing)',
            'text': 'Your interview will be conducted via Zoom only.',
            'expected_companies': []
        },
        {
            'name': 'With Google Meet only (should extract: nothing)',
            'text': 'We will meet with Google Meet for the discussion.',
            'expected_companies': []
        }
    ]
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 Test {i}: {test_case['name']}")
        
        agent_input = AgentInput(data={'text': test_case['text']})
        result = await extractor.execute(agent_input)
        
        if result.success:
            actual_companies = result.data.get('COMPANY', [])
            expected_companies = test_case['expected_companies']
            
            success = actual_companies == expected_companies
            results.append(success)
            
            print(f"   Text: \"{test_case['text'][:50]}...\"")
            print(f"   Expected: {expected_companies}")
            print(f"   Actual:   {actual_companies}")
            print(f"   Result:   {'✅ PASS' if success else '❌ FAIL'}")
        else:
            print(f"   ❌ ERROR: {result.errors}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"📊 COMPANY EXTRACTION SUMMARY: {passed}/{total} tests passed")
    return results


async def test_complete_pipeline():
    """Test complete pipeline with realistic email examples"""
    print_header("COMPLETE PIPELINE INTEGRATION TESTS")
    
    pipeline = EnhancedEmailPipeline()
    
    test_emails = [
        {
            'id': 'test_pixelwave',
            'subject': 'Interview for Frontend Engineer at PixelWave',
            'body': '''Hi John,

We are excited to invite you for an interview for the Frontend Engineer position at PixelWave.

The interview will be conducted via Zoom on August 10, 2025 at 2:00 PM.

Best regards,
PixelWave Recruiting Team

https://calendar.google.com/calendar/whatever
Reply for user@example.com
            ''',
            'sender': 'recruiting@pixelwave.com',
            'expected': {
                'candidate': 'John',
                'company': 'PixelWave', 
                'role': 'Frontend Engineer',
                'classification': 'Interview_invite'
            }
        },
        {
            'id': 'test_seeds',
            'subject': '🌱 SEEDS Internship Interview Invitation – Let\'s Chat!',
            'body': '''Hello Seedling,

We would like to invite you for a video interview with Google Meet for our internship program at SEEDS.

Interview Details:
- Date: Thursday, August 8, 2025
- Time: 3:00 PM EST
- Duration: 30 minutes

Best,
SEEDS Team
            ''',
            'sender': 'careers@seeds.com',
            'expected': {
                'candidate': 'Seedling',
                'company': 'SEEDS',
                'role': None,  # Internship roles might not be extracted
                'classification': 'Interview_invite'
            }
        },
        {
            'id': 'test_juteq',
            'subject': 'Invitation to Interview for Internship Opportunity with JUTEQ',
            'body': '''Hi Calamari,

We are pleased to invite you for an internship opportunity with JUTEQ.

The interview will be on Tuesday, August 12, 2025.

Best regards,
JUTEQ Recruiting
            ''',
            'sender': 'hr@juteq.com',
            'expected': {
                'candidate': 'Calamari',
                'company': 'JUTEQ',
                'role': None,
                'classification': 'Interview_invite'
            }
        },
        {
            'id': 'test_real_juteq',
            'subject': 'Interview Invitation - JUTEQ Internship Program',
            'body': '''Hi Calamari,

I hope this message finds you well. I'm Rakesh Gohel, I'm pleased to invite you to an interview for our internship program. This will be an excellent opportunity for us to discuss your background, explore your interests in AI and cloud technologies, and share how you could contribute to exciting projects here at JUTEQ.

Interview Details:
Date Options: Tuesday, August 6 or Wednesday, August 7
Time: Flexible between 10:00 a.m. and 4:00 p.m. (ET)
Duration: 30 minutes
Format: Virtual via Zoom (link to be provided after scheduling)

Our discussion will focus on your technical skills, problem-solving approach, and how you envision leveraging AI and cloud-native platforms in real-world solutions.

Please reply with your preferred date and time slot by end of day Friday, August 2, so we can confirm the schedule.

Looking forward to learning more about your passion and ambitions in technology.

Best regards,
Rakesh Gohel
Founder & CEO, JUTEQ
Scaling with AI Agents | Cloud-Native Solutions | Agile Leadership
rakesh.gohel@juteq.com
            ''',
            'sender': 'rakesh.gohel@juteq.com',
            'expected': {
                'candidate': 'Calamari',
                'company': 'JUTEQ',
                'role': None,  # Internship program might not extract specific role
                'interviewer': 'Rakesh Gohel',
                'classification': 'Interview_invite'
            }
        }
    ]
    
    results = []
    
    for i, email in enumerate(test_emails, 1):
        print(f"📧 Email {i}: {email['subject'][:40]}...")
        print(f"   Sender: {email['sender']}")
        
        result = await pipeline.process_email(email)
        
        # Extract results
        classification = result.get('classification', {}).get('category', 'Unknown')
        entities_success = result.get('entities', {}).get('success', False)
        memory_updated = result.get('memory_updated', False)
        
        print(f"   📂 Classification: {classification}")
        print(f"   ✅ Entity Extraction: {'Success' if entities_success else 'Failed'}")
        print(f"   💾 Storage: {'Success' if memory_updated else 'Failed'}")
        
        # Detailed entity comparison
        if entities_success:
            entities = result['entities']['data']
            actual_candidate = entities.get('CANDIDATE', [None])[0]
            actual_company = entities.get('COMPANY', [None])[0]
            actual_role = entities.get('ROLE', [None])[0]
            actual_interviewer = entities.get('INTERVIEWER', [None])[0]
            
            expected = email['expected']
            
            print(f"   👤 Candidate: {actual_candidate} (expected: {expected['candidate']})")
            print(f"   🏢 Company: {actual_company} (expected: {expected['company']})")
            print(f"   💼 Role: {actual_role} (expected: {expected['role']})")
            
            # Show interviewer if expected
            if 'interviewer' in expected:
                print(f"   🎯 Interviewer: {actual_interviewer} (expected: {expected['interviewer']})")
            
            # Check if results match expectations
            candidate_match = actual_candidate == expected['candidate']
            company_match = actual_company == expected['company']
            role_match = actual_role == expected['role'] or (actual_role is None and expected['role'] is None)
            classification_match = classification == expected['classification']
            
            # Check interviewer if specified
            interviewer_match = True
            if 'interviewer' in expected:
                interviewer_match = actual_interviewer == expected['interviewer']
            
            overall_success = candidate_match and company_match and role_match and classification_match and interviewer_match
            
            print(f"   🎯 Overall Result: {'✅ PASS' if overall_success else '❌ FAIL'}")
            
            if not overall_success:
                print(f"      - Candidate: {'✅' if candidate_match else '❌'}")
                print(f"      - Company: {'✅' if company_match else '❌'}")
                print(f"      - Role: {'✅' if role_match else '❌'}")
                print(f"      - Classification: {'✅' if classification_match else '❌'}")
                if 'interviewer' in expected:
                    print(f"      - Interviewer: {'✅' if interviewer_match else '❌'}")
            
            results.append(overall_success)
        else:
            print(f"   ❌ Entity extraction failed")
            results.append(False)
        
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"📊 COMPLETE PIPELINE SUMMARY: {passed}/{total} tests passed")
    return results


async def run_all_tests():
    """Run all test suites"""
    print("🚀 STARTING ENTITY EXTRACTION TEST SUITE")
    print("=" * 60)
    
    # Run individual test suites
    candidate_results = await test_candidate_extraction()
    company_results = await test_company_extraction()
    pipeline_results = await test_complete_pipeline()
    
    # Overall summary
    print_header("FINAL TEST SUMMARY", "=", 60)
    
    total_candidate = len(candidate_results)
    passed_candidate = sum(candidate_results)
    
    total_company = len(company_results)
    passed_company = sum(company_results)
    
    total_pipeline = len(pipeline_results)
    passed_pipeline = sum(pipeline_results)
    
    overall_total = total_candidate + total_company + total_pipeline
    overall_passed = passed_candidate + passed_company + passed_pipeline
    
    print(f"📊 TEST RESULTS:")
    print(f"   🎭 Candidate Extraction: {passed_candidate}/{total_candidate} passed")
    print(f"   🏢 Company Extraction:   {passed_company}/{total_company} passed")
    print(f"   🔄 Complete Pipeline:    {passed_pipeline}/{total_pipeline} passed")
    print(f"   {'─' * 40}")
    print(f"   🎯 OVERALL:              {overall_passed}/{overall_total} passed")
    
    success_rate = (overall_passed / overall_total) * 100 if overall_total > 0 else 0
    print(f"   📈 Success Rate:         {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"   🎉 EXCELLENT! Entity extraction is working great!")
    elif success_rate >= 75:
        print(f"   ✅ GOOD! Minor improvements may be needed.")
    else:
        print(f"   ⚠️  NEEDS WORK! Significant improvements required.")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
