# resume-ai-agents
![Project Banner](docs/images/banner.png) <!-- temporary -->

Resume AI Agents is a modular AI system that automates job search and application workflows using specialized agents. It streamlines:

- LinkedIn profile discovery
- Resume analysis and skill extraction
- Job matching and recommendations
- Personalized follow-up and application emails
- Calendar integration for interviews

All powered by a Streamlit dashboard UI and orchestrated workflows for seamless execution.

## Features

- <!-- showcase added here --> Modular AI agent design
- <!-- showcase added here --> Orchestrator pattern for flexible workflows
- <!-- showcase added here --> Resume-to-job semantic matching
- <!-- showcase added here --> Personalized email drafting matching user tone
- <!-- showcase added here --> Streamlit dashboard for easy interaction
- <!-- showcase added here --> Future-ready for Retrieval-Augmented Generation (RAG) modules

## Setup

### Clone the Repository
### Install Dependencies

Using pip:
```bash
pip install -r requirements.txt
```

Or with Poetry:
```bash
poetry install
```

### Set Up Environment Variables
Copy `.env.example` to `.env` and fill in your:
- OpenAI API Key
- Tavily API Key
- Google API credentials

```bash
cp .env.example .env
```

### Run Streamlit Frontend
```bash
streamlit run ui/app.py
```