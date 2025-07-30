
import spacy
import os
import sys
import json
from pathlib import Path
# Running the trained NER model
print("Loading trained NER model...")
nlp = spacy.load("./agents/entity_extractor/invitation_email_ner_model")

print("\n" + "="*60)
print("TESTING YOUR TRAINED NER MODEL")
print("="*60)

# Test texts with various entity combinations
test_texts = [
    # Basic candidate detection
    "Hi Sarah, your interview is scheduled.",
    
    # Candidate + Duration  
    "Hi Jamie, your 45-minute technical interview is scheduled.",
    
    # Candidate + Duration + Company + Date
    "Hi Jamie, your 45-minute interview is scheduled at Launchpad AI on August 25, 2025.",
    
    # Candidate + Duration + Date + Format
    "Hello Kathy, please join your behavioral interview via Zoom at 3pm on September 10, 2025.",
    
    # Candidate + Interviewer + Company + Date
    "Dear Alex, your interview with CTO John Smith at Orbit is set for October 1.",
    
    # All entity types example
    "Hi Michael, you're invited to a 60-minute virtual interview for the Senior Developer role at TechCorp on Friday with Manager Johnson.",
    
    # Complex example
    "Dear Maya, your Data Scientist interview with Dr. Smith at Microsoft is on Tuesday, November 5, 2025 via Zoom meeting.",
]

for i, test_text in enumerate(test_texts, 1):
    print(f"\nExample {i}:")
    print(f"Text: {test_text}")
    print("Entities:")
    doc = nlp(test_text)
    for ent in doc.ents:
        print(f"  - {ent.text} ({ent.label_})")
    if not doc.ents:
        print("  No entities found")


print("Model testing completed!")