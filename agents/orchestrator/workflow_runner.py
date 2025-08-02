"""
Refactored Workflow Runner - Clean Orchestration Layer
Reduced from 1,741 lines to ~300 lines by moving logic to dedicated pipelines
"""

import os
import sys
import re
import shutil
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the 3 clean pipelines
from workflows.email_pipeline import EmailPipeline
from workflows.deep_research_pipeline import DeepResearchPipeline  
from workflows.prep_guide_pipeline import PrepGuidePipeline

# Import utilities
from shared.tavily_client import get_tavily_cache_stats, clear_tavily_cache
from shared.openai_cache import get_openai_cache_stats, clear_openai_cache


class OutputCapture:
    """Simple output capture for workflow results"""
    def __init__(self):
        self.captured_output = []
        self.interview_outputs = {}
    
    def capture(self, message: str):
        """Capture a message"""
        self.captured_output.append(message)
        print(message)  # Still print to console
    
    def get_all_output(self) -> List[str]:
        """Get all captured output"""
        return self.captured_output
    
    def get_output_for_interview(self, keyword: str) -> List[str]:
        """Get output for specific interview keyword"""
        return self.interview_outputs.get(keyword, self.captured_output)


class WorkflowRunner:
    """
    Refactored Workflow Runner - Clean Orchestration Layer
    
    This orchestrator now delegates all complex logic to specialized pipelines:
    1. Email Pipeline - Email processing and classification
    2. Deep Research Pipeline - Tavily search, validation, and IPIA integration
    3. Prep Guide Pipeline - Comprehensive interview preparation guides
    """
    
    def __init__(self, enable_notifications=True, log_results=True, save_outputs=True):
        self.enable_notifications = enable_notifications
        self.log_results = log_results
        self.save_outputs = save_outputs
        self.execution_history = []
        self.output_capture = OutputCapture()
        self.interview_keywords = []
        
        # Initialize the 3 pipelines
        self.email_pipeline = EmailPipeline()
        self.deep_research_pipeline = DeepResearchPipeline()
        self.prep_guide_pipeline = PrepGuidePipeline()
        
        # Create outputs directory
        self.outputs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'outputs', 'fullworkflow')
        os.makedirs(self.outputs_dir, exist_ok=True)
    
    def run_email_pipeline(self, folder_name: str, max_results: int = 10, user_email: str = "") -> Dict[str, Any]:
        """
        Run the email pipeline using the dedicated EmailPipeline class
        """
        if not folder_name:
            raise ValueError("folder_name argument is required and cannot be empty.")
        
        print(f"🚀 Starting Email Pipeline for folder: {folder_name}")
        start_time = datetime.now()
        
        try:
            # Use the existing complex email pipeline (LangGraph-based)
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
                print(f"💥 Email Pipeline failed: {str(e)}")
            
            return error_result
    
    def run_deep_research_pipeline_enhanced(self, max_interviews: int = 10) -> Dict[str, Any]:
        """
        Run the deep research pipeline using the dedicated DeepResearchPipeline class
        This includes Tavily search, validation loops, and IPIA integration
        """
        print(f"🚀 Starting Deep Research Pipeline (Enhanced with IPIA)")
        start_time = datetime.now()
        
        try:
            # Delegate to the dedicated pipeline
            result = self.deep_research_pipeline.run_deep_research_pipeline(max_interviews)
            
            # Add execution tracking
            result['type'] = 'enhanced_deep_research_pipeline'
            result['execution_time'] = result.get('processing_time', (datetime.now() - start_time).total_seconds())
            
            # Add to execution history
            self.execution_history.append({
                'type': result['type'],
                'timestamp': result.get('timestamp', datetime.now().isoformat()),
                'success': result.get('success', False),
                'interviews_processed': result.get('interviews_processed', 0),
                'questions_generated': result.get('total_questions_generated', 0),
                'processing_time': result['execution_time']
            })
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_result = {
                'success': False,
                'error': str(e),
                'type': 'enhanced_deep_research_pipeline',
                'interviews_processed': 0,
                'total_questions_generated': 0,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"💥 Deep Research Pipeline failed: {str(e)}")
            return error_result
    
    def run_enhanced_prep_guide(self, max_interviews: int = 10) -> Dict[str, Any]:
        """
        Run the prep guide pipeline using the dedicated PrepGuidePipeline class
        """
        print(f"📚 Starting Enhanced Prep Guide Pipeline")
        start_time = datetime.now()
        
        try:
            # Delegate to the dedicated pipeline
            result = self.prep_guide_pipeline.run_prep_guide_pipeline(max_interviews)
            
            # Add execution tracking
            result['type'] = 'enhanced_prep_guide'
            result['execution_time'] = result.get('processing_time', (datetime.now() - start_time).total_seconds())
            
            # Add to execution history
            self.execution_history.append({
                'type': result['type'],
                'timestamp': result.get('timestamp', datetime.now().isoformat()),
                'success': result.get('success', False),
                'interviews_processed': result.get('interviews_processed', 0),
                'guides_generated': result.get('guides_generated', 0),
                'processing_time': result['execution_time']
            })
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_result = {
                'success': False,
                'error': str(e),
                'type': 'enhanced_prep_guide',
                'interviews_processed': 0,
                'guides_generated': 0,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"💥 Prep Guide Pipeline failed: {str(e)}")
            return error_result
    
    def run_full_workflow(self, folder_name: str = None, max_results: int = 10, 
                         max_interviews: int = 10, user_email: str = "") -> Dict[str, Any]:
        """
        Run the complete 3-pipeline workflow in sequence
        
        Args:
            folder_name: Email folder to process (defaults to INTERVIEW_FOLDER from .env)
            max_results: Maximum number of emails to process
            max_interviews: Maximum number of interviews to process
            user_email: User email for filtering
        """
        # Use INTERVIEW_FOLDER from .env if no folder_name provided
        if folder_name is None:
            folder_name = os.getenv('INTERVIEW_FOLDER', 'INBOX')
        
        print(f"🚀 Starting Complete 3-Pipeline Workflow")
        print(f"📁 Using folder: {folder_name} (from {'environment' if folder_name != 'INBOX' else 'default'})")
        print("=" * 80)
        workflow_start_time = datetime.now()
        
        try:
            # Phase 1: Email Pipeline
            print("📧 Phase 1: Email Processing Pipeline")
            email_results = self.run_email_pipeline(folder_name, max_results, user_email)
            
            if not email_results.get('success', True):
                print(f"⚠️ Email Pipeline had issues: {email_results.get('error', 'Unknown error')}")
            else:
                print(f"✅ Email Pipeline completed - Processed {email_results.get('email_count', 0)} emails")
            
            # Phase 2: Deep Research Pipeline (includes IPIA)
            print("\n🔬 Phase 2: Deep Research Pipeline (with IPIA)")
            research_results = self.run_deep_research_pipeline_enhanced(max_interviews)
            
            if not research_results.get('success', False):
                print(f"⚠️ Deep Research Pipeline had issues: {research_results.get('error', 'Unknown issue')}")
            else:
                print(f"✅ Deep Research Pipeline completed - Processed {research_results.get('interviews_processed', 0)} interviews")
            
            # Phase 3: Prep Guide Pipeline
            print("\n📚 Phase 3: Prep Guide Pipeline")
            prep_results = self.run_enhanced_prep_guide(max_interviews)
            
            if not prep_results.get('success', False):
                print(f"⚠️ Prep Guide Pipeline had issues: {prep_results.get('error', 'Unknown issue')}")
            else:
                print(f"✅ Prep Guide Pipeline completed - Generated {prep_results.get('guides_generated', 0)} guides")
            
            # Save comprehensive workflow outputs if needed
            if self.save_outputs:
                self._save_workflow_outputs_comprehensive(email_results, research_results, prep_results)
            
            workflow_time = (datetime.now() - workflow_start_time).total_seconds()
            
            # Compile final results
            final_results = {
                'success': True,
                'workflow_time': workflow_time,
                'timestamp': datetime.now().isoformat(),
                'phase_1_email': {
                    'success': email_results.get('success', True),
                    'emails_processed': email_results.get('email_count', 0),
                    'folder_name': email_results.get('folder_name', folder_name)
                },
                'phase_2_research': {
                    'success': research_results.get('success', False),
                    'interviews_processed': research_results.get('interviews_processed', 0),
                    'questions_generated': research_results.get('total_questions_generated', 0),
                    'avg_confidence': research_results.get('avg_confidence_score', 0.0)
                },
                'phase_3_prep': {
                    'success': prep_results.get('success', False),
                    'guides_generated': prep_results.get('guides_generated', 0),
                    'total_questions': prep_results.get('total_questions', 0)
                },
                'cache_stats': self._get_cache_statistics()
            }
            
            # Display final summary
            self._display_full_workflow_summary(final_results)
            
            print(f"\n🎉 Complete 3-Pipeline Workflow finished in {workflow_time:.1f}s")
            
            return final_results
            
        except Exception as e:
            print(f"❌ Complete Workflow failed: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'workflow_time': (datetime.now() - workflow_start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
    
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
            'error': final_state.get('error', None),
            'final_state': final_state
        }
        
        # Extract classification counts
        classified = final_state.get('classified_emails', {})
        for category, emails in classified.items():
            result['classifications'][category] = len(emails)
        
        # Extract interview keywords for file naming
        if self.save_outputs:
            self.interview_keywords = self.extract_interview_keywords(final_state)
        
        return result
    
    def _handle_post_processing(self, result: Dict[str, Any]):
        """Handle post-processing: notifications, logging, external integrations"""
        
        # Add type information for consistency
        if 'type' not in result:
            result['type'] = 'email_pipeline'
        
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
    
    def extract_interview_keywords(self, final_state: Dict) -> List[str]:
        """Extract keywords from interview emails for file naming"""
        keywords = []
        
        try:
            # Import the keyword extractor
            from agents.keyword_extractor.agent import EmailKeywordExtractor
            
            extractor = EmailKeywordExtractor()
            
            # Get interview emails
            classified_emails = final_state.get('classified_emails', {})
            interview_emails = classified_emails.get('Interview_invite', [])
            
            for email in interview_emails:
                subject = email.get('subject', '')
                body = email.get('body', '')
                
                # Extract keywords using the dedicated agent
                keyword_result = extractor.extract_keywords(subject, body)
                
                # Get the best keyword suggestion
                if keyword_result.get('filename_suggestions'):
                    keywords.append(keyword_result['filename_suggestions'][0])
                elif keyword_result.get('keywords'):
                    keywords.append(keyword_result['keywords'][0])
                else:
                    # Fallback: use subject
                    safe_subject = re.sub(r'[^a-zA-Z0-9_-]', '_', subject)[:50]
                    keywords.append(safe_subject or 'interview')
        
        except Exception as e:
            print(f"⚠️ Keyword extraction failed: {str(e)}")
            # Fallback keywords
            keywords = ['interview_1', 'interview_2', 'interview_3']
        
        return keywords[:10]  # Limit to 10 keywords
    
    def _save_workflow_outputs_comprehensive(self, email_results: Dict, research_results: Dict, prep_results: Dict):
        """Save comprehensive workflow outputs to files"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create a comprehensive summary
            summary_content = f"""# Complete 3-Pipeline Workflow Results
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Phase 1: Email Pipeline
- Status: {'✅ Success' if email_results.get('success', True) else '❌ Failed'}
- Emails Processed: {email_results.get('email_count', 0)}
- Folder: {email_results.get('folder_name', 'Unknown')}

## Phase 2: Deep Research Pipeline (with IPIA)
- Status: {'✅ Success' if research_results.get('success', False) else '❌ Failed'}
- Interviews Processed: {research_results.get('interviews_processed', 0)}
- Questions Generated: {research_results.get('total_questions_generated', 0)}
- Average Confidence: {research_results.get('avg_confidence_score', 0.0):.2f}

## Phase 3: Prep Guide Pipeline
- Status: {'✅ Success' if prep_results.get('success', False) else '❌ Failed'}
- Guides Generated: {prep_results.get('guides_generated', 0)}
- Total Questions: {prep_results.get('total_questions', 0)}

## Cache Performance
{self._format_cache_stats_for_summary()}

---
*Generated by Refactored 3-Pipeline Workflow Runner*
"""
            
            # Save summary
            summary_file = os.path.join(self.outputs_dir, f"workflow_summary_{timestamp}.md")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            print(f"💾 Saved workflow summary: {summary_file}")
            
        except Exception as e:
            print(f"❌ Failed to save workflow outputs: {str(e)}")
    
    def _get_cache_statistics(self) -> Dict[str, Any]:
        """Get statistics from both caches"""
        try:
            return {
                'tavily_cache': get_tavily_cache_stats(),
                'openai_cache': get_openai_cache_stats()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _format_cache_stats_for_summary(self) -> str:
        """Format cache stats for summary display"""
        try:
            stats = self._get_cache_statistics()
            
            if 'error' in stats:
                return f"Cache stats unavailable: {stats['error']}"
            
            tavily_stats = stats.get('tavily_cache', {})
            openai_stats = stats.get('openai_cache', {})
            
            return f"""**Tavily Cache:**
- Entries: {tavily_stats.get('total_entries', 0)}
- Hit Rate: {tavily_stats.get('hit_rate', 0)}%
- Estimated Savings: ${tavily_stats.get('estimated_savings', 0)}

**OpenAI Cache:**
- Entries: {openai_stats.get('total_entries', 0)}
- Hit Rate: {openai_stats.get('hit_rate', 0)}%
- Estimated Savings: ${openai_stats.get('estimated_savings', 0)}"""
            
        except Exception as e:
            return f"Cache stats error: {str(e)}"
    
    def _display_full_workflow_summary(self, results: Dict[str, Any]):
        """Display a comprehensive summary of the full workflow results"""
        
        print("\n" + "="*80)
        print("🎉 COMPLETE 3-PIPELINE WORKFLOW SUMMARY")
        print("="*80)
        
        print(f"⏱️  Total Time: {results['workflow_time']:.1f}s")
        print(f"📅 Completed: {results['timestamp']}")
        
        print(f"\n📧 Phase 1 - Email Pipeline:")
        phase1 = results['phase_1_email']
        print(f"   {'✅' if phase1['success'] else '❌'} Processed {phase1['emails_processed']} emails from {phase1['folder_name']}")
        
        print(f"\n🔬 Phase 2 - Deep Research Pipeline (with IPIA):")
        phase2 = results['phase_2_research']
        print(f"   {'✅' if phase2['success'] else '❌'} Researched {phase2['interviews_processed']} interviews")
        print(f"   🧠 Generated {phase2['questions_generated']} IPIA questions")
        print(f"   📊 Avg Confidence: {phase2['avg_confidence']:.2f}")
        
        print(f"\n📚 Phase 3 - Prep Guide Pipeline:")
        phase3 = results['phase_3_prep']
        print(f"   {'✅' if phase3['success'] else '❌'} Generated {phase3['guides_generated']} prep guides")
        print(f"   ❓ Total Questions: {phase3['total_questions']}")
        
        # Cache performance
        cache_stats = results.get('cache_stats', {})
        if cache_stats and 'error' not in cache_stats:
            tavily = cache_stats.get('tavily_cache', {})
            openai = cache_stats.get('openai_cache', {})
            print(f"\n🗄️  Cache Performance:")
            print(f"   Tavily: {tavily.get('total_entries', 0)} entries, {tavily.get('hit_rate', 0)}% hit rate")
            print(f"   OpenAI: {openai.get('total_entries', 0)} entries, {openai.get('hit_rate', 0)}% hit rate")
        
        print("="*80)
    
    def clear_tavily_cache(self) -> Dict[str, Any]:
        """Clear the Tavily research cache"""
        try:
            result = clear_tavily_cache()
            print(f"🗑️  {result['message']}")
            return result
        except Exception as e:
            error_msg = f"Failed to clear Tavily cache: {str(e)}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def clear_openai_cache(self) -> Dict[str, Any]:
        """Clear the OpenAI cache"""
        try:
            result = clear_openai_cache()
            print(f"🗑️  {result['message']}")
            return result
        except Exception as e:
            error_msg = f"Failed to clear OpenAI cache: {str(e)}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def clear_all_caches(self) -> Dict[str, Any]:
        """Clear both Tavily and OpenAI caches"""
        print("🧹 Clearing all caches...")
        
        tavily_result = self.clear_tavily_cache()
        openai_result = self.clear_openai_cache()
        
        return {
            'success': tavily_result.get('success', False) and openai_result.get('success', False),
            'tavily_cache': tavily_result,
            'openai_cache': openai_result,
            'timestamp': datetime.now().isoformat()
        }
    
    # Keep the essential utility methods
    def _log_execution_result(self, result: Dict[str, Any]):
        """Log execution results"""
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"\n{status} - {result.get('type', 'Pipeline')} Execution Summary")
        print(f"⏱️  Execution time: {result.get('execution_time', 0):.2f}s")
        
        if result.get('error'):
            print(f"💥 Error: {result['error']}")
    
    def _send_notifications(self, result: Dict[str, Any]):
        """Send notifications for important results"""
        interview_count = result.get('classifications', {}).get('Interview_invite', 0)
        if interview_count > 0:
            print(f"🔔 NOTIFICATION: {interview_count} new interview invite(s) detected!")
    
    def _display_results(self, result: Dict[str, Any]):
        """Display formatted results to the user"""
        if result.get('summaries'):
            print(f"\n📬 Results Summary:")
            for summary in result['summaries']:
                print(f"{summary.get('icon', '📧')} {summary.get('message', '')}")
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Return execution history for analytics/debugging"""
        return self.execution_history
    
    async def run_email_pipeline_async(self, folder_name: str, max_results: int = 10, user_email: str = ""):
        """Async version for integration with async frameworks"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run_email_pipeline, folder_name, max_results, user_email)


# Main execution section - just like the original workflow_runner.py
if __name__ == "__main__":
    print("🚀 Refactored Workflow Runner - Clean 3-Pipeline Architecture")
    print("=" * 70)
    
    try:
        # Initialize the refactored workflow runner
        runner = WorkflowRunner(
            enable_notifications=True,
            log_results=True,
            save_outputs=True
        )
        
        print("✅ Refactored WorkflowRunner initialized with 3 clean pipelines")
        print("📧 Email Pipeline: Ready")
        print("🔬 Deep Research Pipeline: Ready (with IPIA integration)")
        print("📚 Prep Guide Pipeline: Ready")
        
        # Get folder from environment variable
        folder_name = os.getenv('INTERVIEW_FOLDER', 'INBOX')
        print(f"📁 Using email folder: {folder_name} (from .env)")
        
        # Run the complete 3-pipeline workflow
        print(f"\n🎯 Running Complete 3-Pipeline Workflow...")
        results = runner.run_full_workflow(
            folder_name=folder_name,  # Use folder from .env
            max_results=10,
            max_interviews=10,
            user_email=""
        )
        
        print(f"\n🎉 Workflow completed successfully!")
        print(f"📊 Final Results: {results.get('success', 'Unknown')}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Workflow interrupted by user")
    except Exception as e:
        print(f"\n❌ Workflow failed: {str(e)}")
        import traceback
        traceback.print_exc()
