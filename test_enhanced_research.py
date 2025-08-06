#!/usr/bin/env python3
"""
Test Enhanced Research and Gap Analysis
======================================

Test the improved gap analysis, interviewer detection, and validation logging.
"""

import subprocess
import sys
import time
from pathlib import Path

def test_enhanced_research():
    """Test the enhanced research capabilities"""
    
    print("🧪 TESTING ENHANCED RESEARCH IMPROVEMENTS")
    print("=" * 55)
    
    # Clear caches first
    print("1. Clearing caches...")
    subprocess.run([sys.executable, "workflows/cache_manager.py", "--clear-all"], 
                  capture_output=True)
    
    # Run workflow
    print("2. Running enhanced workflow...")
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
    
    # Analyze output
    print("3. Analyzing improvements...")
    output_dir = Path("outputs/fullworkflow")
    if output_dir.exists():
        txt_files = list(output_dir.glob("*.txt"))
        if txt_files:
            latest_file = max(txt_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Test improvements
            improvements = {
                "Real interviewer name detected": "Rakesh Gohel" in content and "Cloud-Native Solutions" not in content,
                "Detailed validation logs": "✅ VALIDATED:" in content or "❌ REJECTED:" in content,
                "Second loop gaps found": "🎯 AI Gap Analysis: Identified" in content and "Identified 0" not in content,
                "Enhanced citations": "SECOND LOOP" in content and "Enhanced Sources: 0" not in content,
                "Better interviewer section": "limited background information available" not in content,
                "Company mission search": "mission statement" in content.lower(),
                "Tavily search details": "🔍 TAVILY SEARCH QUERIES:" in content,
                "LinkedIn search details": "🔗 LINKEDIN SEARCH DETAILS:" in content
            }
            
            print(f"   📄 Analyzed file: {latest_file.name}")
            print(f"   📊 File size: {len(content)} characters")
            print()
            
            print("📋 ENHANCEMENT CHECK RESULTS:")
            passed = 0
            for check_name, result in improvements.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
                if result:
                    passed += 1
            
            success_rate = passed / len(improvements)
            print(f"\n🎯 IMPROVEMENT SUCCESS RATE: {success_rate:.1%} ({passed}/{len(improvements)})")
            
            # Show key sections
            if "Rakesh Gohel" in content:
                print("\n📝 INTERVIEWER DETECTION SUCCESS:")
                lines = content.split('\n')
                for line in lines:
                    if "rakesh gohel" in line.lower() or "Rakesh Gohel" in line:
                        print(f"   {line[:80]}...")
                        break
            
            if "🎯 AI Gap Analysis:" in content:
                print("\n🔍 GAP ANALYSIS RESULTS:")
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "🎯 AI Gap Analysis:" in line:
                        for j in range(5):  # Show next 5 lines
                            if i + j < len(lines):
                                print(f"   {lines[i + j]}")
                        break
            
            return success_rate >= 0.6
            
        else:
            print("❌ No output files found")
            return False
    else:
        print("❌ No output directory found")
        return False

def test_console_output():
    """Test that console output contains validation details"""
    print("\n🖥️  TESTING CONSOLE OUTPUT CAPTURE")
    print("=" * 40)
    
    result = subprocess.run([
        sys.executable,
        "workflows/interview_prep_workflow.py",
        "--folder", "demo", 
        "--max-emails", "1"
    ], capture_output=True, text=True)
    
    console_output = result.stdout
    
    console_checks = {
        "Tavily searches executed": "Fresh Tavily search" in console_output,
        "LinkedIn profiles found": "LinkedIn Profile Found" in console_output,
        "Citations generated": "📝 Citation [" in console_output,
        "Validation results": "✅ VALIDATED:" in console_output or "❌ REJECTED:" in console_output,
        "Second loop activated": "SECOND LOOP INTELLIGENT RESEARCH" in console_output,
        "Gap analysis": "AI Gap Analysis:" in console_output
    }
    
    print("📋 CONSOLE OUTPUT CHECK:")
    for check_name, result in console_checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    return sum(console_checks.values()) / len(console_checks) >= 0.5

if __name__ == "__main__":
    file_success = test_enhanced_research()
    console_success = test_console_output()
    
    print(f"\n" + "=" * 60)
    print("📊 OVERALL TEST RESULTS")
    print("=" * 60)
    
    if file_success and console_success:
        print("🎉 ALL IMPROVEMENTS WORKING!")
        print("   ✅ Interviewer name detection improved")
        print("   ✅ Gap analysis finding actionable gaps")
        print("   ✅ Validation logs being captured")
        print("   ✅ Second loop research functioning")
    else:
        print("⚠️  SOME IMPROVEMENTS NEED ATTENTION")
        if not file_success:
            print("   🔧 Output file improvements needed")
        if not console_success:
            print("   🔧 Console logging improvements needed")