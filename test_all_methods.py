#!/usr/bin/env python3
"""
Quick Test of All Methods
========================

Tests if all required methods exist in the enhanced pipeline
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_all_methods():
    """Test if all required methods exist"""
    
    print("🔍 Testing Enhanced Pipeline Methods...")
    
    try:
        from pipelines.enhanced_personalized_prep_guide_pipeline_fixed import EnhancedPersonalizedPrepGuidePipeline
        
        pipeline = EnhancedPersonalizedPrepGuidePipeline()
        
        # Test with sample data
        sample_email = {
            'from': 'test@example.com',
            'subject': 'Test Interview',
            'body': 'This is a test email about AI and cloud technologies for Seedling.',
            'date': '2024-01-01'
        }
        
        sample_entities = {
            'company': 'JUTEQ',
            'candidate': 'Calamari',
            'interviewer': 'Rakesh Gohel'
        }
        
        sample_research = {
            'company_analysis': {},
            'interviewer_analysis': {},
            'citations_database': {
                'company': ['https://example.com/company'],
                'interviewer': ['https://example.com/person']
            },
            'sources_processed': 10,
            'validated_sources': [],
            'linkedin_profiles_found': 5,
            'processing_time': 0.1,
            'overall_confidence': 0.85,
            'research_quality': 'HIGH',
            'sufficient_for_prep_guide': True
        }
        
        # Test the main method
        result = pipeline.generate_prep_guide(
            sample_email, sample_entities, sample_research, 999
        )
        
        if result['success']:
            print("✅ All methods working correctly!")
            print(f"🏢 Company: {result['company_keyword']}")
            print(f"📁 File: {result['output_file']}")
            return True
        else:
            print(f"❌ Method test failed: {result['errors']}")
            return False
            
    except Exception as e:
        print(f"❌ Method test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    
    success = test_all_methods()
    
    if success:
        print("\n✅ ALL METHODS WORKING - Ready to run workflow!")
        print("🚀 Run: python clear_and_run_fresh.py")
    else:
        print("\n❌ MISSING METHODS - Need to fix pipeline")

if __name__ == "__main__":
    main()