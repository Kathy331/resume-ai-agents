# agents/interview_prep_intelligence/models.py
"""
Data models for Interview Prep Intelligence Agent system
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """Types of interview questions"""
    COMPANY_AWARE = "company_aware"
    INTERVIEWER_SPECIFIC = "interviewer_specific" 
    ROLE_SPECIFIC = "role_specific"
    GENERAL_BEHAVIORAL = "general_behavioral"


class ResearchContext(BaseModel):
    """Research context from workflow runner output"""
    interview_id: str
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    interviewer_name: Optional[str] = None
    
    # Research data from Tavily - structured format
    research_data: Dict[str, Any] = {}  # Contains company_research, interviewer_research, role_research
    
    # Quality indicators
    quality_indicators: Dict[str, float] = {}
    
    # Legacy compatibility
    company_research: Optional[Dict[str, Any]] = None
    interviewer_research: Optional[Dict[str, Any]] = None
    role_research: Optional[Dict[str, Any]] = None
    quality_score: float = 0.0
    research_confidence: float = 0.0
    processing_time: float = 0.0


class UserProfile(BaseModel):
    """User profile for personalization"""
    name: str
    experience_level: str  # entry, mid, senior
    skills: List[str] = []
    interests: List[str] = []
    preferences: Dict[str, Any] = {}
    background: Optional[str] = None


class WorkflowResults(BaseModel):
    """Results from workflow runner"""
    workflow_id: str
    results: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class Question(BaseModel):
    """Individual interview question"""
    id: str
    question_type: QuestionType
    question_text: str
    context: str  # Why this question is relevant
    difficulty_level: str  # easy, medium, hard
    expected_answer_points: List[str]  # Key points to cover in answer
    follow_up_questions: List[str] = []
    source_research: Optional[str] = None  # Which research finding inspired this
    
    
class QuestionCluster(BaseModel):
    """Cluster of related questions"""
    cluster_id: str
    cluster_name: str
    focus_area: str  # company, interviewer, role, behavioral
    questions: List[Question]
    priority_score: float = 0.0
    estimated_time_minutes: int = 5


class PrepSummary(BaseModel):
    """Comprehensive preparation summary"""
    interview_id: str
    generated_at: datetime
    
    # Question clusters
    company_questions: QuestionCluster
    interviewer_questions: QuestionCluster  
    role_questions: QuestionCluster
    behavioral_questions: QuestionCluster
    
    # Summary metrics
    total_questions: int
    estimated_prep_time_minutes: int
    confidence_score: float
    
    # Key insights
    company_insights: List[str]
    interviewer_insights: List[str]
    role_insights: List[str]
    success_strategies: List[str]
    
    # RAG sources
    sources_used: List[Dict[str, str]]  # title, url, relevance_score


class DeepResearchInput(BaseModel):
    """Input for deep research question planning"""
    workflow_results: Optional[WorkflowResults] = None  # For pipeline integration
    research_contexts: Optional[List[ResearchContext]] = None  # Direct input
    user_profile: Optional[UserProfile] = None  # User profile object
    preferences: Optional[Dict[str, Any]] = None  # Interview prep preferences
    processing_options: Optional[Dict[str, Any]] = None  # Processing configuration
    previous_prep_history: Optional[List[Dict[str, Any]]] = None


class DeepResearchOutput(BaseModel):
    """Output from deep research question planning"""
    success: bool
    prep_summaries: List[PrepSummary]
    processing_time: float
    total_questions_generated: int
    avg_confidence_score: float
    errors: List[str] = []
    metadata: Dict[str, Any] = {}
