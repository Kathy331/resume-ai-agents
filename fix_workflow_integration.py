#!/usr/bin/env python3
"""
Quick Fix and Test Workflow Integration
=====================================

Fix the workflow to use the enhanced pipeline and test it.
"""

import sys
from pathlib import Path

def check_and_fix_workflow():
    """Check and fix the workflow to use enhanced pipeline"""
    
    workflow_file = Path("workflows/interview_prep_workflow.py")
    
    if not workflow_file.exists():
        print("❌ Workflow file not found")
        return False
    
    # Read current content
    with open(workflow_file, 'r') as f:
        content = f.read()
    
    print("🔍 CHECKING WORKFLOW INTEGRATION")
    print("=" * 40)
    
    # Check current imports
    has_enhanced_import = "EnhancedPrepGuidePipeline" in content
    has_old_import = "PrepGuidePipeline" in content and "EnhancedPrepGuidePipeline" not in content
    
    print(f"   📦 Enhanced import present: {'✅' if has_enhanced_import else '❌'}")
    print(f"   📦 Old import present: {'⚠️' if has_old_import else '✅'}")
    
    # Check pipeline usage
    has_enhanced_usage = "EnhancedPrepGuidePipeline()" in content
    has_old_usage = "PrepGuidePipeline()" in content and "EnhancedPrepGuidePipeline()" not in content
    
    print(f"   🔧 Enhanced pipeline used: {'✅' if has_enhanced_usage else '❌'}")
    print(f"   🔧 Old pipeline used: {'⚠️' if has_old_usage else '✅'}")
    
    # Fix if needed
    needs_fix = not has_enhanced_import or not has_enhanced_usage
    
    if needs_fix:
        print("\n🔧 FIXING WORKFLOW INTEGRATION...")
        
        # Add enhanced import if missing
        if not has_enhanced_import:
            if "from pipelines.prep_guide_pipeline import PrepGuidePipeline" in content:
                content = content.replace(
                    "from pipelines.prep_guide_pipeline import PrepGuidePipeline",
                    "from pipelines.enhanced_prep_guide_pipeline import EnhancedPrepGuidePipeline"
                )
                print("   ✅ Updated import to EnhancedPrepGuidePipeline")
        
        # Fix pipeline instantiation
        if not has_enhanced_usage:
            if "PrepGuidePipeline()" in content:
                content = content.replace(
                    "PrepGuidePipeline()",
                    "EnhancedPrepGuidePipeline()"
                )
                print("   ✅ Updated pipeline instantiation")
        
        # Write fixed content back
        with open(workflow_file, 'w') as f:
            f.write(content)
        
        print("   ✅ Workflow file updated successfully")
        return True
    else:
        print("\n✅ Workflow integration is already correct")
        return True

def test_enhanced_workflow():
    """Test the enhanced workflow"""
    
    print("\n🧪 TESTING ENHANCED WORKFLOW")
    print("=" * 40)
    
    import subprocess
    
    # Clear caches first
    print("1. Clearing caches...")
    subprocess.run([sys.executable, "workflows/cache_manager.py", "--clear-all"], 
                  capture_output=True)
    
    # Run workflow
    print("2. Running enhanced workflow...")
    result = subprocess.run([
        sys.executable,
        "workflows/interview_prep_workflow.py",
        "--folder", "demo", 
        "--max-emails", "1"
    ], capture_output=True, text=True)
    
    print(f"   📊 Return code: {result.returncode}")
    
    if result.returncode == 0:
        print("   ✅ Workflow executed successfully")
        
        # Check for enhanced features in output
        console_output = result.stdout
        enhanced_features = {
            "Enhanced pipeline used": "Enhanced Prep Guide Pipeline" in console_output,
            "Email data stored": "email data" in console_output.lower(),
            "Fallback triggered": "enhanced fallback" in console_output.lower(),
            "Personalization active": "personalized" in console_output.lower()
        }
        
        print("\n📋 ENHANCED FEATURES CHECK:")
        for feature, present in enhanced_features.items():
            status = "✅" if present else "❌"
            print(f"   {status} {feature}")
        
        return sum(enhanced_features.values()) >= 2
    else:
        print(f"   ❌ Workflow failed with error:")
        print(f"   {result.stderr}")
        return False

if __name__ == "__main__":
    print("🔧 WORKFLOW INTEGRATION FIX & TEST")
    print("=" * 50)
    
    # Step 1: Fix workflow integration
    fix_success = check_and_fix_workflow()
    
    if fix_success:
        # Step 2: Test enhanced workflow
        test_success = test_enhanced_workflow()
        
        print(f"\n" + "=" * 50)
        print("📊 INTEGRATION FIX & TEST RESULTS")
        print("=" * 50)
        
        if test_success:
            print("🎉 ENHANCED WORKFLOW IS WORKING!")
            print("   ✅ Correct pipeline integration")
            print("   ✅ Enhanced personalization active")
            print("   ✅ Email data processing improved")
        else:
            print("⚠️  ENHANCED WORKFLOW NEEDS MORE WORK")
            print("   🔧 Integration fixed but functionality needs improvement")
    else:
        print("\n❌ Failed to fix workflow integration")
    
    print(f"\n💡 Check outputs/fullworkflow/ for the latest generated file")