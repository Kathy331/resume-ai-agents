# agents/entity_extractor/patterns.py

from spacy.language import Language
from spacy.matcher import Matcher

def add_patterns(nlp: Language):
    matcher = Matcher(nlp.vocab)

    # CANDIDATE - Look for names after greetings, but don't include the greeting
    matcher.add("CANDIDATE", [
        # Match just the name part after greetings - single name only
        [{"LOWER": {"IN": ["hi", "hello", "dear", "hey"]}}, {"IS_TITLE": True, "POS": "PROPN", "LENGTH": {">=": 3}}],
        # Full names (first + last) but exclude common job titles
        [{"IS_TITLE": True, "POS": "PROPN", "LOWER": {"NOT_IN": ["software", "product", "data", "backend", "frontend", "full"]}}, 
         {"IS_TITLE": True, "POS": "PROPN", "LOWER": {"NOT_IN": ["engineer", "manager", "scientist", "developer", "designer"]}}],
        # Names with titles like "Dr. S. Patel"
        [{"LOWER": {"IN": ["dr", "mr", "ms", "mrs", "prof"]}}, {"IS_PUNCT": True, "OP": "?"}, 
         {"IS_TITLE": True, "POS": "PROPN"}, {"IS_TITLE": True, "POS": "PROPN", "OP": "?"}],
    ])

    # ROLE - Job positions and roles
    matcher.add("ROLE", [
        # Standard job titles
        [{"LOWER": {"IN": ["software", "backend", "frontend", "full", "data", "product", "ux", "ui"]}}, 
         {"LOWER": {"IN": ["engineer", "developer", "scientist", "manager", "designer", "stack"]}}],
        # Internship roles
        [{"LOWER": {"IN": ["software", "engineering", "research", "ai", "ux", "data"]}}, 
         {"LOWER": {"IN": ["internship", "intern"]}}],
        # Executive roles
        [{"LOWER": {"IN": ["cto", "ceo", "coo", "head"]}}],
        # Multi-word roles like "Full Stack Developer"
        [{"LOWER": "full"}, {"LOWER": "stack"}, {"LOWER": {"IN": ["developer", "engineer"]}}],
        # "AI Research Internship"
        [{"LOWER": "ai"}, {"LOWER": "research"}, {"LOWER": "internship"}],
    ])

    # COMPANY - Company names and organizations
    matcher.add("COMPANY", [
        # Company names WITHOUT the preposition - match what comes after "at", "from", etc.
        [{"LOWER": "at"}, {"IS_TITLE": True, "POS": "PROPN", "OP": "+"}],
        [{"LOWER": "from"}, {"IS_TITLE": True, "POS": "PROPN", "OP": "+"}],
        # Multi-word company names (but not team names)
        [{"IS_TITLE": True, "POS": "PROPN", "LOWER": {"NOT_IN": ["recruiting", "hr", "hiring", "talent", "team"]}}, 
         {"IS_TITLE": True, "POS": "PROPN", "LOWER": {"NOT_IN": ["team", "labs", "recruiting"]}}],
        # Companies with "Labs", "AI", "Design" suffixes
        [{"IS_TITLE": True, "POS": "PROPN"}, {"LOWER": {"IN": ["labs", "ai", "design", "works", "shell", "mind"]}}],
        # Exclude team references
        [{"IS_TITLE": True, "POS": "PROPN"}, {"IS_TITLE": True, "POS": "PROPN"}, 
         {"LOWER": {"NOT_IN": ["team", "recruiting", "hiring"]}}],
    ])

    # DATE - Various date formats (be more specific to avoid false positives)
    matcher.add("DATE", [
        # spaCy's built-in DATE entities
        [{"ENT_TYPE": "DATE"}],
        # Full day names only
        [{"LOWER": {"IN": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]}}],
        # Full month names + day
        [{"LOWER": {"IN": ["january", "february", "march", "april", "may", "june", 
                          "july", "august", "september", "october", "november", "december"]}}, 
         {"IS_DIGIT": True}],
        # Abbreviated month + day
        [{"LOWER": {"IN": ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]}}, 
         {"IS_DIGIT": True}],
        # 4-digit years only
        [{"SHAPE": "dddd", "IS_DIGIT": True, "TEXT": {"REGEX": r"^20\d{2}$"}}],
        # Relative time phrases (complete phrases only)
        [{"LOWER": "this"}, {"LOWER": "week"}],
        [{"LOWER": "next"}, {"LOWER": "week"}],
        [{"LOWER": "this"}, {"LOWER": "month"}],
        [{"LOWER": "next"}, {"LOWER": "month"}],
    ])

    # DURATION - Time durations
    matcher.add("DURATION", [
        # "45 minutes", "1 hour", "45-minute"
        [{"LIKE_NUM": True}, {"LOWER": {"IN": ["minute", "minutes", "hour", "hours", "hr", "hrs"]}}],
        # "60-minute", "30-minute" (with dash)
        [{"TEXT": {"REGEX": r"^\d{1,3}(-|–)minute$"}}],
        # "24 hours before"
        [{"LIKE_NUM": True}, {"LOWER": "hours"}, {"LOWER": "before"}],
    ])

    # FORMAT - Interview formats
    matcher.add("FORMAT", [
        # Video conferencing platforms
        [{"LOWER": {"IN": ["zoom", "teams", "meet", "webex", "skype"]}}],
        # Format descriptions
        [{"LOWER": {"IN": ["remote", "online", "video", "phone", "in-person", "virtual"]}}],
        # "Google Meet", "Microsoft Teams"
        [{"LOWER": "google"}, {"LOWER": "meet"}],
        [{"LOWER": "microsoft"}, {"LOWER": "teams"}],
        # Format specifications like "Format: Zoom"
        [{"LOWER": "format"}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"IN": ["zoom", "remote", "online"]}}],
    ])

    # INTERVIEWER - People conducting interviews
    matcher.add("INTERVIEWER", [
        # "with John Doe", "Interview with: Jane Doe"
        [{"LOWER": "with"}, {"IS_TITLE": True, "POS": "PROPN"}, {"IS_TITLE": True, "POS": "PROPN", "OP": "?"}],
        [{"LOWER": "interview"}, {"LOWER": "with"}, {"IS_PUNCT": True, "OP": "?"}, 
         {"IS_TITLE": True, "POS": "PROPN"}, {"IS_TITLE": True, "POS": "PROPN", "OP": "?"}],
        # Professional titles
        [{"LOWER": {"IN": ["dr", "prof", "mr", "ms", "mrs"]}}, {"IS_PUNCT": True, "OP": "?"}, 
         {"IS_TITLE": True}, {"IS_TITLE": True, "OP": "?"}],
        # Team roles
        [{"LOWER": {"IN": ["head", "lead", "director", "manager"]}}, {"LOWER": "of"}, {"IS_TITLE": True}],
    ])

    # LINK - URLs and links
    matcher.add("LINK", [
        [{"LIKE_URL": True}],
        [{"TEXT": {"REGEX": r"^https?://.*"}}],
        # Common meeting link patterns
        [{"TEXT": {"REGEX": r".*zoom\.us.*"}}],
        [{"TEXT": {"REGEX": r".*calendly\.com.*"}}],
    ])

    # TIME - Specific times
    matcher.add("TIME", [
        # "2:00pm", "11am", "4:15pm"
        [{"TEXT": {"REGEX": r"^\d{1,2}:\d{2}(am|pm|AM|PM)$"}}],
        [{"TEXT": {"REGEX": r"^\d{1,2}(am|pm|AM|PM)$"}}],
        # Time ranges "2:00pm – 3:00pm"
        [{"TEXT": {"REGEX": r"^\d{1,2}:\d{2}(am|pm|AM|PM)$"}}, 
         {"IS_PUNCT": True}, 
         {"TEXT": {"REGEX": r"^\d{1,2}:\d{2}(am|pm|AM|PM)$"}}],
    ])

    # LOCATION - Physical and virtual locations
    matcher.add("LOCATION", [
        # Room numbers and building names
        [{"LOWER": "room"}, {"IS_DIGIT": True}],
        [{"IS_TITLE": True}, {"LOWER": "center"}],
        # "Iribe Center, Room 1105"
        [{"IS_TITLE": True}, {"LOWER": "center"}, {"IS_PUNCT": True, "OP": "?"}, 
         {"LOWER": "room"}, {"IS_DIGIT": True}],
        # Virtual locations
        [{"LOWER": {"IN": ["online", "virtual"]}}, {"LOWER": "event"}],
    ])

    return matcher


# Test function to help debug patterns
def test_patterns(nlp, matcher, text_samples):
    """Test patterns against sample texts and return results"""
    results = []
    
    for i, text in enumerate(text_samples):
        doc = nlp(text)
        matches = matcher(doc)
        
        sample_results = {
            'sample': i + 1,
            'text': text,
            'matches': []
        }
        
        for match_id, start, end in matches:
            label = nlp.vocab.strings[match_id]
            span = doc[start:end]
            sample_results['matches'].append({
                'label': label,
                'text': span.text,
                'start': start,
                'end': end
            })
        
        results.append(sample_results)
    
    return results