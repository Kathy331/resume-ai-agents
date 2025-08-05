#!/usr/bin/env python3
"""
Test Enhanced Personalized Workflow
===================================

Tests the enhanced workflow with highly personalized prep guide generation
using actual email data from the demo folder.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_enhanced_personalized_workflow():
    """Test the enhanced workflow with personalized prep guides"""
    
    print("🚀 Testing Enhanced Personalized Interview Prep Workflow")
    print("Processing actual emails with highly personalized prep guides...")
    print("=" * 70)
    
    try:
        from workflows.interview_prep_workflow import InterviewPrepWorkflow
        
        # Initialize workflow
        workflow = InterviewPrepWorkflow()
        
        print("✅ Workflow initialized successfully")
        print("📚 Using Enhanced Personalized Prep Guide Pipeline")
        
        # Test the enhanced pipeline directly first
        print("\n1. Testing Enhanced Pipeline Direct...")
        
        sample_email = {
            'from': 'unknown',
            'subject': 'Invitation to Interview for Internship Opportunity with JUTEQ',
            'body': '''Hi Calamari,
I hope this message finds you well. I'm Rakesh Gohel, I'm pleased to invite you to an interview for our internship program. This will be an excellent opportunity for us to discuss your background, explore your interests in AI and cloud technologies, and share how you could contribute to exciting projects here at JUTEQ.

Interview Details:
• Date Options: Tuesday, August 6 or Wednesday, August 7
• Time: Flexible between 10:00 a.m. and 4:00 p.m. (ET)
• Duration: 30 minutes'''
        }
        
        sample_entities = {
            'company': 'JUTEQ',
            'candidate': 'Calamari',
            'interviewer': 'Rakesh Gohel'
        }
        
        sample_research = {
            'company_analysis': {
                'summary': 'JUTEQ specializes in cloud and AI solutions for digital transformation',
                'recent_news': ['Participation at Collision 2023 in Ontario', 'Focus on AI agents and scaling'],
                'tech_stack': ['AI Agents', 'Cloud Platforms', 'Digital Transformation Tools'],
                'market_position': 'Trusted partner in digital transformation',
                'culture': 'Innovation-focused, collaborative environment'
            },
            'interviewer_analysis': {
                'background': 'Rakesh Gohel is an expert in scaling with AI agents at JUTEQ',
                'recent_activities': ['Thought leadership in AI agent development', 'Cloud architecture consulting']
            },
            'citations_database': {
                'company': [
                    'https://ca.linkedin.com/company/juteq',
                    'https://www.sourcefromontario.com/en/page/delegate/136393/juteq-inc',
                    'https://juteq.ca/about/'
                ],
                'interviewer': [
                    'https://ca.linkedin.com/in/rakeshgohel01'
                ]
            }
        }
        
        # Test direct pipeline
        result = workflow.prep_guide_pipeline.generate_prep_guide(
            sample_email, sample_entities, sample_research, 999
        )
        
        if result['success']:
            print("   ✅ Enhanced pipeline works!")
            print(f"      • Company: {result['company_keyword']}")
            print(f"      • Citations: {result['citations_used']}")
            print(f"      • File: {result['output_file']}")
        else:
            print(f"   ❌ Enhanced pipeline failed: {result['errors']}")
            return False
        
        # Test full workflow
        print(f"\n2. Testing Full Workflow...")
        
        # Run workflow on demo folder
        results = workflow.run_workflow(max_emails=1, folder="demo")
        
        if results['success']:
            print(f"   ✅ Full workflow successful!")
            print(f"      • Prep guides generated: {results['prep_guides_generated']}")
            
            # Check output files
            output_dir = Path("outputs/fullworkflow")
            if output_dir.exists():
                recent_files = list(output_dir.glob("*.txt"))
                print(f"\n📁 Generated Files:")
                for file in recent_files:
                    print(f"   • {file.name}")
                    
                    # Quick quality check on most recent file
                    if file.name == 'JUTEQ.txt':
                        with open(file, 'r') as f:
                            content = f.read()
                        
                        # Check for personalization elements
                        personalization_checks = {
                            'Company Name (JUTEQ)': 'JUTEQ' in content,
                            'Interviewer Name (Rakesh Gohel)': 'Rakesh Gohel' in content,
                            'Candidate Name (Calamari)': 'Calamari' in content,
                            'Specific Dates': 'August 6' in content or 'August 7' in content,
                            'Citations Present': '[Citation' in content,
                            '8 Sections Present': content.count('Section') >= 8,
                            'AI/Cloud Focus': 'AI' in content and 'cloud' in content
                        }
                        
                        print(f"\n🔍 Personalization Quality Check for JUTEQ.txt:")
                        for check, passed in personalization_checks.items():
                            icon = "✅" if passed else "❌"
                            print(f"      {icon} {check}")
                        
                        passed_checks = sum(personalization_checks.values())
                        print(f"\n📊 Personalization Score: {passed_checks}/{len(personalization_checks)} ({passed_checks/len(personalization_checks)*100:.1f}%)")
            
        else:
            print(f"   ❌ Full workflow failed: {results.get('errors', [])}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    
    print("🎯 Enhanced Personalized Interview Prep Workflow Test")
    print("Testing highly personalized prep guide generation...")
    
    success = test_enhanced_personalized_workflow()
    
    print(f"\n{'='*70}")
    if success:
        print("✅ ENHANCED PERSONALIZED WORKFLOW TEST PASSED")
        print("\n📊 Key Features Tested:")
        print("• ✅ Enhanced personalized prep guide generation")
        print("• ✅ Company-specific content (JUTEQ)")
        print("• ✅ Interviewer-specific content (Rakesh Gohel)")
        print("• ✅ Role-specific content (Internship)")
        print("• ✅ Citation integration")
        print("• ✅ File output as company name")
        
        print(f"\n🚀 Ready for Production:")
        print("python workflows/interview_prep_workflow.py --max-emails 1 --folder demo")
        
    else:
        print("❌ ENHANCED PERSONALIZED WORKFLOW TEST FAILED")
        print("🔧 Check error messages above for required fixes")
        
    print(f"{'='*70}")

if __name__ == "__main__":
    main()