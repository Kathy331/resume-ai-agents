#!/usr/bin/env python3
"""
Final Integration Test
====================

Test that the interview_prep_workflow produces the JUTEQ goal output.
"""

import subprocess
import sys
import time
from pathlib import Path

def test_final_integration():
    """Test that everything is working together"""
    
    print("🎯 FINAL INTEGRATION TEST FOR JUTEQ GOAL")
    print("=" * 50)
    
    # Step 1: Clear everything
    print("1. Clearing all caches and outputs...")
    subprocess.run([sys.executable, "workflows/cache_manager.py", "--clear-all"], 
                  capture_output=True)
    
    # Clear output directory
    output_dir = Path("outputs/fullworkflow")
    if output_dir.exists():
        for file in output_dir.glob("*.txt"):
            file.unlink()
    
    # Step 2: Run the workflow
    print("2. Running interview_prep_workflow...")
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
    
    if result.returncode != 0:
        print("❌ WORKFLOW FAILED!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    # Step 3: Check output against JUTEQ goal
    print("3. Analyzing output against JUTEQ goal...")
    
    if not output_dir.exists():
        print("   ❌ No output directory")
        return False
    
    txt_files = list(output_dir.glob("*.txt"))
    if not txt_files:
        print("   ❌ No output files generated")
        return False
    
    latest_file = max(txt_files, key=lambda p: p.stat().st_mtime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"   📄 Generated file: {latest_file.name}")
    print(f"   📊 File size: {len(content)} characters")
    
    # Test against JUTEQ goal specifications
    goal_tests = {
        # Section 1: Before Interview
        "Specific date options": "tuesday, august 6" in content.lower() and "wednesday, august 7" in content.lower(),
        "Specific time range": "10:00 a.m." in content.lower() and "4:00 p.m." in content.lower(),
        "Duration mentioned": "30" in content and "minute" in content.lower(),
        "Response deadline": "friday, august 2" in content.lower(),
        "Virtual/Zoom format": ("virtual" in content.lower() or "zoom" in content.lower()) and "test your zoom" in content.lower(),
        "AI/cloud discussion prep": "ai and cloud technologies" in content.lower(),
        
        # Section 2: Interviewer Background
        "Rakesh Gohel name": "rakesh gohel" in content.lower(),
        "AI/cloud expertise": "ai and cloud technologies" in content.lower() and "expertise" in content.lower(),
        "Scaling AI agents": "scaling" in content.lower() and ("ai agents" in content.lower() or "agents" in content.lower()),
        "LinkedIn profile": "rakeshgohel01" in content.lower(),
        
        # Section 3: Company Background
        "JUTEQ as tech company": "technology company" in content.lower() and "ai and cloud-native" in content.lower(),
        "DevOps solutions": "devops" in content.lower() or "cloud-native" in content.lower(),
        "Internship hiring": "internship" in content.lower() and "ai and cloud" in content.lower(),
        
        # Section 4: Technical Prep
        "JUTEQ internship program": "juteq internship program" in content.lower(),
        "Email reference": "mentioned in email" in content.lower() or "as mentioned" in content.lower(),
        "Cloud-native concepts": "cloud-native" in content.lower(),
        "AI project examples": "ai" in content.lower() and "projects" in content.lower(),
        
        # Section 5: Questions
        "Rakesh-specific questions": "what drew you" in content.lower() and "ai and cloud" in content.lower(),
        "Scaling approach question": "scaling" in content.lower() or "approach" in content.lower(),
        "Exciting projects question": "exciting projects" in content.lower(),
        "Intern success question": "success" in content.lower() and "intern" in content.lower(),
        
        # Section 6: Common Questions
        "AI/cloud experience question": "ai or cloud technologies" in content.lower(),
        "Learning approach question": "learning about a new" in content.lower(),
        "Interest description question": "describe your interest" in content.lower()
    }
    
    print("\n📋 JUTEQ GOAL COMPLIANCE TEST:")
    passed = 0
    critical_fails = []
    
    for test_name, result in goal_tests.items():
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
        else:
            # Mark critical failures
            if any(keyword in test_name.lower() for keyword in ["rakesh gohel", "date options", "juteq internship", "ai/cloud"]):
                critical_fails.append(test_name)
    
    success_rate = passed / len(goal_tests)
    print(f"\n🎯 JUTEQ GOAL COMPLIANCE: {success_rate:.1%} ({passed}/{len(goal_tests)})")
    
    if critical_fails:
        print(f"\n⚠️  CRITICAL FAILURES:")
        for fail in critical_fails:
            print(f"   ❌ {fail}")
    
    # Show actual sections
    if "## 1. before interview" in content:
        print("\n📅 ACTUAL BEFORE INTERVIEW SECTION:")
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
        print("\n👤 ACTUAL INTERVIEWER SECTION:")
        lines = content.split('\n')
        in_section = False
        for line in lines:
            if "## 2. interviewer background" in line.lower():
                in_section = True
            elif line.startswith("## 3."):
                in_section = False
            
            if in_section and line.strip():
                print(f"   {line}")
    
    return success_rate >= 0.8 and len(critical_fails) == 0

if __name__ == "__main__":
    success = test_final_integration()
    
    print(f"\n" + "=" * 60)
    print("📊 FINAL INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    if success:
        print("🎉 SUCCESS! JUTEQ GOAL ACHIEVED!")
        print("   ✅ All critical features working")
        print("   ✅ Specific email details extracted")
        print("   ✅ Real interviewer information")
        print("   ✅ Company-specific content")
        print("   ✅ Personalized questions and prep")
        print("\n📋 The interview_prep_workflow now produces the desired JUTEQ output!")
    else:
        print("⚠️  NEEDS MORE WORK")
        print("   🔧 Some critical features missing")
        print("   🔧 May need additional fixes")
    
    print(f"\n💡 Check outputs/fullworkflow/ for the actual generated content")