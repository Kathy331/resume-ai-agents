# agents/memory_systems/interview_store/interview_utils.py
"""
Shared utilities for interview store operations
"""

import json
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, Union
from difflib import SequenceMatcher

# Import the clean models
from shared.models import EntityExtractionResult, InterviewData

def get_first_or_none(items: List[str]) -> Optional[str]:
    """Get first item from list or None, with data cleaning."""
    if not items:
        return None
    
    # Take the first item
    first_item = items[0]
    
    # Clean up the data - remove common artifacts
    if isinstance(first_item, str):
        # Remove quotes, brackets, and common extraction artifacts
        cleaned = first_item.strip().strip('"\'[](){}')
        
        # Handle cases where extracted text contains multiple names or formats
        # Common patterns: "Format, Archana" -> "Archana"
        if ',' in cleaned:
            parts = cleaned.split(',')
            # Look for actual names (capitalized words)
            for part in parts:
                part = part.strip()
                if part and part[0].isupper() and len(part) > 2:
                    # Skip common artifacts like "Format", "Subject", "Re", etc.
                    if part.lower() not in ['format', 'subject', 're', 'fw', 'fwd', 'email', 'from', 'to']:
                        return part
        
        # Handle cases where there are multiple words, pick the most likely name
        words = cleaned.split()
        if len(words) > 1:
            # Look for capitalized words that are likely names
            for word in words:
                if word and word[0].isupper() and len(word) > 2:
                    if word.lower() not in ['format', 'subject', 're', 'fw', 'fwd', 'email', 'from', 'to']:
                        return word
        
        # Return cleaned version if it looks valid
        if cleaned and len(cleaned) > 1:
            return cleaned
    
    return first_item if first_item else None


def create_content_hash(entities: Union[Dict[str, Any], EntityExtractionResult]) -> str:
    """Create hash for exact duplicate detection."""
    if isinstance(entities, EntityExtractionResult):
        # Use the pydantic model's dict representation
        content = json.dumps(entities.dict(), sort_keys=True)
    else:
        # Fallback for raw dict (legacy)
        content = json.dumps(entities, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()


def entities_to_extraction_result(entities: Dict[str, Any]) -> EntityExtractionResult:
    """Convert raw entities dict to EntityExtractionResult model."""
    return EntityExtractionResult(
        candidates=entities.get("CANDIDATE", []),
        companies=entities.get("COMPANY", []),
        roles=entities.get("ROLE", []),
        interviewers=entities.get("INTERVIEWER", []),
        dates=entities.get("DATE", []),
        times=entities.get("TIME", []),
        durations=entities.get("DURATION", []),
        locations=entities.get("LOCATION", []),
        email_id=entities.get("email_id")
    )


def clean_interviewer_name(interviewer_list: List[str]) -> Optional[str]:
    """Specifically clean interviewer names from extraction artifacts."""
    if not interviewer_list:
        return None
    
    # Join all items if multiple, then clean
    raw_text = ' '.join(interviewer_list) if isinstance(interviewer_list, list) else str(interviewer_list)
    
    # Remove common email artifacts
    cleaned = raw_text.strip().strip('"\'[](){}')
    
    # Handle comma-separated values (e.g., "Format, Archana")
    if ',' in cleaned:
        parts = cleaned.split(',')
        for part in parts:
            part = part.strip()
            # Look for actual human names
            if part and len(part) > 2 and part[0].isupper():
                # Skip common email artifacts
                if part.lower() not in ['format', 'subject', 're', 'fw', 'fwd', 'email', 'from', 'to', 'dear', 'hi', 'hello']:
                    # Check if it looks like a name (contains only letters, spaces, hyphens, apostrophes)
                    if all(c.isalpha() or c in " '-." for c in part):
                        return part
    
    # Handle space-separated words
    words = cleaned.split()
    potential_names = []
    
    for word in words:
        word = word.strip()
        if word and len(word) > 2 and word[0].isupper():
            # Skip artifacts and common words
            if word.lower() not in ['format', 'subject', 're', 'fw', 'fwd', 'email', 'from', 'to', 'dear', 'hi', 'hello', 'best', 'regards']:
                # Check if it looks like a name
                if all(c.isalpha() or c in "'-." for c in word):
                    potential_names.append(word)
    
    # Return the first potential name found, or the cleaned original
    if potential_names:
        return potential_names[0]
    elif cleaned and len(cleaned) > 1:
        return cleaned
    
    return None


def extraction_result_to_interview_data(
    extraction: EntityExtractionResult, 
    email_id: Optional[str] = None,
    status: str = "preparing"
) -> InterviewData:
    """Convert EntityExtractionResult to InterviewData model."""
    return InterviewData(
        email_id=email_id or extraction.email_id,
        candidate_name=get_first_or_none(extraction.candidates),
        company_name=get_first_or_none(extraction.companies),
        role=get_first_or_none(extraction.roles),
        interviewer=clean_interviewer_name(extraction.interviewers),  # Use specialized cleaning
        interview_date=get_first_or_none(extraction.dates),
        interview_time=get_first_or_none(extraction.times),
        duration=get_first_or_none(extraction.durations),
        location=get_first_or_none(extraction.locations),
        status=status,
        raw_entities=json.dumps(extraction.dict())
    )


def text_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity using SequenceMatcher."""
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object."""
    if not date_str:
        return None
        
    formats = [
        "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", 
        "%B %d, %Y", "%b %d, %Y", "%Y-%m-%d %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def calculate_similarity(entities: Dict, interview: Dict, 
                         similarity_threshold: float, 
                         date_tolerance_days: int,
                         target_date: datetime = None) -> Tuple[float, List[str]]:
    """Calculate similarity between entities and stored interview."""
    score = 0.0
    reasons = []
    
    candidate = get_first_or_none(entities.get("CANDIDATE", []))
    company = get_first_or_none(entities.get("COMPANY", []))
    role = get_first_or_none(entities.get("ROLE", []))
    
    # Candidate similarity (40% weight)
    if candidate and interview.get("candidate_name"):
        sim = text_similarity(candidate, interview["candidate_name"])
        if sim > similarity_threshold:
            score += 0.4
            reasons.append(f"Candidate match: {sim:.2f}")
    
    # Company similarity (30% weight)
    if company and interview.get("company_name"):
        sim = text_similarity(company, interview["company_name"])
        if sim > similarity_threshold:
            score += 0.3
            reasons.append(f"Company match: {sim:.2f}")
    
    # Role similarity (20% weight)
    if role and interview.get("role"):
        sim = text_similarity(role, interview["role"])
        if sim > similarity_threshold:
            score += 0.2
            reasons.append(f"Role match: {sim:.2f}")
    
    # Date proximity (10% weight)
    if target_date and interview.get("interview_date"):
        interview_date = parse_date(interview["interview_date"])
        if interview_date and abs((target_date - interview_date).days) <= date_tolerance_days:
            score += 0.1
            reasons.append("Date proximity")
    
    return score, reasons