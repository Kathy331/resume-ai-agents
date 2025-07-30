# shared/models.py
"""
Shared data models for the Resume AI Agents system

This module contains all the common data structures used across agents,
including input/output formats and domain-specific models.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

class AgentInput(BaseModel):
    """Standard input format for all agents"""
    data: Dict[str, Any]  # Input data for the agent, in a dictionary format, key value pairs
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata about the input (e.g., source, timestamp)
    previous_agent_output: Optional[Dict[str, Any]] = None  # Output from a previous agent, if needed for context

class AgentOutput(BaseModel):
    """Standard output format for all agents"""
    success: bool  # Indicates if the agent executed successfully
    data: Dict[str, Any]  # Output data from the agent, in a dictionary format
    metadata: Dict[str, Any]  # Additional metadata about the output (e.g., processing time, source)
    errors: Optional[List[str]] = None  # List of errors encountered during execution, if any
    next_agent_suggestions: Optional[List[str]] = None  # Suggestions for next agents to handle the output, if applicable

class EmailData(BaseModel):
    """Email data structure"""
    id: str
    subject: str
    sender: str
    recipients: str
    body: str
    snippet: str
    date: str
    has_attachments: bool = False
    star: bool = False
    label: Optional[str] = None

class InterviewData(BaseModel):
    """Interview data structure"""
    id: Optional[int] = None
    email_id: Optional[str] = None
    candidate_name: Optional[str] = None
    company_name: Optional[str] = None
    role: Optional[str] = None
    interviewer: Optional[str] = None
    interview_date: Optional[str] = None
    interview_time: Optional[str] = None
    duration: Optional[str] = None
    location: Optional[str] = None
    format: Optional[str] = None
    status: str = "preparing"  # preparing, prepped, scheduled, completed, cancelled
    raw_entities: Optional[str] = None
    content_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class EntityExtractionResult(BaseModel):
    """Result from entity extraction"""
    candidates: List[str] = []
    companies: List[str] = []
    roles: List[str] = []
    interviewers: List[str] = []
    dates: List[str] = []
    times: List[str] = []
    durations: List[str] = []
    locations: List[str] = []
    email_id: Optional[str] = None

class ResearchData(BaseModel):
    """Research data structure"""
    company_info: Optional[Dict[str, Any]] = None
    role_info: Optional[Dict[str, Any]] = None
    interviewer_info: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class ClassificationResult(BaseModel):
    """Email classification result"""
    category: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None