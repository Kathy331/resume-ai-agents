#!/usr/bin/env python3
"""
Comprehensive Interview Prep Guide Generator
Production module for generating interview preparation materials
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.llm_client import call_llm
from agents.memory_systems.shared_memory import SharedMemorySystem
from shared.models import AgentInput, AgentOutput


class PrepGuideGenerator:
    """
    Production-ready comprehensive prep guide generator
    """
    
    def __init__(self):
        self.memory_system = SharedMemorySystem()
    
    async def generate_prep_guide_for_interview(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive prep guide for a single interview
        
        Args:
            interview_data: Interview information from memory system
            
        Returns:
            Dict containing the prep guide content
        """
        company = interview_data.get('company', 'Unknown Company')
        role = interview_data.get('role', 'Unknown Role')
        interviewer = interview_data.get('interviewer', 'Unknown Interviewer')
        
        # Create prompt for comprehensive prep guide
        prompt = f"""
        Generate a comprehensive interview preparation guide for the following interview:
        
        Company: {company}
        Role: {role}
        Interviewer: {interviewer}
        
        Please provide:
        1. Company-specific research points
        2. Role-specific technical questions to prepare for
        3. Behavioral questions likely to be asked
        4. Key talking points to highlight
        5. Questions to ask the interviewer
        6. Strategic recommendations for success
        
        Format the response as a structured preparation guide.
        """
        
        try:
            llm_response = await call_llm(prompt)
            
            return {
                'interview_id': interview_data.get('id'),
                'company': company,
                'role': role,
                'interviewer': interviewer,
                'prep_content': llm_response,
                'generated_at': datetime.now().isoformat(),
                'success': True
            }
        except Exception as e:
            return {
                'interview_id': interview_data.get('id'),
                'company': company,
                'role': role,
                'interviewer': interviewer,
                'error': str(e),
                'success': False
            }
    
    def print_prep_guide(self, prep_guide: Dict[str, Any]) -> None:
        """
        Print a formatted prep guide to console
        """
        if not prep_guide.get('success'):
            print(f"❌ Failed to generate prep guide: {prep_guide.get('error', 'Unknown error')}")
            return
        
        print("\n" + "=" * 100)
        print(f"🎯 INTERVIEW PREP GUIDE")
        print("=" * 100)
        print(f"🏢 Company: {prep_guide['company']}")
        print(f"👤 Role: {prep_guide['role']}")
        print(f"👨‍💼 Interviewer: {prep_guide['interviewer']}")
        print(f"📅 Generated: {prep_guide['generated_at']}")
        print("\n" + "-" * 100)
        print(prep_guide['prep_content'])
        print("=" * 100 + "\n")


async def generate_comprehensive_prep_guide(interview_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main function to generate comprehensive prep guides
    Can be called from workflow_runner.py
    
    Args:
        interview_data: Optional specific interview data. If None, fetches from memory.
        
    Returns:
        Results dictionary with success status and details
    """
    generator = PrepGuideGenerator()
    
    if interview_data:
        # Generate for specific interview
        result = await generator.generate_prep_guide_for_interview(interview_data)
        generator.print_prep_guide(result)
        return {
            'success': result['success'],
            'guides_generated': 1 if result['success'] else 0,
            'results': [result]
        }
    else:
        # Generate for all prepped interviews in memory
        memory_system = SharedMemorySystem()
        
        # Get all interviews and filter for prepped ones
        all_interviews = memory_system.get_all_interviews()
        interviews = [
            interview for interview in all_interviews 
            if interview.get('status', '').lower() == 'prepped'
        ]
        
        if not interviews:
            print("ℹ️  No prepped interviews found in memory")
            return {
                'success': True,
                'guides_generated': 0,
                'results': [],
                'message': 'No prepped interviews found'
            }
        
        results = []
        guides_generated = 0
        
        print(f"📚 Generating prep guides for {len(interviews)} interviews...")
        
        for interview in interviews:
            result = await generator.generate_prep_guide_for_interview(interview)
            results.append(result)
            
            if result['success']:
                guides_generated += 1
                generator.print_prep_guide(result)
            else:
                print(f"❌ Failed to generate prep guide for {interview.get('company', 'Unknown')}: {result.get('error')}")
        
        return {
            'success': True,
            'guides_generated': guides_generated,
            'total_interviews': len(interviews),
            'results': results
        }


# For backward compatibility with existing code
async def generate_enhanced_prep_guide():
    """Legacy function name for backward compatibility"""
    return await generate_comprehensive_prep_guide()


if __name__ == "__main__":
    # Test the prep guide generator
    asyncio.run(generate_comprehensive_prep_guide())
