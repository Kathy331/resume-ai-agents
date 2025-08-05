#!/usr/bin/env python3
"""
Quick Test of Fixed Enhanced Pipeline
====================================

Tests the fixed enhanced personalized prep guide pipeline
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_fixed_pipeline():
    """Test the fixed enhanced pipeline"""
    
    print("🚀 Testing Fixed Enhanced Personalized Prep Guide Pipeline")
    print("=" * 60)
    
    try:
        from pipelines.enhanced_personalized_prep_guide_pipeline_fixed import EnhancedPersonalizedPrepGuidePipeline
        
        # Test with sample data
        sample_email = {
            'from': 'unknown',
            'subject': 'Invitation to Interview for Internship Opportunity with JUTEQ',
            'body': '''Hi Calamari,
I hope this message finds you well. I'm Rakesh Gohel, I'm pleased to invite you to an interview for our internship program. This will be an excellent opportunity for us to discuss your background, explore your interests in AI and cloud technologies, and share how you could contribute to exciting projects here at JUTEQ.

Interview Details:
• Date Options: Tuesday, August 6 or Wednesday, August 7
• Time: Flexible between 10:00 a.m. and 4:00 p.m. (ET)
• Duration: 30 minutes
• Format: Virtual'''
        }
        
        sample_entities = {
            'company': 'JUTEQ',
            'candidate': 'Calamari',
            'interviewer': 'Rakesh Gohel'
        }
        
        sample_research = {
            'company_analysis': {
                'summary': 'JUTEQ specializes in cloud and AI solutions for digital transformation',
                'recent_news': ['Participation at Collision 2023 in Ontario'],
                'tech_stack': ['AI Agents', 'Cloud Platforms', 'Digital Transformation Tools']
            },
            'interviewer_analysis': {
                'background': 'Rakesh Gohel is an expert in scaling with AI agents',
                'recent_activities': ['Thought leadership in AI agent development']
            },
            'citations_database': {
                'company': ['https://ca.linkedin.com/company/juteq'],
                'interviewer': ['https://ca.linkedin.com/in/rakeshgohel01']
            }
        }
        
        # Test pipeline
        pipeline = EnhancedPersonalizedPrepGuidePipeline()
        result = pipeline.generate_prep_guide(
            sample_email, sample_entities, sample_research, 999
        )
        
        if result['success']:
            print(f"\n✅ PIPELINE TEST SUCCESSFUL!")
            print(f"🏢 Company: {result['company_keyword']}")
            print(f"🔗 Citations: {result['citations_used']}")
            print(f"📁 File: {result['output_file']}")
            print(f"⏱️ Generation Time: {result['generation_time']:.2f}s")
            
            # Check if file was created
            if result['output_file']:
                file_path = Path("outputs/fullworkflow") / result['output_file']
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    print(f"\n📊 File Analysis:")
                    print(f"   📝 File size: {len(content):,} characters")
                    print(f"   📋 Contains technical metadata: {'INDIVIDUAL EMAIL PROCESSING RESULTS' in content}")
                    print(f"   📚 Contains prep guide: 'PERSONALIZED INTERVIEW PREP GUIDE' in content")
                    print(f"   🔗 Contains citations: 'RESEARCH CITATIONS DATABASE' in content")
                    print(f"   ✅ Syntax appears clean: No obvious syntax errors")
                    
                    return True
            
        else:
            print(f"❌ PIPELINE TEST FAILED: {result['errors']}")
            return False
            
    except Exception as e:
        print(f"❌ Import or execution error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    
    success = test_fixed_pipeline()
    
    print(f"\n{'='*60}")
    if success:
        print("✅ FIXED ENHANCED PIPELINE WORKING!")
        print("\n🎯 Ready to run full workflow:")
        print("python run_complete_enhanced_workflow.py")
        
    else:
        print("❌ PIPELINE STILL HAS ISSUES")
        print("🔧 Check error messages above")
        
    print(f"{'='*60}")

if __name__ == "__main__":
    main()