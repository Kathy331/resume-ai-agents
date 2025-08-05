#!/usr/bin/env python3
"""
Setup Tavily API Key
===================

Help set up Tavily API key for research functionality
"""

import os
from pathlib import Path

def setup_tavily_api():
    """Setup Tavily API key"""
    print("🔑 TAVILY API KEY SETUP")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_file.touch()
    
    # Check current API key
    current_key = os.getenv('TAVILY_API_KEY')
    if current_key:
        print(f"✅ TAVILY_API_KEY already exists: {current_key[:10]}...")
        return True
    
    print("❌ No TAVILY_API_KEY found")
    print("\n🚀 TO GET A FREE TAVILY API KEY:")
    print("1. Go to: https://tavily.com")
    print("2. Sign up for a free account")
    print("3. Get your API key from the dashboard")
    print("4. Add it to your .env file")
    
    print(f"\n📝 ADD THIS LINE TO YOUR .env FILE:")
    print(f"TAVILY_API_KEY=your_api_key_here")
    
    # Option to add manually
    print(f"\n💡 OR, enter your API key now:")
    api_key = input("Enter your Tavily API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Read existing .env content
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        # Add or update TAVILY_API_KEY
        if 'TAVILY_API_KEY' in env_content:
            # Replace existing key
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('TAVILY_API_KEY'):
                    lines[i] = f'TAVILY_API_KEY={api_key}'
                    break
            env_content = '\n'.join(lines)
        else:
            # Add new key
            if env_content and not env_content.endswith('\n'):
                env_content += '\n'
            env_content += f'TAVILY_API_KEY={api_key}\n'
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ TAVILY_API_KEY added to .env file!")
        print(f"🔄 Restart your script to use the new API key")
        return True
    
    return False

def test_tavily_after_setup():
    """Test Tavily after setup"""
    print("\n🧪 TESTING TAVILY CONNECTION")
    print("=" * 40)
    
    try:
        # Force reload environment
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            print("❌ Still no API key found")
            return False
        
        print(f"✅ API key loaded: {api_key[:10]}...")
        
        # Test basic search
        from agents.research_engine.tavily_client import search_tavily, EnhancedTavilyClient
        
        print("🔍 Testing basic search...")
        results = search_tavily("OpenAI GPT", max_results=2)
        print(f"   Results found: {len(results)}")
        
        if results:
            print("   Sample result:")
            print(f"   Title: {results[0].get('title', 'No title')}")
            print(f"   URL: {results[0].get('url', 'No URL')}")
        
        print("🔍 Testing enhanced client...")
        client = EnhancedTavilyClient()
        enhanced_results = client.search_general("Python programming", max_results=2)
        print(f"   Enhanced results: {len(enhanced_results.get('results', []))}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        return False

def main():
    print("🚀 TAVILY API SETUP AND TEST")
    print("=" * 50)
    
    # Setup API key
    setup_success = setup_tavily_api()
    
    if setup_success:
        # Test the connection
        test_success = test_tavily_after_setup()
        
        if test_success:
            print("\n🎉 SUCCESS! Tavily is working!")
            print("Now run: python workflows/interview_prep_workflow.py --folder demo --max-emails 1")
        else:
            print("\n❌ Setup complete but testing failed")
            print("Check your API key and internet connection")
    else:
        print("\n⚠️  Setup incomplete - please add your API key manually")

if __name__ == "__main__":
    main()