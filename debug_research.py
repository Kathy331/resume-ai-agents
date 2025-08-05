#!/usr/bin/env python3
"""
Debug Research Pipeline
======================

Test why the deep research pipeline isn't finding sources
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path.cwd()))

def test_tavily_connection():
    """Test if Tavily is properly configured"""
    print("🔍 TESTING TAVILY CONNECTION")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('TAVILY_API_KEY')
    if api_key:
        print(f"✅ TAVILY_API_KEY found: {api_key[:10]}...")
    else:
        print("❌ TAVILY_API_KEY not found in environment")
        return False
    
    # Test basic search
    try:
        from agents.research_engine.tavily_client import search_tavily, EnhancedTavilyClient
        
        print("\n🧪 Testing basic search...")
        results = search_tavily("JUTEQ company", max_results=3)
        print(f"   Results found: {len(results)}")
        
        if results:
            for i, result in enumerate(results[:2]):
                print(f"   {i+1}. {result.get('title', 'No title')}")
                print(f"      URL: {result.get('url', 'No URL')}")
        
        print("\n🧪 Testing enhanced client...")
        client = EnhancedTavilyClient()
        enhanced_results = client.search("JUTEQ cloud solutions", max_results=3)
        print(f"   Enhanced results: {len(enhanced_results.get('results', []))}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Tavily test error: {str(e)}")
        return False

def test_deep_research_pipeline():
    """Test the deep research pipeline directly"""
    print("\n🔬 TESTING DEEP RESEARCH PIPELINE")
    print("=" * 40)
    
    try:
        from pipelines.deep_research_pipeline import DeepResearchPipeline
        
        # Mock entities like the real workflow
        test_entities = {
            'company': 'JUTEQ',
            'candidate': 'Calamari',
            'interviewer': 'Rakesh Gohel',
            'role': 'Cloud-Native Solutions'
        }
        
        pipeline = DeepResearchPipeline()
        print("✅ Pipeline initialized")
        
        print("\n🔍 Running research with test entities...")
        result = pipeline.conduct_deep_research(test_entities, email_index=1)
        
        print(f"\n📊 RESULTS:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Sources processed: {result.get('sources_processed', 0)}")
        print(f"   Validated sources: {len(result.get('validated_sources', []))}")
        print(f"   Citations database: {len(result.get('citations_database', {}))}")
        print(f"   Overall confidence: {result.get('overall_confidence', 0)}")
        
        # Show citations database
        citations_db = result.get('citations_database', {})
        if citations_db:
            print(f"\n📝 CITATIONS FOUND:")
            for category, sources in citations_db.items():
                print(f"   {category}: {len(sources) if sources else 0} sources")
                if sources and len(sources) > 0:
                    for i, source in enumerate(sources[:2]):
                        print(f"      {i+1}. {source}")
        else:
            print(f"\n❌ NO CITATIONS GENERATED")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Deep research pipeline error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🕵️ DEBUGGING RESEARCH PIPELINE")
    print("=" * 50)
    
    # Test 1: Tavily connection
    tavily_works = test_tavily_connection()
    
    # Test 2: Deep research pipeline
    research_works = test_deep_research_pipeline()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print(f"   Tavily Connection: {'✅ Working' if tavily_works else '❌ Failed'}")
    print(f"   Research Pipeline: {'✅ Working' if research_works else '❌ Failed'}")
    
    if not tavily_works:
        print("\n🔧 TAVILY FIXES:")
        print("   1. Add TAVILY_API_KEY to .env file")
        print("   2. Get API key from https://tavily.com")
        print("   3. Install tavily: pip install tavily-python")
    
    if not research_works:
        print("\n🔧 RESEARCH PIPELINE FIXES:")
        print("   1. Check entity extraction is working")
        print("   2. Debug search query generation")
        print("   3. Check research agent logic")

if __name__ == "__main__":
    main()