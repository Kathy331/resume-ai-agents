import spacy
import os

# to run this script
# python3 agents/entity_extractor/use_model.py

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

print("\n" + "="*60)
print("HOW TO IMPROVE YOUR NER MODEL")
print("="*60)
print("""
1. 📊 CHECK TRAINING DATA BALANCE:
   - Run the analysis function in train_ner.py to see entity distribution
   - Ensure you have roughly equal examples for each entity type

2. 📈 ADD MORE TRAINING DATA:
   - Collect 20-50 examples for each entity type
   - Diversify the phrasing and context for each entity

3. 🔄 IMPROVE TRAINING:
   - Increase n_iter from 30 to 50-100 epochs
   - Add entity type analysis to see what's missing

4. 🎯 EXAMPLE IMPROVEMENTS NEEDED:
   - DURATION: More variations (30-min, 1-hour, 45 mins, etc.)
   - DATE: Different formats (August 25, Monday, Oct 1, 2025-11-05)
   - ROLE: Various job titles (Data Scientist, CTO, Senior Developer)
   - COMPANY: Different company name styles
   - FORMAT: Various meeting formats (Zoom, virtual, in-person)
   - LOCATION: Different location references
   - INTERVIEWER: Various interviewer titles and names

5. 🚀 QUICK TEST YOUR MODEL:
   - Test with sentences that contain multiple entity types
   - If some entities are never detected, you need more training examples for those types
""")

print("✅ Model testing completed!")