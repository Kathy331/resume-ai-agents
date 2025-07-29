import spacy
import random
from spacy.util import minibatch, compounding
import json
import os
from sklearn.metrics import precision_recall_fscore_support
from tqdm import tqdm
# to run this script, 
# pip install -r requirements.txt
# python -m spacy download en_core_web_sm
# python3 agents/entity_extractor/train_ner.py

# Entity labels used in your dataset:
# CANDIDATE - Name of the candidate/applicant
# ROLE - Job position or role title
# COMPANY - Company or organization name
# DATE - Date of the interview or event
# LOCATION - Location of the interview or event
# INTERVIEWER - Name of the interviewer
# DURATION - Length of the interview or event (e.g., "45 minutes")
# FORMAT - Format of the interview (e.g., Zoom, Remote)
# LINK - URL or link to interview or resources


def load_data(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():
                item = json.loads(line)
                entities = [(start, end, label) for start, end, label in item['entities']]
                data.append((item['text'], {"entities": entities}))
    return data



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
        true_ents = [(start, end, label) for start, end, label in annotations.get("entities")]
        pred_ents = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        
        true_entities.extend(true_ents)
        pred_entities.extend(pred_ents)
    
    # Extract labels for evaluation
    true_labels = [label for _, _, label in true_entities]
    pred_labels = [label for _, _, label in pred_entities]
    
    precision, recall, f1, _ = precision_recall_fscore_support(true_labels, pred_labels, average='micro')
    
    print(f"Evaluation results -- Precision: {precision:.3f}, Recall: {recall:.3f}, F1-score: {f1:.3f}")


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
    
    # Simple train/test split (80/20)
    split = int(len(data)*0.8)
    train_data = data[:split]
    test_data = data[split:]
    
    print(f"Training on {len(train_data)} examples, evaluating on {len(test_data)} examples.")
    
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
    
    # Save the model
    output_dir = "./invitation_email_ner_model"
    nlp.to_disk(output_dir)
    print(f"Saved model to {output_dir}")
