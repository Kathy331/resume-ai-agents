"""
Entity Extractor Agent

This agent processes raw text (typically an email or message body) and extracts structured entities
such as company names, candidate names, roles, interviewers, dates, times, and durations using a
combination of regex patterns and spaCy named entity recognition (NER).

Input:
- AgentInput with a `data` dictionary containing:
    - "text": (str) The raw text to extract entities from (required).
    - "email_id": (str) Optional unique identifier for the email or message.

Output:
- AgentOutput with:
    - success: (bool) Whether extraction succeeded.
    - data: (dict) Extracted entities grouped by type, e.g.:
        {
            "CANDIDATE": ["Jane Doe"],
            "COMPANY": ["Launchpad AI"],
            "ROLE": ["Software Engineer"],
            "INTERVIEWER": ["John Smith"],
            "DATE": ["July 30, 2025"],
            "TIME": ["3:00 PM"],
            "DURATION": ["45 minutes"],
            "email_id": "abc123"  # if provided in input
        }
    - errors: (list) List of error messages if extraction failed; otherwise None.

The agent uses:
- Regex patterns (fast, exact matches).
- spaCy NER model ("en_core_web_sm") for fuzzy entity detection.
- Custom heuristic filters to remove false positives and overlaps.

Typical usage:
    input_data = AgentInput(data={"text": email_body, "email_id": email_identifier})
    output = await entity_extractor_agent.execute(input_data)
    if output.success:
        entities = output.data
    else:
        print("Errors:", output.errors)
"""

import os
import re
import spacy
from typing import Dict, Any, List, Tuple
from pathlib import Path
from collections import defaultdict
from spacy.matcher import Matcher

from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from agents.entity_extractor.patterns import add_patterns

# Technologies used for entity extraction:
# - Regex: Finds exact text patterns, fast but breaks if text changes.
# - spaCy NER: ML model to find names, dates, companies in natural text
class EntityExtractor(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp.add_pipe("merge_entities", last=True)
        self.matcher = add_patterns(self.nlp)

    def validate_input(self, input_data: AgentInput) -> bool:
        return "text" in input_data.data and bool(input_data.data["text"].strip())

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        try:
            text = input_data.data.get("text", "")
            email_id = input_data.data.get("email_id")  # Optional

            doc = self.nlp(text)
            matches = self.matcher(doc)
            cleaned_matches = self.clean_matches(matches, doc)

            entities = self.extract_entities(doc, cleaned_matches)

            if email_id:
                entities["email_id"] = email_id

            return AgentOutput(
                success=True,
                data=dict(entities),
                metadata={},
                errors=None,
            )

        except Exception as e:
            return AgentOutput(
                success=False,
                data={},
                metadata={},
                errors=[str(e)],
            )

    def extract_entities(self, doc, cleaned_matches: List[Tuple[str, int, int]]) -> Dict[str, List[str]]:
        entities = defaultdict(list)

        interviewer_spans = [
            doc[start:end] for label, start, end in cleaned_matches if label == "INTERVIEWER"
        ]

        for label, start, end in cleaned_matches:
            span = doc[start:end]
            entity_text = span.text.strip().replace('\n', ' ')

            if len(entity_text) < 2:
                continue

            # === CANDIDATE ===
            if label == "CANDIDATE":
                if any(span.start >= ctx.start and span.end <= ctx.end for ctx in interviewer_spans):
                    continue
                if any(word in entity_text.lower() for word in [
                    "team", "labs", "manager", "acquisition", "engineer", "invitation", "bitwise"
                ]):
                    continue
                    
                # For candidate matches, extract only the name part (skip greetings)
                # If the match starts with "Hi", "Hello", "Dear", etc., take only the name
                candidate_text = entity_text
                greeting_words = ["hi", "hello", "dear", "hey"]
                words = candidate_text.split()
                
                if len(words) >= 2 and words[0].lower() in greeting_words:
                    # Take only the name part (second word)
                    candidate_text = words[1]
                
                # Only add if it looks like a proper name (capitalized, reasonable length)
                if candidate_text and candidate_text[0].isupper() and 2 <= len(candidate_text) <= 20:
                    if candidate_text not in entities["CANDIDATE"]:
                        entities["CANDIDATE"].append(candidate_text)
                continue  # Skip the default addition at the end

            # === INTERVIEWER ===
            elif label == "INTERVIEWER":
                for ent in span.ents:
                    if ent.label_ == "PERSON":
                        # Handle multi-line person entities (e.g., "Archana\nDandilyonn SEEDS Team")
                        # Extract just the first line/name
                        person_text = ent.text.strip()
                        if '\n' in person_text:
                            # Take the first line, which is usually the person's name
                            first_line = person_text.split('\n')[0].strip()
                            if first_line and len(first_line) >= 2:
                                person_text = first_line
                        
                        # Clean up the person name
                        person_text = person_text.replace('\n', ' ').strip()
                        
                        # Skip if it looks like an organization or email
                        if any(word in person_text.lower() for word in [
                            "team", "company", "corp", "inc", "ltd", "llc", "@", ".com"
                        ]):
                            continue
                            
                        if person_text not in entities["INTERVIEWER"] and len(person_text) >= 2:
                            entities["INTERVIEWER"].append(person_text)
                continue  # Skip adding raw INTERVIEWER span later

            # === COMPANY ===
            elif label == "COMPANY":
                if entity_text.lower().startswith("at "):
                    entity_text = entity_text[3:].strip()
                    
                # Skip partial/invalid company extractions
                invalid_company_phrases = [
                    "team", "recruiting", "hiring", "acquisition", "with google", "for internship", 
                    "google meet", "zoom meeting", "zoom call", "meet", "call", "session",
                    "opportunity", "interview", "meeting", "with", "for"
                ]
                
                if any(phrase in entity_text.lower() for phrase in invalid_company_phrases):
                    continue
                    
                # Skip if it's just a platform/tool name without context
                platform_tools = ["zoom", "google", "meet", "teams", "slack"]
                if entity_text.lower() in platform_tools:
                    continue
                    
                # Only keep if it looks like a real company name
                if len(entity_text.strip()) >= 3 and not entity_text.lower().startswith(('hi ', 'hello ', 'dear ')):
                    if entity_text not in entities["COMPANY"]:
                        entities["COMPANY"].append(entity_text)
                continue  # Skip the default addition

            # === DATE ===
            elif label == "DATE":
                if entity_text.isdigit():
                    continue

            # === DURATION ===
            elif label == "DURATION":
                if not any(w in entity_text.lower() for w in ["minute", "hour", "hr"]):
                    continue

            if entity_text not in entities[label]:
                entities[label].append(entity_text)

        return entities

    def clean_matches(self, matches, doc) -> List[Tuple[str, int, int]]:
        """Deduplicate overlapping matches using priority and length."""
        priority = [
            'CANDIDATE', 'ROLE', 'COMPANY', 'INTERVIEWER',
            'TIME', 'DATE', 'LOCATION', 'LINK', 'DURATION', 'FORMAT'
        ]

        labeled_matches = [
            (self.nlp.vocab.strings[match_id], start, end, doc[start:end].text.strip())
            for match_id, start, end in matches
        ]

        labeled_matches.sort(key=lambda x: (x[1], x[2]))  # Sort by span start/end

        filtered = []
        for label, start, end, text in labeled_matches:
            overlap_found = False
            for kept in filtered:
                kept_label, kept_start, kept_end, kept_text = kept
                if not (end <= kept_start or start >= kept_end):
                    label_pri = priority.index(label) if label in priority else len(priority)
                    kept_pri = priority.index(kept_label) if kept_label in priority else len(priority)

                    if label_pri < kept_pri or (label_pri == kept_pri and len(text) > len(kept_text)):
                        filtered = [
                            m for m in filtered if not (m[0] == kept_label and m[1] == kept_start and m[2] == kept_end)
                        ]
                    else:
                        overlap_found = True
                        break
            if not overlap_found:
                filtered.append((label, start, end, text))

        return [(label, start, end) for label, start, end, _ in filtered]
