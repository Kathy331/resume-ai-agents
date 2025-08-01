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
    
    def run_email_pipeline(self, folder_name: str, max_results: int = 10, user_email: str = "") -> Dict[str, Any]:
        """
        Main entry point - runs the email pipeline and handles results
        
        Args:
            folder_name: Gmail folder to process
            max_results: Maximum number of emails to process
            user_email: User's email for personal classification
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
            initial_state = initialize_state(folder_name, max_results, user_email)
            
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
        
        # Add type information for consistency
        if 'type' not in result:
            result['type'] = 'email_pipeline'
        
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
    
    async def run_email_pipeline_async(self, folder_name: str, max_results: int = 10, user_email: str = ""):
        """Async version for integration with async frameworks"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run_email_pipeline, folder_name, max_results, user_email)
    
    def run_research_pipeline(self, max_interviews: int = 10, priority_filter: str = "all") -> Dict[str, Any]:
        """
        Run the research engine pipeline for unprepped interviews
        
        Args:
            max_interviews: Maximum number of interviews to research
            priority_filter: Filter by priority level (all, high, normal, low)
        """
        print(f"🔬 Starting Research Engine Pipeline for unprepped interviews")
        start_time = datetime.now()
        
        try:
            # Import and run the research pipeline
            from workflows.research_engine_pipeline import create_research_pipeline
            
            # Create pipeline
            pipeline = create_research_pipeline()
            
            # Execute the research pipeline asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                execution_result = loop.run_until_complete(
                    pipeline.run_research_pipeline(max_interviews, priority_filter)
                )
            finally:
                loop.close()
            
            # Process results
            execution_result['runner_processing_time'] = (datetime.now() - start_time).total_seconds()
            
            # Handle post-processing
            self._handle_research_post_processing(execution_result)
            
            return execution_result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'max_interviews': max_interviews,
                'priority_filter': priority_filter,
                'runner_processing_time': (datetime.now() - start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
            
            if self.log_results:
                print(f"💥 Research Pipeline failed: {str(e)}")
            
            return error_result
    
    def _handle_research_post_processing(self, result: Dict[str, Any]):
        """Handle post-processing for research pipeline results"""
        try:
            # Log results
            if self.log_results and result.get('success'):
                self._display_research_results(result)
            
            # Add to execution history
            self.execution_history.append({
                'type': 'research_pipeline',
                'timestamp': result.get('timestamp'),
                'success': result.get('success'),
                'interviews_researched': result.get('interviews_researched', 0),
                'processing_time': result.get('processing_time', 0)
            })
            
            # Send notifications if enabled
            if self.enable_notifications and result.get('interviews_researched', 0) > 0:
                self._send_research_notification(result)
                
        except Exception as e:
            print(f"⚠️ Post-processing error: {str(e)}")
    
    def _display_research_results(self, result: Dict[str, Any]):
        """Display formatted research results to the user"""
        if not result['success']:
            print(f"❌ Research Pipeline Failed: {result.get('error', 'Unknown error')}")
            return
            
        print(f"\n🔬 Research Engine Pipeline Results:")
        print("=" * 80)
        print(f"📊 Interviews Found: {result.get('interviews_found', 0)}")
        print(f"✅ Successfully Researched: {result.get('interviews_researched', 0)}")
        print(f"❌ Failed Research: {result.get('failed_research', 0)}")
        print(f"📈 Average Quality Score: {result.get('average_quality', 0):.2f}")
        print(f"⏱️  Processing Time: {result.get('processing_time', 0):.2f}s")
        
        # Display detailed results for each interview
        research_results = result.get('research_results', [])
        if research_results:
            print(f"\n📋 Detailed Interview Research Results:")
            print("=" * 80)
            
            for i, res in enumerate(research_results, 1):
                # Get company name
                company = "Unknown Company"
                if hasattr(res, 'company_research') and res.company_research and res.company_research.get('data'):
                    company_data = res.company_research['data']
                    if isinstance(company_data, dict):
                        company = company_data.get('company_name', company_data.get('name', company))
                elif hasattr(res, 'company_name'):
                    company = res.company_name or 'Unknown Company'
                elif hasattr(res, 'interview_id'):
                    company = f"Interview {res.interview_id}"
                
                quality_score = getattr(res, 'quality_score', 0.0)
                processing_time = getattr(res, 'processing_time', 0.0)
                
                print(f"\n🎯 INTERVIEW {i}: {company}")
                print(f"   📈 Quality Score: {quality_score:.2f} | ⏱️ Time: {processing_time:.1f}s")
                print("-" * 60)
                
                # Show Company Research Results
                if hasattr(res, 'company_research') and res.company_research:
                    print("🏢 COMPANY RESEARCH:")
                    company_data = res.company_research.get('data', {})
                    if isinstance(company_data, dict) and 'search_results' in company_data:
                        search_results = company_data['search_results']
                        if isinstance(search_results, list) and search_results:
                            print(f"   📊 Found {len(search_results)} company results:")
                            for j, sr in enumerate(search_results[:3], 1):  # Show top 3
                                title = sr.get('title', 'No title')[:50] + ('...' if len(sr.get('title', '')) > 50 else '')
                                url = sr.get('url', 'No URL')
                                print(f"     {j}. {title}")
                                print(f"        🔗 {url}")
                        else:
                            print("   ✅ Company research completed (no detailed results)")
                    else:
                        print("   ✅ Company research completed")
                else:
                    print("🏢 COMPANY RESEARCH: ❌ Not performed")
                
                # Show Interviewer Research Results  
                if hasattr(res, 'interviewer_research') and res.interviewer_research:
                    print("👤 INTERVIEWER RESEARCH:")
                    interviewer_data = res.interviewer_research.get('data', {})
                    if isinstance(interviewer_data, dict) and 'search_results' in interviewer_data:
                        search_results = interviewer_data['search_results']
                        if isinstance(search_results, list) and search_results:
                            print(f"   📊 Found {len(search_results)} interviewer results:")
                            for j, sr in enumerate(search_results[:3], 1):  # Show top 3
                                title = sr.get('title', 'No title')[:50] + ('...' if len(sr.get('title', '')) > 50 else '')
                                url = sr.get('url', 'No URL')
                                print(f"     {j}. {title}")
                                print(f"        🔗 {url}")
                        else:
                            print("   ✅ Interviewer research completed (no detailed results)")
                    else:
                        print("   ✅ Interviewer research completed")
                else:
                    print("👤 INTERVIEWER RESEARCH: ❌ Not performed")
                
                # Show Role Research Results
                if hasattr(res, 'role_research') and res.role_research:
                    print("💼 ROLE RESEARCH:")
                    role_data = res.role_research.get('data', {})
                    if isinstance(role_data, dict) and 'search_results' in role_data:
                        search_results = role_data['search_results']
                        if isinstance(search_results, list) and search_results:
                            print(f"   📊 Found {len(search_results)} role results:")
                            for j, sr in enumerate(search_results[:3], 1):  # Show top 3
                                title = sr.get('title', 'No title')[:50] + ('...' if len(sr.get('title', '')) > 50 else '')
                                url = sr.get('url', 'No URL')
                                print(f"     {j}. {title}")
                                print(f"        🔗 {url}")
                        else:
                            print("   ✅ Role research completed (no detailed results)")
                    else:
                        print("   ✅ Role research completed")
                else:
                    print("💼 ROLE RESEARCH: ❌ Not performed")
                    
                if i < len(research_results):  # Add separator between interviews
                    print()
        
        print("=" * 80)
    
    def _send_research_notification(self, result: Dict[str, Any]):
        """Send notification about research completion (placeholder)"""
        # This could be extended to send email, Slack, or other notifications
        researched_count = result.get('interviews_researched', 0)
        avg_quality = result.get('average_quality', 0)
        
        print(f"🔔 Notification: {researched_count} interviews researched with {avg_quality:.1%} average quality")

    def demo_research_engine(self, company_name: str = "JUTEQ", role_title: str = "AI Engineer") -> Dict[str, Any]:
        """
        Demo the research engine with real Tavily API calls
        
        Args:
            company_name: Company to research
            role_title: Role to research
        """
        print(f"🚀 RESEARCH ENGINE DEMO")
        print(f"🎯 Researching: {company_name} - {role_title}")
        print("=" * 50)
        
        try:
            # Check if Tavily API key is available
            import os
            if not os.getenv('TAVILY_API_KEY'):
                print("⚠️  TAVILY_API_KEY not found - using simulation mode")
                return self._demo_simulation(company_name, role_title)
            
            # Import search function
            from shared.tavily_client import search_tavily
            
            # Research company
            print(f"\n🏢 Researching {company_name}...")
            company_query = f"{company_name} company overview industry technology"
            company_results = search_tavily(company_query, search_depth="advanced", max_results=5)
            
            # Research role
            print(f"💼 Researching {role_title} role...")
            role_query = f"{role_title} {company_name} job requirements skills salary"
            role_results = search_tavily(role_query, search_depth="basic", max_results=4)
            
            # Generate summary
            print(f"\n📊 RESEARCH SUMMARY:")
            print(f"✅ Company results: {len(company_results)} sources found")
            print(f"✅ Role results: {len(role_results)} sources found")
            
            if company_results:
                print(f"\n🏢 Company insights:")
                for i, result in enumerate(company_results[:2], 1):
                    title = result.get('title', 'No title')[:60]
                    print(f"  {i}. {title}{'...' if len(result.get('title', '')) > 60 else ''}")
            
            if role_results:
                print(f"\n💼 Role insights:")
                for i, result in enumerate(role_results[:2], 1):
                    title = result.get('title', 'No title')[:60]
                    print(f"  {i}. {title}{'...' if len(result.get('title', '')) > 60 else ''}")
            
            return {
                'success': True,
                'company_results': len(company_results),
                'role_results': len(role_results),
                'company_name': company_name,
                'role_title': role_title
            }
            
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _demo_simulation(self, company_name: str, role_title: str) -> Dict[str, Any]:
        """Simulation mode when no API key available"""
        print(f"\n📝 SIMULATION MODE:")
        print(f"🏢 Would research: {company_name} company overview and industry")
        print(f"💼 Would research: {role_title} market data and requirements")
        print(f"💡 Set TAVILY_API_KEY to see real results!")
        
        return {
            'success': True,
            'simulation': True,
            'company_name': company_name,
            'role_title': role_title
        }

# Entry point
if __name__ == "__main__":
    runner = WorkflowRunner(enable_notifications=True, log_results=True)
    
    # Get interview folder from environment variable
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    interview_folder = os.getenv('INTERVIEW_FOLDER', 'INBOX').strip('"').strip("'")
    if not interview_folder:
        interview_folder = 'INBOX'  # fallback to INBOX if not set
    
    print(f"📁 Using folder from INTERVIEW_FOLDER: {interview_folder}")
    
    # Example 1: Run the email pipeline with EmailClassifierAgent
    print("🚀 Running Email Pipeline...")
    email_result = runner.run_email_pipeline(
        folder_name=interview_folder, 
        max_results=10, 
        user_email='user@example.com'  # Replace with actual user email
    )
    
    # Example 2: Run the research pipeline for unprepped interviews
    print("\n🔬 Running Research Engine Pipeline...")
    research_result = runner.run_research_pipeline(
        max_interviews=5,
        priority_filter='all'
    )
    
    # Example 3: Demo the research engine with live API calls
    print("\n🎯 Running Research Engine Demo...")
    demo_result = runner.demo_research_engine(
        company_name="QuantMind",
        role_title="Data Scientist"
    )
    
    # You can also access execution history
    print(f"\n📊 Execution history: {len(runner.get_execution_history())} total runs")
    for run in runner.get_execution_history():
        run_type = run.get('type', 'unknown_pipeline')
        success_icon = '✅' if run.get('success', False) else '❌'
        processing_time = run.get('processing_time', run.get('execution_time', 0))
        print(f"  - {run_type}: {success_icon} ({processing_time:.1f}s)")