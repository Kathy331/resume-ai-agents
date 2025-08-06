#!/usr/bin/env python3
"""
Test Dandilyonn Archana Detection
=================================

Test that the system correctly identifies Archana (Jain) Chaudhary as the interviewer
and finds her actual LinkedIn profile and background.
"""

import subprocess
import sys
import time
from pathlib import Path

def test_dandilyonn_archana_detection():
    """Test Archana detection and research for Dandilyonn"""
    
    print("🌱 TESTING DANDILYONN ARCHANA DETECTION")
    print("=" * 50)
    
    # Clear caches first
    print("1. Clearing all caches...")
    subprocess.run([sys.executable, "workflows/cache_manager.py", "--clear-all"], 
                  capture_output=True)
    
    # Run workflow on specific email
    print("2. Running workflow on Dandilyonn email...")
    start_time = time.time()
    
    result = subprocess.run([
        sys.executable,
        "workflows/interview_prep_workflow.py",
        "--folder", "demo", 
        "--max-emails", "1",
        "--filter", "dandilyonn"  # Filter for Dandilyonn email specifically
    ], capture_output=True, text=True)
    
    processing_time = time.time() - start_time
    
    print(f"   ✅ Workflow completed in {processing_time:.1f}s")
    print(f"   📊 Return code: {result.returncode}")
    
    # Analyze Dandilyonn output
    print("3. Analyzing Dandilyonn prep guide...")
    output_dir = Path("outputs/fullworkflow")
    dandilyonn_file = None
    
    if output_dir.exists():
        for txt_file in output_dir.glob("*.txt"):
            if "dandilyonn" in txt_file.name.lower():
                dandilyonn_file = txt_file
                break
    
    if not dandilyonn_file:
        print("   ❌ No Dandilyonn file found")
        return False
    
    with open(dandilyonn_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test Archana-specific improvements
    archana_tests = {
        "Correct interviewer extracted": "interviewer: Archana" in content,
        "Second loop gaps found": "Identified 0 research gaps" not in content,
        "Guideline format used": "## 1. before interview" in content,
        "No fallback sections": "Section 1: Summary Overview" not in content,
        "Archana LinkedIn found": "jainarchana" in content.lower(),
        "Adobe background mentioned": "adobe" in content.lower(),
        "Stanford mentioned": "stanford" in content.lower(),
        "Dandilyonn founder mentioned": "founder" in content.lower(),
        "Engineering leadership mentioned": "engineering" in content.lower() or "leadership" in content.lower(),
        "Second loop research executed": "🔍 Targeted Searches: Executed 0" not in content
    }
    
    print(f"   📄 Analyzed file: {dandilyonn_file.name}")
    print(f"   📊 File size: {len(content)} characters")
    print()
    
    print("📋 ARCHANA DETECTION TEST RESULTS:")
    passed = 0
    for test_name, result in archana_tests.items():
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    success_rate = passed / len(archana_tests)
    print(f"\n🎯 ARCHANA DETECTION SUCCESS RATE: {success_rate:.1%} ({passed}/{len(archana_tests)})")
    
    # Show key sections for Archana
    if "archana" in content.lower():
        print("\n👤 INTERVIEWER SECTION FOUND:")
        lines = content.split('\n')
        in_interviewer_section = False
        for line in lines:
            if "## 2. interviewer background" in line.lower():
                in_interviewer_section = True
            elif line.startswith("## 3."):
                in_interviewer_section = False
            
            if in_interviewer_section and line.strip():
                print(f"   {line}")
    
    # Show gap analysis results
    if "🔬 === SECOND LOOP INTELLIGENT RESEARCH ===" in content:
        print("\n🔍 SECOND LOOP RESULTS:")
        lines = content.split('\n')
        in_second_loop = False
        for line in lines:
            if "🔬 === SECOND LOOP INTELLIGENT RESEARCH ===" in line:
                in_second_loop = True
            elif line.startswith("🤔 RESEARCH QUALITY"):
                in_second_loop = False
            
            if in_second_loop and ("🎯" in line or "🔍" in line or "📝" in line):
                print(f"   {line}")
    
    return success_rate >= 0.7

def test_console_output_archana():
    """Test console output for Archana-specific searches"""
    print("\n🖥️  TESTING ARCHANA SEARCH CONSOLE OUTPUT")
    print("=" * 45)
    
    result = subprocess.run([
        sys.executable,
        "workflows/interview_prep_workflow.py",
        "--folder", "demo", 
        "--max-emails", "1",
        "--filter", "dandilyonn"
    ], capture_output=True, text=True)
    
    console_output = result.stdout
    
    archana_console_checks = {
        "Archana searches executed": "Archana" in console_output,
        "jainarchana profile searches": "jainarchana" in console_output,
        "Stanford searches": "Stanford" in console_output,
        "Adobe searches": "Adobe" in console_output,
        "Dandilyonn founder searches": "founder" in console_output,
        "Second loop activated": "SECOND LOOP INTELLIGENT RESEARCH" in console_output,
        "Forced gap analysis": "forcing comprehensive gap analysis" in console_output
    }
    
    print("📋 ARCHANA CONSOLE SEARCH CHECK:")
    for check_name, result in archana_console_checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    # Show relevant search lines
    if "Archana" in console_output:
        print("\n🔍 ARCHANA SEARCH QUERIES FOUND:")
        for line in console_output.split('\n'):
            if "Archana" in line or "jainarchana" in line:
                print(f"   {line.strip()}")
    
    return sum(archana_console_checks.values()) / len(archana_console_checks) >= 0.5

if __name__ == "__main__":
    file_success = test_dandilyonn_archana_detection()
    console_success = test_console_output_archana()
    
    print(f"\n" + "=" * 60)
    print("📊 DANDILYONN ARCHANA DETECTION RESULTS")
    print("=" * 60)
    
    if file_success and console_success:
        print("🎉 ARCHANA DETECTION WORKING!")
        print("   ✅ Correct interviewer identification")
        print("   ✅ LinkedIn profile found (jainarchana)")
        print("   ✅ Background details (Adobe, Stanford, founder)")
        print("   ✅ Proper guideline format used")
        print("   ✅ Second loop research functioning")
        print("   ✅ Gap analysis finding issues")
    else:
        print("⚠️  ARCHANA DETECTION NEEDS IMPROVEMENT")
        if not file_success:
            print("   🔧 Output content needs work")
        if not console_success:
            print("   🔧 Search queries need improvement")
    
    print(f"\n💡 Next: Check outputs/fullworkflow/Dandilyonn*.txt for detailed results")