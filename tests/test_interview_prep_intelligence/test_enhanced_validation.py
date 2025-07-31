#!/usr/bin/env python3
"""
Test the enhanced source validation system for interviewer research
"""

import asyncio
import sys
import os
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from shared.tavily_client import search_tavily


def validate_source_relevance(source: Dict, interviewer_name: str, company_name: str) -> Dict[str, Any]:
    """Validate if a source is about the correct person based on company connection"""
    url = source.get('url', '')
    title = source.get('title', '')
    content = source.get('content', '')
    content_lower = content.lower()
    company_lower = company_name.lower()
    
    validation_result = {
        'is_relevant': False,
        'confidence': 0.0,
        'reasons': [],
        'company_connection': False,
        'name_match': False,
        'profile_type': 'unknown'
    }
    
    # Check company connection (highest priority)
    if company_lower in content_lower or company_lower in url.lower() or company_lower in title.lower():
        validation_result['company_connection'] = True
        validation_result['confidence'] += 0.5
        validation_result['reasons'].append(f"Company '{company_name}' mentioned")
    
    # Check name variations
    name_parts = interviewer_name.lower().split()
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[-1] if len(name_parts) > 1 else ""
    
    if interviewer_name.lower() in content_lower or interviewer_name.lower() in title.lower():
        validation_result['name_match'] = True
        validation_result['confidence'] += 0.3
        validation_result['reasons'].append("Full name match")
    elif first_name and first_name in content_lower and last_name and last_name in content_lower:
        validation_result['name_match'] = True
        validation_result['confidence'] += 0.2
        validation_result['reasons'].append("First and last name match")
    
    # Identify profile type and adjust confidence
    if 'linkedin.com' in url:
        if '/in/' in url:  # Individual LinkedIn profile
            validation_result['profile_type'] = 'linkedin_profile'
            validation_result['confidence'] += 0.2  # Higher bonus for individual profiles
        elif '/pub/dir/' in url:  # LinkedIn directory page
            validation_result['profile_type'] = 'linkedin_directory'
            validation_result['confidence'] += 0.05  # Lower bonus for directory pages
        else:
            validation_result['profile_type'] = 'linkedin_other'
            validation_result['confidence'] += 0.1
    elif 'medium.com' in url:
        validation_result['profile_type'] = 'blog'
        validation_result['confidence'] += 0.15  # Good source for professional content
    elif any(domain in url for domain in ['.edu', '.org', 'company', 'about']):
        validation_result['profile_type'] = 'professional'
        validation_result['confidence'] += 0.1
    
    # Check for contradictory information (red flags)
    if validation_result['company_connection']:
        # If we have company connection, check for other companies that might indicate wrong person
        other_companies = ['lyft', 'google', 'microsoft', 'amazon', 'meta', 'netflix']
        for other_company in other_companies:
            if other_company in content_lower and other_company != company_lower:
                if f"former {other_company}" not in content_lower and f"previously at {other_company}" not in content_lower:
                    validation_result['confidence'] -= 0.3
                    validation_result['reasons'].append(f"Warning: Current role at {other_company} (might be wrong person)")
    
    # Final relevance decision
    validation_result['is_relevant'] = validation_result['confidence'] > 0.4 and (
        validation_result['company_connection'] or 
        (validation_result['name_match'] and validation_result['confidence'] > 0.6)
    )
    
    return validation_result


async def research_interviewer_with_enhanced_validation(interviewer_name: str, company_name: str) -> Dict[str, Any]:
    """Research interviewer with enhanced source validation"""
    
    print(f"🔍 Enhanced Research: {interviewer_name} at {company_name}")
    
    # Phase 1: Initial Search
    search_queries = [
        f'{interviewer_name} LinkedIn {company_name}',
        f'"{interviewer_name}" {company_name} founder CEO',
        f'{interviewer_name} {company_name} profile bio about',
        f'"{interviewer_name}" site:linkedin.com',
        f'{interviewer_name} {company_name} experience background'
    ]
    
    print("\n📊 **PHASE 1: Source Discovery**")
    all_sources = []
    
    for i, query in enumerate(search_queries):
        try:
            print(f"   🔍 Query {i+1}: {query}")
            results = search_tavily(query, search_depth="advanced", max_results=3)
            
            for result in results:
                source_info = {
                    "url": result.get('url', ''),
                    "title": result.get('title', ''),
                    "content": result.get('content', ''),
                    "relevance_score": result.get('score', 0),
                    "query_source": f"query_{i+1}"
                }
                all_sources.append(source_info)
            
            print(f"      ✅ Found {len(results)} results")
        except Exception as e:
            print(f"      ❌ Query failed: {str(e)}")
    
    # Phase 2: Validation & Filtering
    print("\n🔍 **PHASE 2: Source Validation**")
    validated_sources = []
    rejected_sources = []
    
    for source in all_sources:
        validation = validate_source_relevance(source, interviewer_name, company_name)
        source['validation'] = validation
        
        print(f"\n   📄 Source: {source['title'][:60]}...")
        print(f"      🔗 URL: {source['url']}")
        print(f"      🎯 Confidence: {validation['confidence']:.2f}")
        print(f"      📋 Reasons: {', '.join(validation['reasons']) if validation['reasons'] else 'No specific reasons'}")
        
        if validation['is_relevant']:
            validated_sources.append(source)
            print(f"      ✅ VALIDATED - Adding to prep guide")
        else:
            rejected_sources.append(source)
            print(f"      ❌ REJECTED - Excluding from prep guide")
    
    # Phase 3: Primary Profile Detection
    print(f"\n🎯 **PHASE 3: Primary Profile Selection**")
    validated_sources.sort(key=lambda x: (
        x['validation']['profile_type'] == 'linkedin_profile',  # Prioritize individual profiles
        x['validation']['company_connection'],  # Then company connection
        x['validation']['confidence']  # Finally confidence score
    ), reverse=True)
    
    primary_profile = None
    for source in validated_sources:
        if source['validation']['company_connection']:
            primary_profile = source
            print(f"   🏆 PRIMARY PROFILE SELECTED:")
            print(f"      📋 Title: {source['title']}")
            print(f"      🔗 URL: {source['url']}")
            print(f"      🎯 Confidence: {source['validation']['confidence']:.2f}")
            print(f"      📱 Profile Type: {source['validation']['profile_type']}")
            break
    
    if not primary_profile and validated_sources:
        primary_profile = validated_sources[0]
        print(f"   ⚠️  FALLBACK PRIMARY PROFILE:")
        print(f"      📋 Title: {primary_profile['title']}")
        print(f"      🎯 Confidence: {primary_profile['validation']['confidence']:.2f}")
    
    # Results Summary
    print(f"\n📈 **VALIDATION SUMMARY:**")
    print(f"   🔍 Total sources found: {len(all_sources)}")
    print(f"   ✅ Validated sources: {len(validated_sources)}")
    print(f"   ❌ Rejected sources: {len(rejected_sources)}")
    print(f"   🏆 Primary profile: {'Found' if primary_profile else 'Not found'}")
    
    return {
        "all_sources": all_sources,
        "validated_sources": validated_sources,
        "rejected_sources": rejected_sources,
        "primary_profile": primary_profile,
        "validation_stats": {
            "total_found": len(all_sources),
            "validated": len(validated_sources),
            "rejected": len(rejected_sources),
            "primary_profile_found": primary_profile is not None
        }
    }


async def main():
    """Test the enhanced validation system"""
    print("="*100)
    print("🚀 TESTING ENHANCED SOURCE VALIDATION SYSTEM")
    print("="*100)
    
    # Test with Rakesh Kumar at JUTEQ (should find correct profile)
    results = await research_interviewer_with_enhanced_validation("Rakesh Kumar", "JUTEQ")
    
    print(f"\n🎯 **FINAL RESULTS:**")
    if results['primary_profile']:
        primary = results['primary_profile']
        print(f"   ✅ SUCCESS: Found verified profile for Rakesh Kumar at JUTEQ")
        print(f"   📋 Profile: {primary['title']}")
        print(f"   🔗 URL: {primary['url']}")
        print(f"   🎯 Confidence: {primary['validation']['confidence']:.2f}")
        
        if 'rakeshgohel01' in primary['url']:
            print(f"   🎉 CORRECT: Found the right Rakesh (JUTEQ founder)")
        elif 'lyft' in primary['url'].lower():
            print(f"   ⚠️  WARNING: This appears to be the Lyft Rakesh Kumar (wrong person)")
    else:
        print(f"   ❌ FAILED: No validated profile found")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    asyncio.run(main())
