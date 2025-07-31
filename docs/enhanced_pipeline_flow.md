# Enhanced Email Pipeline Flow with LangGraph

## Flow Diagram

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

## LangGraph Nodes

1. **setup_gmail** - Initialize Gmail service
2. **fetch_emails** - Retrieve emails from specified folder
3. **classify_emails** - Categorize emails (Interview_invite, Personal, etc.)
4. **setup_enhanced_pipeline** - Initialize enhanced processing agents
5. **process_interviews** - Advanced interview processing chain:
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
    'enhanced_pipeline': EnhancedEmailPipeline,
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

```python
# Run the enhanced pipeline
from agents.orchestrator.workflow_runner import WorkflowRunner

runner = WorkflowRunner()
result = runner.run_email_pipeline(folder_name='INBOX', max_results=10)

# Results include enhanced metrics
print(f"Research performed: {result['research_performed_count']}")
print(f"Memory hits: {result['memory_hits_count']}")
```
