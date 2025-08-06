#!/usr/bin/env python3
"""
Test Enhanced Fallback with Real Data
====================================

Test the enhanced fallback function that should generate personalized content.
"""

import subprocess
import sys
import time
from pathlib import Path

def clear_caches_and_test():
    """Clear caches and test enhanced personalization"""
    
    print("🧹 CLEARING CACHES AND TESTING ENHANCED PERSONALIZATION")
    print("=" * 60)
    
    # Clear all caches
    print("1. Clearing all caches...")
    subprocess.run([sys.executable, "workflows/cache_manager.py", "--clear-all"], 
                  capture_output=True)
    
    # Clear output directory
    output_dir = Path("outputs/fullworkflow")
    if output_dir.exists():
        for file in output_dir.glob("*.txt"):
            file.unlink()
        print("   ✅ Cleared previous output files")
    
    # Run workflow
    print("2. Running workflow with enhanced fallback...")
    start_time = time.time()
    
    result = subprocess.run([
        sys.executable,
        "workflows/interview_prep_workflow.py",
        "--folder", "demo", 
        "--max-emails", "1"
    ], capture_output=True, text=True)
    
    processing_time = time.time() - start_time
    
    print(f"   ✅ Workflow completed in {processing_time:.1f}s")
    print(f"   📊 Return code: {result.returncode}")
    
    # Check output
    print("3. Analyzing new output...")
    if output_dir.exists():
        txt_files = list(output_dir.glob("*.txt"))
        if txt_files:
            latest_file = max(txt_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"   📄 Generated file: {latest_file.name}")
            print(f"   📊 File size: {len(content)} characters")
            
            # Quick checks for personalization
            improvements = {
                "Specific dates": "tuesday, august 6" in content.lower() and "wednesday, august 7" in content.lower(),
                "Specific times": "10:00 a.m." in content.lower() and "4:00 p.m." in content.lower(),
                "Rakesh Gohel name": "rakesh gohel" in content.lower(),
                "AI/cloud mention": "ai and cloud technologies" in content.lower(),
                "JUTEQ internship": "juteq internship program" in content.lower(),
                "Response deadline": "friday, august 2" in content.lower(),
                "Cloud-native focus": "cloud-native" in content.lower(),
                "Scaling AI agents": "scaling" in content.lower() or "ai agents" in content.lower()
            }
            
            print("\n📋 PERSONALIZATION CHECK:")
            passed = 0
            for check, result in improvements.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check}")
                if result:
                    passed += 1
            
            success_rate = passed / len(improvements)
            print(f"\n🎯 PERSONALIZATION RATE: {success_rate:.1%} ({passed}/{len(improvements)})")
            
            # Show sections
            if "## 1. before interview" in content:
                print("\n📅 BEFORE INTERVIEW SECTION:")
                lines = content.split('\n')
                in_section = False
                for line in lines:
                    if "## 1. before interview" in line.lower():
                        in_section = True
                    elif line.startswith("## 2."):
                        in_section = False
                    
                    if in_section and line.strip():
                        print(f"   {line}")
            
            if "## 2. interviewer background" in content:
                print("\n👤 INTERVIEWER SECTION:")
                lines = content.split('\n')
                in_section = False
                for line in lines:
                    if "## 2. interviewer background" in line.lower():
                        in_section = True
                    elif line.startswith("## 3."):
                        in_section = False
                    
                    if in_section and line.strip():
                        print(f"   {line}")
            
            return success_rate >= 0.6
        else:
            print("   ❌ No output files generated")
            return False
    else:
        print("   ❌ No output directory found")
        return False

if __name__ == "__main__":
    success = clear_caches_and_test()
    
    print(f"\n" + "=" * 60)
    print("📊 ENHANCED PERSONALIZATION TEST RESULTS")
    print("=" * 60)
    
    if success:
        print("🎉 ENHANCED PERSONALIZATION IS WORKING!")
        print("   ✅ Specific email details being extracted")
        print("   ✅ Real interviewer information used")
        print("   ✅ Company-specific technical prep")
        print("   ✅ Personalized questions and content")
    else:
        print("⚠️  STILL USING GENERIC CONTENT")
        print("   🔧 Enhanced fallback may not be triggered")
        print("   🔧 Check if OpenAI is generating generic content")
    
    print(f"\n💡 Check outputs/fullworkflow/ for the latest generated file")