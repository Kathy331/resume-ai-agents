# Research Engine Pipeline Flow with LangGraph Integration

## Overview & Purpose

The Research Engine Pipeline is an intelligent research automation system designed to process unprepped interviews and gather comprehensive intelligence using multi-agent research. This pipeline automatically identifies interviews that need research and executes parallel research across company, interviewer, and role domains.

## Flow Diagram

```
📋 Interview Memory Query
    ↓
🔍 Fetch Unprepped Interviews (status != 'prepped')
    ↓
    ├─ No interviews? ──→ ✅ Complete (Nothing to research)
    │
    └─ Found interviews ──→ 🧠 Entity Validation & Request Creation
                              ↓
                         🎯 Multi-Agent Research Pipeline (Parallel)
                              ├─ 🏢 Company Research ──→ CompanyResearcher/Tavily
                              ├─ 👤 Interviewer Research ──→ InterviewerResearcher/Tavily
                              └─ 💼 Role Research ──→ RoleResearcher/Tavily
                              ↓
                         📊 Quality Assessment & Confidence Scoring
                              ├─ Calculate Quality Score (0.0 - 1.0)
                              └─ Calculate Confidence Score (0.0 - 1.0)
                              ↓
                         💾 Memory Update Pipeline
                              ├─ Store Research Results
                              └─ Update Status: 'preparing' → 'prepped'
                              ↓
                         📈 Results Aggregation & Statistics
                              ↓
                         ✅ Pipeline Complete
```

## Core Tools & Technologies
- **Multi-Agent Architecture**: Specialized research agents for different domains
- **Tavily API Integration**: Real-time web intelligence gathering
- **Parallel Processing**: Concurrent research execution for efficiency
- **Quality Assessment**: Automated research validation and scoring
- **Memory System Integration**: Smart status tracking and result storage
- **LangGraph Compatible**: Seamless integration with email processing workflows

## How It Works
1. **Query** interview memory system for unprepped interviews (excludes 'prepped', 'completed', 'archived')
2. **Validate** extracted entities from interview data (company, interviewer, role)
3. **Execute** parallel multi-agent research using specialized researchers or Tavily fallback
4. **Assess** research quality based on completeness and data richness
5. **Calculate** confidence scores based on success rates and data quality
6. **Update** interview status to 'prepped' and store comprehensive research results
7. **Report** pipeline statistics and individual interview results

## Pipeline Components

### 1. Interview Query System
**Purpose**: Fetches interviews that need research from memory system

**Query Logic**:
- Filter: `status NOT IN ('prepped', 'completed', 'archived')`
- Priority support: Filter by priority level (high, normal, low, all)
- Limit: Configurable maximum interviews per run
- Result: List of interview records with entities and metadata

### 2. Entity Validation & Request Creation
**Purpose**: Validates extracted entities and creates structured research requests

**Validation Process**:
- Extract entities: COMPANY, INTERVIEWER, ROLE from interview data
- Create ResearchRequest objects with available entity data
- Add context from email subjects and additional metadata
- Prioritize requests based on interview priority levels

### 3. Multi-Agent Research System
**Purpose**: Executes parallel research across multiple domains

**Research Agents**:
- **CompanyResearcher**: Company intelligence, news, leadership, technology
- **InterviewerResearcher**: Professional background, LinkedIn, experience  
- **RoleResearcher**: Market analysis, salary data, skill requirements

**Fallback System**: Direct Tavily API calls if specialized agents unavailable

### 4. Quality Assessment Engine
**Purpose**: Validates research quality and calculates confidence scores

**Quality Metrics**:
- **Completeness**: Number of successful research areas (0-3)
- **Data Richness**: Amount and depth of returned data
- **Error Rate**: Failed research attempts and API errors
- **Final Score**: Normalized quality score (0.0 - 1.0)

**Confidence Calculation**:
- Base confidence: 0.8 (no errors) or 0.5 (with errors)
- Coverage boost: +0.2 based on successful research areas
- Final range: 0.0 - 1.0

### 5. Memory Integration System
**Purpose**: Updates interview records with research results and status

**Update Process**:
- Store research data in structured format
- Update interview status: 'preparing' → 'prepped'
- Add research metadata: timestamps, quality scores, confidence
- Maintain research audit trail for analytics

## Pipeline State Management

The Research Pipeline maintains state through each processing stage:

```python
ResearchPipelineState = {
    'unprepped_interviews': List[Dict],     # Interviews needing research
    'research_requests': List[ResearchRequest],  # Structured research requests
    'research_results': List[ResearchResult],    # Individual research outcomes
    'quality_scores': List[float],          # Quality assessment results
    'confidence_scores': List[float],       # Confidence assessment results
    'updated_interviews': List[str],        # Successfully updated interview IDs
    'processing_stats': Dict[str, Any],     # Pipeline execution statistics
    'errors': List[str]                     # Processing errors and warnings
}
```

## Conditional Processing Logic

### Research Execution Decision Tree
```python
For each unprepped interview:
    1. Validate entities (company, interviewer, role exist?)
    2. Create research request with available data
    3. Execute parallel research:
        - Company research (if company_name available)
        - Interviewer research (if interviewer_name available)  
        - Role research (if role_title available)
    4. Quality assessment:
        - Quality score > 0.5: Mark as successful
        - Quality score ≤ 0.5: Mark as failed/retry candidate
    5. Memory update:
        - Successful: Update status to 'prepped'
        - Failed: Keep status as 'preparing' for retry
```

## Benefits

1. **Intelligent Filtering** - Only processes interviews that actually need research
2. **Parallel Efficiency** - Concurrent research execution reduces processing time
3. **Quality Assurance** - Automated validation ensures research completeness
4. **Cost Optimization** - Smart status tracking prevents redundant API calls
5. **Extensible Architecture** - Easy to add new research agents or domains
6. **Integration Ready** - Seamless connection with email processing workflows
7. **Error Resilience** - Graceful handling of API failures and partial results

## Usage

### Basic Pipeline Execution
```python
from agents.orchestrator.workflow_runner import WorkflowRunner

# Initialize workflow runner
runner = WorkflowRunner()

# Run research pipeline
result = runner.run_research_pipeline(
    max_interviews=10,      # Process up to 10 interviews
    priority_filter='all'   # Include all priority levels
)

# Check results
if result['success']:
    print(f"✅ Researched {result['interviews_researched']} interviews")
    print(f"📊 Average quality: {result['average_quality']:.2f}")
    print(f"⏱️ Processing time: {result['processing_time']:.1f}s")
else:
    print(f"❌ Pipeline failed: {result['error']}")
```

### Advanced Configuration
```python
# Focus on high-priority interviews only
high_priority_result = runner.run_research_pipeline(
    max_interviews=5,
    priority_filter='high'
)

# Process specific interview batches
normal_priority_result = runner.run_research_pipeline(
    max_interviews=15,
    priority_filter='normal'
)
```

### Integration with Email Pipeline
```python
def complete_interview_workflow():
    """Complete email processing + research workflow"""
    runner = WorkflowRunner()
    
    # Step 1: Process emails and identify new interviews
    email_result = runner.run_email_pipeline('INBOX', max_results=50)
    
    # Step 2: Research any newly identified interviews
    research_result = runner.run_research_pipeline(max_interviews=20)
    
    return {
        'emails_processed': email_result.get('email_count', 0),
        'new_interviews': email_result.get('classifications', {}).get('Interview_invite', 0),
        'interviews_researched': research_result.get('interviews_researched', 0),
        'total_processing_time': email_result.get('processing_time', 0) + research_result.get('processing_time', 0)
    }
```

### Real-World Usage Examples

#### Daily Automation Script
```python
async def daily_interview_prep():
    """Automated daily interview preparation"""
    runner = WorkflowRunner()
    
    # Morning: Process overnight emails
    email_result = runner.run_email_pipeline('INBOX', max_results=100)
    new_interviews = email_result.get('classifications', {}).get('Interview_invite', 0)
    
    print(f"📧 Processed {email_result.get('email_count', 0)} emails")
    print(f"🎯 Found {new_interviews} new interview invitations")
    
    # Research new interviews if any found
    if new_interviews > 0:
        research_result = runner.run_research_pipeline(max_interviews=new_interviews)
        
        if research_result['success']:
            print(f"🔬 Successfully researched {research_result['interviews_researched']} interviews")
            print(f"📈 Average research quality: {research_result['average_quality']:.1%}")
            
            # Send summary notification
            notify_research_completion(research_result)
        else:
            print(f"❌ Research pipeline failed: {research_result['error']}")
    
    return email_result, research_result if new_interviews > 0 else None
```

#### Batch Processing for Interview Season
```python
def batch_interview_research():
    """Process large batches during interview season"""
    runner = WorkflowRunner()
    
    # Process in batches to avoid API rate limits
    batch_size = 20
    total_researched = 0
    
    for batch_num in range(1, 6):  # Process 5 batches
        print(f"🔄 Processing batch {batch_num}/5...")
        
        result = runner.run_research_pipeline(
            max_interviews=batch_size,
            priority_filter='all'
        )
        
        if result['success']:
            batch_researched = result['interviews_researched']
            total_researched += batch_researched
            
            print(f"✅ Batch {batch_num}: {batch_researched} interviews researched")
            
            # Brief pause between batches
            time.sleep(30)
        else:
            print(f"❌ Batch {batch_num} failed: {result['error']}")
    
    print(f"🎯 Total interviews researched: {total_researched}")
    return total_researched
```

## Performance Metrics

### Key Performance Indicators
- **Research Success Rate**: Percentage of interviews successfully researched
- **Average Quality Score**: Mean quality score across all research results
- **Processing Throughput**: Interviews researched per minute
- **API Efficiency**: Research cost per interview (Tavily API calls)
- **Error Rate**: Percentage of failed research attempts

### Monitoring & Analytics
```python
def analyze_research_performance(results):
    """Analyze research pipeline performance"""
    total_interviews = results['interviews_found']
    successful_research = results['interviews_researched']
    failed_research = results['failed_research']
    
    success_rate = (successful_research / total_interviews) * 100 if total_interviews > 0 else 0
    average_quality = results['average_quality']
    processing_time = results['processing_time']
    
    print(f"📊 Research Pipeline Analytics:")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Average Quality: {average_quality:.2f}/1.0")
    print(f"   Processing Speed: {total_interviews/processing_time:.1f} interviews/second")
    print(f"   Total API Time: {processing_time:.1f} seconds")
    
    return {
        'success_rate': success_rate,
        'average_quality': average_quality,
        'processing_speed': total_interviews/processing_time if processing_time > 0 else 0,
        'total_processing_time': processing_time
    }
```

## Troubleshooting

### Common Issues

**1. No Unprepped Interviews Found**
- Check interview memory system status
- Verify interviews exist with status != 'prepped'
- Review priority_filter settings

**2. Low Research Quality Scores**
- Verify Tavily API key is valid and has credits
- Check entity extraction quality (company, interviewer, role names)
- Review network connectivity and API response times

**3. Memory Update Failures**
- Check interview store agent connectivity
- Verify interview IDs exist in memory system
- Review memory system permissions and storage

**4. High Error Rates**
- Monitor Tavily API rate limits and quotas
- Check for network timeouts or connectivity issues
- Review research agent initialization and dependencies

### Debug Mode
```python
# Enable detailed logging for troubleshooting
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with enhanced error reporting
result = runner.run_research_pipeline(max_interviews=5, priority_filter='high')

# Analyze individual research results
for research in result.get('research_results', []):
    print(f"Interview {research.interview_id}:")
    print(f"  Quality: {research.quality_score:.2f}")
    print(f"  Confidence: {research.research_confidence:.2f}")
    print(f"  Errors: {len(research.errors)}")
    if research.errors:
        for error in research.errors:
            print(f"    - {error}")
```

---

## Quick Start

1. **Setup**: Ensure Tavily API key is configured
2. **Initialize**: `runner = WorkflowRunner()`
3. **Execute**: `result = runner.run_research_pipeline(max_interviews=10)`
4. **Monitor**: Check `result['interviews_researched']` and `result['average_quality']`

For integration examples, see `agents/orchestrator/workflow_runner.py`.
