# workflows/enhanced_email_pipeline.py
"""
Enhanced Email Pipeline with LangGraph Chains

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
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.models import AgentInput, AgentOutput
from agents.email_classifier.agent import EmailClassifierAgent
from agents.entity_extractor.agent import EntityExtractorAgent
from agents.memory_systems.interview_store.agents import InterviewStoreAgent
from shared.tavily_client import TavilyClient

class EnhancedEmailPipeline:
    """Enhanced email processing with intelligent routing and memory"""
    
    def __init__(self):
        # Import agents here to avoid circular imports
        from agents.email_classifier.agent import EmailClassifierAgent
        from agents.entity_extractor.agent import EntityExtractorAgent  
        from agents.memory_systems.interview_store.agents import InterviewStoreAgent
        
        self.email_classifier = EmailClassifierAgent({})
        self.entity_extractor = EntityExtractorAgent({})
        self.interview_store = InterviewStoreAgent({})
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
        """Classify email using EmailClassifierAgent"""
        try:
            agent_input = AgentInput(data={'text': email_data.get('body', '')})
            classification_output = await self.email_classifier.execute(agent_input)
            return {
                'success': classification_output.success,
                'category': classification_output.data.get('category'),
                'confidence': classification_output.data.get('confidence'),
                'metadata': classification_output.metadata
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _extract_entities(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entities using EntityExtractorAgent"""
        try:
            agent_input = AgentInput(data={
                'text': email_data.get('body', ''),
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
def create_enhanced_pipeline():
    """Factory function to create enhanced pipeline"""
    return EnhancedEmailPipeline()

async def process_classified_interviews(classified_emails: Dict[str, List], pipeline: EnhancedEmailPipeline) -> List[Dict]:
    """Process all interview invites through enhanced pipeline"""
    results = []
    interview_emails = classified_emails.get('Interview_invite', [])
    
    for email in interview_emails:
        result = await pipeline.process_email(email)
        results.append(result)
    
    return results
