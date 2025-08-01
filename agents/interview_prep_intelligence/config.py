# agents/interview_prep_intelligence/config.py
"""
Configuration for Interview Prep Intelligence Agent system
"""

from typing import Dict, Any, List

# LLM Configuration
LLM_CONFIG = {
    "model_name": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 30
}

# Question Generation Configuration
QUESTION_CONFIG = {
    "max_questions_per_category": 8,
    "min_questions_per_category": 3,
    "difficulty_distribution": {
        "easy": 0.3,
        "medium": 0.5, 
        "hard": 0.2
    },
    "estimated_time_per_question": 3  # minutes
}

# Research Processing Configuration
RESEARCH_CONFIG = {
    "min_quality_threshold": 0.3,
    "max_search_results_per_type": 5,
    "content_similarity_threshold": 0.8,
    "max_content_length": 1000  # characters per search result
}

# Chain-of-Thought Prompts
COT_PROMPTS = {
    "company_analysis": """
    Think step by step about this company research data:
    1. What are the key business areas and values?
    2. What recent developments or challenges might they face?
    3. What would they want candidates to understand about their culture?
    4. What questions would test cultural fit and company knowledge?
    
    Research data: {research_data}
    """,
    
    "interviewer_analysis": """
    Think step by step about this interviewer research data:
    1. What is their professional background and expertise?
    2. What would they likely focus on in an interview?
    3. What communication style might they prefer?
    4. What questions would demonstrate you've researched them professionally?
    
    Research data: {research_data}
    """,
    
    "role_analysis": """
    Think step by step about this role research data:
    1. What are the core technical and soft skills required?
    2. What challenges would someone in this role face?
    3. What growth opportunities exist in this role?
    4. What questions would test relevant competencies?
    
    Research data: {research_data}
    """,
    
    "behavioral_synthesis": """
    Think step by step about creating behavioral questions:
    1. What behaviors would predict success in this context?
    2. What common challenges might arise?
    3. What values and work styles are important?
    4. What STAR method questions would be most revealing?
    
    Context: Company: {company}, Role: {role}, Interviewer: {interviewer}
    """
}

# RAG Configuration
RAG_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "top_k_retrieval": 5,
    "similarity_threshold": 0.7,
    "rerank_top_k": 3
}

# Vector Store Configuration  
VECTOR_CONFIG = {
    "embedding_model": "text-embedding-3-small",
    "dimension": 1536,
    "index_type": "flat",
    "metric": "cosine"
}

# Memory and Personalization
MEMORY_CONFIG = {
    "max_history_entries": 50,
    "personalization_weight": 0.3,
    "recency_decay": 0.9,
    "similarity_boost": 0.2
}

# Output Structure Templates
OUTPUT_TEMPLATES = {
    "question_format": {
        "question": "",
        "context": "",
        "difficulty": "",
        "key_points": [],
        "follow_ups": [],
        "source": ""
    },
    
    "summary_format": {
        "overview": "",
        "key_insights": [],
        "success_strategies": [],
        "preparation_time": 0,
        "confidence_level": ""
    }
}

# Quality Assessment Weights
QUALITY_WEIGHTS = {
    "research_completeness": 0.4,
    "question_relevance": 0.3,
    "difficulty_balance": 0.2,
    "personalization": 0.1
}
