import spacy
import spacy.training
import random
from spacy.util import minibatch, compounding
import json
import os
from sklearn.metrics import precision_recall_fscore_support
from tqdm import tqdm
# to run this script
# pip install -r requirements.txt
# pip install -m spacy download en_core_web_sm
# python3 agents/entity_extractor/train_ner.py 

# LABELS = [
#     "CANDIDATE",  # Candidate/applicant name
#     "ROLE",       # Job role/title
#     "COMPANY",    # Company name
#     "DATE",       # Date of interview/event
#     "LOCATION",   # Interview location
#     "INTERVIEWER",# Interviewer name
#     "DURATION",   # Length of interview
#     "FORMAT",     # Interview format (e.g., Zoom)
#     "LINK"        # URL/link
# ]
def load_data(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():
                item = json.loads(line)
                entities = [(start, end, label) for start, end, label in item['entities']]
                data.append((item['text'], {"entities": entities}))
    return data

def validate_and_clean_data(data):
    """Validate and clean training data to remove overlapping entities"""
    cleaned_data = []
    overlap_count = 0
    
    for i, (text, annotations) in enumerate(data):
        entities = annotations.get("entities", [])
        
        # Check for overlapping entities
        entities.sort()  # Sort by start position
        valid_entities = []
        prev_end = 0
        has_overlap = False
        
        for j, (start, end, label) in enumerate(entities):
            # Validate bounds
            if start < 0 or end > len(text) or start >= end:
                print(f"!!  Example {i}: Invalid entity bounds [{start}, {end}] for '{label}' in text: {text[:50]}...")
                continue
                
            # Check for overlap
            if start < prev_end:
                print(f"!! Example {i}: OVERLAPPING ENTITIES!")
                print(f"   Text: {text}")
                print(f"   Previous entity: {valid_entities[-1] if valid_entities else 'None'}")
                print(f"   Current entity: ({start}, {end}, '{label}') = '{text[start:end]}'")
                print(f"   Previous end: {prev_end}, Current start: {start}")
                has_overlap = True
                overlap_count += 1
                # Skip the overlapping entity
                continue
            
            valid_entities.append((start, end, label))
            prev_end = end
        
        if not has_overlap and valid_entities:
            cleaned_data.append((text, {"entities": valid_entities}))
        elif valid_entities:
            # Use only non-overlapping entities
            cleaned_data.append((text, {"entities": valid_entities}))
            print(f"** Example {i}: Kept {len(valid_entities)} non-overlapping entities (removed overlaps)")
    
    print(f"\n Summary: Found {overlap_count} overlapping entity cases")
    return cleaned_data

def train_ner(train_data, labels, n_iter=30):
    # Load base model
    nlp = spacy.load("en_core_web_sm")
    
    # Get NER pipeline component
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")
    
    # Add custom labels
    for label in labels:
        ner.add_label(label)
    
    # Disable other pipes during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.resume_training()
        
        # Outer loop: epochs, wrapped with tqdm
        for itn in tqdm(range(n_iter), desc="Epochs", unit="epoch"):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
            
            # Wrap batches with tqdm for batch progress
            for batch in tqdm(batches, desc=f"Epoch {itn+1} batches", leave=False, unit="batch"):
                # Convert to Example objects (spaCy 3.x requirement)
                examples = []
                for text, annotations in batch:
                    doc = nlp.make_doc(text)
                    example = spacy.training.Example.from_dict(doc, annotations)
                    examples.append(example)
                
                nlp.update(examples, sgd=optimizer, drop=0.35, losses=losses)
            
            print(f"Iteration {itn + 1}/{n_iter}, Losses: {losses}")
    
    return nlp

def evaluate_ner(nlp, data):
    true_entities = []
    pred_entities = []
    
    for text, annotations in data:
        doc = nlp(text)
        # Fix: Get entities from annotations correctly
        true_ents = annotations.get("entities", [])
        pred_ents = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        
        # Extract only the labels for sklearn metrics
        true_labels = [label for _, _, label in true_ents]
        pred_labels = [label for _, _, label in pred_ents]
        
        true_entities.extend(true_labels)
        pred_entities.extend(pred_labels)
    
    print(f"True entities count: {len(true_entities)}")
    print(f"Predicted entities count: {len(pred_entities)}")
    
    if len(true_entities) > 0 and len(pred_entities) > 0:
        try:
            # Handle case where we have different numbers of predictions
            precision, recall, f1, _ = precision_recall_fscore_support(
                true_entities, pred_entities, average='micro', zero_division=0
            )
            print(f"Evaluation results -- Precision: {precision:.3f}, Recall: {recall:.3f}, F1-score: {f1:.3f}")
        except Exception as e:
            print(f"!!  Evaluation error: {e}")
            print("This is okay - it happens when there are no predictions or true entities to compare")
    else:
        print("📊 Evaluation results -- No entities to evaluate (this is normal during training)")

def test_ner(nlp, texts):
    for text in texts:
        doc = nlp(text)
        print(f"\nText: {text}")
        print("Entities:")
        for ent in doc.ents:
            print(f"  - {ent.text} ({ent.label_})")

if __name__ == "__main__":
    # Path to your training data JSONL file
    file_path = os.path.abspath("tests/sample_data/entity_alltraindata.jsonl")
    
    # Define your labels here (must match those in your training data)
    LABELS = [
        "CANDIDATE",  # Candidate/applicant name
        "ROLE",       # Job role/title
        "COMPANY",    # Company name
        "DATE",       # Date of interview/event
        "LOCATION",   # Interview location
        "INTERVIEWER",# Interviewer name
        "DURATION",   # Length of interview
        "FORMAT",     # Interview format (e.g., Zoom)
        "LINK"        # URL/link
    ]
    
    print("Loading data...")
    data = load_data(file_path)
    print(f"Loaded {len(data)} examples")
    
    print("\nValidating and cleaning data...")
    data = validate_and_clean_data(data)
    
    # Simple train/test split (80/20)
    split = int(len(data)*0.8)
    train_data = data[:split]
    test_data = data[split:]
    
    print(f"\nTraining on {len(train_data)} examples, evaluating on {len(test_data)} examples.")
    
    # Show first training example for debugging
    if train_data:
        print("\nFirst training example:")
        text, ents = train_data[0]
        print(f"Text: {text[:100]}...")
        print(f"Entities: {ents}")
    
    nlp = train_ner(train_data, LABELS, n_iter=30)
    
    print("Evaluating model...")
    evaluate_ner(nlp, test_data)
    
    # Example test sentences
    test_texts = [
        "Hi Jamie, your 45-minute technical interview is scheduled at Launchpad AI on August 25, 2025.",
        "Hello Kathy, please join your behavioral interview via Zoom at 3pm on September 10, 2025.",
        "Dear Alex, your interview with CTO John Smith at Orbit is set for October 1.",
    ]
    
    print("Testing model on example texts...")
    test_ner(nlp, test_texts)
    
    # Save the model to your desired location
    output_dir = "./agents/entity_extractor/invitation_email_ner_model"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_dir), exist_ok=True)
    
    nlp.to_disk(output_dir)
    print(f"✅ Saved model to {output_dir}")
    print(f"📁 To use later: nlp = spacy.load('{output_dir}')")
    
