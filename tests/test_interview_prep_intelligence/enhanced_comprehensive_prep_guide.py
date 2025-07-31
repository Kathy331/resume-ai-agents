#!/usr/bin/env python3
"""
Enhanced Comprehensive Interview Prep Guide
Provides specific, researched guidance with actionable steps instead of generic advice
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from workflows.deep_research_pipeline import DeepResearchPipeline, create_sample_user_profile
from shared.llm_client import call_llm


def print_banner(title: str, emoji: str = "🎯"):
    """Print a nice banner"""
    print("\n" + "=" * 100)
    print(f"{emoji} {title}")
    print("=" * 100)


def print_section(title: str, emoji: str = "📋"):
    """Print a section header"""
    print(f"\n{emoji} {title}")
    print("-" * 80)


def print_checklist_item(item: str, details: str = ""):
    """Print a checklist item with details"""
    print(f"   ✅ {item}")
    if details:
        print(f"      {details}")


def extract_name_clues(sources: List[Dict], original_name: str, company_name: str) -> Dict[str, Any]:
    """Extract name variations and clues from existing sources for iterative refinement"""
    import re
    
    name_variations = set()
    company_connections = []
    profile_hints = []
    best_clue = None
    best_confidence = 0.0
    
    # Original name parts
    original_parts = original_name.lower().split()
    first_name = original_parts[0] if original_parts else ""
    
    for source in sources:
        content = source.get('content', '').lower()
        title = source.get('title', '').lower()
        url = source.get('url', '').lower()
        
        # Extract full names from content (patterns like "Name Lastname" or "First M. Last")
        name_patterns = [
            r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b',  # First Last
            r'\b([A-Z][a-z]+)\s+([A-Z]\.)\s+([A-Z][a-z]+)\b',  # First M. Last
            r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'  # First Middle Last
        ]
        
        original_content = source.get('content', '')  # Keep original case for extraction
        for pattern in name_patterns:
            matches = re.findall(pattern, original_content)
            for match in matches:
                if isinstance(match, tuple):
                    full_name = ' '.join(match).replace('.', '').strip()
                else:
                    full_name = match.strip()
                
                # Check if this could be a variation of our target
                if first_name and first_name in full_name.lower():
                    confidence = calculate_name_confidence(full_name, original_name, content, company_name)
                    if confidence > 0.3:  # Minimum threshold
                        name_variations.add(full_name)
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_clue = full_name
        
        # Extract company connections
        if company_name.lower() in content:
            company_connections.append({
                'source': source['title'][:50],
                'connection_type': 'mentioned',
                'confidence': 0.7
            })
        
        # Extract LinkedIn profile hints
        if 'linkedin' in url and '/in/' in url:
            profile_hints.append({
                'type': 'linkedin_profile',
                'url': source['url'],
                'title': source['title']
            })
    
    # Filter out new variations (not seen before)
    existing_variations = {original_name.lower()}
    new_variations = [name for name in name_variations 
                     if name.lower() not in existing_variations]
    
    return {
        'all_variations': list(name_variations),
        'new_variations': new_variations,
        'company_connections': company_connections,
        'profile_hints': profile_hints,
        'best_clue': best_clue,
        'best_confidence': best_confidence
    }


def calculate_name_confidence(candidate_name: str, original_name: str, context: str, company_name: str) -> float:
    """Calculate confidence that a candidate name refers to the same person"""
    confidence = 0.0
    
    original_parts = original_name.lower().split()
    candidate_parts = candidate_name.lower().split()
    
    # First name match
    if original_parts and candidate_parts and original_parts[0] == candidate_parts[0]:
        confidence += 0.4
    
    # Last name match (if original has last name)
    if len(original_parts) > 1 and len(candidate_parts) > 1:
        if original_parts[-1] == candidate_parts[-1]:
            confidence += 0.3
    
    # Company context
    if company_name.lower() in context.lower():
        confidence += 0.2
    
    # LinkedIn profile context
    if 'linkedin' in context.lower():
        confidence += 0.1
    
    return min(confidence, 1.0)


def generate_refined_queries(name_clues: Dict, original_name: str, company_name: str, iteration: int) -> List[str]:
    """Generate refined search queries based on discovered clues"""
    queries = []
    
    # Use best clue if available
    if name_clues['best_clue'] and name_clues['best_confidence'] > 0.5:
        best_name = name_clues['best_clue']
        queries.extend([
            f'"{best_name}" {company_name} LinkedIn',
            f'"{best_name}" site:linkedin.com/in/',
            f'{best_name} {company_name} profile'
        ])
    
    # Use other name variations
    for variation in name_clues['new_variations'][:2]:  # Limit to 2 variations per iteration
        queries.extend([
            f'"{variation}" {company_name}',
            f'{variation} site:linkedin.com'
        ])
    
    # Company-focused searches if we have company connections
    if name_clues['company_connections'] and iteration <= 4:
        queries.extend([
            f'{company_name} team members staff',
            f'{company_name} leadership founders employees',
            f'"{original_name}" OR "{name_clues["best_clue"]}" {company_name}' if name_clues['best_clue'] else f'{original_name} {company_name} about'
        ])
    
    # Remove duplicates and limit
    unique_queries = []
    seen = set()
    for query in queries:
        if query.lower() not in seen:
            unique_queries.append(query)
            seen.add(query.lower())
    
    return unique_queries[:4]  # Limit to 4 queries per iteration


async def research_interviewer_with_tavily(interviewer_name: str, company_name: str, email_context: str = "") -> Dict[str, Any]:
    """Use Tavily to research real interviewer information with intelligent iterative search"""
    from shared.tavily_client import search_tavily
    import re
    
    print(f"   🔍 Deep researching {interviewer_name} at {company_name}...")
    
    # Initialize tracking variables
    all_sources = []
    research_results = {}
    discovered_names = set()  # Track name variations discovered
    search_iterations = []
    max_iterations = 8  # Prevent infinite loops
    
    # Phase 1: Initial broad search
    print("   📊 **PHASE 1: Initial Broad Discovery**")
    initial_queries = [
        f'{interviewer_name} LinkedIn {company_name}',
        f'"{interviewer_name}" {company_name}',
        f'{interviewer_name} {company_name} profile',
        f'"{interviewer_name}" site:linkedin.com'
    ]
    
    if email_context:
        initial_queries.insert(1, f'{interviewer_name} {email_context} {company_name}')
    
    # Execute initial searches
    for i, query in enumerate(initial_queries):
        try:
            print(f"      🔍 Initial Query {i+1}: {query}")
            results = search_tavily(query, search_depth="advanced", max_results=4)
            research_results[f"initial_query_{i+1}"] = results
            
            for result in results:
                source_info = {
                    "url": result.get('url', ''),
                    "title": result.get('title', ''),
                    "content": result.get('content', ''),
                    "relevance_score": result.get('score', 0),
                    "query_source": f"initial_query_{i+1}",
                    "iteration": 1
                }
                all_sources.append(source_info)
            
            print(f"         ✅ Found {len(results)} results")
        except Exception as e:
            print(f"         ❌ Query failed: {str(e)}")
            research_results[f"initial_query_{i+1}"] = []
    
    # Phase 2: Intelligent Iterative Search Loop
    print("   � **PHASE 2: Intelligent Iterative Refinement**")
    
    iteration = 2
    while iteration <= max_iterations:
        print(f"      📈 **ITERATION {iteration}:**")
        
        # Analyze current sources for clues
        name_clues = extract_name_clues(all_sources, interviewer_name, company_name)
        
        if not name_clues['new_variations'] and iteration > 3:
            print("         🎯 No new name variations found - search converged")
            break
        
        # Generate refined queries based on discovered clues
        refined_queries = generate_refined_queries(
            name_clues, 
            interviewer_name, 
            company_name, 
            iteration
        )
        
        if not refined_queries:
            print("         ⚠️  No new refined queries generated")
            break
        
        # Execute refined searches
        iteration_found_new = False
        for i, query in enumerate(refined_queries[:3]):  # Limit to 3 per iteration
            try:
                print(f"         🔍 Refined Query {i+1}: {query}")
                results = search_tavily(query, search_depth="advanced", max_results=3)
                research_results[f"iteration_{iteration}_query_{i+1}"] = results
                
                new_sources_count = 0
                for result in results:
                    # Check if this is truly a new source
                    existing_urls = [s['url'] for s in all_sources]
                    if result.get('url', '') not in existing_urls:
                        source_info = {
                            "url": result.get('url', ''),
                            "title": result.get('title', ''),
                            "content": result.get('content', ''),
                            "relevance_score": result.get('score', 0),
                            "query_source": f"iteration_{iteration}_query_{i+1}",
                            "iteration": iteration,
                            "discovered_from": name_clues['best_clue'] if name_clues['best_clue'] else "refinement"
                        }
                        all_sources.append(source_info)
                        new_sources_count += 1
                        iteration_found_new = True
                
                print(f"            ✅ Found {new_sources_count} new sources")
                
            except Exception as e:
                print(f"            ❌ Refined query failed: {str(e)}")
        
        if not iteration_found_new:
            print("         🎯 No new sources found - search exhausted")
            break
        
        # Track this iteration
        search_iterations.append({
            'iteration': iteration,
            'clues_found': name_clues,
            'queries_used': refined_queries[:3],
            'new_sources_found': sum(1 for s in all_sources if s.get('iteration') == iteration)
        })
        
        iteration += 1
    
    
    # Phase 3: Enhanced Source Validation & Filtering
    print("   🔍 **PHASE 3: Enhanced Source Validation & Filtering**")
    validated_sources = []
    rejected_sources = []
    
    # Track name variations discovered during search
    discovered_names = set()
    for iteration_data in search_iterations:
        if iteration_data.get('clues_found', {}).get('all_variations'):
            discovered_names.update(iteration_data['clues_found']['all_variations'])
    
    for source in all_sources:
        # Enhanced validation that considers discovered names
        validation = validate_source_relevance_enhanced(
            source, 
            interviewer_name, 
            company_name, 
            discovered_names
        )
        source['validation'] = validation
        
        if validation['is_relevant']:
            validated_sources.append(source)
            iteration_info = f" (iter {source.get('iteration', '1')})" if source.get('iteration', 1) > 1 else ""
            print(f"      ✅ VALIDATED{iteration_info}: {source['title'][:50]}... (confidence: {validation['confidence']:.2f})")
            if validation['reasons']:
                print(f"         Reasons: {', '.join(validation['reasons'])}")
            if source.get('discovered_from'):
                print(f"         Discovered from: {source['discovered_from']}")
        else:
            rejected_sources.append(source)
            print(f"      ❌ REJECTED: {source['title'][:50]}... (confidence: {validation['confidence']:.2f})")
    
    # Phase 4: Deep Information Extraction with Iteration Context
    print("   🎯 **PHASE 4: Deep Information Extraction**")
    primary_profile = None
    linkedin_profiles = []
    real_info_found = {}
    
    # Sort validated sources by confidence, iteration (newer = better), and profile type priority
    validated_sources.sort(key=lambda x: (
        x['validation']['profile_type'] == 'linkedin_profile',  # Prioritize individual profiles
        x['validation']['company_connection'],  # Then company connection  
        x.get('iteration', 1),  # Prefer later iterations (more refined)
        x['validation']['confidence']  # Finally confidence score
    ), reverse=True)
    
    # Find primary profile (highest confidence with company connection from latest iterations)
    for source in validated_sources:
        if source['validation']['company_connection'] and not primary_profile:
            primary_profile = source
            iteration_info = f" (discovered in iteration {source.get('iteration', 1)})" if source.get('iteration', 1) > 1 else ""
            print(f"      🎯 PRIMARY PROFILE{iteration_info}: {source['title']}")
            print(f"         URL: {source['url']}")
            print(f"         Profile Type: {source['validation']['profile_type']}")
            if source.get('discovered_from'):
                print(f"         Discovery Path: {source['discovered_from']}")
            break
    
    # Extract LinkedIn profiles
    for source in validated_sources:
        if 'linkedin.com' in source['url']:
            linkedin_profiles.append(source)
    
    # Extract information only from validated sources
    for source in validated_sources:
        url = source['url']
        title = source['title']
        content = source['content']
        content_lower = content.lower()
        
        # Extract role information (prioritize primary profile and latest iterations)
        source_priority = (source == primary_profile) or (source.get('iteration', 1) > 2)
        if source_priority or company_name.lower() in content_lower:
            if 'founder' in content_lower and company_name.lower() in content_lower:
                real_info_found['role'] = 'Founder'
                real_info_found['role_source'] = {'url': url, 'title': title, 'iteration': source.get('iteration', 1)}
            elif 'ceo' in content_lower and company_name.lower() in content_lower:
                real_info_found['role'] = 'CEO'
                real_info_found['role_source'] = {'url': url, 'title': title, 'iteration': source.get('iteration', 1)}
            elif 'cto' in content_lower and company_name.lower() in content_lower:
                real_info_found['role'] = 'CTO'
                real_info_found['role_source'] = {'url': url, 'title': title, 'iteration': source.get('iteration', 1)}
        
        # Extract technical expertise
        tech_terms = ['ai', 'cloud', 'devops', 'kubernetes', 'aws', 'azure', 'python', 'javascript', 'machine learning', 'saas', 'cloud-native', 'generative ai', 'agentai']
        found_tech = [term for term in tech_terms if term in content_lower]
        if found_tech and len(found_tech) > len(real_info_found.get('technical_expertise', [])):
            real_info_found['technical_expertise'] = found_tech
            real_info_found['tech_expertise_source'] = {'url': url, 'title': title, 'found_terms': found_tech, 'iteration': source.get('iteration', 1)}
        
        # Extract education (only from high-confidence sources from later iterations)
        if source['validation']['confidence'] > 0.6 and source.get('iteration', 1) >= 2:
            edu_terms = ['university', 'college', 'degree', 'bachelor', 'master', 'phd', 'institute', 'mca']
            for term in edu_terms:
                if term in content_lower and 'education' not in real_info_found:
                    sentences = content.split('.')
                    for sentence in sentences:
                        if term in sentence.lower() and len(sentence.strip()) > 10:
                            real_info_found['education'] = sentence.strip()
                            real_info_found['education_source'] = {'url': url, 'title': title, 'iteration': source.get('iteration', 1)}
                            break
                    break
    
    # Final validation summary with iteration context
    print(f"   📊 **ITERATIVE SEARCH SUMMARY:**")
    print(f"      🔄 Total iterations completed: {len(search_iterations) + 1}")
    print(f"      🔍 Total sources discovered: {len(all_sources)}")
    print(f"      ✅ Validated sources: {len(validated_sources)}")
    print(f"      ❌ Rejected sources: {len(rejected_sources)}")
    print(f"      🎯 Primary profile: {'Found' if primary_profile else 'Not found'}")
    print(f"      🔗 LinkedIn profiles: {len(linkedin_profiles)}")
    print(f"      📝 Name variations discovered: {len(discovered_names)}")
    
    # Show iteration breakdown
    if search_iterations:
        print(f"      📈 **Iteration Breakdown:**")
        for iter_data in search_iterations:
            print(f"         Iteration {iter_data['iteration']}: {iter_data['new_sources_found']} new sources")
            if iter_data['clues_found']['best_clue']:
                print(f"           └─ Best clue: {iter_data['clues_found']['best_clue']} (confidence: {iter_data['clues_found']['best_confidence']:.2f})")
    
    # Compile final results with iteration context
    extracted_info = {
        "name": interviewer_name,
        "company": company_name,
        "research_results": research_results,
        "all_sources": validated_sources,  # Only return validated sources
        "rejected_sources": rejected_sources,
        "primary_profile": primary_profile,
        "linkedin_profiles": linkedin_profiles,
        "linkedin_found": len(linkedin_profiles) > 0,
        "real_info_extracted": real_info_found,
        "confidence_score": len(validated_sources) / 10 if len(validated_sources) <= 10 else 1.0,
        "total_sources": len(validated_sources),
        "search_iterations": search_iterations,
        "discovered_names": list(discovered_names),
        "validation_stats": {
            "total_found": len(all_sources),
            "validated": len(validated_sources),
            "rejected": len(rejected_sources),
            "primary_profile_found": primary_profile is not None,
            "iterations_completed": len(search_iterations) + 1,
            "name_variations_discovered": len(discovered_names)
        }
    }
    
    return extracted_info


def validate_source_relevance_enhanced(source: Dict, interviewer_name: str, company_name: str, discovered_names: set) -> Dict[str, Any]:
    """Enhanced validation that considers discovered name variations from iterative search"""
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
        'profile_type': 'unknown',
        'discovered_name_match': False
    }
    
    # Check company connection (highest priority)
    if company_lower in content_lower or company_lower in url.lower() or company_lower in title.lower():
        validation_result['company_connection'] = True
        validation_result['confidence'] += 0.5
        validation_result['reasons'].append(f"Company '{company_name}' mentioned")
    
    # Check original name variations
    name_parts = interviewer_name.lower().split()
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[-1] if len(name_parts) > 1 else ""
    
    if interviewer_name.lower() in content_lower or interviewer_name.lower() in title.lower():
        validation_result['name_match'] = True
        validation_result['confidence'] += 0.3
        validation_result['reasons'].append("Original name match")
    elif first_name and first_name in content_lower and last_name and last_name in content_lower:
        validation_result['name_match'] = True
        validation_result['confidence'] += 0.2
        validation_result['reasons'].append("First and last name match")
    
    # Check discovered name variations (NEW FEATURE)
    for discovered_name in discovered_names:
        if discovered_name.lower() in content_lower or discovered_name.lower() in title.lower():
            validation_result['discovered_name_match'] = True
            validation_result['confidence'] += 0.4  # High confidence for discovered variations
            validation_result['reasons'].append(f"Discovered name variation match: {discovered_name}")
            break
    
    # Identify profile type and adjust confidence
    if 'linkedin.com' in url:
        if '/in/' in url:  # Individual LinkedIn profile
            validation_result['profile_type'] = 'linkedin_profile'
            validation_result['confidence'] += 0.2  # Higher bonus for individual profiles
        elif '/pub/dir/' in url:  # LinkedIn directory page
            validation_result['profile_type'] = 'linkedin_directory'
            validation_result['confidence'] += 0.05  # Lower bonus for directory pages
        elif '/company/' in url:  # Company page
            validation_result['profile_type'] = 'linkedin_company'
            validation_result['confidence'] += 0.15  # Good for company context
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
        other_companies = ['lyft', 'google', 'microsoft', 'amazon', 'meta', 'netflix', 'apple', 'uber']
        for other_company in other_companies:
            if other_company in content_lower and other_company != company_lower:
                if f"former {other_company}" not in content_lower and f"previously at {other_company}" not in content_lower:
                    validation_result['confidence'] -= 0.3
                    validation_result['reasons'].append(f"Warning: Current role at {other_company} (might be wrong person)")
    
    # Enhanced relevance decision considering discovered names
    validation_result['is_relevant'] = validation_result['confidence'] > 0.4 and (
        validation_result['company_connection'] or 
        validation_result['discovered_name_match'] or
        (validation_result['name_match'] and validation_result['confidence'] > 0.6)
    )
    
    return validation_result
    
    # Phase 2: Source Validation & Filtering
    print("   🔍 **PHASE 2: Source Validation & Filtering**")
    validated_sources = []
    rejected_sources = []
    
    for source in all_sources:
        validation = validate_source_relevance(source, interviewer_name, company_name)
        source['validation'] = validation
        
        if validation['is_relevant']:
            validated_sources.append(source)
            print(f"      ✅ VALIDATED: {source['title'][:50]}... (confidence: {validation['confidence']:.2f})")
            if validation['reasons']:
                print(f"         Reasons: {', '.join(validation['reasons'])}")
        else:
            rejected_sources.append(source)
            print(f"      ❌ REJECTED: {source['title'][:50]}... (confidence: {validation['confidence']:.2f})")
            if validation['reasons']:
                print(f"         Issues: {', '.join(validation['reasons'])}")
    
    # Phase 3: Deep Research on Validated Sources
    print("   🎯 **PHASE 3: Deep Information Extraction**")
    primary_profile = None
    linkedin_profiles = []
    real_info_found = {}
    
    # Sort validated sources by confidence and profile type priority
    validated_sources.sort(key=lambda x: (
        x['validation']['profile_type'] == 'linkedin_profile',  # Prioritize individual profiles
        x['validation']['company_connection'],  # Then company connection
        x['validation']['confidence']  # Finally confidence score
    ), reverse=True)
    
    # Find primary profile (highest confidence with company connection)
    for source in validated_sources:
        if source['validation']['company_connection'] and not primary_profile:
            primary_profile = source
            print(f"      🎯 PRIMARY PROFILE: {source['title']}")
            print(f"         URL: {source['url']}")
            print(f"         Profile Type: {source['validation']['profile_type']}")
            break
    
    # Extract LinkedIn profiles
    for source in validated_sources:
        if 'linkedin.com' in source['url']:
            linkedin_profiles.append(source)
    
    # Extract information only from validated sources
    for source in validated_sources:
        url = source['url']
        title = source['title']
        content = source['content']
        content_lower = content.lower()
        
        # Extract role information (prioritize primary profile)
        if source == primary_profile or company_name.lower() in content_lower:
            if 'founder' in content_lower and company_name.lower() in content_lower:
                real_info_found['role'] = 'Founder'
                real_info_found['role_source'] = {'url': url, 'title': title}
            elif 'ceo' in content_lower and company_name.lower() in content_lower:
                real_info_found['role'] = 'CEO'
                real_info_found['role_source'] = {'url': url, 'title': title}
            elif 'cto' in content_lower and company_name.lower() in content_lower:
                real_info_found['role'] = 'CTO'
                real_info_found['role_source'] = {'url': url, 'title': title}
        
        # Extract technical expertise
        tech_terms = ['ai', 'cloud', 'devops', 'kubernetes', 'aws', 'azure', 'python', 'javascript', 'machine learning', 'saas', 'cloud-native']
        found_tech = [term for term in tech_terms if term in content_lower]
        if found_tech and len(found_tech) > len(real_info_found.get('technical_expertise', [])):
            real_info_found['technical_expertise'] = found_tech
            real_info_found['tech_expertise_source'] = {'url': url, 'title': title, 'found_terms': found_tech}
        
        # Extract education (only from high-confidence sources)
        if source['validation']['confidence'] > 0.6:
            edu_terms = ['university', 'college', 'degree', 'bachelor', 'master', 'phd', 'institute', 'mca']
            for term in edu_terms:
                if term in content_lower and 'education' not in real_info_found:
                    sentences = content.split('.')
                    for sentence in sentences:
                        if term in sentence.lower() and len(sentence.strip()) > 10:
                            real_info_found['education'] = sentence.strip()
                            real_info_found['education_source'] = {'url': url, 'title': title}
                            break
                    break
    
    # Final validation summary
    print(f"   📊 **VALIDATION SUMMARY:**")
    print(f"      🔍 Total sources found: {len(all_sources)}")
    print(f"      ✅ Validated sources: {len(validated_sources)}")
    print(f"      ❌ Rejected sources: {len(rejected_sources)}")
    print(f"      🎯 Primary profile: {'Found' if primary_profile else 'Not found'}")
    print(f"      🔗 LinkedIn profiles: {len(linkedin_profiles)}")
    
    # Compile final results
    extracted_info = {
        "name": interviewer_name,
        "company": company_name,
        "research_results": research_results,
        "all_sources": validated_sources,  # Only return validated sources
        "rejected_sources": rejected_sources,
        "primary_profile": primary_profile,
        "linkedin_profiles": linkedin_profiles,
        "linkedin_found": len(linkedin_profiles) > 0,
        "real_info_extracted": real_info_found,
        "confidence_score": len(validated_sources) / 10 if len(validated_sources) <= 10 else 1.0,
        "total_sources": len(validated_sources),
        "validation_stats": {
            "total_found": len(all_sources),
            "validated": len(validated_sources),
            "rejected": len(rejected_sources),
            "primary_profile_found": primary_profile is not None
        }
    }
    
    return extracted_info


async def generate_interviewer_background(interviewer_name: str, company_name: str, email_context: str = "") -> Dict[str, Any]:
    """Generate detailed interviewer background using real Tavily research with minimal AI synthesis"""
    
    # Get real research data from Tavily
    research_data = await research_interviewer_with_tavily(interviewer_name, company_name, email_context)
    
    # Use extracted real information directly, minimal AI processing
    real_info = research_data.get('real_info_extracted', {})
    linkedin_profiles = research_data.get('linkedin_profiles', [])
    
    # Build profile from REAL data found
    profile = {
        "name": interviewer_name,
        "company": company_name,
        "research_data": research_data,
        "total_research_sources": research_data['total_sources'],
        "linkedin_profile_found": research_data['linkedin_found'],
        "confidence_score": research_data['confidence_score']
    }
    
    # Use real extracted information instead of AI generation
    if real_info.get('role'):
        profile['role'] = f"{real_info['role']} at {company_name}"
    else:
        profile['role'] = f"Team Member at {company_name}"
    
    if real_info.get('technical_expertise'):
        profile['expertise_areas'] = real_info['technical_expertise']
        profile['background'] = f"Professional with expertise in {', '.join(real_info['technical_expertise'][:3])}"
    else:
        profile['expertise_areas'] = ["Leadership", "Technology"]
        profile['background'] = "Technology professional"
    
    if real_info.get('education'):
        profile['education'] = real_info['education']
    else:
        profile['education'] = "Technical education background"
    
    if real_info.get('experience_years'):
        profile['experience_years'] = real_info['experience_years']
    else:
        profile['experience_years'] = "Professional experience"
    
    # Communication style based on role
    if 'founder' in profile['role'].lower() or 'ceo' in profile['role'].lower():
        profile['communication_style'] = "Strategic and visionary leadership style"
    else:
        profile['communication_style'] = "Professional and collaborative"
    
    # Interests based on technical expertise
    profile['likely_interests'] = real_info.get('technical_expertise', ['Innovation', 'Technology', 'Leadership'])[:3]
    
    # Real sources found
    actual_sources = []
    for source in research_data['all_sources'][:5]:  # Top 5 sources
        actual_sources.append(f"{source['title']}: {source['url']}")
    
    profile['potential_sources'] = actual_sources
    profile['research_confidence'] = "high" if research_data['confidence_score'] > 0.7 else "medium" if research_data['confidence_score'] > 0.4 else "low"
    
    return profile


async def generate_technical_prep_topics(role_title: str, company_name: str) -> Dict[str, Any]:
    """Generate specific technical topics to study for the role"""
    
    prompt = f"""
You are a technical interview expert. For the role "{role_title}" at "{company_name}", 
generate specific technical topics the candidate should review.

Provide a JSON response with:
{{
    "core_technologies": ["tech1", "tech2", "tech3"],
    "programming_languages": ["lang1", "lang2"],
    "concepts_to_review": [
        {{
            "topic": "Topic Name",
            "description": "Why this is important for the role",
            "key_points": ["point1", "point2", "point3"]
        }}
    ],
    "hands_on_practice": [
        "Specific coding exercise or project type",
        "Another practical exercise"
    ],
    "common_interview_topics": [
        {{
            "category": "Category Name",
            "topics": ["topic1", "topic2", "topic3"],
            "preparation_tip": "How to prepare for this category"
        }}
    ]
}}

Be specific to the role and company type. Focus on actionable preparation steps.
"""
    
    try:
        response = await call_llm(prompt, model="gpt-4o-mini", max_tokens=1000, temperature=0.3)
        import json
        return json.loads(response)
    except Exception as e:
        print(f"   ⚠️ Could not generate technical prep topics: {str(e)}")
        return {
            "core_technologies": ["Python", "Cloud Platforms", "APIs"],
            "programming_languages": ["Python", "JavaScript"],
            "concepts_to_review": [
                {
                    "topic": "System Design",
                    "description": "Understanding scalable architecture",
                    "key_points": ["Scalability", "Performance", "Reliability"]
                }
            ],
            "hands_on_practice": ["Build a small API", "Deploy to cloud platform"],
            "common_interview_topics": [
                {
                    "category": "Problem Solving",
                    "topics": ["Algorithms", "Data Structures", "Optimization"],
                    "preparation_tip": "Practice coding problems on LeetCode or similar platforms"
                }
            ]
        }


async def generate_company_specific_questions(company_name: str, role_title: str, company_research: Dict) -> List[str]:
    """Generate specific questions to ask based on company research"""
    
    research_summary = "No specific research available"
    if company_research and "error" not in company_research:
        # Extract key points from research
        research_points = []
        for query_results in company_research.values():
            if isinstance(query_results, list):
                for result in query_results[:2]:
                    if result.get('title'):
                        research_points.append(f"- {result['title']}")
        research_summary = "\n".join(research_points[:6])
    
    prompt = f"""
Based on the company research for {company_name} and the {role_title} role, generate 8-10 specific, 
insightful questions to ask during the interview. Mix strategic, role-specific, and culture questions.

Research Context:
{research_summary}

Provide questions in this JSON format:
{{
    "strategic_questions": [
        "Question about company direction/strategy",
        "Another strategic question"
    ],
    "role_specific_questions": [
        "Question about the specific role responsibilities",
        "Question about team structure or processes"
    ],
    "culture_questions": [
        "Question about company culture or values",
        "Question about growth opportunities"
    ],
    "technical_questions": [
        "Question about technical challenges or stack",
        "Question about development practices"
    ]
}}

Make questions specific to {company_name} and avoid generic questions. Show you've done research.
"""
    
    try:
        response = await call_llm(prompt, model="gpt-4o-mini", max_tokens=1000, temperature=0.4)
        import json
        question_data = json.loads(response)
        
        # Flatten into a single list with categories
        all_questions = []
        for category, questions in question_data.items():
            category_name = category.replace('_', ' ').title()
            all_questions.append(f"\n   📋 {category_name}:")
            for i, question in enumerate(questions, 1):
                all_questions.append(f"      {i}. {question}")
        
        return all_questions
    except Exception as e:
        print(f"   ⚠️ Could not generate specific questions: {str(e)}")
        return [
            "\n   📋 Strategic Questions:",
            f"      1. What are {company_name}'s main priorities for the next 12 months?",
            f"      2. How does this role contribute to {company_name}'s growth?",
            "\n   📋 Role-Specific Questions:",
            f"      1. What would success look like in this {role_title} position?",
            "      2. What are the biggest challenges the team is currently facing?",
            "\n   📋 Culture Questions:",
            "      1. How would you describe the company culture and values?",
            "      2. What opportunities exist for professional development?"
        ]


async def generate_personal_narrative_guide(role_title: str, company_name: str) -> Dict[str, Any]:
    """Generate guidance for personal narrative preparation"""
    
    prompt = f"""
Create a structured guide for preparing a personal narrative for a {role_title} role at {company_name}.
Focus on practical, actionable advice for crafting compelling stories.

Provide JSON response with:
{{
    "why_field_questions": [
        "Self-reflection question about why they chose this field",
        "Another question to help them think through their motivation"
    ],
    "why_company_framework": {{
        "research_points": ["What to research about the company", "Another research area"],
        "connection_points": ["How to connect personal goals with company mission", "Another connection strategy"],
        "example_response_structure": "Template for answering 'Why this company?'"
    }},
    "why_role_framework": {{
        "skill_alignment": ["How to identify relevant skills", "How to present them effectively"],
        "growth_narrative": "How to discuss career growth and learning goals",
        "example_response_structure": "Template for answering 'Why this role?'"
    }},
    "story_preparation": [
        {{
            "story_type": "Challenge/Problem-solving story",
            "framework": "STAR method guidance",
            "key_elements": ["What to include", "How to structure", "What impact to highlight"]
        }},
        {{
            "story_type": "Learning/Growth story", 
            "framework": "How to structure learning stories",
            "key_elements": ["Learning trigger", "Process", "Application"]
        }}
    ]
}}
"""
    
    try:
        response = await call_llm(prompt, model="gpt-4o-mini", max_tokens=1200, temperature=0.3)
        import json
        return json.loads(response)
    except Exception as e:
        print(f"   ⚠️ Could not generate personal narrative guide: {str(e)}")
        return {
            "why_field_questions": [
                "What initially drew you to this field?",
                "What excites you most about working in this area?"
            ],
            "why_company_framework": {
                "research_points": ["Company mission and values", "Recent developments and growth"],
                "connection_points": ["Align personal values with company mission", "Connect career goals with company direction"],
                "example_response_structure": "I'm excited about [company] because [specific reason based on research]. This aligns with my goal to [personal goal] and I see opportunities to [contribution]."
            },
            "why_role_framework": {
                "skill_alignment": ["Identify skills that match job requirements", "Prepare examples of using these skills"],
                "growth_narrative": "Show how this role advances your career while benefiting the company",
                "example_response_structure": "This role appeals to me because [specific aspects]. My background in [relevant area] and interest in [growth area] make this a perfect next step."
            },
            "story_preparation": [
                {
                    "story_type": "Challenge/Problem-solving story",
                    "framework": "STAR: Situation, Task, Action, Result",
                    "key_elements": ["Clear context", "Your specific actions", "Measurable impact"]
                }
            ]
        }


async def generate_enhanced_prep_guide():
    """Generate the enhanced comprehensive prep guide"""
    
    print_banner("ENHANCED COMPREHENSIVE INTERVIEW PREP GUIDE", "🚀")
    print("🎯 AI-Powered Interview Preparation with Specific, Actionable Guidance")
    print("📅 No more generic advice - get researched, customized preparation")
    print(f"📅 Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    # Initialize pipeline and get research data
    pipeline = DeepResearchPipeline()
    user_profile = create_sample_user_profile()
    
    # Example interview scenarios
    interviews = [
        {
            "company_name": "Dandilyonn",
            "role_title": "AI Researcher",
            "interviewer_name": "Archana",
            "interview_date": "August 8, 2025",
            "interview_time": "2 PM - 4 PM ET",
            "contact_deadline": "Friday, August 2, 2025"
        },
        {
            "company_name": "JUTEQ",
            "role_title": "Cloud Engineer Intern",
            "interviewer_name": "Rakesh Kumar",
            "interview_date": "August 6-7, 2025",
            "interview_time": "10 AM - 4 PM ET",
            "contact_deadline": "Friday, August 2, 2025"
        },
    ]
    
    for interview in interviews:
        company_name = interview["company_name"]
        role_title = interview["role_title"]
        interviewer_name = interview["interviewer_name"]
        
        print_banner(f"PREP GUIDE: {company_name} - {role_title}", "🎯")
        
        # Get company research data
        print("   🔍 Gathering company research data...")
        company_research = await pipeline.perform_deep_company_research(company_name)
        role_research = await pipeline.perform_deep_role_research(role_title, company_name)
        
        # ✅ BEFORE THE INTERVIEW
        print_section("BEFORE THE INTERVIEW", "✅")
        
        print_checklist_item(
            "1. Confirm the Time",
            f"📅 Available: {interview['interview_date']}, {interview['interview_time']}"
        )
        print(f"      📞 Contact: {interviewer_name}")
        print(f"      ⏰ Reply by: {interview['contact_deadline']}")
        print(f"      💡 Action: Send professional confirmation email mentioning your enthusiasm")
        
        print_checklist_item("2. Technical Setup Test")
        print("      🖥️  Test Zoom/video platform 24 hours before")
        print("      🎤 Check microphone, camera, lighting")
        print("      🌐 Ensure stable internet connection")
        print("      🔇 Find quiet space or backup location")
        
        # INTERVIEWER RESEARCH
        print_section(f"INTERVIEWER RESEARCH: {interviewer_name}", "👤")
        print("   🔍 Performing deep web research with Tavily...")
        
        interviewer_bg = await generate_interviewer_background(interviewer_name, company_name)
        
        # Display research statistics
        print(f"\n   � **RESEARCH RESULTS:**")
        print(f"      🌐 Total Sources Found: {interviewer_bg.get('total_research_sources', 0)}")
        print(f"      🔗 LinkedIn Profile Found: {'✅' if interviewer_bg.get('linkedin_profile_found', False) else '❌'}")
        print(f"      📈 Research Confidence: {interviewer_bg.get('research_confidence', 'unknown').upper()}")
        
        print(f"\n   �📋 **{interviewer_bg['name']} - RESEARCH-BASED PROFILE:**")
        print(f"      🏢 Role: {interviewer_bg['role']}")
        print(f"      📚 Background: {interviewer_bg['background']}")
        print(f"      🎓 Education: {interviewer_bg['education']}")
        print(f"      💼 Experience: {interviewer_bg['experience_years']}")
        print(f"      🔧 Expertise: {', '.join(interviewer_bg['expertise_areas'])}")
        print(f"      💬 Communication Style: {interviewer_bg['communication_style']}")
        
        # Show actual sources found
        print("\n   📖 **VERIFIED INFORMATION SOURCES:**")
        research_data = interviewer_bg.get('research_data', {})
        
        if research_data.get('all_sources'):
            # Show LinkedIn profile first if found
            linkedin_sources = [s for s in research_data['all_sources'] if 'linkedin' in s.get('url', '').lower()]
            for source in linkedin_sources[:1]:
                print(f"      🔗 LINKEDIN: {source['title']}")
                print(f"          └─ {source['url']}")
            
            # Show other professional sources
            other_sources = [s for s in research_data['all_sources'] if 'linkedin' not in s.get('url', '').lower()]
            for i, source in enumerate(other_sources[:3], 1):
                domain = source['url'].split('/')[2] if len(source['url'].split('/')) > 2 else 'Source'
                print(f"      � {domain.upper()}: {source['title'][:60]}{'...' if len(source['title']) > 60 else ''}")
                print(f"          └─ {source['url']}")
        else:
            print("      ⚠️  No direct sources found - based on industry patterns")
        
        # Show research insights
        research_data = interviewer_bg.get('research_data', {})
        if research_data.get('role_info'):
            print("\n   � **ROLE INSIGHTS FROM RESEARCH:**")
            unique_roles = list(set([info['keyword'] for info in research_data['role_info'][:3]]))
            for role in unique_roles:
                print(f"      • {role.title()}")
        
        if research_data.get('technical_expertise'):
            print("\n   🔧 **TECHNICAL EXPERTISE FOUND:**")
            unique_tech = list(set([info['keyword'] for info in research_data['technical_expertise'][:5]]))
            for tech in unique_tech:
                print(f"      • {tech.title()}")
        
        print("\n   💡 **CONNECTION POINTS:**")
        for interest in interviewer_bg['likely_interests']:
            print(f"      • Show interest in {interest}")
        
        # Show confidence level and recommendations
        confidence = interviewer_bg.get('research_confidence', 'low')
        if confidence == 'high':
            print("\n   ✅ **HIGH CONFIDENCE RESEARCH** - Use specific details in conversation")
        elif confidence == 'medium':
            print("\n   ⚠️  **MEDIUM CONFIDENCE RESEARCH** - Verify details, use general approach")
        else:
            print("\n   ❌ **LOW CONFIDENCE RESEARCH** - Manual LinkedIn search recommended")
        
        # COMPANY & ROLE RESEARCH INSIGHTS
        print_section(f"COMPANY RESEARCH: {company_name}", "🏢")
        
        if company_research and "error" not in company_research:
            print("   ✅ **Company Intelligence Gathered:**")
            research_count = 0
            for query_key, results in company_research.items():
                if isinstance(results, list) and results:
                    print(f"\n   📊 {query_key.replace('_', ' ').title()}:")
                    for result in results[:2]:
                        print(f"      • {result.get('title', 'Research finding')}")
                        research_count += 1
            print(f"\n   📈 **Total Research Points:** {research_count} insights gathered")
        else:
            print("   ⚠️  Limited company research available - generating AI insights...")
            
        # TECHNICAL PREP
        print_section("TECHNICAL PREPARATION", "🔧")
        print("   🧠 Generating role-specific technical prep guide...")
        
        tech_prep = await generate_technical_prep_topics(role_title, company_name)
        
        print("   **Core Technologies to Review:**")
        for tech in tech_prep['core_technologies']:
            print(f"      • {tech}")
        
        print("\n   **Programming Languages:**")
        for lang in tech_prep['programming_languages']:
            print(f"      • {lang}")
        
        print("\n   **Key Concepts to Study:**")
        for concept in tech_prep['concepts_to_review']:
            print(f"      📚 **{concept['topic']}**")
            print(f"         Why: {concept['description']}")
            print(f"         Focus: {', '.join(concept['key_points'])}")
        
        print("\n   **Hands-on Practice:**")
        for practice in tech_prep['hands_on_practice']:
            print(f"      🛠️  {practice}")
        
        print("\n   **Common Interview Topics:**")
        for category in tech_prep['common_interview_topics']:
            print(f"      📋 **{category['category']}**")
            print(f"         Topics: {', '.join(category['topics'])}")
            print(f"         Prep Tip: {category['preparation_tip']}")
        
        # QUESTIONS TO ASK
        print_section("STRATEGIC QUESTIONS TO ASK", "❓")
        print("   🎯 Research-informed questions that show preparation:")
        
        questions = await generate_company_specific_questions(company_name, role_title, company_research)
        for question in questions:
            print(question)
        
        # PERSONAL NARRATIVE
        print_section("PERSONAL NARRATIVE FRAMEWORK", "📖")
        print("   📝 Structured approach to crafting your story...")
        
        narrative_guide = await generate_personal_narrative_guide(role_title, company_name)
        
        print("   **Self-Reflection Questions:**")
        for question in narrative_guide['why_field_questions']:
            print(f"      🤔 {question}")
        
        print(f"\n   **Why {company_name}? Framework:**")
        framework = narrative_guide['why_company_framework']
        print("      📊 Research These Points:")
        for point in framework['research_points']:
            print(f"         • {point}")
        print("      🔗 Connection Strategy:")
        for point in framework['connection_points']:
            print(f"         • {point}")
        print(f"      💭 Response Template: {framework['example_response_structure']}")
        
        print(f"\n   **Why {role_title}? Framework:**")
        role_framework = narrative_guide['why_role_framework']
        print("      🎯 Skill Alignment:")
        for point in role_framework['skill_alignment']:
            print(f"         • {point}")
        print(f"      📈 Growth Narrative: {role_framework['growth_narrative']}")
        print(f"      💭 Response Template: {role_framework['example_response_structure']}")
        
        # RESUME/PORTFOLIO PREP
        print_section("RESUME & PORTFOLIO PREPARATION", "📄")
        print("   🎯 **Be Ready to Explain:**")
        
        if "AI" in role_title or "Cloud" in role_title:
            print("      🤖 **AI/Cloud Projects:**")
            print("         • Any machine learning or data analysis projects")
            print("         • Cloud platform experience (AWS, GCP, Azure)")
            print("         • API development or integration work")
            print("         • Automation or scripting projects")
        
        print("\n      🚧 **Challenge Stories (Use STAR Method):**")
        for story in narrative_guide['story_preparation']:
            print(f"         📚 **{story['story_type']}**")
            print(f"            Framework: {story['framework']}")
            print(f"            Include: {', '.join(story['key_elements'])}")
        
        print("\n      💡 **What Excites You Most:**")
        if "AI" in role_title:
            print("         • Solving problems with intelligent systems")
            print("         • Learning cutting-edge ML techniques")
            print("         • Impact of AI on industry/society")
        if "Cloud" in role_title:
            print("         • Building scalable, distributed systems")
            print("         • Modern development practices (DevOps, CI/CD)")
            print("         • Cloud-native architecture patterns")
        
        print("\n" + "="*50)
    
    # FINAL SUCCESS CHECKLIST
    print_banner("FINAL SUCCESS CHECKLIST", "🏆")
    print("📋 **24 Hours Before:**")
    print("   ✅ Confirm interview time and platform")
    print("   ✅ Review company research notes")
    print("   ✅ Practice key stories using STAR method")
    print("   ✅ Prepare questions to ask (have backup questions)")
    print("   ✅ Test all technology")
    
    print("\n📋 **Day Of Interview:**")
    print("   ✅ Join 5 minutes early")
    print("   ✅ Have resume and notes ready")
    print("   ✅ Smile and show enthusiasm")
    print("   ✅ Ask thoughtful questions")
    print("   ✅ Send thank-you email within 24 hours")
    
    print("\n🎯 **Success Metrics:**")
    print("   • Demonstrate specific knowledge about the company")
    print("   • Show technical competence relevant to the role")
    print("   • Ask insightful questions that show research")
    print("   • Tell compelling stories about your experience")
    print("   • Express genuine enthusiasm for the opportunity")
    
    print_banner("ENHANCED PREP GUIDE COMPLETE! 🚀", "🎉")
    print("📊 All research completed, questions prepared, narratives structured!")
    print("💪 You're ready to make a great impression!")


if __name__ == "__main__":
    asyncio.run(generate_enhanced_prep_guide())
