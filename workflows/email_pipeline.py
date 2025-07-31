# workflows/email_pipeline.py
"""
Email Pipeline with LangGraph Chains

This pipeline implements sophisticated conditional routing:
1. Email Classification
2. Entity Extraction (for Interview_invite emails)
3. Similarity Check (against existing interview memory)
4. Conditional Research (only for new/unprepped interviews)
5. Memory Update

Flow:
Email -> Classify -> [If Interview] -> Extract Entities -> Check Memory -> 
[If New/Not Prepped] -> Research -> Store/Update Memory
[If Duplicate/Prepped] -> Skip Research -> Log
"""

import os
import sys
import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.models import AgentInput, AgentOutput
from shared.google_oauth.google_email_setup import get_gmail_service
from shared.google_oauth.google_email_functions import get_email_messages, get_email_message_details
from agents.entity_extractor.agent import EntityExtractor
from agents.memory_systems.interview_store.agents import InterviewStore
from shared.tavily_client import TavilyClient

# Core utility functions (moved from email_pipeline.py)
class EmailPipelineError(Exception):
    """Custom exception for email pipeline errors"""
    pass

def create_gmail_service():
    """Initialize Gmail service - can be mocked for testing"""
    return get_gmail_service()

def fetch_and_parse_emails(service, folder_name, max_results=10):
    """
    Pure function: Gmail service + params -> parsed emails
    No side effects, just data transformation
    """
    try:
        raw_emails = get_email_messages(service, folder_name=folder_name, max_results=max_results)
        emails = [get_email_message_details(service, msg['id']) for msg in raw_emails]
        return emails
    except Exception as e:
        raise EmailPipelineError(f"Failed to fetch emails from {folder_name}: {str(e)}")

def classify_emails(emails):
    """
    Pure function: emails -> classified emails
    Returns structured data, doesn't print or route
    
    TEMPORARY IMPLEMENTATION: Uses simple rule-based classification
    TODO: Replace with AI-based EmailClassifierAgent when ready
    """
    classified = {
        'Personal_sent': [],
        'Interview_invite': [],
        'Others': []
    }
    
    for email in emails:
        subject = email.get('subject', '').lower()
        sender = email.get('sender', '').lower()
        
        # TEMPORARY RULES - replace with AI classification
        # Interview-related keywords
        interview_keywords = ['interview', 'invitation', 'invite', 'schedule', 'meeting', 'call', 'chat', 'discussion', 'screening', 'phone screen', 'video call', 'zoom', 'hiring', 'position', 'role', 'job', 'opportunity', 'application']
        
        if any(keyword in subject for keyword in interview_keywords):
            classified['Interview_invite'].append(email)
        elif 'dinner' in subject or 'plans' in subject or 'from kathy' in subject:
            classified['Personal_sent'].append(email)
        else:
            classified['Others'].append(email)
    
    return classified

def format_email_summaries(classified_emails):
    """
    Pure function: classified emails -> formatted output
    Returns data structure, doesn't print
    """
    summaries = []
    
    for email in classified_emails.get('Interview_invite', []):
        summaries.append({
            'type': 'interview',
            'icon': '📬',
            'message': f"Interview invite: {email['subject']} from {email['sender']}"
        })
    
    for email in classified_emails.get('Personal_sent', []):
        summaries.append({
            'type': 'personal',
            'icon': '👤',
            'message': f"Personal: {email['subject']} from {email['sender']}"
        })
    
    for email in classified_emails.get('Others', []):
        summaries.append({
            'type': 'other',
            'icon': '📎',
            'message': f"Other: {email['subject']} from {email['sender']}"
        })
    
    return summaries

def clean_email_content(text: str) -> str:
    """Clean email content by removing URLs, tracking links, and noise"""
    if not text:
        return text
    
    # Remove URLs and tracking links
    text = re.sub(r'https?://[^\s\]]+', '', text)
    
    # Remove email addresses in brackets/links
    text = re.sub(r'\[[^\]]*@[^\]]*\]', '', text)
    
    # Remove calendar tracking text
    text = re.sub(r'Reply for \S+@\S+', '', text)
    text = re.sub(r'mark_sender_as_known\S*', '', text)
    
    # Remove extra whitespace and clean up formatting
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()

class EmailPipeline:
    """Email processing with intelligent routing and memory"""
    
    def __init__(self):
        # Import agents here to avoid circular imports
        try:
            from agents.entity_extractor.agent import EntityExtractor
            self.entity_extractor = EntityExtractor({})
        except ImportError:
            print("Warning: EntityExtractor not available, using mock")
            self.entity_extractor = None
            
        try:
            from agents.memory_systems.interview_store.agents import InterviewStore
            self.interview_store = InterviewStore({})
        except ImportError:
            print("Warning: InterviewStore not available, using mock")
            self.interview_store = None
        # Note: TavilyClient will be imported when needed
        
    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single email through the enhanced pipeline"""
        
        result = {
            'email_id': email_data.get('id', 'unknown'),
            'subject': email_data.get('subject', ''),
            'classification': None,
            'entities': None,
            'memory_check': None,
            'research_performed': False,
            'research_data': None,
            'memory_updated': False,
            'processing_time': 0,
            'errors': []
        }
        
        start_time = datetime.now()
        
        try:
            # Step 1: Classify Email
            classification_result = await self._classify_email(email_data)
            result['classification'] = classification_result
            
            # Step 2: If Interview_invite, extract entities
            if classification_result.get('category') == 'Interview_invite':
                entities_result = await self._extract_entities(email_data)
                result['entities'] = entities_result
                
                if entities_result.get('success'):
                    # Step 3: Check memory for similar interviews
                    memory_check = await self._check_interview_memory(entities_result['data'])
                    result['memory_check'] = memory_check
                    
                    # Step 4: Conditional research based on memory
                    if self._should_perform_research(memory_check):
                        research_data = await self._perform_research(entities_result['data'])
                        result['research_performed'] = True
                        result['research_data'] = research_data
                        
                        # Step 5: Store/Update memory
                        memory_update = await self._update_memory(entities_result['data'], research_data)
                        result['memory_updated'] = memory_update.get('success', False)
                    else:
                        print(f"🔄 Skipping research for {entities_result['data'].get('COMPANY', ['Unknown'])[0]} - similar interview already prepped")
            
            result['processing_time'] = (datetime.now() - start_time).total_seconds()
            return result
            
        except Exception as e:
            result['errors'].append(str(e))
            result['processing_time'] = (datetime.now() - start_time).total_seconds()
            return result
    
    async def _classify_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify email using simple classification function"""
        try:
            # Use the simple classifier (now available in this file)
            # TODO: Replace with AI-based EmailClassifierAgent when ready
            emails = [email_data]  # Wrap in list as expected by classify_emails
            classified = classify_emails(emails)
            
            # Determine the category for this email
            category = 'Others'  # default
            if email_data in classified.get('Interview_invite', []):
                category = 'Interview_invite'
            elif email_data in classified.get('Personal_sent', []):
                category = 'Personal_sent'
            
            return {
                'success': True,
                'category': category,
                'confidence': 0.8,  # Simple classifier confidence
                'metadata': {'classifier': 'temporary_simple_rules'}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _extract_entities(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entities using EntityExtractorAgent"""
        try:
            # Combine subject and body for better entity extraction
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            
            # Clean the content to remove tracking URLs and noise
            clean_subject = clean_email_content(subject)
            clean_body = clean_email_content(body)
            
            # Use both cleaned subject and body for entity extraction
            combined_text = f"{clean_subject}\n\n{clean_body}".strip()
            if not combined_text:
                combined_text = clean_subject  # Fallback to just subject if body is empty
                
            agent_input = AgentInput(data={
                'text': combined_text,
                'email_id': email_data.get('id')
            })
            entities_output = await self.entity_extractor.execute(agent_input)
            return {
                'success': entities_output.success,
                'data': entities_output.data,
                'errors': entities_output.errors
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _check_interview_memory(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Check for similar interviews in memory"""
        try:
            # Build query parameters from entities
            query_params = {}
            if 'COMPANY' in entities and entities['COMPANY']:
                query_params['company'] = entities['COMPANY'][0]
            if 'ROLE' in entities and entities['ROLE']:
                query_params['role'] = entities['ROLE'][0]
            if 'CANDIDATE' in entities and entities['CANDIDATE']:
                query_params['candidate'] = entities['CANDIDATE'][0]
            
            agent_input = AgentInput(data={
                'action': 'get_duplicates',
                'query_params': query_params
            })
            
            memory_output = await self.interview_store.execute(agent_input)
            return {
                'success': memory_output.success,
                'duplicates': memory_output.data.get('duplicates', []),
                'similarity_scores': memory_output.data.get('similarity_scores', [])
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _should_perform_research(self, memory_check: Dict[str, Any]) -> bool:
        """Determine if research should be performed based on memory check"""
        if not memory_check.get('success'):
            return True  # If memory check failed, perform research
        
        duplicates = memory_check.get('duplicates', [])
        similarity_scores = memory_check.get('similarity_scores', [])
        
        # Check if any duplicate has high similarity and is already prepped/completed
        for i, duplicate in enumerate(duplicates):
            if i < len(similarity_scores) and similarity_scores[i] > 0.8:  # High similarity threshold
                status = duplicate.get('status', '').lower()
                if status in ['prepped', 'scheduled', 'completed']:
                    return False  # Skip research
        
        return True  # Perform research
    
    async def _perform_research(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Perform research using Tavily API"""
        try:
            research_data = {}
            
            # For now, we'll create mock research data since TavilyClient might not be implemented
            # In production, you would use:
            # from shared.tavily_client import TavilyClient
            # tavily_client = TavilyClient()
            
            # Research company if available
            if 'COMPANY' in entities and entities['COMPANY']:
                company_name = entities['COMPANY'][0]
                # company_research = tavily_client.search_company(company_name)
                company_research = {"name": company_name, "mock": "research data"}
                research_data['company'] = company_research
            
            # Research role if available
            if 'ROLE' in entities and entities['ROLE']:
                role_title = entities['ROLE'][0]
                # role_research = tavily_client.search_role(role_title)
                role_research = {"title": role_title, "mock": "role data"}
                research_data['role'] = role_research
            
            return {
                'success': True,
                'data': research_data,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _update_memory(self, entities: Dict[str, Any], research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store or update interview in memory"""
        try:
            # Prepare data for storage
            store_data = {
                'action': 'store',
                'entities': entities,
                'research_data': research_data,
                'status': 'preparing'  # Initial status
            }
            
            agent_input = AgentInput(data=store_data)
            memory_output = await self.interview_store.execute(agent_input)
            
            return {
                'success': memory_output.success,
                'interview_id': memory_output.data.get('interview_id'),
                'errors': memory_output.errors
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Convenience functions for LangGraph integration
def create_email_pipeline():
    """Factory function to create email pipeline"""
    return EmailPipeline()

async def process_classified_interviews(classified_emails: Dict[str, List], pipeline: EmailPipeline) -> List[Dict]:
    """Process all interview invites through enhanced pipeline"""
    results = []
    interview_emails = classified_emails.get('Interview_invite', [])
    
    for email in interview_emails:
        result = await pipeline.process_email(email)
        results.append(result)
    
    return results
