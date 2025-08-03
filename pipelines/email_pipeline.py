#!/usr/bin/env python3
"""
Email Pipeline - Email Classification, Entity Extraction & Memory Check
======================================================================
Handles:
1. Email Classification (interview vs non-interview)  
2. Entity Extraction (company, role, interviewer, dates, etc.)
3. Memory Store Check (already prepped vs new interview)
4. Terminal Display (prepped vs not prepped status)
"""

import asyncio
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.email_classifier.agent import EmailClassifierAgent
from agents.entity_extractor.agent import EntityExtractor
from agents.memory_systems.shared_memory import SharedMemorySystem
from shared.models import AgentInput, AgentOutput


class EmailPipeline:
    """
    Email Pipeline: Classification → Entity Extraction → Memory Check
    """
    
    def __init__(self):
        # Initialize agents with configuration
        agent_config = {'model': 'gpt-4', 'temperature': 0.7}
        self.classifier = EmailClassifierAgent(config=agent_config)
        self.entity_extractor = EntityExtractor(config=agent_config)
        self.memory_system = SharedMemorySystem()
    
    def process_email(self, email: Dict[str, Any], email_index: int) -> Dict[str, Any]:
        """
        Process single email through classification, entity extraction, and memory check
        
        Args:
            email: Email data dictionary
            email_index: Index of email being processed
            
        Returns:
            Pipeline result dictionary
        """
        print(f"\n📧 EMAIL PIPELINE - Processing Email {email_index}")
        print("=" * 50)
        
        pipeline_start_time = datetime.now()
        
        result = {
            'success': False,
            'email_index': email_index,
            'is_interview': False,
            'classification': None,
            'entities': {},
            'already_prepped': False,
            'memory_status': None,
            'processing_time': 0,
            'errors': []
        }
        
        try:
            # Step 1: Email Classification
            print(f"🔍 Step 1: Email Classification")
            classification_result = self._classify_email(email)
            
            result['classification'] = classification_result.get('category', 'Unknown')
            result['is_interview'] = classification_result.get('is_interview', False)
            
            if not result['is_interview']:
                print(f"   📋 Classification: {result['classification']} (Non-interview)")
                print(f"   ⏭️  SKIPPING: Non-interview email")
                result['success'] = True
                result['processing_time'] = (datetime.now() - pipeline_start_time).total_seconds()
                return result
            
            print(f"   🎯 Classification: INTERVIEW EMAIL DETECTED!")
            print(f"   📧 Category: {result['classification']}")
            
            # Step 2: Entity Extraction
            print(f"\n🧩 Step 2: Entity Extraction")
            entity_result = self._extract_entities(email)
            
            if not entity_result.get('success'):
                result['errors'].append(f"Entity extraction failed: {entity_result.get('error', 'Unknown')}")
                result['processing_time'] = (datetime.now() - pipeline_start_time).total_seconds()
                return result
            
            result['entities'] = entity_result.get('entities', {})
            self._display_extracted_entities(result['entities'])
            
            # Step 3: Memory Store Check
            print(f"\n💾 Step 3: Memory Store Check")
            memory_result = self._check_memory_store(result['entities'])
            
            result['already_prepped'] = memory_result.get('already_prepped', False)
            result['memory_status'] = memory_result.get('status', 'Unknown')
            
            self._display_memory_status(result['already_prepped'], result['memory_status'])
            
            result['success'] = True
            result['processing_time'] = (datetime.now() - pipeline_start_time).total_seconds()
            
            print(f"\n✅ EMAIL PIPELINE COMPLETED")
            print(f"   📊 Status: Interview={'Yes' if result['is_interview'] else 'No'}, Prepped={'Yes' if result['already_prepped'] else 'No'}")
            print(f"   ⏱️  Processing Time: {result['processing_time']:.2f}s")
            
            return result
            
        except Exception as e:
            result['errors'].append(str(e))
            result['processing_time'] = (datetime.now() - pipeline_start_time).total_seconds()
            print(f"❌ EMAIL PIPELINE ERROR: {str(e)}")
            return result
    
    def _classify_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Classify email using EmailClassifierAgent"""
        try:
            # The classifier expects a list of emails with specific fields
            input_data = AgentInput(
                data={"emails": [email]},
                metadata={}
            )
            
            # Use asyncio to run the classifier
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(self.classifier.execute(input_data))
                
                # Get classification results - classifier returns 'interview', 'personal', 'other' keys
                interview_ids = result.data.get('interview', [])
                
                # Check if this email was classified as interview
                email_id = email.get('id', '')
                is_interview = email_id in interview_ids
                
                category = 'Interview_invite' if is_interview else 'Other'
                
                return {
                    'success': True,
                    'category': category,
                    'is_interview': is_interview
                }
            finally:
                loop.close()
                
        except Exception as e:
            print(f"   ❌ Classification error: {str(e)}")
            return {
                'success': False,
                'category': 'Unknown',
                'is_interview': False,
                'error': str(e)
            }
    
    def _extract_entities(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entities using EntityExtractor"""
        try:
            # Combine email content for entity extraction
            email_text = f"Subject: {email.get('subject', '')}\n\nFrom: {email.get('from', '')}\n\nBody: {email.get('body', '')}"
            
            input_data = AgentInput(
                data={"text": email_text},
                metadata={}
            )
            
            # Use asyncio to run the entity extractor
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(self.entity_extractor.execute(input_data))
                raw_entities = result.data if result.success else {}
                
                # Map uppercase keys to lowercase for consistency
                entities = {}
                for key, value in raw_entities.items():
                    if isinstance(value, list) and value:
                        entities[key.lower()] = value[0] if len(value) == 1 else value
                    else:
                        entities[key.lower()] = value
                
                return {
                    'success': True,
                    'entities': entities
                }
                
            finally:
                loop.close()
                
        except Exception as e:
            print(f"   ❌ Entity extraction error: {str(e)}")
            return {
                'success': False,
                'entities': {},
                'error': str(e)
            }
    
    def _display_extracted_entities(self, entities: Dict[str, Any]):
        """Display extracted entities in terminal"""
        print(f"   🧩 Entities Extracted:")
        if entities:
            for key, value in entities.items():
                if value and key not in ['email_id']:
                    display_value = value if not isinstance(value, list) else ', '.join(map(str, value))
                    print(f"      {key.upper()}: {display_value}")
        else:
            print(f"      No entities found")
    
    def _check_memory_store(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Check if interview already exists in memory store"""
        try:
            company = entities.get('company', '')
            role = entities.get('role', '')
            interviewer = entities.get('interviewer', '')
            
            if not company:
                return {
                    'already_prepped': False,
                    'status': 'New interview - no company identified',
                    'match_details': None
                }
            
            # Check memory for similar interviews
            all_interviews = self.memory_system.get_all_interviews()
            
            for existing in all_interviews:
                if (existing.get('company_name', '').lower() == company.lower() and
                    existing.get('role', '').lower() == role.lower() and
                    existing.get('status', '').lower() in ['prepped', 'completed']):
                    
                    match_details = {
                        'matched_company': existing.get('company_name', ''),
                        'matched_role': existing.get('role', ''),
                        'matched_interviewer': existing.get('interviewer', ''),
                        'prep_date': existing.get('created_at', ''),
                        'status': existing.get('status', '')
                    }
                    
                    return {
                        'already_prepped': True,
                        'status': f'Interview already prepped for {company} - {role}',
                        'match_details': match_details
                    }
            
            return {
                'already_prepped': False,
                'status': f'New interview for {company} - {role}',
                'match_details': None
            }
            
        except Exception as e:
            print(f"   ❌ Memory check error: {str(e)}")
            return {
                'already_prepped': False,
                'status': f'Memory check failed: {str(e)}',
                'match_details': None
            }
    
    def _display_memory_status(self, already_prepped: bool, status: str):
        """Display memory check status in terminal"""
        if already_prepped:
            print(f"   ✅ MEMORY STATUS: ALREADY PREPPED")  
            print(f"   📋 Details: {status}")
            print(f"   ⏭️  Will skip research pipeline")
        else:
            print(f"   🆕 MEMORY STATUS: NEW INTERVIEW")
            print(f"   📋 Details: {status}")
            print(f"   🔬 Will proceed to deep research pipeline")
