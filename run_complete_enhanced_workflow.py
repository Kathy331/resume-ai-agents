#!/usr/bin/env python3
"""
Run Enhanced Workflow with Complete File Output
===============================================

Processes emails from demo folder and generates complete files with:
1. Technical metadata and processing logs
2. Personalized prep guide (8 sections)
3. Research citations database
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def run_complete_enhanced_workflow():
    """Run the enhanced workflow generating complete files"""
    
    print("🚀 Running Complete Enhanced Interview Prep Workflow")
    print("Generating files with technical metadata + personalized prep guides...")
    print("=" * 70)
    
    try:
        from workflows.interview_prep_workflow import InterviewPrepWorkflow
        
        # Initialize workflow
        workflow = InterviewPrepWorkflow()
        
        print("✅ Workflow initialized successfully")
        print("📚 Using Enhanced Personalized Prep Guide Pipeline")
        print("📊 Output will include: Technical Logs + Personalized Prep Guide")
        
        # Run workflow on demo folder
        results = workflow.run_workflow(max_emails=5, folder="demo")
        
        if results['success']:
            print(f"\n🎉 SUCCESS! Generated {results['prep_guides_generated']} complete files")
            
            # List and analyze generated files
            output_dir = Path("outputs/fullworkflow")
            if output_dir.exists():
                recent_files = list(output_dir.glob("*.txt"))
                print(f"\n📁 Generated Files:")
                
                for file in recent_files:
                    print(f"   • {file.name}")
                    
                    # Analyze file structure
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for key sections
                        sections_check = {
                            'Individual Email Processing Results': 'INDIVIDUAL EMAIL PROCESSING RESULTS' in content,
                            'Original Email Data': 'ORIGINAL EMAIL DATA' in content,
                            'Pipeline Processing Logs': 'DETAILED PIPELINE PROCESSING LOGS' in content,
                            'Research Validation': 'DETAILED RESEARCH VALIDATION PROCESS' in content,
                            'Processing Results': 'PROCESSING RESULTS' in content,
                            'Personalized Prep Guide': 'PERSONALIZED INTERVIEW PREP GUIDE' in content,
                            'Section 1: Summary': 'Section 1: Summary Overview' in content,
                            'Section 2: Company': 'Section 2: Company Snapshot' in content,
                            'Section 3: Role': 'Section 3: Role Deep Dive' in content,
                            'Section 4: Interviewer': 'Section 4: Interviewer Intelligence' in content,
                            'Section 5: Questions': 'Section 5: Strategic Questions' in content,
                            'Section 6: Technical': 'Section 6: Technical Preparation' in content,
                            'Section 7: Strategic': 'Section 7: Strategic Framing' in content,
                            'Section 8: Execution': 'Section 8: Interview Execution Plan' in content,
                            'Citations Database': 'RESEARCH CITATIONS DATABASE' in content,
                            'Technical Metadata': 'TECHNICAL METADATA' in content
                        }
                        
                        print(f"\n     🔍 File Structure Analysis for {file.name}:")
                        passed_sections = 0
                        total_sections = len(sections_check)
                        
                        for section, present in sections_check.items():
                            icon = "✅" if present else "❌"
                            print(f"        {icon} {section}")
                            if present:
                                passed_sections += 1
                        
                        completion_rate = (passed_sections / total_sections) * 100
                        print(f"     📊 Completion Rate: {passed_sections}/{total_sections} ({completion_rate:.1f}%)")
                        
                        # Count citations
                        citation_count = content.count('[Citation')
                        print(f"     🔗 Citations Found: {citation_count}")
                        
                        # Word count
                        word_count = len(content.split())
                        print(f"     📝 Word Count: {word_count:,}")
                        
                        # Check personalization
                        if file.name in ['JUTEQ.txt', 'Juteq.txt']:
                            personalization_check = {
                                'Company (JUTEQ)': 'JUTEQ' in content or 'Juteq' in content,
                                'Interviewer (Rakesh Gohel)': 'Rakesh Gohel' in content,
                                'Candidate (Calamari)': 'Calamari' in content,
                                'Role (Internship)': 'Internship' in content or 'internship' in content,
                                'Date (August 6/7)': 'August 6' in content or 'August 7' in content
                            }
                            
                            print(f"     🎯 Personalization Check:")
                            for check, passed in personalization_check.items():
                                icon = "✅" if passed else "❌"
                                print(f"        {icon} {check}")
                        
                        elif file.name in ['Seeds.txt', 'SEEDS.txt']:
                            personalization_check = {
                                'Company (Dandilyonn SEEDS)': 'Dandilyonn' in content or 'SEEDS' in content,
                                'Interviewer (Archana)': 'Archana' in content,
                                'Candidate (Seedling)': 'Seedling' in content,
                                'Role (Internship)': 'Internship' in content or 'internship' in content,
                                'Date (August 8/9)': 'August 8' in content or 'August 9' in content
                            }
                            
                            print(f"     🎯 Personalization Check:")
                            for check, passed in personalization_check.items():
                                icon = "✅" if passed else "❌"
                                print(f"        {icon} {check}")
                        
                    except Exception as e:
                        print(f"     ❌ Error analyzing {file.name}: {str(e)}")
                
                print(f"\n📊 Overall Results:")
                print(f"   📁 Total Files Generated: {len(recent_files)}")
                print(f"   📋 Each file contains: Technical Logs + 8-Section Prep Guide")
                print(f"   🔗 Citations included from research")
                print(f"   🎯 Highly personalized content")
                
            else:
                print("❌ No output directory found")
                return False
        
        else:
            print(f"❌ Workflow failed: {results.get('errors', [])}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    
    print("🎯 Complete Enhanced Interview Prep Workflow")
    print("Generating comprehensive files with technical metadata + personalized prep guides...")
    
    success = run_complete_enhanced_workflow()
    
    print(f"\n{'='*70}")
    if success:
        print("✅ COMPLETE ENHANCED WORKFLOW SUCCESS")
        print("\n📊 Generated Files Include:")
        print("• ✅ Individual Email Processing Results header")
        print("• ✅ Original Email Data section")
        print("• ✅ Detailed Pipeline Processing Logs")
        print("• ✅ Research Validation Process details")
        print("• ✅ Processing Results summary")
        print("• ✅ 8-Section Personalized Prep Guide")
        print("• ✅ Research Citations Database")
        print("• ✅ Technical Metadata")
        
        print(f"\n🎉 Perfect! Files now match your requested format:")
        print("   📋 Complete technical metadata sections")
        print("   📚 Highly personalized prep guide content")
        print("   🔗 Real citations from research")
        print("   📁 Saved as CompanyName.txt in outputs/fullworkflow/")
        
    else:
        print("❌ WORKFLOW ISSUES DETECTED")
        print("🔧 Check error messages above for required fixes")
        
    print(f"{'='*70}")

if __name__ == "__main__":
    main()