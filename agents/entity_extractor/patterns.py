# agents/entity_extractor/patterns.py

from spacy.language import Language
from spacy.matcher import Matcher

def add_patterns(nlp: Language):
    matcher = Matcher(nlp.vocab)

    # CANDIDATE - Only actual person names, exclude greetings and company/role words
    matcher.add("CANDIDATE", [
        # Names after greetings - capture ONLY the name, not the greeting
        # More flexible approach: any proper noun after greeting, but exclude business terms
        [{"LOWER": {"IN": ["hi", "hello", "dear", "hey"]}}, 
         {"IS_TITLE": True, "POS": "PROPN", "LENGTH": {">=": 3}, 
          "LOWER": {"NOT_IN": ["google", "zoom", "meet", "teams", "slack", "software", "product", "data", "backend", "frontend", "full", "engineering", "research", "interview", "shell", "design", "labs", "team", "recruiting", "talent", "acquisition", "online", "event", "options", "center", "jul", "tue", "wed", "thu", "fri", "sat", "sun", "senior", "principal", "technical", "marketing", "manager", "director", "internship", "opportunity", "candidate", "there", "everyone", "all", "applicant", "intern", "student"]}}],
        
        # Do NOT match standalone names without clear context - too error-prone
        # Only match names when they clearly appear in candidate context
    ])

    # ROLE - Job positions and roles (more specific patterns)
    matcher.add("ROLE", [
        # Specific two-word job titles
        [{"LOWER": "software"}, {"LOWER": "engineer"}],
        [{"LOWER": "backend"}, {"LOWER": "engineer"}],
        [{"LOWER": "frontend"}, {"LOWER": "engineer"}],
        [{"LOWER": "full"}, {"LOWER": "stack"}, {"LOWER": "developer"}],
        [{"LOWER": "data"}, {"LOWER": "scientist"}],
        [{"LOWER": "product"}, {"LOWER": "manager"}],
        [{"LOWER": "marketing"}, {"LOWER": "manager"}],
        [{"LOWER": "brand"}, {"LOWER": "marketing"}, {"LOWER": "manager"}],
        [{"LOWER": "engineering"}, {"LOWER": "manager"}],
        [{"LOWER": "ux"}, {"LOWER": {"IN": ["intern", "designer"]}}],
        [{"LOWER": "ui"}, {"LOWER": "designer"}],
        
        # Generic manager titles
        [{"IS_TITLE": True}, {"LOWER": "manager"}],
        [{"IS_TITLE": True}, {"LOWER": "director"}],
        [{"IS_TITLE": True}, {"LOWER": "lead"}],
        
        # Internship roles
        [{"LOWER": "software"}, {"LOWER": "engineering"}, {"LOWER": "internship"}],
        [{"LOWER": "ai"}, {"LOWER": "research"}, {"LOWER": "internship"}],
        [{"LOWER": "ux"}, {"LOWER": "internship"}],
        
        # Executive roles
        [{"LOWER": {"IN": ["cto", "ceo", "coo"]}}],
        [{"LOWER": "head"}, {"LOWER": "of"}, {"IS_TITLE": True}],
        [{"LOWER": "engineering"}, {"LOWER": "lead"}],
    ])

    # COMPANY - More precise company name extraction
    matcher.add("COMPANY", [
        # Companies after "at" - exclude job titles and roles
        [{"LOWER": "at"}, {"POS": "PROPN", 
          "LOWER": {"NOT_IN": ["marketing", "engineering", "software", "product", "data", "brand", "senior", "junior", "lead", "director", "manager", "google", "zoom", "meet", "internship", "opportunity", "interview", "session", "call", "meeting"]}}, 
         {"POS": "PROPN", "OP": "?"}],
        
        # Specific multi-token company names
        [{"LOWER": "dandilyonn"}, {"LOWER": "seeds"}],  # "Dandilyonn SEEDS"
        [{"LOWER": "the", "OP": "?"}, {"LOWER": "dandilyonn"}, {"LOWER": "seeds"}],  # "the Dandilyonn SEEDS" (optional "the")
        [{"LOWER": "launchpad"}, {"LOWER": "ai"}],
        [{"LOWER": "startup"}, {"LOWER": "shell"}],
        [{"LOWER": "bitwise"}, {"LOWER": "labs"}],
        [{"LOWER": "ripple"}, {"LOWER": "design"}],
        [{"LOWER": "cognivault"}, {"LOWER": "ai", "OP": "?"}, {"LOWER": "labs", "OP": "?"}],
        
        # Single token company names
        [{"LOWER": "techflow"}],
        [{"LOWER": "pixelwave"}],
        [{"LOWER": "juteq"}],
        [{"LOWER": "seeds"}],
        
        # Single word well-known companies (exclude platform/tool names)
        [{"IS_TITLE": True, "LOWER": {"IN": ["novaworks", "cloudspire", "quantmind", "orbit", "pixelwave", "techflow", "juteq", "seeds", "openai", "canva", "dropbox", "microsoft", "apple", "facebook", "meta", "amazon", "netflix", "spotify", "uber", "lyft", "airbnb", "stripe", "slack", "notion", "figma", "github", "gitlab", "atlassian", "salesforce", "oracle", "ibm", "intel", "nvidia", "amd", "tesla", "spacex", "techcorp", "dasher"]}}],
        
        # DO NOT match phrases like "with Google Meet", "for Internship", etc.
        # Only match actual company names in proper context
        
        # Company names with recruiting/team context
        [{"IS_TITLE": True, "POS": "PROPN", 
          "LOWER": {"NOT_IN": ["dear", "hi", "hello", "hey", "best", "thanks", "sincerely", "regards", "google", "zoom", "meet", "internship", "opportunity", "interview", "session", "call", "meeting", "marketing", "engineering", "software", "product", "data", "brand", "senior", "junior", "lead", "director", "manager", "recruiting", "hr", "hiring", "talent", "team", "with", "for"]}}, 
         {"LOWER": {"IN": ["recruiting", "team", "hr"]}}],
    ])

    # DURATION - More comprehensive time durations
    matcher.add("DURATION", [
        # Standard patterns like "45 minutes", "1 hour"
        [{"LIKE_NUM": True}, {"LOWER": {"IN": ["minute", "minutes", "hour", "hours", "hr", "hrs"]}}],
        # Hyphenated patterns like "45-minute", "30-minute"
        [{"TEXT": {"REGEX": r"^\d{1,3}(-|–)minute$"}}],
        # "90-minute session"
        [{"TEXT": {"REGEX": r"^\d{1,3}(-|–)minute$"}}, {"LOWER": {"IN": ["session", "interview", "call"]}}],
        # "24 hours before"
        [{"LIKE_NUM": True}, {"LOWER": "hours"}, {"LOWER": "before"}],
    ])

    # DATE - Much more restrictive to avoid false positives
    matcher.add("DATE", [
        # spaCy's built-in DATE entities (but we'll filter these)
        [{"ENT_TYPE": "DATE"}],
        
        # Complete day names only
        [{"LOWER": {"IN": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]}}],
        
        # Month + day combinations (must be together)
        [{"LOWER": {"IN": ["january", "february", "march", "april", "may", "june", 
                          "july", "august", "september", "october", "november", "december"]}}, 
         {"IS_DIGIT": True}],
        [{"LOWER": {"IN": ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]}}, 
         {"IS_DIGIT": True}],
        
        # 4-digit years only (20xx format)
        [{"SHAPE": "dddd", "IS_DIGIT": True, "TEXT": {"REGEX": r"^20\d{2}$"}}],
        
        # Complete relative phrases only
        [{"LOWER": "this"}, {"LOWER": "week"}],
        [{"LOWER": "next"}, {"LOWER": "week"}],
        [{"LOWER": "this"}, {"LOWER": "month"}],
        [{"LOWER": "next"}, {"LOWER": "month"}],
        
        # Complete date patterns like "August 23, 2025"
        [{"LOWER": {"IN": ["january", "february", "march", "april", "may", "june", 
                          "july", "august", "september", "october", "november", "december"]}}, 
         {"IS_DIGIT": True}, {"IS_PUNCT": True}, {"SHAPE": "dddd", "IS_DIGIT": True}],
    ])

    # TIME - Specific time patterns
    matcher.add("TIME", [
        # Standard time formats
        [{"TEXT": {"REGEX": r"^\d{1,2}:\d{2}(am|pm|AM|PM)$"}}],
        [{"TEXT": {"REGEX": r"^\d{1,2}(am|pm|AM|PM)$"}}],
        # Time ranges like "2:00pm – 3:00pm"
        [{"TEXT": {"REGEX": r"^\d{1,2}:\d{2}(am|pm|AM|PM)$"}}, 
         {"IS_PUNCT": True}, 
         {"TEXT": {"REGEX": r"^\d{1,2}:\d{2}(am|pm|AM|PM)$"}}],
        # Time ranges like "4:15pm - 5:30pm"
        [{"TEXT": {"REGEX": r"^\d{1,2}:\d{2}(am|pm|AM|PM)$"}}, 
         {"TEXT": "-"}, 
         {"TEXT": {"REGEX": r"^\d{1,2}:\d{2}(am|pm|AM|PM)$"}}],
    ])

    # FORMAT - Interview formats and platforms
    matcher.add("FORMAT", [
        # Video platforms (standalone)
        [{"LOWER": {"IN": ["zoom", "teams", "meet", "webex", "skype"]}}],
        # Format descriptions
        [{"LOWER": {"IN": ["remote", "online", "virtual", "phone"]}}],
        # "Google Meet", "Microsoft Teams"
        [{"LOWER": "google"}, {"LOWER": "meet"}],
        [{"LOWER": "microsoft"}, {"LOWER": "teams"}],
        # "Format: X" patterns
        [{"LOWER": "format"}, {"IS_PUNCT": True, "OP": "?"}, 
         {"LOWER": {"IN": ["zoom", "remote", "online", "phone", "video"]}}],
    ])

    # INTERVIEWER - People conducting interviews (broader patterns)
    matcher.add("INTERVIEWER", [
        # "with [Name]" patterns
        [{"LOWER": "with"}, {"ENT_TYPE": "PERSON", "OP": "+"}],
        [{"LOWER": "with"}, {"IS_TITLE": True}, {"ENT_TYPE": "PERSON", "OP": "+"}],

        # "Interview with: [Name]" patterns
        [{"LOWER": "interview"}, {"LOWER": "with"}, {"IS_PUNCT": True, "OP": "?"}, 
        {"ENT_TYPE": "PERSON", "OP": "+"}],

        # "Interviewers: [Name]" patterns
        [{"LOWER": "interviewers"}, {"IS_PUNCT": True}, {"ENT_TYPE": "PERSON", "OP": "+"}],

        # Names in parentheses patterns
        [{"TEXT": "("}, {"ENT_TYPE": "PERSON", "OP": "+"}, {"TEXT": ")"}],

        # Self-introduction patterns like "I'm [Name]"
        [{"LOWER": "i"}, {"LOWER": "am"}, {"ENT_TYPE": "PERSON", "OP": "+"}],
        [{"LOWER": "i"}, {"TEXT": "'m"}, {"ENT_TYPE": "PERSON", "OP": "+"}],
        [{"LOWER": "this"}, {"LOWER": "is"}, {"ENT_TYPE": "PERSON", "OP": "+"}],
        [{"LOWER": "my"}, {"LOWER": "name"}, {"LOWER": "is"}, {"ENT_TYPE": "PERSON", "OP": "+"}],

        # Signature patterns - names after common signature words
        [{"LOWER": {"IN": ["best", "regards", "thanks", "sincerely"]}}, 
         {"IS_PUNCT": True, "OP": "?"}, {"ENT_TYPE": "PERSON", "OP": "+"}],
        [{"LOWER": "best"}, {"LOWER": "regards"}, {"IS_PUNCT": True, "OP": "?"}, 
         {"ENT_TYPE": "PERSON", "OP": "+"}],
        
        # Extended signature patterns for various closing styles
        [{"LOWER": "with"}, {"LOWER": {"IN": ["warmth", "excitement", "gratitude", "appreciation"]}}, 
         {"IS_PUNCT": True, "OP": "?"}, {"IS_SPACE": True, "OP": "*"}, {"ENT_TYPE": "PERSON", "OP": "+"}],
        [{"LOWER": "with"}, {"LOWER": {"IN": ["warmth", "excitement", "gratitude", "appreciation"]}}, 
         {"LOWER": "and"}, {"LOWER": {"IN": ["excitement", "gratitude", "appreciation", "joy"]}},
         {"IS_PUNCT": True, "OP": "?"}, {"IS_SPACE": True, "OP": "*"}, {"ENT_TYPE": "PERSON", "OP": "+"}],
        
        # More flexible signature patterns that handle line breaks
        [{"LOWER": "excitement"}, {"IS_PUNCT": True}, {"IS_SPACE": True, "OP": "*"}, 
         {"ENT_TYPE": "PERSON", "LENGTH": {">=": 3}}],
        [{"LOWER": {"IN": ["warmth", "gratitude", "excitement"]}}, {"IS_PUNCT": True}, 
         {"IS_SPACE": True, "OP": "*"}, {"ENT_TYPE": "PERSON", "LENGTH": {">=": 3}}],
        
        # Names that appear alone on a line (common in email signatures)
        [{"ENT_TYPE": "PERSON", "IS_TITLE": True, "LENGTH": {">=": 3}, 
          "LOWER": {"NOT_IN": ["seedling", "calamari", "dear", "hi", "hello", "hey", "google", "zoom", "meet"]}}],
        
        # Names with titles/positions in signatures
        [{"ENT_TYPE": "PERSON", "OP": "+"}, {"LOWER": {"IN": ["founder", "ceo", "recruiter", "hr", "manager", "director"]}}],
        [{"ENT_TYPE": "PERSON", "OP": "+"}, {"TEXT": ","}, {"LOWER": {"IN": ["founder", "ceo", "recruiter", "hr", "manager", "director"]}}],
        
        # Sender name patterns
        [{"LOWER": "from"}, {"ENT_TYPE": "PERSON", "OP": "+"}],
        [{"LOWER": "sent"}, {"LOWER": "by"}, {"ENT_TYPE": "PERSON", "OP": "+"}],
    ])

    # LINK - URLs and meeting links
    matcher.add("LINK", [
        [{"LIKE_URL": True}],
        [{"TEXT": {"REGEX": r"^https?://.*"}}],
    ])

    # LOCATION - Physical locations
    matcher.add("LOCATION", [
        # Room patterns
        [{"LOWER": "room"}, {"IS_DIGIT": True}],
        # Building + room combinations
        [{"IS_TITLE": True, "POS": "PROPN"}, {"LOWER": "center"}, {"IS_PUNCT": True, "OP": "?"}, 
         {"LOWER": "room"}, {"IS_DIGIT": True}],
        # Virtual event locations
        [{"LOWER": "online"}, {"LOWER": "event"}],
    ])

    return matcher


# Enhanced test function
def test_patterns_detailed(nlp, matcher, text_samples):
    """Test patterns with detailed analysis"""
    for i, text in enumerate(text_samples):
        print(f"\n=== SAMPLE {i+1} DEBUG ===")
        print(f"Text: {text[:100]}...")
        
        doc = nlp(text)
        matches = matcher(doc)
        
        print("Raw matches:")
        for match_id, start, end in matches:
            label = nlp.vocab.strings[match_id]
            span = doc[start:end]
            print(f"  {label}: '{span.text}' (tokens {start}-{end})")
            
        print("Tokens with POS tags:")
        for token in doc[:20]:  # First 20 tokens
            print(f"  {token.text} ({token.pos_}, {token.tag_}, title={token.is_title}, propn={token.pos_ == 'PROPN'})")