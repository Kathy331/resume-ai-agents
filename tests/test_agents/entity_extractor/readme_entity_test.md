# Entity Extraction Tests

This directory contains comprehensive tests for the entity extraction improvements.

## Files

- `test_entity_extraction.py` - Complete test suite with visualization
- `run_entity_tests.py` - Quick test runner for specific categories

## Usage

### Run All Tests
```bash
python tests/test_agents/test_entity_extraction.py
```

### Run Specific Test Categories
```bash
# Test candidate extraction only
python tests/test_agents/run_entity_tests.py candidates

# Test company extraction only
python tests/test_agents/run_entity_tests.py companies

# Test complete pipeline integration
python tests/test_agents/run_entity_tests.py pipeline
```

## What's Being Tested

### Candidate Extraction
- ✅ Extracts names without greetings ("Hi John" → "John")
- ✅ Filters out non-names ("Hi Engineering" → nothing)
- ✅ Handles various greeting formats (Hi, Hello, Dear, Hey)

### Company Extraction  
- ✅ Extracts real company names ("at PixelWave" → "PixelWave")
- ✅ Ignores platform tools ("with Google Meet" → nothing)
- ✅ Avoids partial phrases ("for Internship" → nothing)

### Complete Pipeline
- ✅ Email classification as Interview_invite
- ✅ Entity extraction with cleaning
- ✅ Database storage integration
- ✅ End-to-end workflow validation

## Expected Results

- **Candidate Extraction**: 5/6 tests (83% - "Seedling" edge case)
- **Company Extraction**: 5/5 tests (100%)
- **Complete Pipeline**: 3/3 tests (100%)
- **Overall Success**: 92.9% (Excellent!)

## Key Improvements Tested

1. **Greeting Removal**: "Hi John" becomes just "John"
2. **Platform Filtering**: Ignores "Zoom", "Google Meet" as companies
3. **Email Cleaning**: Removes tracking URLs before extraction
4. **Smart Filtering**: Excludes generic terms like "Team", "Engineering"
