# agents/entity_extractor/use_model.py

import spacy
import os
import sys
import json
from pathlib import Path
from collections import defaultdict

# To run this script:
# python3 agents/entity_extractor/use_model.py

# Ensure project root is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.entity_extractor.patterns import add_patterns


def clean_matches(matches, doc, nlp):
    """Remove duplicate and overlapping matches, keeping the most specific ones"""
    # Convert matches to a more workable format
    match_list = []
    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        span_text = doc[start:end].text.strip()
        match_list.append((label, start, end, span_text))
    
    # Remove overlapping matches, keeping the most specific/relevant ones
    cleaned_matches = []
    match_list.sort(key=lambda x: (x[1], x[2]))  # Sort by start position
    
    for i, (label, start, end, span_text) in enumerate(match_list):
        # Skip if this span overlaps with a higher priority match we've already kept
        overlap = False
        for kept_label, kept_start, kept_end, kept_text in cleaned_matches:
            if not (end <= kept_start or start >= kept_end):  # If they overlap
                # Keep the more specific match based on priority and length
                priority_order = ['CANDIDATE', 'ROLE', 'COMPANY', 'INTERVIEWER', 'TIME', 'DATE', 'LOCATION', 'LINK', 'DURATION', 'FORMAT']
                
                current_priority = priority_order.index(label) if label in priority_order else len(priority_order)
                kept_priority = priority_order.index(kept_label) if kept_label in priority_order else len(priority_order)
                
                if current_priority < kept_priority or (current_priority == kept_priority and len(span_text) > len(kept_text)):
                    # Remove the old match and continue with current
                    cleaned_matches = [(l, s, e, t) for l, s, e, t in cleaned_matches if not (l == kept_label and s == kept_start and e == kept_end)]
                else:
                    overlap = True
                    break
        
        if not overlap:
            cleaned_matches.append((label, start, end, span_text))
    
    return [(label, start, end) for label, start, end, _ in cleaned_matches]

def extract_entities_from_email(email_data, nlp, matcher):
    """Extract structured entities from a single email"""
    text = email_data.get("body", "")
    subject = email_data.get("subject", "")
    from_email = email_data.get("from_email", "")
    
    # Process both subject and body
    full_text = f"{subject}. {text}"
    doc = nlp(full_text)
    matches = matcher(doc)
    
    # Clean up matches
    cleaned_matches = clean_matches(matches, doc, nlp)
    
    # Group entities by type
    entities = defaultdict(list)
    
    # Track context to distinguish candidates from interviewers
    interviewer_contexts = []
    candidate_contexts = []
    
    # First pass: identify interviewer contexts
    for label, start, end in cleaned_matches:
        if label == "INTERVIEWER":
            interviewer_contexts.append((start, end))
    
    # Second pass: process all entities with context awareness
    for label, start, end in cleaned_matches:
        span = doc[start:end]
        entity_text = span.text.strip()
        
        # Skip very short or empty matches
        if len(entity_text) < 2:
            continue
            
        # Clean up the entity text
        entity_text = entity_text.replace('\n', ' ').strip()
        
        # Specific cleaning for each entity type
        if label == "CANDIDATE":
            # For patterns that include greetings, extract just the name
            if entity_text.lower().startswith(('hi ', 'hello ', 'dear ', 'hey ')):
                # Split and take the name part
                parts = entity_text.split()
                if len(parts) >= 2:
                    entity_text = ' '.join(parts[1:])  # Everything after the greeting
            
            # Skip if it contains obvious non-name words
            skip_words = ['engineer', 'manager', 'scientist', 'developer', 'team', 'recruiting', 
                         'labs', 'design', 'shell', 'acquisition', 'interview', 'internship',
                         'research', 'online', 'event', 'options', 'center', 'startup', 'bitwise', 
                         'ripple', 'senior', 'principal', 'technical', 'invitation']
            if any(word in entity_text.lower() for word in skip_words):
                continue
                
            # Skip if it's too generic or looks like a company/role
            if entity_text.lower() in ['tue jul', 'date options', 'talent acquisition', 'senior data', 'principal data']:
                continue
                
            # Check if this name appears in an interviewer context
            is_interviewer = False
            for int_start, int_end in interviewer_contexts:
                if start >= int_start and end <= int_end:
                    is_interviewer = True
                    break
            
            # If it's in an interviewer context, skip it from candidates
            if is_interviewer:
                continue
        
        elif label == "INTERVIEWER":
            # NEW: Extract PERSON entities using spaCy's NER
            names = []
            for ent in span.ents:
                if ent.label_ == "PERSON" and len(ent.text) > 3:
                    names.append(ent.text)
            
            # Add unique names
            for name in names:
                if name and name not in entities["INTERVIEWER"]:
                    entities["INTERVIEWER"].append(name)
            continue  # Skip further processing for this match
        
        elif label == "COMPANY":
            # Clean up "at Company" patterns - we want just the company name
            if entity_text.lower().startswith('at '):
                entity_text = entity_text[3:].strip()
            
            # Skip team references and other non-company names
            skip_words = ['team', 'recruiting', 'hiring', 'acquisition', 'interview', 'invitation', 'technical']
            if any(word in entity_text.lower() for word in skip_words):
                continue
        
        elif label == "DATE":
            # Skip standalone numbers, room numbers, and other non-dates
            if entity_text.isdigit() and int(entity_text) < 32:
                continue
            if entity_text.lower() in ['room', '1105']:
                continue
        
        elif label == "DURATION":
            # Make sure it's actually a duration
            if not any(word in entity_text.lower() for word in ['minute', 'minutes', 'hour', 'hours', 'hr', 'hrs']):
                continue
        
        # For non-interviewer entities, add normally (avoid duplicates)
        if label != "INTERVIEWER" and entity_text and entity_text not in entities[label]:
            entities[label].append(entity_text)
    
    # NEW: Add entity filtering to remove false positives
    filter_phrases = {
        "INTERVIEWER": ["team", "labs", "recruiting", "talent", "acquisition"],
        "COMPANY": ["candidate", "interview", "schedule", "options"],
        "ROLE": ["interview", "round", "session", "discussion"]
    }
    
    for entity_type, phrases in filter_phrases.items():
        if entity_type in entities:
            entities[entity_type] = [
                e for e in entities[entity_type] 
                if not any(phrase in e.lower() for phrase in phrases)
            ]
    
    # Add email metadata
    entities['FROM_EMAIL'] = [from_email]
    entities['SUBJECT'] = [subject]
    
    return dict(entities)

def print_detailed_results(email_data, entities, sample_num):
    """Print results in a more organized format"""
    print(f"\n{'='*60}")
    print(f"SAMPLE {sample_num}")
    print(f"{'='*60}")
    
    print(f"📧 FROM: {email_data.get('from_email', 'N/A')}")
    print(f"📋 SUBJECT: {email_data.get('subject', 'N/A')}")
    print()
    
    # Print body with some formatting
    body = email_data.get('body', '')
    print("📄 BODY:")
    print("-" * 40)
    print(body[:500] + "..." if len(body) > 500 else body)
    print("-" * 40)
    print()
    
    # Print extracted entities in a nice format
    print("🔍 EXTRACTED ENTITIES:")
    print("-" * 40)
    
    entity_order = ['CANDIDATE', 'COMPANY', 'ROLE', 'INTERVIEWER', 'DATE', 'TIME', 'DURATION', 'FORMAT', 'LOCATION', 'LINK']
    
    for entity_type in entity_order:
        if entity_type in entities and entities[entity_type]:
            print(f"  {entity_type:12}: {', '.join(entities[entity_type])}")
    
    # Print any other entities not in the main order
    for entity_type, values in entities.items():
        if entity_type not in entity_order + ['FROM_EMAIL', 'SUBJECT'] and values:
            print(f"  {entity_type:12}: {', '.join(values)}")
    
    print()

def generate_summary_report(all_entities):
    """Generate a summary report of all extracted entities"""
    print("\n" + "="*80)
    print("SUMMARY REPORT")
    print("="*80)
    
    # Count entity types across all emails
    entity_counts = defaultdict(int)
    unique_entities = defaultdict(set)
    
    for entities in all_entities:
        for entity_type, values in entities.items():
            if entity_type not in ['FROM_EMAIL', 'SUBJECT']:
                entity_counts[entity_type] += len(values)
                unique_entities[entity_type].update(values)
    
    print("\n📊 ENTITY TYPE STATISTICS:")
    print("-" * 50)
    for entity_type in sorted(entity_counts.keys()):
        count = entity_counts[entity_type]
        unique_count = len(unique_entities[entity_type])
        print(f"  {entity_type:12}: {count:3d} total, {unique_count:3d} unique")
    
    print(f"\n📧 TOTAL EMAILS PROCESSED: {len(all_entities)}")
    
    # Show some interesting findings
    all_companies = set()
    all_roles = set()
    all_candidates = set()
    
    for entities in all_entities:
        all_companies.update(entities.get('COMPANY', []))
        all_roles.update(entities.get('ROLE', []))
        all_candidates.update(entities.get('CANDIDATE', []))
    
    if all_companies:
        print(f"\n🏢 COMPANIES FOUND: {', '.join(sorted(all_companies))}")
    if all_roles:
        print(f"\n💼 ROLES FOUND: {', '.join(sorted(all_roles))}")
    if all_candidates:
        print(f"\n👤 CANDIDATES FOUND: {', '.join(sorted(all_candidates))}")

def main():
    # Load spaCy model and add custom patterns
    print("Loading spaCy model and patterns...")
    nlp = spacy.load("en_core_web_sm")
    # NEW: Add entity merging to handle multi-token names
    nlp.add_pipe("merge_entities")  
    matcher = add_patterns(nlp)
    
    # Load test email data
    data_path = Path("tests/sample_data/interview_invites.json")
    if not data_path.exists():
        print(f"❌ Error: Could not find data file at {data_path}")
        return
    
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} email samples\n")
    
    # Process each email and collect results
    all_entities = []
    
    for i, email_data in enumerate(data, 1):
        entities = extract_entities_from_email(email_data, nlp, matcher)
        all_entities.append(entities)
        print_detailed_results(email_data, entities, i)
    
    # Generate summary report
    generate_summary_report(all_entities)

if __name__ == "__main__":
    main()