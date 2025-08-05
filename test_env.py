#!/usr/bin/env python3
"""
Test Environment Variables
=========================

Test if environment variables are loading correctly
"""

import os
from dotenv import load_dotenv

def test_env_loading():
    print("🔍 TESTING ENVIRONMENT VARIABLE LOADING")
    print("=" * 50)
    
    # Load environment
    print("📁 Loading .env file...")
    load_result = load_dotenv(override=True)
    print(f"   Load result: {load_result}")
    
    # Check all environment variables
    print("\n🔑 CHECKING API KEYS:")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"   ✅ OPENAI_API_KEY: {openai_key[:10]}...{openai_key[-4:]}")
    else:
        print(f"   ❌ OPENAI_API_KEY: Not found")
    
    tavily_key = os.getenv('TAVILY_API_KEY')
    if tavily_key:
        print(f"   ✅ TAVILY_API_KEY: {tavily_key[:10]}...{tavily_key[-4:]}")
    else:
        print(f"   ❌ TAVILY_API_KEY: Not found")
    
    interview_folder = os.getenv('INTERVIEW_FOLDER')
    print(f"   📁 INTERVIEW_FOLDER: {interview_folder}")
    
    return bool(tavily_key)

def test_tavily_basic():
    print("\n🧪 TESTING TAVILY BASIC FUNCTIONALITY")
    print("=" * 50)
    
    try:
        from agents.research_engine.tavily_client import search_tavily
        
        print("🔍 Testing search_tavily function...")
        results = search_tavily("test search", max_results=2)
        print(f"   Results: {len(results)} found")
        
        if results:
            print("   Sample result:")
            for key, value in results[0].items():
                print(f"     {key}: {str(value)[:50]}...")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Tavily test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Test environment loading
    env_works = test_env_loading()
    
    if env_works:
        # Test basic Tavily functionality
        tavily_works = test_tavily_basic()
        
        print("\n" + "=" * 50)
        print("🎯 SUMMARY:")
        print(f"   Environment loading: {'✅ Working' if env_works else '❌ Failed'}")
        print(f"   Tavily basic test: {'✅ Working' if tavily_works else '❌ Failed'}")
        
        if env_works and tavily_works:
            print("\n🚀 READY TO TEST RESEARCH PIPELINE!")
            print("   Run: python debug_research.py")
        else:
            print("\n🔧 FIXES NEEDED:")
            if not env_works:
                print("   - Check .env file format")
            if not tavily_works:
                print("   - Check Tavily API key validity")
                print("   - Check internet connection")
    else:
        print("\n❌ Environment variables not loading properly")

if __name__ == "__main__":
    main()