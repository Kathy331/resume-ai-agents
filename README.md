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

### 1. Clone the Repository

### 2. Create a virtual environment
Make sure local python interpreter is also in the same venv

For Mac/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

For Windows (PowerShell):
```bash
python -m venv .venv
.venv\Scripts\Activate
```

### 3. Install Dependencies
Using pip:
```bash
pip install -r requirements.txt
```

Or with Poetry:
```bash
poetry install
```

### 4. Set Up Environment Variables
Copy `.env.example` to `.env` and fill in your:
- OpenAI API Key (create one here: https://platform.openai.com/api-keys)
- Tavily API Key (create one here: https://www.tavily.com/)
- Google API credentials

```bash
cp .env.example .env
```

### 5. Run Streamlit Frontend
```bash
streamlit run ui/app.py
```

### 6. Docker (Optional: for deployment only)
Download Docker for Mac or Windows: https://www.docker.com/  
```bash
docker compose up --build 
```
### 7. Testing 
to run all test you could run: 
```bash
pytest
```
but please be careful of token limits, to run a single test, run: 
```bash
pytest tests/test_agents/test_keyword_extractor.py
```
there will be an `outputs` file generated for you to better see your test results 
