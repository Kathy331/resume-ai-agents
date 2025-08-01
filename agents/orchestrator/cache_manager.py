#!/usr/bin/env python3
# agents/orchestrator/cache_manager.py
"""
Cache Manager - Simple command-line tool for managing Tavily and OpenAI caches

Usage:
    python cache_manager.py --help
    python cache_manager.py --status
    python cache_manager.py --clear-tavily
    python cache_manager.py --clear-openai
    python cache_manager.py --clear-all
    python cache_manager.py --info

This tool provides easy command-line access to cache management functions
without needing to run the full workflow runner.
"""

import os
import sys
import argparse
import shutil
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def get_tavily_cache_info() -> Dict[str, Any]:
    """Get information about the current Tavily cache"""
    try:
        cache_dir = ".tavily_cache"
        
        if not os.path.exists(cache_dir):
            return {
                'cache_exists': False,
                'cached_queries': 0,
                'cache_size_mb': 0,
                'message': 'No Tavily cache directory found'
            }
        
        # Count cache files
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
        files_count = len(cache_files)
        
        # Calculate total cache size
        total_size = 0
        for file in cache_files:
            file_path = os.path.join(cache_dir, file)
            total_size += os.path.getsize(file_path)
        
        size_mb = total_size / (1024 * 1024)  # Convert to MB
        
        return {
            'cache_exists': True,
            'cached_queries': files_count,
            'cache_size_mb': round(size_mb, 2),
            'cache_directory': cache_dir,
            'message': f'Tavily cache contains {files_count} queries ({size_mb:.2f} MB)'
        }
        
    except Exception as e:
        return {
            'cache_exists': False,
            'error': str(e),
            'message': f'Error accessing Tavily cache: {str(e)}'
        }

def get_openai_cache_info() -> Dict[str, Any]:
    """Get information about the current OpenAI cache"""
    try:
        from shared.openai_cache import OpenAICache
        
        cache = OpenAICache()
        stats = cache.get_cache_stats()  # Fixed method name
        
        return {
            'cache_exists': True,
            'cached_responses': stats.get('cached_queries', 0),
            'cache_size_mb': stats.get('cache_size_mb', 0),
            'cache_directory': stats.get('cache_dir', '.openai_cache'),
            'estimated_savings': stats.get('estimated_savings', 0),
            'message': f"OpenAI cache contains {stats.get('cached_queries', 0)} responses ({stats.get('cache_size_mb', 0):.2f} MB)"
        }
        
    except Exception as e:
        return {
            'cache_exists': False,
            'error': str(e),
            'message': f'Error accessing OpenAI cache: {str(e)}'
        }

def clear_tavily_cache() -> Dict[str, Any]:
    """Clear the Tavily research cache"""
    try:
        cache_dir = ".tavily_cache"
        
        if not os.path.exists(cache_dir):
            return {
                'success': True,
                'message': 'Tavily cache directory does not exist - nothing to clear',
                'files_removed': 0
            }
        
        # Count files before removal
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
        files_count = len(cache_files)
        
        # Remove the entire cache directory
        shutil.rmtree(cache_dir)
        
        return {
            'success': True,
            'message': f'Successfully cleared Tavily cache - {files_count} files removed',
            'files_removed': files_count
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Failed to clear Tavily cache: {str(e)}',
            'files_removed': 0
        }

def clear_openai_cache() -> Dict[str, Any]:
    """Clear the OpenAI cache"""
    try:
        from shared.openai_cache import OpenAICache
        
        cache = OpenAICache()
        cleared_count = cache.clear()
        
        return {
            'success': True,
            'message': f'Successfully cleared OpenAI cache - {cleared_count} responses removed',
            'responses_removed': cleared_count
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Failed to clear OpenAI cache: {str(e)}',
            'responses_removed': 0
        }

def clear_all_caches() -> Dict[str, Any]:
    """Clear both Tavily and OpenAI caches"""
    tavily_result = clear_tavily_cache()
    openai_result = clear_openai_cache()
    
    total_items_removed = tavily_result.get('files_removed', 0) + openai_result.get('responses_removed', 0)
    overall_success = tavily_result.get('success', False) and openai_result.get('success', False)
    
    return {
        'success': overall_success,
        'tavily_result': tavily_result,
        'openai_result': openai_result,
        'total_items_removed': total_items_removed,
        'message': f'Cleared {total_items_removed} total cached items'
    }

def display_cache_status():
    """Display current cache status in a formatted way"""
    print("📊 CACHE STATUS")
    print("=" * 60)
    
    # Tavily Cache
    print("🔍 TAVILY CACHE:")
    tavily_info = get_tavily_cache_info()
    if tavily_info['cache_exists']:
        print(f"   📁 Directory: {tavily_info.get('cache_directory', 'N/A')}")
        print(f"   📊 Queries: {tavily_info.get('cached_queries', 0)}")
        print(f"   💾 Size: {tavily_info.get('cache_size_mb', 0)} MB")
        print(f"   ✅ Status: Active")
    else:
        print(f"   ❌ Status: No cache found")
        if 'error' in tavily_info:
            print(f"   ⚠️  Error: {tavily_info['error']}")
    
    print()
    
    # OpenAI Cache
    print("🤖 OPENAI CACHE:")
    openai_info = get_openai_cache_info()
    if openai_info['cache_exists']:
        print(f"   📁 Directory: {openai_info.get('cache_directory', 'N/A')}")
        print(f"   📊 Responses: {openai_info.get('cached_responses', 0)}")
        print(f"   💾 Size: {openai_info.get('cache_size_mb', 0)} MB")
        print(f"   💰 Estimated savings: ${openai_info.get('estimated_savings', 0):.3f}")
        print(f"   ✅ Status: Active")
    else:
        print(f"   ❌ Status: No cache found")
        if 'error' in openai_info:
            print(f"   ⚠️  Error: {openai_info['error']}")
    
    print("=" * 60)

def display_detailed_info():
    """Display detailed information about both caches"""
    print("📋 DETAILED CACHE INFORMATION")
    print("=" * 60)
    
    tavily_info = get_tavily_cache_info()
    openai_info = get_openai_cache_info()
    
    total_queries = tavily_info.get('cached_queries', 0)
    total_responses = openai_info.get('cached_responses', 0)
    total_size = tavily_info.get('cache_size_mb', 0) + openai_info.get('cache_size_mb', 0)
    total_savings = openai_info.get('estimated_savings', 0)
    
    print(f"📊 SUMMARY:")
    print(f"   Total cached items: {total_queries + total_responses}")
    print(f"   Total cache size: {total_size:.2f} MB")
    print(f"   Estimated API savings: ${total_savings:.3f}")
    
    print(f"\n🔍 TAVILY CACHE DETAILS:")
    print(f"   Location: {tavily_info.get('cache_directory', 'Not found')}")
    print(f"   Status: {'Active' if tavily_info['cache_exists'] else 'Inactive'}")
    print(f"   Cached queries: {tavily_info.get('cached_queries', 0)}")
    print(f"   Storage size: {tavily_info.get('cache_size_mb', 0)} MB")
    
    print(f"\n🤖 OPENAI CACHE DETAILS:")
    print(f"   Location: {openai_info.get('cache_directory', 'Not found')}")
    print(f"   Status: {'Active' if openai_info['cache_exists'] else 'Inactive'}")
    print(f"   Cached responses: {openai_info.get('cached_responses', 0)}")
    print(f"   Storage size: {openai_info.get('cache_size_mb', 0)} MB")
    print(f"   Cost savings: ${openai_info.get('estimated_savings', 0):.3f}")
    
    print("=" * 60)

def main():
    """Main entry point for cache manager"""
    parser = argparse.ArgumentParser(
        description="Cache Manager - Manage Tavily and OpenAI caches",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cache_manager.py --status          # Show cache status
  python cache_manager.py --info            # Show detailed cache info
  python cache_manager.py --clear-tavily    # Clear only Tavily cache
  python cache_manager.py --clear-openai    # Clear only OpenAI cache
  python cache_manager.py --clear-all       # Clear both caches

Cache Locations:
  Tavily: .tavily_cache/
  OpenAI: .openai_cache/
        """
    )
    
    parser.add_argument('--status', action='store_true',
                       help='Show current cache status')
    parser.add_argument('--info', action='store_true',
                       help='Show detailed cache information')
    parser.add_argument('--clear-tavily', action='store_true',
                       help='Clear Tavily research cache')
    parser.add_argument('--clear-openai', action='store_true',
                       help='Clear OpenAI response cache')
    parser.add_argument('--clear-all', action='store_true',
                       help='Clear both Tavily and OpenAI caches')
    
    args = parser.parse_args()
    
    # If no arguments provided, show status by default
    if not any(vars(args).values()):
        args.status = True
    
    print(f"🗂️  Cache Manager - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Handle status display
    if args.status:
        display_cache_status()
        return
    
    # Handle detailed info
    if args.info:
        display_detailed_info()
        return
    
    # Handle cache clearing operations
    if args.clear_all:
        print("🗑️  CLEARING ALL CACHES")
        print("-" * 30)
        result = clear_all_caches()
        
        if result['success']:
            print(f"✅ Successfully cleared all caches!")
            print(f"📊 Total items removed: {result['total_items_removed']}")
            
            tavily_result = result['tavily_result']
            openai_result = result['openai_result']
            
            print(f"   🔍 Tavily: {tavily_result.get('files_removed', 0)} files")
            print(f"   🤖 OpenAI: {openai_result.get('responses_removed', 0)} responses")
        else:
            print("❌ Some caches failed to clear:")
            if not result['tavily_result'].get('success'):
                print(f"   🔍 Tavily: {result['tavily_result'].get('message')}")
            if not result['openai_result'].get('success'):
                print(f"   🤖 OpenAI: {result['openai_result'].get('message')}")
        
        return
    
    if args.clear_tavily:
        print("🗑️  CLEARING TAVILY CACHE")
        print("-" * 30)
        result = clear_tavily_cache()
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"🗑️  Cleared {result.get('files_removed', 0)} cached queries")
        else:
            print(f"❌ {result['message']}")
        return
    
    if args.clear_openai:
        print("🗑️  CLEARING OPENAI CACHE")
        print("-" * 30)
        result = clear_openai_cache()
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"🗑️  Cleared {result.get('responses_removed', 0)} cached responses")
        else:
            print(f"❌ {result['message']}")
        return

if __name__ == "__main__":
    main()
