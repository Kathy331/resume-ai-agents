# Test Organization - Resume AI Agents

## Overview

The test suite is organized by agent sections to provide clear, focused testing for each component of the Interview Prep Workflow system.

## Test Structure

### Agent-Specific Tests

#### 📧 Email Classifier Tests (`tests/test_agents/email_classifier/`)
- **test_email_classifier.py**: Tests for email classification functionality
- Tests interview vs personal vs other email categorization
- Validates classification accuracy and edge cases

#### 🎯 Entity Extractor Tests (`tests/test_agents/entity_extractor/`)
- **test_entity_extraction.py**: Core entity extraction testing
- **run_entity_tests.py**: Automated entity extraction test runner
- **readme_entity_test.md**: Documentation for entity extraction testing
- Tests company name, interviewer, role, and timing extraction

#### 🔤 Keyword Extractor Tests (`tests/test_agents/keyword_extractor/`)
- **test_keyword_extractor.py**: Keyword extraction functionality
- Tests company name extraction for filename generation
- Validates keyword extraction accuracy

#### 🔬 Research Engine Tests (`tests/test_agents/research_engine/`)
- **test_real_tavily_research.py**: Real Tavily API integration testing
- Tests actual API calls and caching functionality
- Validates research quality and data structure

### Pipeline Tests (`tests/test_pipelines/`)
Currently empty - ready for pipeline integration tests

### Workflow Tests (`tests/test_workflows/`)
Currently empty - ready for end-to-end workflow testing

### Shared Component Tests (`tests/test_shared/`)
- **test_utils.py**: Utility function testing
- **test_enhanced_pipeline.py**: Enhanced pipeline components
- **test_interview_database.py**: Database functionality testing
- **test_models.py**: Data model validation

### Interview Prep Intelligence Tests (`tests/test_interview_prep_intelligence/`)
- **enhanced_comprehensive_prep_guide.py**: Comprehensive preparation guide testing

## Test Categories

### Unit Tests
- Individual agent functionality
- Component-level validation
- Edge case handling

### Integration Tests
- Pipeline component interaction
- Agent coordination testing
- Data flow validation

### End-to-End Tests
- Complete workflow execution
- Real API integration testing
- Output validation

## Running Tests

### Agent-Specific Tests
```bash
# Run email classifier tests
python -m pytest tests/test_agents/email_classifier/

# Run entity extractor tests
python tests/test_agents/entity_extractor/run_entity_tests.py

# Run keyword extractor tests
python -m pytest tests/test_agents/keyword_extractor/

# Run research engine tests
python -m pytest tests/test_agents/research_engine/
```

### All Tests
```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_agents/ -v
python -m pytest tests/test_shared/ -v
```

## Test Data

### Sample Data (`tests/sample_data/`)
- Sample email files for testing
- Mock interview data
- Test configuration files

### Testing Sample Data (`tests/testing_sampledata/`)
- Extended test datasets
- Edge case examples
- Performance testing data

## Configuration

### Test Configuration (`tests/conftest.py`)
- Shared test fixtures
- Common setup and teardown
- Test environment configuration

### Environment Variables
```bash
# For testing with real APIs
TAVILY_API_KEY=your_test_key
OPENAI_API_KEY=your_test_key
TEST_DATA_PATH=tests/sample_data/
```

## Best Practices

### Test Organization
- Keep tests close to the code they test
- Use descriptive test names
- Group related tests in the same file

### Test Data
- Use mock data for unit tests
- Use real API calls only for integration tests
- Clean up test data after execution

### Coverage Goals
- Aim for >80% code coverage
- Focus on critical path testing
- Include edge case validation

## Future Enhancements

### Pipeline Testing
- End-to-end pipeline tests
- Performance benchmarking
- Cache effectiveness testing

### Workflow Testing
- Complete workflow validation
- Multi-email processing tests
- Output quality assessment

### Performance Testing
- Load testing for high email volumes
- API rate limiting validation
- Cache optimization verification
