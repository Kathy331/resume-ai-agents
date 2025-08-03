# Interview Prep Workflow - Main Flow Diagram

## Complete System Flow Visualization

```
🚀 Interview Prep Workflow Entry Point
    ↓
📂 INTERVIEW_FOLDER Configuration (.env)
    ↓
📧 Individual Email Processing (One-by-One)
    ↓
📬 Email Classifier Agent
    ↓
    ├─ Interview Email? ──→ NO ──→ ⏭️ Skip Non-Interview
    │                                    ↓
    │                               ➡️ Process Next Email
    │
    └─ YES (Interview Email) ──→ 🎯 Entity Extractor Agent
                                    ├─ Extract Company Name
                                    ├─ Extract Interviewer Names  
                                    ├─ Extract Role Details
                                    └─ Extract Interview Timing
                                    ↓
                               🧠 Memory Store Check
                                    ├─ Query Local Interview Store
                                    └─ Check Processing History
                                    ↓
                               ┌─ Already Processed? ──→ YES ──→ ⏭️ Skip Duplicate
                               │                                    ↓
                               │                               🖥️ Terminal: "Already Prepped"
                               │                                    ↓
                               │                               ➡️ Process Next Email
                               │
                               └─ NO (New Email) ──→ 💾 Store Entity Information
                                              ↓
                                         🖥️ Terminal: "New Email Processing"
                                              ↓
                                         🔬 Deep Research Pipeline
                                              ├─ 🏢 Company Research (Tavily + Cache)
                                              ├─ 👤 Interviewer Research (Tavily + Cache)
                                              └─ 💼 Role Research (Tavily + Cache)
                                              ↓
                                         🤔 Research Quality Reflection
                                              ├─ Assess Information Adequacy
                                              ├─ Validate Source Reliability
                                              └─ Check Coverage Completeness
                                              ↓
                                         ┌─ Research Adequate? ──→ NO ──→ 🔄 Additional Research Loop
                                         │                                    ├─ Fill Information Gaps
                                         │                                    ├─ Targeted Follow-up Queries
                                         │                                    └─ Enhanced Data Gathering
                                         │                                    ↓
                                         │                               📊 Re-evaluate Quality ←──────┘
                                         │
                                         └─ YES (Adequate) ──→ 📚 Prep Guide Pipeline
                                                              ├─ 📋 Before Interview Section
                                                              ├─ ⚙️ Technical Prep Section
                                                              ├─ 👤 Interviewer Background
                                                              └─ ❓ Strategic Questions
                                                              ↓
                                                         📚 Citation Integration
                                                              ├─ Source References
                                                              ├─ Research Backing
                                                              └─ Credibility Validation
                                                              ↓
                                                         🔤 Keyword Extractor (Company Name)
                                                              ↓
                                                         🖥️ Terminal Display (Complete Guide)
                                                              ↓
                                                         💾 Individual File Storage
                                                              ├─ Path: outputs/fullworkflow/
                                                              └─ File: [company_name].md
                                                              ↓
                                                         ➡️ Process Next Email
                                                              ↓
                                                         ┌─ More Emails Available? ──→ YES ──→ 📧 Individual Email Processing
                                                         │
                                                         └─ NO ──→ 🎊 Workflow Complete
                                                                   ├─ Display Processing Statistics  
                                                                   ├─ Show Cache Performance
                                                                   └─ Individual Guides Generated
```

## Key Features

### Individual Email Processing
- Each email in INTERVIEW_FOLDER is processed separately
- No batch processing - ensures focused, personalized preparation
- Individual output files stored as `outputs/fullworkflow/[company_name].md`

### Terminal Feedback
- Real-time classification results shown in terminal
- Memory check status: "Already Prepped" vs "New Email"
- Research progress and quality assessment displayed
- Complete prep guide displayed before storage

### Tavily Cache Integration
- All research calls use Tavily cache for optimization
- Cache manager available: `python workflows/cache_manager.py --status`
- Reduces API costs and improves performance

### Quality Assurance
- Deep reflection on research adequacy before guide generation
- Additional research loops if information is insufficient
- Citation integration for all personalized conclusions
- Structured output with clear sections and source references

## Workflow Steps Detail

### 1. Entry Point & Configuration
- Load environment variables from `.env` file
- Read INTERVIEW_FOLDER path configuration
- Initialize all pipeline components
- Set up cache management systems

### 2. Email Processing Loop
- Process emails one by one (individual processing)
- Each email goes through complete pipeline independently
- No batch processing to ensure personalized results

### 3. Classification & Routing
- Email Classifier determines email type
- Only interview-related emails proceed to next stages
- Non-interview emails are skipped with terminal feedback

### 4. Entity Extraction & Memory Check
- Extract company, interviewer, role, and timing data
- Check local memory store for duplicate processing
- Show terminal status: "Already Prepped" vs "New Email"

### 5. Deep Research with Quality Validation
- Parallel research on company, role, and interviewer
- Tavily API integration with intelligent caching
- Quality reflection to ensure adequate information
- Additional research loops if needed

### 6. Personalized Guide Generation
- Create comprehensive interview preparation guide
- Include citations for all research-backed conclusions
- Generate role-specific technical preparation
- Provide strategic questions tailored to interviewer

### 7. Output & Storage
- Display complete guide in terminal for review
- Generate company-based filename using keyword extractor
- Store individual file in `outputs/fullworkflow/`
- Process next email or complete workflow

## Cache Management Integration

### Tavily Research Cache
- Location: `cache/tavily/`
- Caches company, role, and interviewer research queries
- Automatic cache expiration and cleanup

### OpenAI Response Cache  
- Location: `.openai_cache/`
- Caches guide generation and entity extraction responses
- Cost optimization for repeated patterns

### Cache Monitoring
```bash
# Check cache status
python workflows/cache_manager.py --status

# Clear all caches
python workflows/cache_manager.py --clear-all

# Optimize cache performance
python workflows/cache_manager.py --optimize
```

This visualization shows the complete Interview Prep Workflow with individual email processing, terminal feedback, quality validation, and comprehensive output generation with proper citation integration.
    subgraph EntryPoint["� Interview Prep Workflow Entry Point"]
        direction TB
        StartWorkflow["⭐ START WORKFLOW<br>• Load environment variables<br>• Initialize pipeline components<br>• Read INTERVIEW_FOLDER from .env"]
        ReadEmails["� Read Email Files<br>• Get all emails from INTERVIEW_FOLDER<br>• Process one email at a time<br>• Individual email processing"]
    end

    %% Email Pipeline
    subgraph EmailPipeline["📧 Email Pipeline"]
        direction TB
        EmailClassifier["📬 Email Classifier Agent<br>• Classification: Interview/Personal/Other<br>• Show classification result in terminal<br>• Route based on classification"]
        ClassificationDecision{"✅ Interview Email?<br>Classification Result"}
        SkipNonInterview["⏭️ Skip Non-Interview<br>• Log classification result<br>• Process next email"]
        EntityExtractor["🎯 Entity Extractor Agent<br>• Extract company name<br>• Extract interviewer names<br>• Extract role details<br>• Extract date/time information"]
        MemoryCheck["� Memory Store Check<br>• Check local interview store<br>• Prevent duplicate processing<br>• Show: 'Already Prepped' vs 'New'"]
        AlreadyProcessed{"🤔 Already Processed?<br>Memory Check Result"}
        SkipDuplicate["⏭️ Skip Duplicate<br>• Log: 'Already processed'<br>• Move to next email"]
        StoreEntities["💾 Store Entity Information<br>• Save to memory systems<br>• Update interview store<br>• Log: 'Entities stored'"]
    end

    %% Deep Research Pipeline
    subgraph ResearchPipeline["🔬 Deep Research Pipeline"]
        direction TB
        ResearchCoordinator["🔬 Research Coordinator<br>• Validate extracted entities<br>• Plan research strategy<br>• Coordinate parallel API calls"]
        
        %% Parallel Research with Tavily Cache Integration
        ParallelResearch["🚀 Parallel Research Execution"]
        CompanyResearch["🏢 Company Research<br>• Tavily API with caching<br>• Company information & culture<br>• Recent news & developments<br>• Financial performance"]
        RoleResearch["🎯 Role Research<br>• Tavily API with caching<br>• Job market trends<br>• Skill requirements<br>• Salary benchmarks"]
        InterviewerResearch["👤 Interviewer Research<br>• Tavily API with caching<br>• LinkedIn profiles<br>• Professional background<br>• Publications & expertise"]
        
        ResearchReflection["🤔 Deep Research Reflection<br>• Analyze research quality<br>• Validate information adequacy<br>• Check for missing critical data<br>• Decision: Proceed or Re-research"]
        ResearchAdequate{"✅ Research Adequate?<br>Quality Assessment"}
        AdditionalResearch["🔄 Additional Research Loop<br>• Fill information gaps<br>• Targeted follow-up queries<br>• Enhanced data gathering"]
    end

    %% Prep Guide Pipeline
    subgraph PrepGuidePipeline["📚 Prep Guide Pipeline"]
        direction TB
        GuideGenerator["📝 Prep Guide Generator<br>• Personalized content creation<br>• Research-based insights<br>• Citation integration"]
        
        BeforeInterviewSection["� Before Interview Section<br>• Company overview with citations<br>• Key preparation points<br>• What to expect"]
        TechnicalPrepSection["⚙️ Technical Prep Section<br>• Role-based technical questions<br>• Skill competency areas<br>• Industry-specific knowledge"]
        InterviewerInsights["� Interviewer Background<br>• Professional background<br>• Career trajectory<br>• Areas of expertise<br>• Potential connections"]
        StrategicQuestions["❓ Questions to Ask Interviewer<br>• Personalized strategic questions<br>• Role-specific inquiries<br>• Company direction questions"]
        CitationEngine["📚 Citation Integration<br>• Source references<br>• Research backing<br>• Credibility validation"]
    end

    %% Output and Storage
    subgraph OutputSystem["� Output System"]
        direction TB
        KeywordExtraction["🔤 Keyword Extractor Agent<br>• Use agent_email.py<br>• Extract company name<br>• Generate filename: [company].md"]
        DisplayTerminal["�️ Display in Terminal<br>• Show complete prep guide<br>• Include all sections<br>• Display citations"]
        StoreOutput["💾 Store Individual Output<br>• Path: outputs/fullworkflow/<br>• Filename: [company_name].md<br>• Individual email processing"]
        NextEmail["➡️ Process Next Email<br>• Move to next email in folder<br>• Repeat entire pipeline<br>• Individual processing"]
    end

    %% Main Flow Connections
    StartWorkflow --> ReadEmails
    ReadEmails --> EmailClassifier
    EmailClassifier --> ClassificationDecision
    ClassificationDecision -->|"Not Interview"| SkipNonInterview
    ClassificationDecision -->|"Interview Email"| EntityExtractor
    SkipNonInterview --> NextEmail
    EntityExtractor --> MemoryCheck
    MemoryCheck --> AlreadyProcessed
    AlreadyProcessed -->|"Already Processed"| SkipDuplicate
    AlreadyProcessed -->|"New Email"| StoreEntities
    SkipDuplicate --> NextEmail
    StoreEntities --> ResearchCoordinator

    %% Research Pipeline Flow
    ResearchCoordinator --> ParallelResearch
    ParallelResearch --> CompanyResearch
    ParallelResearch --> RoleResearch
    ParallelResearch --> InterviewerResearch
    CompanyResearch --> ResearchReflection
    RoleResearch --> ResearchReflection
    InterviewerResearch --> ResearchReflection
    ResearchReflection --> ResearchAdequate
    ResearchAdequate -->|"Insufficient"| AdditionalResearch
    AdditionalResearch --> ResearchReflection
    ResearchAdequate -->|"Adequate"| GuideGenerator

    %% Prep Guide Generation Flow
    GuideGenerator --> BeforeInterviewSection
    GuideGenerator --> TechnicalPrepSection
    GuideGenerator --> InterviewerInsights
    GuideGenerator --> StrategicQuestions
    BeforeInterviewSection --> CitationEngine
    TechnicalPrepSection --> CitationEngine
    InterviewerInsights --> CitationEngine
    StrategicQuestions --> CitationEngine
    CitationEngine --> KeywordExtraction

    %% Output Flow
    KeywordExtraction --> DisplayTerminal
    DisplayTerminal --> StoreOutput
    StoreOutput --> NextEmail
    NextEmail -->|"More Emails"| EmailClassifier
    NextEmail -->|"No More Emails"| WorkflowComplete["🎊 Workflow Complete<br>• All emails processed<br>• Individual guides generated<br>• Cache statistics available"]

    %% Styling
    classDef entryPoint fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef emailPipeline fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef researchPipeline fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef prepPipeline fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef output fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    class StartWorkflow,ReadEmails entryPoint
    class EmailClassifier,EntityExtractor,MemoryCheck emailPipeline
    class ResearchCoordinator,CompanyResearch,RoleResearch,InterviewerResearch,ResearchReflection researchPipeline
    class GuideGenerator,BeforeInterviewSection,TechnicalPrepSection,InterviewerInsights,StrategicQuestions,CitationEngine prepPipeline
    class KeywordExtraction,DisplayTerminal,StoreOutput,NextEmail output
```

## Key Features

### Individual Email Processing
- Each email in INTERVIEW_FOLDER is processed separately
- No batch processing - ensures focused, personalized preparation
- Individual output files stored as `outputs/fullworkflow/[company_name].md`

### Terminal Feedback
- Real-time classification results shown in terminal
- Memory check status: "Already Prepped" vs "New Email"
- Research progress and quality assessment displayed
- Complete prep guide displayed before storage

### Tavily Cache Integration
- All research calls use Tavily cache for optimization
- Cache manager available: `python workflows/cache_manager.py --status`
- Reduces API costs and improves performance

### Quality Assurance
- Deep reflection on research adequacy before guide generation
- Additional research loops if information is insufficient
- Citation integration for all personalized conclusions
- Structured output with clear sections and source references

    %% Email System Connections
    UserTrigger --> GmailAPI
    GmailAPI --> Orchestrator
    Orchestrator --> EmailClassifier

    %% Email Classification Routing
    EmailClassifier -->|"Interview Emails"| EntityExtractor
    EmailClassifier -->|"Personal Emails"| UserCheck
    EmailClassifier -->|"Other Emails"| OtherEmailHandler

    %% Interview Processing Flow
    EntityExtractor --> InterviewCheck
    InterviewCheck -->|"New Interview"| ResearchCoordinator
    InterviewCheck -->|"Already Processed"| DiscardDuplicate
    InterviewCheck --> LocalStore

    %% Research Coordination (NEW - Single point before splitting)
    ResearchCoordinator -->|"Company Name"| CompanyResearch
    ResearchCoordinator -->|"Interviewer Names"| InterviewerResearch
    ResearchCoordinator -->|"Role Details"| RoleResearch

    %% Research to Questions
    CompanyResearch --> CompanyQuestions
    InterviewerResearch --> InterviewerQuestions
    RoleResearch --> RoleQuestions

    %% Question Aggregation
    CompanyQuestions --> PrepSummary
    InterviewerQuestions --> PrepSummary
    RoleQuestions --> PrepSummary
    GeneralQuestions --> PrepSummary

    %% Research Data to Summary
    CompanyResearch --> PrepSummary
    InterviewerResearch --> PrepSummary
    RoleResearch --> PrepSummary

    PrepSummary --> EmailSender

    %% Personal Email Flow
    UserCheck -->|"User Email"| EmailEmbedder
    UserCheck -->|"Not User Email"| EmailSender
    EmailEmbedder --> VectorStore
    VectorStore --> PersonalEmailWriter
    PersonalEmailWriter --> EmailSender

    %% Other Email Flow
    OtherEmailHandler --> EmailSender

    %% Resume Processing Connections
    ResumeUpload --> ResumeExtractor
    ResumeExtractor --> ResumeMemory
    ResumeMemory --> BehavioralPrep
    BehavioralPrep --> SelfReflection

    %% Integration Layer Connections
    ResumeMemory <--> SharedMemory
    LocalStore <--> SharedMemory
    VectorStore <--> SharedMemory
    CompanyResearch <--> SharedMemory
    InterviewerResearch <--> SharedMemory

    SharedMemory --> ContextBridge
    ContextBridge --> BehavioralPrep
    ContextBridge --> GeneralQuestions
    ContextBridge --> EmailWriterAgent
    ContextBridge --> PersonalEmailWriter

    %% Feedback Connections
    EmailSender --> UserFeedback
    SelfReflection --> FeedbackLoop
    UserFeedback --> FeedbackLoop
    FeedbackLoop --> SharedMemory

    %% Cross-Pipeline Intelligence (Dotted Lines)
    ResumeMemory -.->|"Skills & Experience"| CompanyQuestions
    ResumeMemory -.->|"Career Timeline"| InterviewerQuestions
    ResumeMemory -.->|"Technical Skills"| RoleQuestions
    BehavioralPrep -.->|"Answer Templates"| EmailWriterAgent
    BehavioralPrep -.->|"Response Patterns"| PersonalEmailWriter
    SelfReflection -.->|"Quality Standards"| EmailSender

    %% Styling
    classDef jobAppStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px,color:#000000
    classDef emailStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000000
    classDef researchStyle fill:#f1f8e9,stroke:#558b2f,stroke-width:2px,color:#000000
    classDef questionStyle fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px,color:#000000
    classDef flowStyle fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#000000
    classDef integrationStyle fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#000000
    classDef resumeStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000000

    %% Apply Styles
    ResumeUpload:::jobAppStyle
    ResumeAnalyzerAgent:::jobAppStyle
    JobDescInput:::jobAppStyle
    JobMatcherAgent:::jobAppStyle
    MatchDecision:::jobAppStyle
    TryDifferentJob:::jobAppStyle
    CompanyResearchJob:::jobAppStyle
    LinkedInFinderAgent:::jobAppStyle
    EmailWriterAgent:::jobAppStyle
    EmailDraftReview:::jobAppStyle
    SendEmail:::jobAppStyle
    ScheduleFollowup:::jobAppStyle
    InterviewSchedulerAgent:::jobAppStyle

    UserTrigger:::emailStyle
    GmailAPI:::emailStyle
    Orchestrator:::emailStyle
    EmailClassifier:::emailStyle
    EmailSender:::emailStyle
    UserFeedback:::emailStyle

    CompanyResearch:::researchStyle
    InterviewerResearch:::researchStyle
    RoleResearch:::researchStyle
    ResearchCoordinator:::researchStyle

    CompanyQuestions:::questionStyle
    InterviewerQuestions:::questionStyle
    RoleQuestions:::questionStyle
    GeneralQuestions:::questionStyle

    EntityExtractor:::flowStyle
    InterviewCheck:::flowStyle
    LocalStore:::flowStyle
    PrepSummary:::flowStyle
    UserCheck:::flowStyle
    EmailEmbedder:::flowStyle
    VectorStore:::flowStyle
    PersonalEmailWriter:::flowStyle
    OtherEmailHandler:::flowStyle
    DiscardDuplicate:::flowStyle

    SharedMemory:::integrationStyle
    ContextBridge:::integrationStyle
    FeedbackLoop:::integrationStyle

    ResumeExtractor:::resumeStyle
    ResumeMemory:::resumeStyle
    BehavioralPrep:::resumeStyle
    SelfReflection:::resumeStyle
```