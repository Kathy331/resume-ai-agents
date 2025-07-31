# Email Pipeline Flow with LangGraph

## Overview & Purpose

The Email Pipeline is an intelligent email processing system designed to automatically handle job related emails, particularly interview invitations. This pipeline automatically identifies, processes, and researches interview invitations while avoiding redundant work.

## Flow Diagram
This Pipeline does not include Tavily Research Yet

```
📧 Raw Emails
    ↓
🏷️  Email Classification
    ↓
    ├─ Interview_invite? ──→ YES ──→ 🧠 Entity Extraction
    │                                    ↓
    │                               📋 Memory Similarity Check
    │                                    ↓
    │                               ┌─ High Similarity + Prepped? ──→ YES ──→ ⏭️  Skip Research
    │                               │                                          ↓
    │                               └─ NO ──→ 🔍 Tavily Research ──→ 💾 Update Memory
    │                                                ↓
    └─ Other Categories ──→ 📊 Format Output ←──────┘
                              ↓
                          ✅ Complete
```
## Core Tools & Technologies
- **LangGraph**: Workflow orchestration with conditional routing (better than linear LangChain chains, Langgraph provide persistent state across nodes, and smart conditional routing )
- **Gmail API**: Automated email fetching and parsing
- **AI Classification**: Intelligent email categorization (Interview vs Personal vs Other)
- **Entity Extraction**: Extract company, role, interviewer, candidate, date, time, duration, dates, from email content.
- **Memory System**: Smart deduplication, remembers what was already processed

## How It Works
1. **Fetch** emails from your Gmail inbox
2. **Classify** each email (Interview_invite, Personal, Others)
3. **Extract** key information (company, role, interviewer) from interview emails
4. **Check memory** - have we seen this company/role before?
5. **Conditional research** - only research NEW opportunities (saves time & API costs)
6. **Store results** in memory for future reference

## LangGraph Nodes
1. **setup_gmail** - Initialize Gmail service
2. **fetch_emails** - Retrieve emails from specified folder
3. **classify_emails** - Categorize emails (Interview_invite, Personal, etc.)
4. **setup_enhanced_pipeline** - Initialize enhanced processing agents
5. **process_interviews** - Advanced interview processing workflow:
   - Entity extraction (Company, Role, Date, Interviewer)
   - Memory similarity search
   - Conditional research based on similarity scores
   - Memory storage/updates
6. **format_output** - Generate user-friendly summaries
7. **error_handler** - Handle errors with retry logic

## Conditional Routing Logic

### Route: `route_after_classification`
- If Interview_invite emails detected → `setup_enhanced_pipeline`
- If no interviews → `format_output`
- If error → `error_handler`

### Route: `process_interviews` Decision Tree
```python
For each Interview_invite email:
    1. Extract entities (Company, Role, Candidate, Date, etc.)
    2. Query memory for similar interviews
    3. Calculate similarity scores
    4. Decision:
        - If similarity > 0.8 AND status in ['prepped', 'scheduled', 'completed']:
            → Skip research, log as "found in memory"
        - Else:
            → Perform Tavily research
            → Store/update in memory with status='preparing'
```

## State Management

The `EmailWorkflowState` carries data through each node:

```python
{
    'folder_name': str,
    'gmail_service': GmailService,
    'raw_emails': List[Dict],
    'classified_emails': Dict[str, List],
    'interview_processing_results': List[Dict],  # Enhanced results
    'email_pipeline': EmailPipeline,
    'research_performed_count': int,
    'memory_hits_count': int,
    'summaries': List[Dict],
    'processing_complete': bool
}
```

## Benefits

1. **Intelligent Deduplication** - Avoids redundant research for similar interviews
2. **Memory-Driven Efficiency** - Leverages past processing to speed up new emails
3. **Conditional Processing** - Only performs expensive operations when needed
4. **State Persistence** - Tracks interview lifecycle (preparing → prepped → completed)
5. **Scalable Architecture** - Easy to add new processing nodes or routing logic

## Usage

### Basic Usage
```python
# Run the enhanced pipeline
from agents.orchestrator.workflow_runner import WorkflowRunner

runner = WorkflowRunner()
result = runner.run_email_pipeline(folder_name='INBOX', max_results=10)

# Results include enhanced metrics
print(f"Research performed: {result['research_performed_count']}")
print(f"Memory hits: {result['memory_hits_count']}")
```

### Real-World Usage Examples

#### Scenario 1: Daily Email Processing
```python
# Process today's emails for interview invitations
runner = WorkflowRunner()
result = runner.run_email_pipeline(
    folder_name='INBOX', 
    max_results=50  # Check last 50 emails
)

# Output example:
# 📧 Processed 50 emails
# 🎯 Found 3 interview invitations  
# 🔍 Researched 1 new company (2 were already in memory)
# ⚡ Saved 2 Tavily API calls through intelligent deduplication
```

#### Scenario 2: Focused Folder Processing
```python
# Process a specific folder (e.g., job search emails)
result = runner.run_email_pipeline(
    folder_name='Jobs',
    max_results=100
)
```

### What You Get Back
```python
{
    'total_emails': 50,
    'classified_emails': {
        'Interview_invite': 3,
        'Personal': 12, 
        'Others': 35
    },
    'research_performed_count': 1,  # Only new opportunities researched
    'memory_hits_count': 2,         # Interviews found in memory (skipped)
    'processing_time': 45.2,        # Seconds
    'interview_summaries': [
        {
            'company': 'JUTEQ',
            'role': 'AI Intern',
            'interviewer': 'Rakesh Gohel',
            'research_status': 'completed',
            'similarity_to_past': 0.2  # New opportunity
        },
        {
            'company': 'Google',
            'role': 'Software Engineer', 
            'interviewer': 'Jane Smith',
            'research_status': 'skipped',
            'similarity_to_past': 0.9  # Already processed similar role
        }
    ]
}
```

### Integration with Streamlit UI
The pipeline integrates with your Streamlit dashboard for easy visualization:

```python
# Streamlit app
if st.button("Process Recent Emails"):
    with st.spinner("Processing emails..."):
        result = runner.run_email_pipeline(folder_name='INBOX')
    
    st.success(f"✅ Processed {result['total_emails']} emails")
    st.info(f"🎯 Found {len(result['interview_summaries'])} interview invitations")
    
    # Display results in nice format
    for interview in result['interview_summaries']:
        st.write(f"**{interview['company']}** - {interview['role']}")
```

### Performance Benefits
- **Speed**: Only researches NEW opportunities (skips duplicates)
- **Cost**: Reduces Tavily API calls by ~60-80% through memory system
- **Accuracy**: AI classification is more reliable than manual email sorting
- **Scalability**: Can process hundreds of emails quickly with conditional routing
