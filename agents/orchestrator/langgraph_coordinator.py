# ============================================================================
# orchestrator/langgraph_coordinator.py
# STATE MANAGEMENT & INTELLIGENT ROUTING using LangGraph
"""
LANGGRAPH COORDINATOR — Defines the state machine for the email processing workflow.

This module is responsible for:
- Defining the EmailWorkflowState that carries data through each node.
- Constructing the LangGraph graph using nodes (steps) and conditional routing.
- Handling Gmail setup, email fetching, classification, formatting, and error recovery.
- Returning a compiled LangGraph object that can be executed by a runner.

NOTE:
This file does NOT execute the workflow or handle output, it only defines the structure 
and logic of the pipeline using LangGraph.
"""

from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
import json

class EmailWorkflowState(TypedDict):
    """Enhanced state object that flows through the LangGraph workflow"""
    folder_name: str
    max_results: int
    gmail_service: Any
    raw_emails: List[Dict]
    classified_emails: Dict[str, List]
    interview_processing_results: List[Dict]  # New: Results from enhanced interview processing
    email_pipeline: Any  # Email pipeline instance
    summaries: List[Dict]
    error: str
    retry_count: int
    should_notify: bool
    processing_complete: bool
    research_performed_count: int  # New: Track how many interviews got research
    memory_hits_count: int  # New: Track how many were found in memory

def initialize_state(folder_name: str, max_results: int = 10) -> EmailWorkflowState:
    """Create initial state for the enhanced workflow"""
    return EmailWorkflowState(
        folder_name=folder_name,
        max_results=max_results,
        gmail_service=None,
        raw_emails=[],
        classified_emails={},
        interview_processing_results=[],
        email_pipeline=None,
        summaries=[],
        error="",
        retry_count=0,
        should_notify=False,
        processing_complete=False,
        research_performed_count=0,
        memory_hits_count=0
    )

# LangGraph Node Functions
def setup_gmail_node(state: EmailWorkflowState) -> EmailWorkflowState:
    """Node: Initialize Gmail service"""
    try:
        from workflows.email_pipeline import create_gmail_service
        state["gmail_service"] = create_gmail_service()
        print(f"✅ Gmail service initialized for folder: {state['folder_name']}")
        return state
    except Exception as e:
        state["error"] = f"Gmail setup failed: {str(e)}"
        return state

def fetch_emails_node(state: EmailWorkflowState) -> EmailWorkflowState:
    """Node: Fetch and parse emails"""
    try:
        from workflows.email_pipeline import fetch_and_parse_emails
        emails = fetch_and_parse_emails(
            state["gmail_service"], 
            state["folder_name"], 
            state["max_results"]
        )
        state["raw_emails"] = emails
        print(f"✅ Fetched {len(emails)} emails from {state['folder_name']}")
        return state
    except Exception as e:
        state["error"] = f"Email fetch failed: {str(e)}"
        state["retry_count"] += 1
        return state

def classify_emails_node(state: EmailWorkflowState) -> EmailWorkflowState:
    """Node: Classify emails into categories"""
    try:
        from workflows.email_pipeline import classify_emails
        classified = classify_emails(state["raw_emails"])
        state["classified_emails"] = classified
        
        # Smart routing decision
        interview_count = len(classified.get('Interview_invite', []))
        if interview_count > 0:
            state["should_notify"] = True
            
        print(f"✅ Classified emails: {interview_count} interviews, "
              f"{len(classified.get('Personal_sent', []))} personal, "
              f"{len(classified.get('Others', []))} others")
        return state
    except Exception as e:
        state["error"] = f"Classification failed: {str(e)}"
        return state

def setup_email_pipeline_node(state: EmailWorkflowState) -> EmailWorkflowState:
    """Node: Initialize enhanced pipeline for interview processing"""
    try:
        from workflows.email_pipeline import create_email_pipeline
        state["email_pipeline"] = create_email_pipeline()
        print("✅ Enhanced pipeline initialized")
        return state
    except Exception as e:
        state["error"] = f"Enhanced pipeline setup failed: {str(e)}"
        return state

def process_interviews_node(state: EmailWorkflowState) -> EmailWorkflowState:
    """Node: Process interview invites through enhanced pipeline"""
    try:
        import asyncio
        from workflows.email_pipeline import process_classified_interviews
        
        # Process interview invites with entity extraction, memory check, and conditional research
        # Use asyncio.run to handle the async function
        results = asyncio.run(process_classified_interviews(
            state["classified_emails"], 
            state["email_pipeline"]
        ))
        
        state["interview_processing_results"] = results
        
        # Count research vs memory hits
        research_count = sum(1 for r in results if r.get('research_performed'))
        memory_hits = len(results) - research_count
        
        state["research_performed_count"] = research_count
        state["memory_hits_count"] = memory_hits
        
        print(f"✅ Processed {len(results)} interview invites: "
              f"{research_count} researched, {memory_hits} found in memory")
        return state
    except Exception as e:
        state["error"] = f"Interview processing failed: {str(e)}"
        return state

def format_output_node(state: EmailWorkflowState) -> EmailWorkflowState:
    """Node: Format final output including enhanced processing results"""
    try:
        from workflows.email_pipeline import format_email_summaries
        summaries = format_email_summaries(state["classified_emails"])
        
        # Add enhanced processing summaries
        if state["interview_processing_results"]:
            interview_summary = {
                'icon': '🎯',
                'message': f"Enhanced Interview Processing: {state['research_performed_count']} researched, "
                          f"{state['memory_hits_count']} found in memory (skipped research)"
            }
            summaries.append(interview_summary)
            
            # Add details for each processed interview
            for result in state["interview_processing_results"]:
                if result.get('entities') and result['entities'].get('success'):
                    entities = result['entities']['data']
                    company = entities.get('COMPANY', ['Unknown'])[0] if entities.get('COMPANY') else 'Unknown'
                    role = entities.get('ROLE', ['Unknown'])[0] if entities.get('ROLE') else 'Unknown'
                    
                    status_icon = "🔍" if result.get('research_performed') else "📋"
                    action = "researched" if result.get('research_performed') else "found in memory"
                    
                    detail_summary = {
                        'icon': status_icon,
                        'message': f"{company} - {role}: {action}"
                    }
                    summaries.append(detail_summary)
        
        state["summaries"] = summaries
        state["processing_complete"] = True
        print("✅ Enhanced email summaries formatted")
        return state
    except Exception as e:
        state["error"] = f"Formatting failed: {str(e)}"
        return state

def error_handler_node(state: EmailWorkflowState) -> EmailWorkflowState:
    """Node: Handle errors with retry logic"""
    print(f"❌ Error encountered: {state['error']}")
    
    # Retry logic for transient failures
    if state["retry_count"] < 3 and "fetch" in state["error"].lower():
        print(f"🔄 Retrying... (attempt {state['retry_count'] + 1}/3)")
        state["error"] = ""  # Clear error to retry
        return state
    
    print("💥 Max retries reached or permanent error")
    return state

# Conditional routing functions
def should_retry(state: EmailWorkflowState) -> str:
    """Route: Determine if we should retry or fail"""
    if state["error"] and state["retry_count"] < 3 and "fetch" in state["error"].lower():
        return "fetch_emails"
    elif state["error"]:
        return "error_handler"
    else:
        return "classify_emails"

def route_after_classification(state: EmailWorkflowState) -> str:
    """Route: Determine next step after classification"""
    if state["error"]:
        return "error_handler"
    
    # Check if we have interview invites to process
    interview_count = len(state["classified_emails"].get('Interview_invite', []))
    if interview_count > 0:
        return "setup_email_pipeline"
    else:
        return "format_output"

def route_after_pipeline_setup(state: EmailWorkflowState) -> str:
    """Route: Continue to interview processing or handle errors"""
    if state["error"]:
        return "error_handler"
    else:
        return "process_interviews"

def route_after_interview_processing(state: EmailWorkflowState) -> str:
    """Route: Continue to formatting after interview processing"""
    if state["error"]:
        return "error_handler"
    else:
        return "format_output"

def is_complete(state: EmailWorkflowState) -> str:
    """Route: Check if processing is complete"""
    if state["processing_complete"]:
        return END
    elif state["error"]:
        return END
    else:
        return "format_output"

# Build the enhanced LangGraph workflow
def build_email_workflow():
    """Construct the enhanced state graph for email processing with conditional routing"""
    workflow = StateGraph(EmailWorkflowState)
    
    # Add nodes
    workflow.add_node("setup_gmail", setup_gmail_node)
    workflow.add_node("fetch_emails", fetch_emails_node)
    workflow.add_node("classify_emails", classify_emails_node)
    workflow.add_node("setup_email_pipeline", setup_email_pipeline_node)
    workflow.add_node("process_interviews", process_interviews_node)  # New
    workflow.add_node("format_output", format_output_node)
    workflow.add_node("error_handler", error_handler_node)
    
    # Define the enhanced flow
    workflow.set_entry_point("setup_gmail")
    
    # Gmail setup -> fetch emails (or error)
    workflow.add_conditional_edges(
        "setup_gmail",
        lambda state: "fetch_emails" if not state["error"] else "error_handler"
    )
    
    # Fetch emails -> classify (with retry logic)
    workflow.add_conditional_edges("fetch_emails", should_retry)
    
    # Classify -> enhanced processing or direct to format (based on interview count)
    workflow.add_conditional_edges("classify_emails", route_after_classification)
    
    # Enhanced pipeline setup -> process interviews (or error)
    workflow.add_conditional_edges("setup_email_pipeline", route_after_pipeline_setup)
    
    # Process interviews -> format output (or error)
    workflow.add_conditional_edges("process_interviews", route_after_interview_processing)
    
    # Format output -> end
    workflow.add_conditional_edges("format_output", is_complete)
    
    # Error handler -> end
    workflow.add_edge("error_handler", END)
    
    return workflow.compile()
