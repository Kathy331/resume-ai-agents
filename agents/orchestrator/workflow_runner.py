# orchestrator/workflow_runner.py  
# EXECUTION LAYER - Runs workflows, handles results, integrates with external systems
import os
import sys
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
WORKFLOW RUNNER — Executes the email processing workflow and handles results.

This module is responsible for:
- Initializing and running the LangGraph workflow defined in langgraph_coordinator.py.
- Handling exceptions, retries, and final state processing.
- Logging results, sending notifications (e.g. interview invites), and printing summaries.
- Supporting both synchronous and asynchronous execution contexts.
- Maintaining execution history for debugging or analytics.

NOTE:
This file does NOT define workflow logic — it delegates that to the LangGraph coordinator.
"""

class WorkflowRunner:
    """
    Orchestrates workflow execution and handles results
    This is where we integrate with external systems, logging, notifications, etc.
    """
    
    def __init__(self, enable_notifications=True, log_results=True):
        self.enable_notifications = enable_notifications
        self.log_results = log_results
        self.execution_history = []
    
    def run_email_pipeline(self, folder_name: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Main entry point - runs the email pipeline and handles results
        """
        if not folder_name:
            raise ValueError("folder_name argument is required and cannot be empty.")
        
        print(f"🚀 Starting email pipeline for folder: {folder_name}")
        start_time = datetime.now()
        
        try:
            # Import and run the LangGraph coordinator
            from agents.orchestrator.langgraph_coordinator import build_email_workflow, initialize_state
            
            # Create workflow and initial state
            workflow = build_email_workflow()
            initial_state = initialize_state(folder_name, max_results)
            
            # Execute the workflow
            final_state = workflow.invoke(initial_state)
            
            # Process results
            execution_result = self._process_workflow_results(final_state, start_time)
            
            # Handle post-processing
            self._handle_post_processing(execution_result)
            
            return execution_result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'folder_name': folder_name,
                'execution_time': (datetime.now() - start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
            
            if self.log_results:
                print(f"💥 Pipeline failed: {str(e)}")
            
            return error_result
    
    def _process_workflow_results(self, final_state: Dict, start_time: datetime) -> Dict[str, Any]:
        """Process the final state from LangGraph into a structured result"""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            'success': final_state.get('processing_complete', False) and not final_state.get('error'),
            'folder_name': final_state.get('folder_name'),
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat(),
            'email_count': len(final_state.get('raw_emails', [])),
            'classifications': {},
            'summaries': final_state.get('summaries', []),
            'should_notify': final_state.get('should_notify', False),
            'error': final_state.get('error', None)
        }
        
        # Extract classification counts
        classified = final_state.get('classified_emails', {})
        for category, emails in classified.items():
            result['classifications'][category] = len(emails)
        
        return result
    
    def _handle_post_processing(self, result: Dict[str, Any]):
        """Handle post-processing: notifications, logging, external integrations"""
        
        # Log results
        if self.log_results:
            self._log_execution_result(result)
        
        # Send notifications if needed
        if self.enable_notifications and result.get('should_notify'):
            self._send_notifications(result)
        
        # Store execution history
        self.execution_history.append(result)
        
        # Display results to user
        self._display_results(result)
    
    def _log_execution_result(self, result: Dict[str, Any]):
        """Log execution results (could write to file, database, etc.)"""
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"\n{status} - Email Pipeline Execution Summary")
        print(f"📁 Folder: {result['folder_name']}")
        print(f"⏱️  Execution time: {result['execution_time']:.2f}s")
        print(f"📧 Emails processed: {result['email_count']}")
        
        if result['success']:
            print("📊 Classifications:")
            for category, count in result['classifications'].items():
                print(f"   {category}: {count}")
        else:
            print(f"💥 Error: {result['error']}")
    
    def _send_notifications(self, result: Dict[str, Any]):
        """Send notifications for important emails (interviews, etc.)"""
        interview_count = result['classifications'].get('Interview_invite', 0)
        if interview_count > 0:
            print(f"🔔 NOTIFICATION: {interview_count} new interview invite(s) detected!")
            # Here you could integrate with:
            # - Slack/Discord webhooks
            # - Push notifications
            # - Email alerts
            # - SMS via Twilio
            # - etc.
    
    def _display_results(self, result: Dict[str, Any]):
        """Display formatted results to the user"""
        if not result['success']:
            return
            
        print(f"\n📬 Email Summary for '{result['folder_name']}':")
        print("=" * 50)
        
        for summary in result['summaries']:
            print(f"{summary['icon']} {summary['message']}")
        
        print("=" * 50)
    
    def get_execution_history(self) -> list:
        """Return execution history for analytics/debugging"""
        return self.execution_history
    
    async def run_email_pipeline_async(self, folder_name: str, max_results: int = 10):
        """Async version for integration with async frameworks"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run_email_pipeline, folder_name, max_results)

# Entry point
if __name__ == "__main__":
    runner = WorkflowRunner(enable_notifications=True, log_results=True)
    
    # Run the pipeline
    result = runner.run_email_pipeline(folder_name='test', max_results=10)
    
    # You can also access execution history
    # print(f"\nExecution history: {len(runner.get_execution_history())} runs")