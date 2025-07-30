# ============================================================================
# orchestrator/langgraph_coordinator.py
# STATE MANAGEMENT & INTELLIGENT ROUTING using LangGraph
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
import json

class EmailWorkflowState(TypedDict):
    """State object that flows through the LangGraph workflow"""
    folder_name: str
    max_results: int
    gmail_service: Any
    raw_emails: List[Dict]
    classified_emails: Dict[str, List]
    summaries: List[Dict]
    error: str
    retry_count: int
    should_notify: bool
    processing_complete: bool

def initialize_state(folder_name: str, max_results: int = 10) -> EmailWorkflowState:
    """Create initial state for the workflow"""
    return EmailWorkflowState(
        folder_name=folder_name,
        max_results=max_results,
        gmail_service=None,
        raw_emails=[],
        classified_emails={},
        summaries=[],
        error="",
        retry_count=0,
        should_notify=False,
        processing_complete=False
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

def format_output_node(state: EmailWorkflowState) -> EmailWorkflowState:
    """Node: Format final output"""
    try:
        from workflows.email_pipeline import format_email_summaries
        summaries = format_email_summaries(state["classified_emails"])
        state["summaries"] = summaries
        state["processing_complete"] = True
        print("✅ Email summaries formatted")
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
    """Route: Continue to formatting or handle errors"""
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

# Build the LangGraph workflow
def build_email_workflow():
    """Construct the state graph for email processing"""
    workflow = StateGraph(EmailWorkflowState)
    
    # Add nodes
    workflow.add_node("setup_gmail", setup_gmail_node)
    workflow.add_node("fetch_emails", fetch_emails_node)
    workflow.add_node("classify_emails", classify_emails_node)
    workflow.add_node("format_output", format_output_node)
    workflow.add_node("error_handler", error_handler_node)
    
    # Define the flow
    workflow.set_entry_point("setup_gmail")
    
    # Gmail setup -> fetch emails (or error)
    workflow.add_conditional_edges(
        "setup_gmail",
        lambda state: "fetch_emails" if not state["error"] else "error_handler"
    )
    
    # Fetch emails -> classify (with retry logic)
    workflow.add_conditional_edges("fetch_emails", should_retry)
    
    # Classify -> format output (or error)
    workflow.add_conditional_edges("classify_emails", route_after_classification)
    
    # Format output -> end
    workflow.add_conditional_edges("format_output", is_complete)
    
    # Error handler -> end
    workflow.add_edge("error_handler", END)
    
    return workflow.compile()
