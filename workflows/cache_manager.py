#!/usr/bin/env python3
"""
Cache Manager - Command-line tool for managing all caches in Interview Prep Workflow
===================================================================================

Usage:
    python workflows/cache_manager.py --help
    python workflows/cache_manager.py --status
    python workflows/cache_manager.py --clear-tavily
    python workflows/cache_manager.py --clear-openai
    python workflows/cache_manager.py --clear-all
    python workflows/cache_manager.py --info

This tool provides easy command-line access to cache management functions
for the Interview Prep Workflow system including Tavily and OpenAI caches.
"""

import os
import sys
import argparse
import shutil
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_tavily_cache_info() -> Dict[str, Any]:
    """Get information about the current Tavily cache"""
    # Check directory first to avoid auto-creation
    cache_dir = "cache/tavily"  
    
    if not os.path.exists(cache_dir):
        return {
            'cache_exists': False,
            'cached_queries': 0,
            'cache_size_mb': 0,
            'cache_directory': cache_dir,
            'message': 'No Tavily cache directory found'
        }
    
    try:
        from shared.tavily_cache import get_tavily_cache
        
        cache = get_tavily_cache()
        stats = cache.get_cache_stats()
        
        return {
            'cache_exists': True,
            'cached_queries': stats.get('total_cached_results', 0),
            'valid_files': stats.get('valid_cache_files', 0),
            'expired_files': stats.get('expired_cache_files', 0),
            'cache_size_mb': stats.get('cache_size_mb', 0),
            'cache_directory': 'cache/tavily',
            'message': f"Tavily cache contains {stats.get('total_cached_results', 0)} queries ({stats.get('cache_size_mb', 0):.2f} MB)"
        }
        
    except Exception as e:
        # Fallback to direct directory check
        try:
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
            
        except Exception as fallback_error:
            return {
                'cache_exists': False,
                'error': str(fallback_error),
                'message': f'Error accessing Tavily cache: {str(fallback_error)}'
            }


def get_openai_cache_info() -> Dict[str, Any]:
    """Get information about the current OpenAI cache"""
    # Check directory first to avoid auto-creation
    cache_dir = ".openai_cache"
    
    if not os.path.exists(cache_dir):
        return {
            'cache_exists': False,
            'cached_responses': 0,
            'cache_size_mb': 0,
            'cache_directory': cache_dir,
            'message': 'No OpenAI cache directory found'
        }
    
    try:
        from shared.openai_cache import OpenAICache
        
        cache = OpenAICache()
        stats = cache.get_cache_stats()
        
        return {
            'cache_exists': True,
            'cached_responses': stats.get('total_entries', 0),  # Fixed: was 'cached_queries'
            'cache_size_mb': stats.get('cache_size_mb', 0),
            'cache_directory': stats.get('cache_dir', '.openai_cache'),
            'estimated_savings': stats.get('estimated_savings', 0),
            'message': f"OpenAI cache contains {stats.get('total_entries', 0)} responses ({stats.get('cache_size_mb', 0):.2f} MB)"
        }
        
    except Exception as e:
        # Fallback to direct directory check
        try:
            # Count cache files (exclude info file)
            cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json') and f != '_cache_info.json']
            files_count = len(cache_files)
            
            # Calculate total cache size
            total_size = 0
            for file in cache_files:
                file_path = os.path.join(cache_dir, file)
                total_size += os.path.getsize(file_path)
            
            size_mb = total_size / (1024 * 1024)  # Convert to MB
            
            return {
                'cache_exists': True,
                'cached_responses': files_count,
                'cache_size_mb': round(size_mb, 2),
                'cache_directory': cache_dir,
                'estimated_savings': 0,  # Can't calculate without cache object
                'message': f'OpenAI cache contains {files_count} responses ({size_mb:.2f} MB)'
            }
            
        except Exception as fallback_error:
            return {
                'cache_exists': False,
                'error': str(fallback_error),
                'message': f'Error accessing OpenAI cache: {str(fallback_error)}'
            }


def clear_tavily_cache() -> Dict[str, Any]:
    """Clear the Tavily research cache"""
    try:
        from shared.tavily_cache import get_tavily_cache
        
        cache = get_tavily_cache()
        
        # Get initial stats
        initial_stats = cache.get_cache_stats()
        initial_files = initial_stats.get('total_cached_results', 0)
        
        # Clear expired cache first
        expired_removed = cache.clear_expired_cache()
        
        # Clear all cache
        cache_dir = "cache/tavily"
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            
        return {
            'success': True,
            'message': f'Successfully cleared Tavily cache - {initial_files} files removed',
            'files_removed': initial_files,
            'expired_removed': expired_removed
        }
        
    except Exception as e:
        # Fallback to direct directory removal
        try:
            cache_dir = "cache/tavily"
            
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
            
        except Exception as fallback_error:
            return {
                'success': False,
                'error': str(fallback_error),
                'message': f'Failed to clear Tavily cache: {str(fallback_error)}',
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
        # Fallback to direct directory removal
        try:
            cache_dir = ".openai_cache"
            
            if not os.path.exists(cache_dir):
                return {
                    'success': True,
                    'message': 'OpenAI cache directory does not exist - nothing to clear',
                    'responses_removed': 0
                }
            
            # Count files before removal
            cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
            files_count = len(cache_files)
            
            # Remove the entire cache directory
            shutil.rmtree(cache_dir)
            
            return {
                'success': True,
                'message': f'Successfully cleared OpenAI cache - {files_count} responses removed',
                'responses_removed': files_count
            }
            
        except Exception as fallback_error:
            return {
                'success': False,
                'error': str(fallback_error),
                'message': f'Failed to clear OpenAI cache: {str(fallback_error)}',
                'responses_removed': 0
            }


def clear_all_caches() -> Dict[str, Any]:
    """Clear both Tavily and OpenAI caches"""
    print("🧹 Clearing Tavily cache...")
    tavily_result = clear_tavily_cache()
    
    print("🧹 Clearing OpenAI cache...")
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
    print("📊 INTERVIEW PREP WORKFLOW - CACHE STATUS")
    print("=" * 70)
    
    # Tavily Cache
    print("🔍 TAVILY RESEARCH CACHE:")
    tavily_info = get_tavily_cache_info()
    if tavily_info['cache_exists']:
        print(f"   📁 Directory: {tavily_info.get('cache_directory', 'N/A')}")
        cached_queries = tavily_info.get('cached_queries', 0)
        print(f"   📊 Cached Queries: {cached_queries}")
        if 'valid_files' in tavily_info:
            print(f"   ✅ Valid Files: {tavily_info['valid_files']}")
            print(f"   ⏰ Expired Files: {tavily_info.get('expired_files', 0)}")
        print(f"   💾 Size: {tavily_info.get('cache_size_mb', 0)} MB")
        if cached_queries > 0:
            print(f"   🟢 Status: Active with cached data")
        else:
            print(f"   🟡 Status: Active but empty")
    else:
        print(f"   🔴 Status: No cache found")
        if 'error' in tavily_info:
            print(f"   ⚠️  Error: {tavily_info['error']}")
    
    print()
    
    # OpenAI Cache
    print("🤖 OPENAI LLM CACHE:")
    openai_info = get_openai_cache_info()
    if openai_info['cache_exists']:
        print(f"   📁 Directory: {openai_info.get('cache_directory', 'N/A')}")
        cached_responses = openai_info.get('cached_responses', 0)
        print(f"   📊 Cached Responses: {cached_responses}")
        print(f"   💾 Size: {openai_info.get('cache_size_mb', 0)} MB")
        if openai_info.get('estimated_savings', 0) > 0:
            print(f"   💰 Estimated Savings: ${openai_info.get('estimated_savings', 0):.3f}")
        if cached_responses > 0:
            print(f"   🟢 Status: Active with cached data")
        else:
            print(f"   🟡 Status: Active but empty")
    else:
        print(f"   🔴 Status: No cache found")
        if 'error' in openai_info:
            print(f"   ⚠️  Error: {openai_info['error']}")
    
    print("=" * 70)


def display_detailed_info():
    """Display detailed information about both caches"""
    print("📋 INTERVIEW PREP WORKFLOW - DETAILED CACHE INFORMATION")
    print("=" * 70)
    
    tavily_info = get_tavily_cache_info()
    openai_info = get_openai_cache_info()
    
    total_queries = tavily_info.get('cached_queries', 0)
    total_responses = openai_info.get('cached_responses', 0)
    total_size = tavily_info.get('cache_size_mb', 0) + openai_info.get('cache_size_mb', 0)
    total_savings = openai_info.get('estimated_savings', 0)
    
    print(f"📊 CACHE SUMMARY:")
    print(f"   Total cached items: {total_queries + total_responses}")
    print(f"   Total cache size: {total_size:.2f} MB")
    if total_savings > 0:
        print(f"   Estimated API savings: ${total_savings:.3f}")
    
    print(f"\n🔍 TAVILY RESEARCH CACHE DETAILS:")
    print(f"   Location: {tavily_info.get('cache_directory', 'Not found')}")
    print(f"   Status: {'🟢 Active' if tavily_info['cache_exists'] else '🔴 Inactive'}")
    print(f"   Cached queries: {tavily_info.get('cached_queries', 0)}")
    if 'valid_files' in tavily_info:
        print(f"   Valid cache files: {tavily_info['valid_files']}")
        print(f"   Expired cache files: {tavily_info.get('expired_files', 0)}")
    print(f"   Storage size: {tavily_info.get('cache_size_mb', 0)} MB")
    print(f"   Purpose: Caches research queries for company, role, and interviewer analysis")
    
    print(f"\n🤖 OPENAI LLM CACHE DETAILS:")
    print(f"   Location: {openai_info.get('cache_directory', 'Not found')}")
    print(f"   Status: {'🟢 Active' if openai_info['cache_exists'] else '🔴 Inactive'}")
    print(f"   Cached responses: {openai_info.get('cached_responses', 0)}")
    print(f"   Storage size: {openai_info.get('cache_size_mb', 0)} MB")
    if openai_info.get('estimated_savings', 0) > 0:
        print(f"   Cost savings: ${openai_info.get('estimated_savings', 0):.3f}")
    print(f"   Purpose: Caches LLM responses for prep guide generation and entity extraction")
    
    print(f"\n🏗️  PIPELINE INTEGRATION:")
    print(f"   📧 Email Pipeline: Uses entity extraction cache")
    print(f"   🔬 Deep Research Pipeline: Uses Tavily research cache heavily")
    print(f"   📚 Prep Guide Pipeline: Uses OpenAI cache for guide generation")
    
    print("=" * 70)


def optimize_caches():
    """Optimize caches by removing expired entries"""
    print("🔧 OPTIMIZING CACHES")
    print("-" * 30)
    
    # Optimize Tavily cache
    try:
        from shared.tavily_cache import get_tavily_cache
        
        cache = get_tavily_cache()
        expired_removed = cache.clear_expired_cache()
        
        if expired_removed > 0:
            print(f"🔍 Tavily: Removed {expired_removed} expired cache files")
        else:
            print(f"🔍 Tavily: No expired cache files found")
            
    except Exception as e:
        print(f"🔍 Tavily: Error optimizing cache - {str(e)}")
    
    # OpenAI cache doesn't typically have expiration, but we can check
    print(f"🤖 OpenAI: Cache optimization not needed (no expiration)")
    
    print("✅ Cache optimization completed")


def main():
    """Main entry point for cache manager"""
    parser = argparse.ArgumentParser(
        description="Interview Prep Workflow Cache Manager - Manage all caches",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python workflows/cache_manager.py --status          # Show cache status
  python workflows/cache_manager.py --info            # Show detailed cache info
  python workflows/cache_manager.py --clear-tavily    # Clear only Tavily cache
  python workflows/cache_manager.py --clear-openai    # Clear only OpenAI cache
  python workflows/cache_manager.py --clear-all       # Clear both caches
  python workflows/cache_manager.py --optimize        # Remove expired cache entries

Cache Integration:
  📧 Email Pipeline: Entity extraction caching
  🔬 Deep Research Pipeline: Tavily API caching for company/role/interviewer research
  📚 Prep Guide Pipeline: OpenAI API caching for personalized guide generation

Cache Locations:
  Tavily Research: cache/tavily/
  OpenAI LLM: .openai_cache/
        """
    )
    
    parser.add_argument('--status', action='store_true',
                       help='Show current cache status for all pipelines')
    parser.add_argument('--info', action='store_true',
                       help='Show detailed cache information and pipeline integration')
    parser.add_argument('--clear-tavily', action='store_true',
                       help='Clear Tavily research cache (used by Deep Research Pipeline)')
    parser.add_argument('--clear-openai', action='store_true',
                       help='Clear OpenAI response cache (used by Prep Guide Pipeline)')
    parser.add_argument('--clear-all', action='store_true',
                       help='Clear both Tavily and OpenAI caches')
    parser.add_argument('--optimize', action='store_true',
                       help='Optimize caches by removing expired entries')
    
    args = parser.parse_args()
    
    # If no arguments provided, show status by default
    if not any(vars(args).values()):
        args.status = True
    
    print(f"🗂️  Interview Prep Workflow Cache Manager")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Handle status display
    if args.status:
        display_cache_status()
        return
    
    # Handle detailed info
    if args.info:
        display_detailed_info()
        return
    
    # Handle cache optimization
    if args.optimize:
        optimize_caches()
        return
    
    # Handle cache clearing operations
    if args.clear_all:
        print("🗑️  CLEARING ALL INTERVIEW PREP WORKFLOW CACHES")
        print("-" * 50)
        result = clear_all_caches()
        
        if result['success']:
            print(f"✅ Successfully cleared all caches!")
            print(f"📊 Total items removed: {result['total_items_removed']}")
            
            tavily_result = result['tavily_result']
            openai_result = result['openai_result']
            
            print(f"   🔍 Tavily Research: {tavily_result.get('files_removed', 0)} files")
            print(f"   🤖 OpenAI LLM: {openai_result.get('responses_removed', 0)} responses")
            
            print(f"\n💡 Note: Next workflow run will rebuild caches as needed")
        else:
            print("❌ Some caches failed to clear:")
            if not result['tavily_result'].get('success'):
                print(f"   🔍 Tavily: {result['tavily_result'].get('message')}")
            if not result['openai_result'].get('success'):
                print(f"   🤖 OpenAI: {result['openai_result'].get('message')}")
        
        return
    
    if args.clear_tavily:
        print("🗑️  CLEARING TAVILY RESEARCH CACHE")
        print("-" * 40)
        print("🔍 This cache is used by the Deep Research Pipeline for:")
        print("   • Company analysis queries")
        print("   • Role analysis queries") 
        print("   • LinkedIn interviewer searches")
        print()
        
        result = clear_tavily_cache()
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"🗑️  Cleared {result.get('files_removed', 0)} cached research queries")
            if result.get('expired_removed', 0) > 0:
                print(f"♻️  Also removed {result['expired_removed']} expired entries")
            print(f"💡 Next research will rebuild cache from fresh API calls")
        else:
            print(f"❌ {result['message']}")
        return
    
    if args.clear_openai:
        print("🗑️  CLEARING OPENAI LLM CACHE")
        print("-" * 40)
        print("🤖 This cache is used by:")
        print("   • Prep Guide Pipeline for personalized guide generation")
        print("   • Entity extraction for email processing")
        print()
        
        result = clear_openai_cache()
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"🗑️  Cleared {result.get('responses_removed', 0)} cached LLM responses")
            print(f"💡 Next LLM calls will be fresh API requests")
        else:
            print(f"❌ {result['message']}")
        return


if __name__ == "__main__":
    main()
