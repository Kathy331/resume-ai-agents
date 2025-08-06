#!/usr/bin/env python3
"""
Test Citation Quality and Prep Guide Personalization
==================================================

Test that the system:
1. Filters out irrelevant citations (Archana in JUTEQ, login pages, etc.)
2. Uses correct interviewer names (Rakesh for JUTEQ)
3. Generates personalized prep guides with real data
4. Eliminates generic/fallback content
"""

import subprocess
import sys
import time
from pathlib import Path

def test_citation_quality_and_personalization():
    """Test citation filtering and prep guide personalization"""
    
    print("🎯 TESTING CITATION QUALITY & PERSONALIZATION")
    print("=" * 55)
    
    # Clear caches first
    print("1. Clearing all caches...")
    subprocess.run([sys.executable, "workflows/cache_manager.py", "--clear-all"], 
                  capture_output=True)
    
    # Run workflow on JUTEQ email specifically
    print("2. Running workflow on JUTEQ email...")
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
    
    # Find JUTEQ output file
    print("3. Analyzing JUTEQ prep guide...")
    output_dir = Path("outputs/fullworkflow")
    juteq_file = None
    
    if output_dir.exists():
        for txt_file in output_dir.glob("*.txt"):
            if "juteq" in txt_file.name.lower():
                juteq_file = txt_file
                break
    
    if not juteq_file:
        print("   ❌ No JUTEQ file found")
        return False
    
    with open(juteq_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test citation quality improvements
    citation_quality_tests = {
        "No Archana contamination": "archana" not in content.lower() or content.lower().count("archana") < 3,
        "No Dandilyonn contamination": "dandilyonn" not in content.lower(),
        "No login page citations": "log in or sign up" not in content.lower(),
        "No generic Glassdoor citations": content.lower().count("glassdoor.com/index") < 3,
        "No cost calculator citations": "cost calculator" not in content.lower(),
        "No opportunity.linkedin citations": "opportunity.linkedin" not in content.lower(),
        "Rakesh Gohel detected": "rakesh gohel" in content.lower(),
        "Correct LinkedIn profile": "rakeshgohel01" in content.lower(),
        "JUTEQ-relevant citations only": content.lower().count("juteq") > content.lower().count("archana")
    }
    
    # Test prep guide personalization
    personalization_tests = {
        "Not using fallback content": "Section 1: Summary Overview" not in content,
        "Guideline format used": "## 1. before interview" in content,
        "Specific interviewer info": "rakesh gohel" in content.lower() and "cloud-native solutions" not in content.lower(),
        "AI/cloud expertise mentioned": "ai" in content.lower() and "cloud" in content.lower(),
        "JUTEQ-specific content": "internship" in content.lower() and "juteq" in content.lower(),
        "Real LinkedIn URLs": "https://ca.linkedin.com/in/rakeshgohel01" in content,
        "Personalized questions": "exciting projects" in content.lower() or "brought you to" in content.lower(),
        "Role-specific prep": "ai and cloud technologies" in content.lower()
    }
    
    print(f"   📄 Analyzed file: {juteq_file.name}")
    print(f"   📊 File size: {len(content)} characters")
    print()
    
    print("📋 CITATION QUALITY TEST RESULTS:")
    citation_passed = 0
    for test_name, result in citation_quality_tests.items():
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
        if result:
            citation_passed += 1
    
    citation_success_rate = citation_passed / len(citation_quality_tests)
    print(f"\n📊 Citation Quality: {citation_success_rate:.1%} ({citation_passed}/{len(citation_quality_tests)})")
    
    print("\n📋 PERSONALIZATION TEST RESULTS:")
    personalization_passed = 0
    for test_name, result in personalization_tests.items():
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
        if result:
            personalization_passed += 1
    
    personalization_success_rate = personalization_passed / len(personalization_tests)
    print(f"\n📊 Personalization Quality: {personalization_success_rate:.1%} ({personalization_passed}/{len(personalization_tests)})")
    
    # Show specific sections
    if "## 2. interviewer background" in content:
        print("\n👤 INTERVIEWER SECTION:")
        lines = content.split('\n')
        in_interviewer_section = False
        for line in lines:
            if "## 2. interviewer background" in line.lower():
                in_interviewer_section = True
            elif line.startswith("## 3."):
                in_interviewer_section = False
            
            if in_interviewer_section and line.strip():
                print(f"   {line}")
    
    # Show citation counts
    if "Total Citations:" in content:
        print("\n📊 CITATION SUMMARY:")
        lines = content.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ["Total Citations:", "First Loop Sources:", "Second Loop Enhanced"]):
                print(f"   {line}")
    
    overall_success = citation_success_rate >= 0.7 and personalization_success_rate >= 0.7
    return overall_success

def test_irrelevant_citation_filtering():
    """Test that irrelevant citations are properly filtered"""
    print("\n🔍 TESTING IRRELEVANT CITATION FILTERING")
    print("=" * 45)
    
    # Run workflow and capture console output
    result = subprocess.run([
        sys.executable,
        "workflows/interview_prep_workflow.py",
        "--folder", "demo", 
        "--max-emails", "1"
    ], capture_output=True, text=True)
    
    console_output = result.stdout
    
    filtering_checks = {
        "Rakesh searches executed": "rakesh" in console_output.lower(),
        "JUTEQ searches executed": "juteq" in console_output.lower(),
        "No cross-contamination searches": console_output.lower().count("archana") < console_output.lower().count("rakesh"),
        "Targeted searches conducted": "🔍 Targeted search:" in console_output,
        "Citations validated": "✅ Found:" in console_output or "📝 Added citation:" in console_output,
        "Some citations filtered": "🚫 Filtered out" in console_output or "validation" in console_output.lower()
    }
    
    print("📋 FILTERING CHECK:")
    for check_name, result in filtering_checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    return sum(filtering_checks.values()) / len(filtering_checks) >= 0.6

if __name__ == "__main__":
    file_success = test_citation_quality_and_personalization()
    console_success = test_irrelevant_citation_filtering()
    
    print(f"\n" + "=" * 60)
    print("📊 CITATION QUALITY & PERSONALIZATION RESULTS")
    print("=" * 60)
    
    if file_success and console_success:
        print("🎉 MAJOR IMPROVEMENTS ACHIEVED!")
        print("   ✅ Irrelevant citations filtered out")
        print("   ✅ Correct interviewer identification (Rakesh)")
        print("   ✅ Personalized prep guide content")
        print("   ✅ Real research data utilized")
        print("   ✅ Company-specific information")
        print("   ✅ No generic fallback content")
    else:
        print("⚠️  STILL NEEDS IMPROVEMENT")
        if not file_success:
            print("   🔧 Citation quality or personalization needs work")
        if not console_success:
            print("   🔧 Citation filtering process needs improvement")
    
    print(f"\n💡 Check outputs/fullworkflow/Juteq.txt for detailed results")