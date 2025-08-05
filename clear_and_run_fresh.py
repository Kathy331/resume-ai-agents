#!/usr/bin/env python3
"""
Clear Everything and Run Interview Prep Workflow
===============================================

This script will:
1. Clear the OpenAI cache completely
2. Clear the memory database 
3. Run the interview prep workflow with fresh data
"""

import os
import sys
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def clear_openai_cache():
    """Clear OpenAI cache directory"""
    try:
        cache_dir = Path("cache/openai_cache")
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            print("✅ OpenAI cache cleared")
            return True
        else:
            print("ℹ️  OpenAI cache directory not found")
            return True
    except Exception as e:
        print(f"❌ Error clearing OpenAI cache: {e}")
        return False

def clear_memory_database():
    """Clear memory database"""
    try:
        memory_files = [
            "memory/interview_memory.json",
            "memory/processed_emails.json",
            "memory/company_research_cache.json"
        ]
        
        cleared_count = 0
        for memory_file in memory_files:
            memory_path = Path(memory_file)
            if memory_path.exists():
                memory_path.unlink()
                cleared_count += 1
                print(f"✅ Cleared {memory_file}")
        
        if cleared_count == 0:
            print("ℹ️  No memory database files found")
        else:
            print(f"✅ Cleared {cleared_count} memory database files")
        
        return True
    except Exception as e:
        print(f"❌ Error clearing memory database: {e}")
        return False

def clear_output_files():
    """Clear previous output files"""
    try:
        output_dir = Path("outputs/fullworkflow")
        if output_dir.exists():
            for file in output_dir.glob("*.txt"):
                file.unlink()
                print(f"✅ Cleared output file: {file.name}")
        return True
    except Exception as e:
        print(f"❌ Error clearing output files: {e}")
        return False

def run_interview_prep_workflow():
    """Run the interview prep workflow"""
    try:
        print("\n🚀 Running Interview Prep Workflow...")
        print("=" * 60)
        
        from workflows.interview_prep_workflow import InterviewPrepWorkflow
        
        # Set environment to disable caching for fresh results
        os.environ['DISABLE_OPENAI_CACHE'] = 'true'
        
        workflow = InterviewPrepWorkflow()
        results = workflow.run_workflow(max_emails=5, folder="demo")
        
        if results['success']:
            print(f"\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print(f"📊 Results:")
            print(f"   📥 Total Emails: {results['total_emails_fetched']}")
            print(f"   🎯 Interview Emails: {results['interview_emails_found']}")
            print(f"   📚 Prep Guides Generated: {results['prep_guides_generated']}")
            print(f"   ⏱️  Processing Time: {results['processing_time']:.2f}s")
            
            # Show generated files
            if results['prep_guides_generated'] > 0:
                print(f"\n📁 Generated Files:")
                output_dir = Path("outputs/fullworkflow")
                for file in output_dir.glob("*.txt"):
                    print(f"   ✅ {file.name}")
            
            return True
        else:
            print(f"\n❌ WORKFLOW FAILED!")
            print(f"   Errors: {results.get('errors', [])}")
            return False
            
    except Exception as e:
        print(f"❌ Error running workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    
    print("🧹 CLEARING EVERYTHING AND RUNNING FRESH WORKFLOW")
    print("=" * 60)
    
    # Step 1: Clear OpenAI cache
    print("\n1️⃣  Clearing OpenAI cache...")
    cache_cleared = clear_openai_cache()
    
    # Step 2: Clear memory database
    print("\n2️⃣  Clearing memory database...")
    memory_cleared = clear_memory_database()
    
    # Step 3: Clear previous output files
    print("\n3️⃣  Clearing previous output files...")
    outputs_cleared = clear_output_files()
    
    # Step 4: Run workflow if clearing was successful
    if cache_cleared and memory_cleared and outputs_cleared:
        print("\n✅ All clearing operations successful!")
        
        # Step 5: Run the workflow
        print("\n4️⃣  Running Interview Prep Workflow with fresh data...")
        workflow_success = run_interview_prep_workflow()
        
        print(f"\n{'='*60}")
        if workflow_success:
            print("🎊 COMPLETE SUCCESS!")
            print("\n📊 What was generated:")
            print("   ✅ Fresh OpenAI responses (no cache)")
            print("   ✅ New memory entries")
            print("   ✅ Complete technical metadata sections")
            print("   ✅ Personalized prep guide sections")
            print("   ✅ Real research citations in content")
            print("   ✅ Detailed pipeline processing logs")
            
            print(f"\n📁 Check outputs/fullworkflow/ for your files!")
        else:
            print("❌ WORKFLOW EXECUTION FAILED")
        print(f"{'='*60}")
        
    else:
        print("\n❌ Clearing operations failed - skipping workflow execution")

if __name__ == "__main__":
    main()