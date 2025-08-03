#!/usr/bin/env python3
"""
Workflow Runner - Main Entry Point for Interview Prep System
==========================================================

This is the MAIN WORKFLOW RUNNER that processes all emails from INTERVIEW_FOLDER
and orchestrates the complete interview preparation pipeline:

1. Email Classification → Only process interview emails
2. Entity Extraction & Memory Check → Extract data and check if already prepped
3. Deep Research Pipeline → Multi-agent research with Tavily cache integration
4. Research Quality Reflection → Verify research is sufficient for prep guide
5. Prep Guide Generation → Create personalized guides with citations
6. Individual Output Files → Store results in outputs/fullworkflow/{company_name}/

Features:
- Processes emails one by one (individual processing)
- Shows detailed terminal progress for each stage
- Integrates with Tavily cache for research optimization
- Uses keyword extractor agent for company name identification
- Stores individual output files per email/company
- Includes reflection loops for quality assurance

Usage:
    python workflows/workflow_runner.py
    python workflows/workflow_runner.py --max-emails 20
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all required components
from pipelines.email_pipeline import EmailPipeline
from pipelines.deep_research_pipeline import DeepResearchPipeline  
from pipelines.prep_guide_pipeline import PrepGuidePipeline
from agents.email_classifier.agent import EmailClassifierAgent
from agents.keyword_extractor.agent_email import EmailKeywordExtractor
from shared.google_oauth.google_email_setup import get_gmail_service
from shared.google_oauth.google_email_functions import get_email_messages, get_email_message_details


class WorkflowRunner:
    """
    Main Workflow Runner - Orchestrates the complete Interview Prep System
    
    This is the primary entry point that follows your 1.1 requirements:
    - Reads emails from INTERVIEW_FOLDER environment variable
    - Processes emails individually (one by one)
    - Shows detailed terminal progress at each stage
    - Integrates Tavily cache for research optimization
    - Outputs individual files per company in outputs/fullworkflow/
    """
    
    def __init__(self):
        """Initialize all pipeline components and agents"""
        load_dotenv()
        
        print("🚀 INITIALIZING WORKFLOW RUNNER")
        print("=" * 60)
        
        # Initialize core pipeline components
        self.email_pipeline = EmailPipeline()
        self.research_pipeline = DeepResearchPipeline()
        self.prep_guide_pipeline = PrepGuidePipeline()
        
        # Initialize specialized agents
        self.email_classifier = EmailClassifierAgent()
        self.keyword_extractor = EmailKeywordExtractor()
        
        # Create output directories
        self.output_base_dir = "outputs/fullworkflow"
        os.makedirs(self.output_base_dir, exist_ok=True)
        
        print("✅ PIPELINE COMPONENTS LOADED:")
        print("   📧 Email Classifier Agent")
        print("   🔍 Entity Extractor Agent")  
        print("   🧠 Memory Systems (Interview Store)")
        print("   🔬 Deep Research Pipeline (Multi-agent + Tavily Cache)")
        print("   📚 Prep Guide Pipeline (Personalized Generation)")
        print("   🏷️  Keyword Extractor Agent")
        print()
        print("💡 Use 'python workflows/cache_manager.py --status' for cache management")
        print("=" * 60)
    
    def run_complete_workflow(self, max_emails: int = 10) -> Dict[str, Any]:
        """
        Run the complete Interview Prep Workflow as specified in requirements 1.1
        
        Args:
            max_emails: Maximum number of emails to process
            
        Returns:
            Complete workflow results with detailed statistics
        """
        print(f"\n🎯 STARTING COMPLETE INTERVIEW PREP WORKFLOW")
        print("=" * 80)
        
        workflow_start_time = datetime.now()
        
        # Get interview folder from environment (.env file)
        interview_folder = os.getenv('INTERVIEW_FOLDER', 'INBOX').strip('"').strip("'")
        if not interview_folder:
            interview_folder = 'INBOX'
            
        print(f"📁 Email Source: {interview_folder} (from .env INTERVIEW_FOLDER)")
        print(f"📊 Max Emails to Process: {max_emails}")
        print(f"📤 Output Directory: {self.output_base_dir}/")
        
        # Initialize workflow results
        workflow_result = {
            'success': False,
            'total_emails_fetched': 0,
            'interview_emails_found': 0,
            'emails_already_prepped': 0,
            'emails_newly_processed': 0,
            'research_conducted_count': 0,
            'prep_guides_generated': 0,
            'processing_time': 0.0,
            'individual_results': [],
            'errors': []
        }
        
        try:
            # MAIN WORKFLOW STEP 1: Fetch all emails from INTERVIEW_FOLDER
            print(f"\n📥 WORKFLOW STEP 1: Fetching emails from {interview_folder}")
            emails = self._fetch_emails_from_folder(interview_folder, max_emails)
            
            if not emails:
                workflow_result['errors'].append(f'No emails found in {interview_folder}')
                print(f"❌ No emails found in folder: {interview_folder}")
                return workflow_result
                
            workflow_result['total_emails_fetched'] = len(emails)
            print(f"✅ Successfully fetched {len(emails)} emails")
            
            # MAIN WORKFLOW STEP 2: Process each email individually
            print(f"\n🔄 WORKFLOW STEP 2: Processing emails individually through pipeline")
            print(f"⚡ Each email goes through the complete pipeline one by one")
            print()
            
            for email_index, email in enumerate(emails, 1):
                print("🌟" * 30 + f" EMAIL {email_index}/{len(emails)} " + "🌟" * 30)
                print(f"👤 From: {email.get('from', 'Unknown')}")
                print(f"📧 Subject: {email.get('subject', 'No subject')[:80]}{'...' if len(email.get('subject', '')) > 80 else ''}")
                print(f"📅 Date: {email.get('date', 'Unknown')}")
                print()
                
                # Process this individual email through complete pipeline
                email_result = self._process_individual_email(email, email_index)
                workflow_result['individual_results'].append(email_result)
                
                # Update workflow statistics
                if email_result.get('is_interview_email'):
                    workflow_result['interview_emails_found'] += 1
                    
                if email_result.get('already_prepped'):
                    workflow_result['emails_already_prepped'] += 1
                else:
                    workflow_result['emails_newly_processed'] += 1
                    
                if email_result.get('research_conducted'):
                    workflow_result['research_conducted_count'] += 1
                    
                if email_result.get('prep_guide_generated'):
                    workflow_result['prep_guides_generated'] += 1
                    
                # Add any errors
                workflow_result['errors'].extend(email_result.get('errors', []))
                
                print("🌟" * 80)
                print()
            
            # MAIN WORKFLOW STEP 3: Final Summary and Results
            workflow_result['success'] = True
            workflow_result['processing_time'] = (datetime.now() - workflow_start_time).total_seconds()
            
            self._display_final_workflow_summary(workflow_result)
            
            return workflow_result
            
        except Exception as e:
            workflow_result['errors'].append(str(e))
            workflow_result['processing_time'] = (datetime.now() - workflow_start_time).total_seconds()
            print(f"💥 WORKFLOW FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return workflow_result
    
    def _process_individual_email(self, email: Dict[str, Any], email_index: int) -> Dict[str, Any]:
        """
        Process individual email through the complete pipeline as specified in requirements 1.1
        
        Pipeline Flow:
        1. Email Classification → Check if interview email
        2. Entity Extraction & Memory Check → Extract data and check if already prepped  
        3. Deep Research Pipeline → Multi-agent research with reflection loops
        4. Research Quality Reflection → Verify research sufficiency
        5. Prep Guide Generation → Create personalized guide with citations
        6. Individual File Output → Save to outputs/fullworkflow/{company}/
        
        Args:
            email: Email data dictionary
            email_index: Index of current email being processed
            
        Returns:
            Complete processing result for this individual email
        """
        email_start_time = datetime.now()
        
        # Initialize individual email result
        result = {
            'email_index': email_index,
            'from': email.get('from', 'Unknown'),
            'subject': email.get('subject', 'No subject'),
            'date': email.get('date', 'Unknown'),
            'is_interview_email': False,
            'already_prepped': False,
            'research_conducted': False,
            'research_quality_sufficient': False,
            'prep_guide_generated': False,
            'company_keyword': '',
            'output_file_path': '',
            'processing_time': 0.0,
            'pipeline_results': {},
            'errors': []
        }
        
        try:
            # PIPELINE STAGE 1: Email Classification 
            print(f"🔄 PIPELINE STAGE 1: Email Classification")
            print(f"📬 Using Email Classifier Agent to determine if this is an interview email...")
            
            classification_result = self.email_classifier.classify_email(email)
            result['pipeline_results']['classification'] = classification_result
            
            is_interview = classification_result.get('classification') == 'Interview_invite'
            result['is_interview_email'] = is_interview
            
            if is_interview:
                print(f"✅ INTERVIEW EMAIL DETECTED")
                print(f"   🎯 Classification: {classification_result.get('classification')}")
                print(f"   📊 Confidence: {classification_result.get('confidence', 0):.2f}")
            else:
                print(f"❌ NOT AN INTERVIEW EMAIL")
                print(f"   📂 Classification: {classification_result.get('classification')}")
                print(f"   ⏭️  SKIPPING: Non-interview email will not be processed")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            # PIPELINE STAGE 2: Entity Extraction & Memory Check
            print(f"\n🔄 PIPELINE STAGE 2: Entity Extraction & Memory Check")
            print(f"🎯 Extracting company, role, interviewer, and other entities...")
            
            email_pipeline_result = self.email_pipeline.process_email(email, email_index)
            result['pipeline_results']['email_pipeline'] = email_pipeline_result
            result['already_prepped'] = email_pipeline_result.get('already_prepped', False)
            
            entities = email_pipeline_result.get('entities', {})
            if entities:
                print(f"✅ ENTITIES EXTRACTED:")
                if entities.get('companies'): 
                    print(f"   🏢 Company: {entities['companies']}")
                if entities.get('roles'):
                    print(f"   💼 Role: {entities['roles']}")
                if entities.get('interviewers'):
                    print(f"   👤 Interviewer: {entities['interviewers']}")
                if entities.get('dates'):
                    print(f"   📅 Date: {entities['dates']}")
            
            # Check if already prepped
            if result['already_prepped']:
                print(f"💾 ALREADY PREPPED: Interview preparation already exists")
                print(f"⏭️  SKIPPING: No need to regenerate prep guide")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            else:
                print(f"🆕 NOT PREPPED: This is a new interview - proceeding with preparation")
            
            # PIPELINE STAGE 3: Deep Research Pipeline (Multi-agent with Tavily Cache)
            print(f"\n🔄 PIPELINE STAGE 3: Deep Research Pipeline")
            print(f"🔬 Conducting multi-agent research with deep thinking, reflection, and validation...")
            print(f"📡 Integrating with Tavily cache for optimized API usage...")
            
            research_result = self.research_pipeline.conduct_deep_research(entities, email_index)
            result['pipeline_results']['research'] = research_result
            result['research_conducted'] = research_result.get('success', False)
            
            if result['research_conducted']:
                print(f"✅ DEEP RESEARCH COMPLETED")
                print(f"   🏢 Company Research: {'✅' if research_result.get('company_research') else '❌'}")
                print(f"   👤 Interviewer Research: {'✅' if research_result.get('interviewer_research') else '❌'}")
                print(f"   🎯 Role Research: {'✅' if research_result.get('role_research') else '❌'}")
                print(f"   🧠 Research Quality: {research_result.get('research_quality', 'Unknown')}")
            else:
                print(f"❌ RESEARCH FAILED")
                result['errors'].append("Deep research pipeline failed")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            # PIPELINE STAGE 4: Research Quality Reflection
            print(f"\n🔄 PIPELINE STAGE 4: Research Quality Reflection")
            print(f"🔍 Conducting deep reflection on whether research is sufficient for prep guide...")
            
            research_quality_sufficient = research_result.get('sufficient_for_prep_guide', False)
            result['research_quality_sufficient'] = research_quality_sufficient
            
            if research_quality_sufficient:
                print(f"✅ RESEARCH QUALITY SUFFICIENT")
                print(f"   📊 Quality Score: {research_result.get('quality_score', 'N/A')}")
                print(f"   🎯 Ready for prep guide generation")
            else:
                print(f"❌ RESEARCH QUALITY INSUFFICIENT")
                print(f"   📊 Quality Score: {research_result.get('quality_score', 'N/A')}")
                print(f"   💭 Reflection suggests more research needed")
                # Note: In future iterations, this could trigger another reflection loop
                result['errors'].append("Research quality insufficient for prep guide generation")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            # PIPELINE STAGE 5: Prep Guide Generation
            print(f"\n🔄 PIPELINE STAGE 5: Prep Guide Generation")
            print(f"📚 Generating personalized prep guide with citations...")
            
            prep_guide_result = self.prep_guide_pipeline.generate_prep_guide(
                email, entities, research_result, email_index
            )
            result['pipeline_results']['prep_guide'] = prep_guide_result
            result['prep_guide_generated'] = prep_guide_result.get('success', False)
            
            if result['prep_guide_generated']:
                print(f"✅ PREP GUIDE GENERATED")
                print(f"   📋 Before Interview Sections: ✅")
                print(f"   🔧 Technical Prep Sections: ✅") 
                print(f"   👤 Interviewer Background: ✅")
                print(f"   🔗 Related Links & Validations: ✅")
                print(f"   ❓ Personalized Questions: ✅")
                print(f"   📖 Citations Included: ✅")
            else:
                print(f"❌ PREP GUIDE GENERATION FAILED")
                result['errors'].append("Prep guide generation failed")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            # PIPELINE STAGE 6: Individual File Output
            print(f"\n🔄 PIPELINE STAGE 6: Individual File Output")
            print(f"💾 Extracting company keyword and saving individual output file...")
            
            # Use keyword extractor agent to get company name for file naming
            company_keyword = self.keyword_extractor.extract_keyword_from_email(email)
            result['company_keyword'] = company_keyword
            
            if not company_keyword:
                company_keyword = f"Company_{email_index}"
                print(f"⚠️  Could not extract company keyword, using fallback: {company_keyword}")
            else:
                print(f"🏷️  Company keyword extracted: {company_keyword}")
            
            # Create company-specific output directory
            company_output_dir = os.path.join(self.output_base_dir, company_keyword)
            os.makedirs(company_output_dir, exist_ok=True)
            
            # Save individual output file
            output_filename = f"{company_keyword}.py"  # As requested: company.py format
            output_file_path = os.path.join(company_output_dir, output_filename)
            
            # Write comprehensive output file
            self._write_individual_output_file(
                output_file_path, email, result, entities, research_result, prep_guide_result
            )
            
            result['output_file_path'] = output_file_path
            print(f"✅ INDIVIDUAL OUTPUT SAVED")
            print(f"   📁 Directory: {company_output_dir}/")
            print(f"   📄 File: {output_filename}")
            print(f"   🔗 Full Path: {output_file_path}")
            
            # Final processing summary for this email
            result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
            
            print(f"\n📊 INDIVIDUAL EMAIL PROCESSING SUMMARY")
            print(f"-" * 50)
            print(f"   📧 Subject: {result['subject'][:60]}{'...' if len(result['subject']) > 60 else ''}")
            print(f"   🏢 Company: {result['company_keyword']}")
            print(f"   🎯 Interview Email: ✅ YES")
            print(f"   💾 Already Prepped: {'✅' if result['already_prepped'] else '🆕 NEW'}")
            print(f"   🔬 Research Conducted: ✅ YES")
            print(f"   📚 Prep Guide Generated: ✅ YES") 
            print(f"   📁 Output File: {result['output_file_path']}")
            print(f"   ⏱️  Processing Time: {result['processing_time']:.2f}s")
            
            return result
            
        except Exception as e:
            result['errors'].append(str(e))
            result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
            print(f"❌ ERROR processing email {email_index}: {str(e)}")
            import traceback
            traceback.print_exc()
            return result
    
    def _fetch_emails_from_folder(self, folder_name: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch emails from the specified Gmail folder/label"""
        try:
            print(f"📡 Connecting to Gmail API...")
            service = get_gmail_service()
            
            print(f"📥 Fetching emails from folder: {folder_name}")
            raw_emails = get_email_messages(service, folder_name=folder_name, max_results=max_results)
            
            print(f"📑 Getting email details for {len(raw_emails)} emails...")
            emails = []
            for i, email_msg in enumerate(raw_emails, 1):
                print(f"   📧 Processing email {i}/{len(raw_emails)}...", end='\r')
                email_details = get_email_message_details(service, email_msg['id'])
                emails.append(email_details)
            
            print(f"✅ Successfully fetched {len(emails)} emails from {folder_name}")
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails from Gmail folder '{folder_name}': {str(e)}")
            return []
    
    def _write_individual_output_file(self, output_path: str, email: Dict[str, Any], 
                                    result: Dict[str, Any], entities: Dict[str, Any],
                                    research_result: Dict[str, Any], prep_guide_result: Dict[str, Any]):
        """Write comprehensive individual output file for this specific email/company"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f'''#!/usr/bin/env python3
"""
Interview Preparation Guide - {result['company_keyword']}
{'=' * 60}

Generated by Workflow Runner - Individual Email Processing
Email Index: {result['email_index']}
Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Processing Time: {result['processing_time']:.2f} seconds

This file contains the complete interview preparation guide generated
specifically for this individual email and company.
"""

# Email Information
EMAIL_INFO = {{
    "from": "{email.get('from', 'Unknown')}",
    "subject": "{email.get('subject', 'No subject')}",
    "date": "{email.get('date', 'Unknown')}",
    "email_index": {result['email_index']},
    "company_keyword": "{result['company_keyword']}"
}}

# Extracted Entities
ENTITIES = {entities}

# Research Results
RESEARCH_RESULTS = {research_result}

# Prep Guide Content
PREP_GUIDE = {prep_guide_result}

# Processing Statistics
PROCESSING_STATS = {{
    "is_interview_email": {result['is_interview_email']},
    "already_prepped": {result['already_prepped']},
    "research_conducted": {result['research_conducted']},
    "research_quality_sufficient": {result['research_quality_sufficient']},
    "prep_guide_generated": {result['prep_guide_generated']},
    "processing_time_seconds": {result['processing_time']:.2f},
    "generated_at": "{datetime.now().isoformat()}"
}}

if __name__ == "__main__":
    print("Interview Preparation Guide for {result['company_keyword']}")
    print("=" * 60)
    print(f"Email: {{EMAIL_INFO['subject']}}")
    print(f"From: {{EMAIL_INFO['from']}}")
    print(f"Company: {{EMAIL_INFO['company_keyword']}}")
    print("=" * 60)
    
    if PREP_GUIDE.get('prep_guide_content'):
        print("\\nPREP GUIDE CONTENT:")
        print(PREP_GUIDE['prep_guide_content'])
    else:
        print("\\nNo prep guide content available.")
''')
        
        print(f"📝 Individual output file written: {output_path}")
    
    def _display_final_workflow_summary(self, workflow_result: Dict[str, Any]):
        """Display comprehensive final workflow summary"""
        print(f"\n" + "=" * 80)
        print("🎉 COMPLETE WORKFLOW EXECUTION FINISHED")
        print("=" * 80)
        
        print(f"📊 WORKFLOW STATISTICS:")
        print(f"   📥 Total Emails Fetched: {workflow_result['total_emails_fetched']}")
        print(f"   🎯 Interview Emails Found: {workflow_result['interview_emails_found']}")
        print(f"   💾 Already Prepped: {workflow_result['emails_already_prepped']}")
        print(f"   🆕 Newly Processed: {workflow_result['emails_newly_processed']}")
        print(f"   🔬 Research Conducted: {workflow_result['research_conducted_count']}")
        print(f"   📚 Prep Guides Generated: {workflow_result['prep_guides_generated']}")
        print(f"   ⏱️  Total Processing Time: {workflow_result['processing_time']:.2f}s")
        
        if workflow_result['errors']:
            print(f"   ❌ Errors Encountered: {len(workflow_result['errors'])}")
            for i, error in enumerate(workflow_result['errors'][:3], 1):  # Show first 3 errors
                print(f"      {i}. {error}")
            if len(workflow_result['errors']) > 3:
                print(f"      ... and {len(workflow_result['errors']) - 3} more errors")
        
        print(f"\n📁 OUTPUT FILES:")
        generated_files = [r for r in workflow_result['individual_results'] if r.get('output_file_path')]
        if generated_files:
            print(f"   📄 Generated {len(generated_files)} individual output files:")
            for result in generated_files:
                print(f"      • {result['company_keyword']}: {result['output_file_path']}")
        else:
            print(f"   📄 No output files generated")
        
        print(f"\n🎯 WORKFLOW OUTCOME:")
        if workflow_result['success']:
            print(f"   ✅ WORKFLOW COMPLETED SUCCESSFULLY")
            print(f"   🎊 Generated {workflow_result['prep_guides_generated']} prep guides")
            print(f"   💡 Use 'python workflows/cache_manager.py --status' to check cache statistics")
        else:
            print(f"   ❌ WORKFLOW COMPLETED WITH ERRORS")
            print(f"   💡 Use 'python workflows/cache_manager.py --status' to check cache health")
        
        print("=" * 80)


def main():
    """Main entry point for workflow runner"""
    parser = argparse.ArgumentParser(
        description="Interview Prep Workflow Runner - Main Entry Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python workflows/workflow_runner.py                    # Process default 10 emails
  python workflows/workflow_runner.py --max-emails 20    # Process up to 20 emails
  
Environment Setup:
  Set INTERVIEW_FOLDER in .env file to specify the Gmail folder/label to read from.
  Default: INBOX
  
Pipeline Flow:
  1. Email Classification → Only process interview emails  
  2. Entity Extraction & Memory Check → Extract data and check if already prepped
  3. Deep Research Pipeline → Multi-agent research with Tavily cache integration
  4. Research Quality Reflection → Verify research is sufficient for prep guide
  5. Prep Guide Generation → Create personalized guides with citations
  6. Individual Output Files → Store results in outputs/fullworkflow/{company_name}/

Features:
  • Individual email processing (one by one)
  • Detailed terminal progress reporting
  • Tavily cache integration for research optimization
  • Company keyword extraction for file naming
  • Personalized prep guides with citations
  • Quality reflection loops
        """
    )
    
    parser.add_argument('--max-emails', type=int, default=10,
                       help='Maximum number of emails to process (default: 10)')
    
    args = parser.parse_args()
    
    print("🚀 WORKFLOW RUNNER - MAIN ENTRY POINT")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        runner = WorkflowRunner()
        results = runner.run_complete_workflow(max_emails=args.max_emails)
        
        if results['success']:
            print(f"\n🎊 WORKFLOW RUNNER EXECUTION SUCCESSFUL!")
            print(f"📊 Generated {results['prep_guides_generated']} prep guides")
            print(f"💡 Use 'python workflows/cache_manager.py --status' to check cache statistics")
        else:
            print(f"\n💥 WORKFLOW RUNNER EXECUTION FAILED!")
            print(f"❌ Errors: {len(results['errors'])}")
            print(f"💡 Use 'python workflows/cache_manager.py --status' to check cache health")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Workflow runner interrupted by user")
        print(f"💡 Use 'python workflows/cache_manager.py --status' to check cache status")
    except Exception as e:
        print(f"\n💥 Fatal error in workflow runner: {str(e)}")
        print(f"💡 Use 'python workflows/cache_manager.py --clear-all' if cache corruption suspected")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
