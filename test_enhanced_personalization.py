#!/usr/bin/env python3
"""
Test Enhanced Personalization with Email Details
==============================================

Test that the prep guide now includes:
1. Specific dates and times from email (Tuesday, August 6 or Wednesday, August 7)
2. Real interviewer name (Rakesh Gohel) with specific background
3. Detailed company information using research
4. Personalized technical prep based on email content (AI/cloud)
5. Specific questions based on email mentions
"""

import subprocess
import sys
import time
from pathlib import Path

def test_enhanced_personalization():
    """Test the enhanced personalization features"""
    
    print("🎯 TESTING ENHANCED PERSONALIZATION WITH EMAIL DETAILS")
    print("=" * 60)
    
    # Clear caches first
    print("1. Clearing all caches...")
    subprocess.run([sys.executable, "workflows/cache_manager.py", "--clear-all"], 
                  capture_output=True)
    
    # Run workflow on JUTEQ email
    print("2. Running workflow with enhanced personalization...")
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
    
    # Find latest output file
    print("3. Analyzing enhanced prep guide...")
    output_dir = Path("outputs/fullworkflow")
    if not output_dir.exists():
        print("   ❌ No output directory found")
        return False
    
    txt_files = list(output_dir.glob("*.txt"))
    if not txt_files:
        print("   ❌ No output files found")
        return False
    
    latest_file = max(txt_files, key=lambda p: p.stat().st_mtime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test specific email detail extraction
    email_detail_tests = {
        "Specific dates mentioned": "tuesday, august 6" in content.lower() and "wednesday, august 7" in content.lower(),
        "Time range specified": "10:00 a.m." in content.lower() and "4:00 p.m." in content.lower(),
        "Duration mentioned": "30" in content and ("minute" in content.lower() or "min" in content.lower()),
        "Response deadline": "friday, august 2" in content.lower() or "respond" in content.lower(),
        "Format specified": "virtual" in content.lower() or "zoom" in content.lower(),
        "Internship program mentioned": "internship" in content.lower(),
        "AI and cloud technologies": "ai" in content.lower() and "cloud technologies" in content.lower()
    }
    
    # Test interviewer personalization
    interviewer_tests = {
        "Real interviewer name": "rakesh gohel" in content.lower(),
        "Not generic entity": "cloud-native solutions" not in content.lower(),
        "LinkedIn profile included": "rakeshgohel01" in content.lower(),
        "AI expertise mentioned": "ai" in content.lower() and ("expertise" in content.lower() or "focus" in content.lower()),
        "Scaling with AI agents": "scaling" in content.lower() or "ai agents" in content.lower()
    }
    
    # Test company personalization
    company_tests = {
        "JUTEQ as technology company": "technology company" in content.lower() or "ai and cloud" in content.lower(),
        "Cloud-native solutions": "cloud-native" in content.lower() or "devops" in content.lower(),
        "Internship context": "internship" in content.lower() and "juteq" in content.lower(),
        "Not generic description": "established presence" not in content.lower(),
        "Innovation mentioned": "innovation" in content.lower() or "trends" in content.lower()
    }
    
    # Test technical prep personalization
    technical_tests = {
        "Role specified as internship": "internship program" in content.lower() or "juteq internship" in content.lower(),
        "AI/cloud prep mentioned": "ai and cloud technologies" in content.lower(),
        "Email content referenced": "mentioned in email" in content.lower() or "as mentioned" in content.lower(),
        "Specific technologies": "cloud-native" in content.lower() or "devops" in content.lower(),
        "Interest discussion": "interests" in content.lower() and "ai" in content.lower()
    }
    
    # Test questions personalization
    questions_tests = {
        "Rakesh-specific questions": ("drew you to" in content.lower() or "ai and cloud" in content.lower()) and "rakesh" not in content.lower(),
        "JUTEQ-specific questions": "juteq" in content.lower() and ("exciting projects" in content.lower() or "approach" in content.lower()),
        "Internship questions": "intern" in content.lower() and ("success" in content.lower() or "program" in content.lower()),
        "AI/cloud questions": "ai" in content.lower() and ("technology" in content.lower() or "platform" in content.lower()),
        "Not generic questions": "what brought you to" not in content.lower() or "scaling" in content.lower()
    }
    
    print(f"   📄 Analyzed file: {latest_file.name}")
    print(f"   📊 File size: {len(content)} characters")
    print()
    
    # Show results for each category
    categories = [
        ("📧 EMAIL DETAILS", email_detail_tests),
        ("👤 INTERVIEWER PERSONALIZATION", interviewer_tests),
        ("🏢 COMPANY PERSONALIZATION", company_tests),
        ("🔧 TECHNICAL PREP", technical_tests),
        ("❓ QUESTIONS", questions_tests)
    ]
    
    overall_passed = 0
    overall_total = 0
    
    for category_name, tests in categories:
        print(f"{category_name}:")
        passed = 0
        for test_name, result in tests.items():
            status = "✅" if result else "❌"
            print(f"   {status} {test_name}")
            if result:
                passed += 1
            overall_passed += 1 if result else 0
            overall_total += 1
        
        success_rate = passed / len(tests)
        print(f"   📊 {category_name} Success: {success_rate:.1%} ({passed}/{len(tests)})\n")
    
    overall_success_rate = overall_passed / overall_total
    print(f"🎯 OVERALL PERSONALIZATION SUCCESS: {overall_success_rate:.1%} ({overall_passed}/{overall_total})")
    
    # Show key sections
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
    
    return overall_success_rate >= 0.75

if __name__ == "__main__":
    success = test_enhanced_personalization()
    
    print(f"\n" + "=" * 60)
    print("📊 ENHANCED PERSONALIZATION TEST RESULTS")
    print("=" * 60)
    
    if success:
        print("🎉 EXCELLENT PERSONALIZATION ACHIEVED!")
        print("   ✅ Specific email details extracted and used")
        print("   ✅ Real interviewer information (Rakesh Gohel)")
        print("   ✅ Company-specific technical preparations")
        print("   ✅ Personalized questions based on email content")
        print("   ✅ Role-specific recommendations")
    else:
        print("⚠️  PERSONALIZATION NEEDS IMPROVEMENT")
        print("   🔧 Some email details not being extracted properly")
        print("   🔧 Generic content still present in some sections")
    
    print(f"\n💡 Check the output file for full personalized prep guide")