#!/usr/bin/env python3
"""
Interview Prep Workflow - Main Entry Point
==========================================
Modular interview preparation workflow that processes emails one by one through:
1. Email Classification → 2. Entity Extraction & Memory Check → 3. Deep Research Pipeline 
→ 4. Research Quality Reflection → 5. Prep Guide Generation → Individual File Output

This is the MAIN ENTRY POINT that orchestrates all pipeline components.
Run this file to execute the complete interview preparation workflow.

Cache Management Integration:
- Automatic cache status reporting
- Support for --clear-openai-cache flag to force fresh content generation
- Integration with cache_manager.py for comprehensive cache control
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import pipeline modules
from pipelines.email_pipeline import EmailPipeline
from pipelines.deep_research_pipeline import DeepResearchPipeline
from pipelines.prep_guide_pipeline import PrepGuidePipeline
from pipelines.enhanced_prep_guide_pipeline import EnhancedPrepGuidePipeline

# Import shared utilities
from shared.google_oauth.google_email_setup import get_gmail_service
from shared.google_oauth.google_email_functions import get_email_messages, get_email_message_details

# Import cache management
from workflows.cache_manager import get_openai_cache_info, clear_openai_cache


class InterviewPrepWorkflow:
    """
    Main Interview Prep Workflow - Orchestrates all pipeline components
    """
    
    def __init__(self):
        load_dotenv()
        
        # Initialize pipeline components
        self.email_pipeline = EmailPipeline()
        self.research_pipeline = DeepResearchPipeline()
        self.prep_guide_pipeline = PrepGuidePipeline()
        
        print("🚀 INTERVIEW PREP WORKFLOW INITIALIZED")
        print("Pipeline Components Loaded:")
        print("   📧 Email Pipeline (Classification, Entity Extraction, Memory Check)")
        print("   🔬 Deep Research Pipeline (Multi-agent Research with Tavily)")
        print("   📚 Prep Guide Pipeline (Personalized Guide Generation)")
        print("💡 Use 'python workflows/cache_manager.py --status' for cache management")
    
    def run_workflow(self, max_emails: int = 10, folder: str = None) -> Dict[str, Any]:
        """
        Run the complete Interview Prep Workflow
        
        Args:
            max_emails: Maximum number of emails to process
            folder: Gmail folder to process (overrides environment variable)
            
        Returns:
            Comprehensive workflow results
        """
        print(f"\n" + "=" * 80)
        print("🎯 STARTING INTERVIEW PREP WORKFLOW")
        print("=" * 80)
        
        workflow_start_time = datetime.now()
        
        # Get interview folder - prioritize parameter, then environment, then default
        if folder:
            interview_folder = folder
        else:
            interview_folder = os.getenv('INTERVIEW_FOLDER', 'INBOX').strip('"').strip("'")
            if not interview_folder:
                interview_folder = 'INBOX'
        
        print(f"📁 Reading emails from folder: {interview_folder}")
        print(f"📊 Maximum emails to process: {max_emails}")
        
        workflow_result = {
            'success': False,
            'total_emails_fetched': 0,
            'interview_emails_found': 0,
            'prep_guides_generated': 0,
            'emails_already_prepped': 0,
            'research_conducted_count': 0,
            'processing_time': 0,
            'individual_results': [],
            'errors': []
        }
        
        try:
            # Step 1: Fetch emails from Gmail
            print(f"\n📥 STEP 1: Fetching emails from {interview_folder}")
            emails = self._fetch_emails_from_gmail(interview_folder, max_emails)
            
            if not emails:
                workflow_result['errors'].append('No emails found in the specified folder')
                print("❌ No emails found in the specified folder")
                return workflow_result
            
            workflow_result['total_emails_fetched'] = len(emails)
            print(f"✅ Fetched {len(emails)} emails from Gmail")
            
            # Step 2: Process each email individually through pipeline
            print(f"\n🔄 STEP 2: Processing emails individually through pipeline")
            
            for email_index, email in enumerate(emails, 1):
                print(f"\n" + "🌟" * 25 + f" EMAIL {email_index}/{len(emails)} " + "🌟" * 25)
                print(f"📤 From: {email.get('from', 'Unknown')}")
                print(f"📧 Subject: {email.get('subject', 'No subject')[:60]}{'...' if len(email.get('subject', '')) > 60 else ''}")
                print(f"📅 Date: {email.get('date', 'Unknown')}")
                
                email_result = self._process_single_email(email, email_index)
                workflow_result['individual_results'].append(email_result)
                
                # Update workflow statistics
                if email_result.get('is_interview'):
                    workflow_result['interview_emails_found'] += 1
                
                if email_result.get('already_prepped'):
                    workflow_result['emails_already_prepped'] += 1
                
                if email_result.get('research_conducted'):
                    workflow_result['research_conducted_count'] += 1
                
                if email_result.get('prep_guide_generated'):
                    workflow_result['prep_guides_generated'] += 1
            
            workflow_result['success'] = True
            workflow_result['processing_time'] = (datetime.now() - workflow_start_time).total_seconds()
            
            # Step 3: Display final workflow summary
            self._display_final_workflow_summary(workflow_result)
            
            return workflow_result
            
        except Exception as e:
            workflow_result['errors'].append(str(e))
            workflow_result['processing_time'] = (datetime.now() - workflow_start_time).total_seconds()
            print(f"💥 WORKFLOW FAILED: {str(e)}")
            return workflow_result
    
    def _fetch_emails_from_gmail(self, folder_name: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail folder"""
        try:
            service = get_gmail_service()
            raw_emails = get_email_messages(service, folder_name=folder_name, max_results=max_results)
            
            emails = []
            for email_msg in raw_emails:
                email_details = get_email_message_details(service, email_msg['id'])
                emails.append(email_details)
            
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails from Gmail: {str(e)}")
            return []
    
    def _process_single_email(self, email: Dict[str, Any], email_index: int) -> Dict[str, Any]:
        """
        Process single email through all pipeline stages
        
        Args:
            email: Email data dictionary
            email_index: Index of email being processed
            
        Returns:
            Complete processing result for this email
        """
        email_start_time = datetime.now()
        
        result = {
            'email_index': email_index,
            'from': email.get('from', 'Unknown'),
            'subject': email.get('subject', 'No subject'),
            'date': email.get('date', 'Unknown'),
            'is_interview': False,
            'already_prepped': False,
            'research_conducted': False,
            'prep_guide_generated': False,
            'company_keyword': '',
            'output_file': '',
            'processing_time': 0,
            'pipeline_results': {},
            'errors': [],
            'detailed_logs': {}  # Store detailed processing logs
        }
        
        try:
            # PIPELINE STAGE 1: Email Processing (Classification + Entity Extraction + Memory Check)
            print(f"\n🔄 PIPELINE STAGE 1: Email Processing")
            email_pipeline_result = self.email_pipeline.process_email(email, email_index)
            result['pipeline_results']['email_pipeline'] = email_pipeline_result
            result['detailed_logs']['email_pipeline'] = self._extract_email_pipeline_logs(email_pipeline_result)
            
            result['is_interview'] = email_pipeline_result.get('is_interview', False)
            result['already_prepped'] = email_pipeline_result.get('already_prepped', False)
            
            if not result['is_interview']:
                print(f"⏭️  SKIPPING: Non-interview email")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            if result['already_prepped']:
                print(f"⏭️  SKIPPING: Interview already prepped")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            # PIPELINE STAGE 2: Deep Research (Multi-agent Research + Reflection Loops)
            print(f"\n🔄 PIPELINE STAGE 2: Deep Research")
            research_pipeline_result = self.research_pipeline.conduct_deep_research(
                email_pipeline_result.get('entities', {}), 
                email_index
            )
            result['pipeline_results']['research_pipeline'] = research_pipeline_result
            result['detailed_logs']['deep_research'] = self._extract_research_pipeline_logs(research_pipeline_result)
            result['research_conducted'] = research_pipeline_result.get('success', False)
            
            if not result['research_conducted']:
                print(f"❌ Research pipeline failed - skipping prep guide")
                result['errors'].append(f"Research failed: {research_pipeline_result.get('errors', ['Unknown error'])[0]}")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            # PIPELINE STAGE 3: Research Quality Reflection
            print(f"\n🔄 PIPELINE STAGE 3: Research Quality Assessment")
            if not research_pipeline_result.get('sufficient_for_prep_guide', False):
                print(f"❌ Research quality insufficient for prep guide generation")
                result['errors'].append("Research quality insufficient for prep guide")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            print(f"✅ Research quality sufficient - proceeding to prep guide generation")
            
            # Add quality reflection to logs
            result['detailed_logs']['deep_research']['quality_reflection'] = {
                'overall_confidence': research_pipeline_result.get('overall_confidence', 0),
                'quality_rating': research_pipeline_result.get('research_quality', 'Unknown'),
                'sufficient_for_prep_guide': research_pipeline_result.get('sufficient_for_prep_guide', False),
                'reflection_reasoning': f"Research quality assessment passed with {research_pipeline_result.get('overall_confidence', 0):.2f} confidence"
            }
            
            # PIPELINE STAGE 4: Enhanced Prep Guide Generation with Reflection System
            print(f"\n🔄 PIPELINE STAGE 4: Enhanced Prep Guide Generation")
            print("Using enhanced pipeline with reflection loops and comprehensive guidelines...")
            
            # Use enhanced prep guide pipeline with reflection system
            prep_guide_result = self.enhanced_prep_guide_pipeline.generate_enhanced_prep_guide(
                email,
                email_pipeline_result.get('entities', {}),
                research_pipeline_result,
                email_index
            )
            
            # Also generate traditional prep guide for comparison (optional fallback)
            traditional_result = self.prep_guide_pipeline.generate_prep_guide(
                email,
                email_pipeline_result.get('entities', {}),
                research_pipeline_result,
                email_index,
                result['detailed_logs']
            )
            
            result['pipeline_results']['enhanced_prep_guide'] = prep_guide_result
            result['pipeline_results']['traditional_prep_guide'] = traditional_result
            result['detailed_logs']['prep_guide_generation'] = {
                'enhanced': self._extract_enhanced_prep_guide_logs(prep_guide_result),
                'traditional': self._extract_prep_guide_logs(traditional_result)
            }
            
            # Use enhanced result as primary
            result['prep_guide_generated'] = prep_guide_result.get('success', False)
            result['company_keyword'] = prep_guide_result.get('company_keyword', '')
            result['output_file'] = prep_guide_result.get('output_file', '')
            result['quality_scores'] = prep_guide_result.get('quality_scores', {})
            result['reflection_iterations'] = prep_guide_result.get('reflection_iterations', 0)
            
            if not result['prep_guide_generated']:
                result['errors'].append(f"Enhanced prep guide generation failed: {prep_guide_result.get('errors', ['Unknown error'])[0]}")
                # Try fallback to traditional if enhanced fails
                if traditional_result.get('success', False):
                    print("⚠️ Falling back to traditional prep guide generation")
                    result['prep_guide_generated'] = True
                    result['output_file'] = traditional_result.get('output_file', '')
                    result['fallback_used'] = True
            
            result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
            
            # Display email processing summary
            self._display_email_processing_summary(result)
            
            return result
            
        except Exception as e:
            result['errors'].append(str(e))
            result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
            print(f"❌ ERROR processing email {email_index}: {str(e)}")
            return result
    
    def _display_email_processing_summary(self, result: Dict[str, Any]):
        """Display processing summary for individual email"""
        print(f"\n📊 EMAIL {result['email_index']} PROCESSING SUMMARY")
        print("-" * 50)
        print(f"   📧 Subject: {result['subject'][:50]}{'...' if len(result['subject']) > 50 else ''}")
        print(f"   🏢 Company: {result['company_keyword'] if result['company_keyword'] else 'Not identified'}")
        print(f"   🎯 Interview Email: {'✅ YES' if result['is_interview'] else '❌ NO'}")
        print(f"   💾 Already Prepped: {'✅ YES' if result['already_prepped'] else '🆕 NO'}")
        print(f"   🔬 Research Conducted: {'✅ YES' if result['research_conducted'] else '⏭️  SKIPPED'}")
        print(f"   📚 Prep Guide Generated: {'✅ YES' if result['prep_guide_generated'] else '❌ NO'}")
        print(f"   📁 Output File: {result['output_file'] if result['output_file'] else 'None'}")
        print(f"   ⏱️  Processing Time: {result['processing_time']:.2f}s")
        
        if result['errors']:
            print(f"   ❌ Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"      • {error}")
    
    def _display_final_workflow_summary(self, workflow_result: Dict[str, Any]):
        """Display final workflow summary with comprehensive statistics"""
        print(f"\n" + "=" * 80)
        print("🎉 INTERVIEW PREP WORKFLOW COMPLETED")
        print("=" * 80)
        
        # Main statistics
        print(f"📊 WORKFLOW STATISTICS:")
        print(f"   📥 Total Emails Fetched: {workflow_result['total_emails_fetched']}")
        print(f"   🎯 Interview Emails Found: {workflow_result['interview_emails_found']}")
        print(f"   💾 Already Prepped: {workflow_result['emails_already_prepped']}")
        print(f"   🔬 Research Conducted: {workflow_result['research_conducted_count']}")
        print(f"   📚 Prep Guides Generated: {workflow_result['prep_guides_generated']}")
        print(f"   ⏱️  Total Processing Time: {workflow_result['processing_time']:.2f}s")
        
        # Pipeline usage analysis
        print(f"\n📋 PIPELINE USAGE ANALYSIS:")
        total_emails = workflow_result['total_emails_fetched']
        interview_emails = workflow_result['interview_emails_found']
        
        print(f"   📧 Email Pipeline: ✅ USED ({total_emails} emails processed)")
        print(f"   🔬 Deep Research Pipeline: {'✅ USED' if workflow_result['research_conducted_count'] > 0 else '❌ NOT USED'} ({workflow_result['research_conducted_count']}/{interview_emails} interviews)")
        print(f"   📚 Prep Guide Pipeline: {'✅ USED' if workflow_result['prep_guides_generated'] > 0 else '❌ NOT USED'} ({workflow_result['prep_guides_generated']}/{interview_emails} interviews)")
        
        # Success rate calculation
        if interview_emails > 0:
            success_rate = (workflow_result['prep_guides_generated'] / interview_emails) * 100
            print(f"\n📈 SUCCESS RATE: {success_rate:.1f}% ({workflow_result['prep_guides_generated']}/{interview_emails})")
        else:
            print(f"\n📈 SUCCESS RATE: N/A (No interview emails found)")
        
        # Individual file outputs
        if workflow_result['prep_guides_generated'] > 0:
            print(f"\n📁 INDIVIDUAL OUTPUT FILES:")
            print(f"   💾 Saved in: outputs/fullworkflow/")
            
            for result in workflow_result['individual_results']:
                if result.get('prep_guide_generated') and result.get('output_file'):
                    company = result.get('company_keyword', 'Unknown')
                    filename = result.get('output_file', 'Unknown')
                    print(f"   ✅ {company}: {filename}")
        
        # Error summary
        total_errors = sum(len(result.get('errors', [])) for result in workflow_result['individual_results'])
        if total_errors > 0:
            print(f"\n⚠️  ERROR SUMMARY:")
            print(f"   📊 Total Errors: {total_errors}")
            for i, result in enumerate(workflow_result['individual_results'], 1):
                if result.get('errors'):
                    print(f"   Email {i}: {result['errors'][0]}")  # Show first error
        else:
            print(f"\n✅ NO PROCESSING ERRORS - ALL PIPELINES COMPLETED SUCCESSFULLY")
        
        print("=" * 80)
        
        # Final status
        if workflow_result['success']:
            print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        else:
            print("❌ WORKFLOW COMPLETED WITH ERRORS")
    
    def _extract_email_pipeline_logs(self, email_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed logs from email pipeline processing"""
        logs = {}
        
        # Classification details
        if 'classification_result' in email_result:
            classification = email_result['classification_result']
            logs['classification'] = {
                'result': classification.get('classification', 'Unknown'),
                'confidence': classification.get('confidence', 0),
                'reasoning': classification.get('reasoning', '')
            }
        
        # Entity extraction details
        if 'entities' in email_result:
            logs['entity_extraction'] = {
                'success': email_result.get('success', False),
                'entities': email_result['entities']
            }
        
        # Memory check details
        if 'memory_result' in email_result:
            memory_result = email_result['memory_result']
            logs['memory_check'] = {
                'status': memory_result.get('status', 'Unknown'),
                'already_prepped': memory_result.get('already_prepped', False),
                'match_details': memory_result.get('match_details')
            }
        
        return logs
    
    def _extract_research_pipeline_logs(self, research_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed logs from deep research pipeline processing"""
        logs = {}
        
        # Overall metrics
        logs['metrics'] = {
            'sources_discovered': research_result.get('sources_processed', 0),
            'sources_validated': len(research_result.get('validated_sources', [])),
            'citations_generated': len(research_result.get('citations_database', {})),
            'linkedin_profiles_found': research_result.get('linkedin_profiles_found', 0),
            'processing_time': research_result.get('processing_time', 0)
        }
        
        # Company analysis details
        research_data = research_result.get('research_data', {})
        if 'company_analysis' in research_data:
            company_data = research_data['company_analysis']
            validation_log = company_data.get('validation_log', [])
            logs['company_analysis'] = {
                'confidence_score': company_data.get('confidence_score', 0),
                'sources_validated': len(company_data.get('validated_sources', [])),
                'validation_log': validation_log
            }
        
        # Role analysis details
        if 'role_analysis' in research_result:
            role_data = research_result['role_analysis']
            logs['role_analysis'] = {
                'confidence_score': role_data.get('confidence_score', 0),
                'sources_validated': len(role_data.get('validated_sources', []))
            }
        
        # Interviewer analysis details
        if 'interviewer_analysis' in research_data:
            interviewer_data = research_data['interviewer_analysis']
            validation_log = interviewer_data.get('validation_log', [])
            logs['interviewer_analysis'] = {
                'confidence_score': interviewer_data.get('confidence_score', 0),
                'linkedin_profiles_found': interviewer_data.get('linkedin_profiles_found', 0),
                'validation_log': validation_log,
                'extracted_names': interviewer_data.get('extracted_names', []),
                'search_suggestions': interviewer_data.get('search_suggestions', []),
                'search_queries': [
                    f'"{interviewer_data.get("interviewer_name", "Unknown")}" linkedin profile',
                    f'"{interviewer_data.get("interviewer_name", "Unknown")}" {research_result.get("company", "")} linkedin',
                    f'"{interviewer_data.get("interviewer_name", "Unknown")}" site:linkedin.com/in'
                ] if interviewer_data else []
            }
        
        # Quality reflection
        logs['quality_reflection'] = {
            'overall_confidence': research_result.get('overall_confidence', 0),
            'quality_rating': research_result.get('research_quality', 'Unknown'),
            'sufficient_for_prep_guide': research_result.get('sufficient_for_prep_guide', False),
            'reflection_reasoning': research_result.get('reflection_reasoning', '')
        }
        
        return logs
    
    def _extract_prep_guide_logs(self, prep_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract logs from prep guide generation"""
        logs = {
            'success': prep_result.get('success', False),
            'guide_length': len(str(prep_result.get('prep_guide_content', ''))),
            'citations_used': prep_result.get('citations_used', 0) if isinstance(prep_result.get('citations_used'), int) else 0,
            'generation_time': prep_result.get('generation_time', 0)
        }
        return logs
    
    def _extract_enhanced_prep_guide_logs(self, prep_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract logs from enhanced prep guide generation with reflection system"""
        logs = {
            'success': prep_result.get('success', False),
            'guide_length': len(str(prep_result.get('prep_guide_content', ''))),
            'citations_count': prep_result.get('citations_count', 0),
            'reflection_iterations': prep_result.get('reflection_iterations', 0),
            'sections_completed': len(prep_result.get('sections_completed', [])),
            'processing_time': prep_result.get('processing_time', 0),
            'quality_scores': prep_result.get('quality_scores', {}),
            'output_file': prep_result.get('output_file', ''),
            'errors': prep_result.get('errors', [])
        }
        return logs


# Main execution with enhanced cache management
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Interview Prep Workflow - Enhanced with cache management')
    parser.add_argument('--clear-openai-cache', action='store_true', 
                       help='Clear OpenAI cache before running to force fresh AI content generation')
    parser.add_argument('--max-emails', type=int, default=10, 
                       help='Maximum number of emails to process (default: 10)')
    parser.add_argument('--folder', type=str, default='demo', 
                       help='Gmail folder to process (default: demo)')
    
    args = parser.parse_args()
    
    print("🚀 Interview Prep Workflow - Main Entry Point")
    print("=" * 60)
    
    # Cache management integration
    if args.clear_openai_cache:
        print("🧹 CLEARING OPENAI CACHE - Forcing fresh AI content generation...")
        
        # Set environment variable to disable caching for this run
        os.environ['DISABLE_OPENAI_CACHE'] = 'true'
        
        try:
            cache_result = clear_openai_cache()
            if cache_result['success']:
                print(f"✅ {cache_result['message']}")
                print(f"📊 Cache size freed: {cache_result.get('size_freed_mb', 0):.2f} MB")
                print(f"🚫 OpenAI caching disabled for this workflow run")
            else:
                print(f"⚠️ {cache_result['message']}")
        except Exception as e:
            print(f"❌ Cache clearing error: {str(e)}")
        print("-" * 60)
    else:
        # Ensure caching is enabled (default behavior)
        os.environ.pop('DISABLE_OPENAI_CACHE', None)
    
    # Display current cache status
    try:
        cache_info = get_openai_cache_info()
        if cache_info['cache_exists']:
            print(f"💾 OpenAI Cache Status: {cache_info['message']}")
            if not args.clear_openai_cache and cache_info.get('cached_responses', 0) > 0:
                print("💡 Note: Using cached responses. Use --clear-openai-cache for fresh content.")
        else:
            print(f"💾 OpenAI Cache Status: No cache found - all responses will be fresh")
        print("-" * 60)
    except Exception as e:
        print(f"⚠️ Cache status check error: {str(e)}")
    
    try:
        workflow = InterviewPrepWorkflow()
        results = workflow.run_workflow(max_emails=args.max_emails, folder=args.folder)
        
        if results['success']:
            print(f"\n🎊 WORKFLOW EXECUTION SUCCESSFUL!")
            print(f"📊 Generated {results['prep_guides_generated']} prep guides")
            print(f"💡 Use 'python workflows/cache_manager.py --status' for detailed cache statistics")
            
            # Show cache usage after execution
            try:
                post_cache_info = get_openai_cache_info()
                if post_cache_info['cache_exists']:
                    print(f"💾 Final Cache Status: {post_cache_info['message']}")
            except:
                pass
        else:
            print(f"\n💥 WORKFLOW EXECUTION FAILED!")
            print(f"❌ Errors: {len(results['errors'])}")
            print(f"💡 Use 'python workflows/cache_manager.py --clear-all' if cache issues suspected")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Workflow interrupted by user")
        print(f"💡 Use 'python workflows/cache_manager.py --status' to check cache status")
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        print(f"💡 Use 'python workflows/cache_manager.py --clear-all' if cache corruption suspected")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point for the interview prep workflow"""
    parser = argparse.ArgumentParser(description='Interview Preparation Workflow')
    parser.add_argument('--max-emails', type=int, default=10, 
                       help='Maximum number of emails to process (default: 10)')
    parser.add_argument('--folder', type=str, 
                       help='Gmail folder to process (overrides env variable)')
    parser.add_argument('--clear-openai-cache', action='store_true',
                       help='Clear OpenAI cache before running')
    
    args = parser.parse_args()
    
    # Clear cache if requested
    if args.clear_openai_cache:
        print("🧹 Clearing OpenAI cache...")
        clear_openai_cache()
    
    # Show cache status
    cache_info = get_openai_cache_info()
    print(f"📊 Cache Status: {cache_info['files']} files, {cache_info['size_mb']} MB")
    
    # Run workflow
    workflow = InterviewPrepWorkflow()
    results = workflow.run_workflow(max_emails=args.max_emails, folder=args.folder)
    
    # Print final summary
    print(f"\n" + "=" * 80)
    print("📊 WORKFLOW SUMMARY")
    print("=" * 80)
    print(f"✅ Processed: {results.get('processed_count', 0)} emails")
    print(f"📝 Generated: {results.get('guide_count', 0)} prep guides")
    if results.get('errors'):
        print(f"❌ Errors: {len(results['errors'])}")


if __name__ == "__main__":
    main()
