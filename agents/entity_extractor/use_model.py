import spacy

# Load your trained model
nlp = spacy.load("./invitation_email_ner_model")

# Test it on new text
text = "Hi Sarah, your 30-minute interview with Manager John at Google is on Monday, October 15, 2025 via Zoom."
doc = nlp(text)

print(f"Text: {text}")
print("Extracted entities:")
for ent in doc.ents:
    print(f"  - {ent.text} ({ent.label_})")