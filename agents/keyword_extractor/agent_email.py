#!/usr/bin/env python3
"""
Email Keyword Extractor Agent
Specialized agent for extracting company names from interview emails
"""

import re
import os
import sys
from typing import List, Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from shared.llm_client import call_llm


class EmailKeywordExtractor:
    """
    Specialized agent for extracting the primary company keyword from interview emails.
    Focuses on identifying the most important company name for file naming purposes.
    """
    
    def __init__(self):
        self.company_indicators = [
            'internship', 'interview', 'opportunity', 'position', 'role',
            'application', 'hiring', 'recruitment', 'job', 'career'
        ]
        
        # Common email domains to ignore
        self.ignore_domains = [
            'gmail', 'yahoo', 'hotmail', 'outlook', 'email', 'mail',
            'live', 'icloud', 'aol', 'protonmail'
        ]
    
    def extract_keyword_from_email(self, email_data: Dict[str, Any]) -> str:
        """
        Extract the primary company keyword from an email
        
        Args:
            email_data: Dictionary containing email information
            
        Returns:
            Single keyword string (company name)
        """
        subject = email_data.get('subject', '')
        sender = email_data.get('sender', email_data.get('from', ''))
        body = email_data.get('body', '')
        
        # Try multiple extraction methods in order of preference
        keyword = (
            self._extract_from_subject(subject) or
            self._extract_from_sender(sender) or
            self._extract_from_body(body) or
            self._extract_from_llm(subject, sender, body) or
            'Interview'  # Fallback
        )
        
        return self._clean_keyword(keyword)
    
    def _extract_from_subject(self, subject: str) -> Optional[str]:
        """Extract company name from email subject"""
        if not subject:
            return None
        
        # Pattern 1: "Interview with [Company]" or "Interview for [Company]"
        patterns = [
            r'interview\s+(?:with|for|at)\s+([A-Z][a-zA-Z]+)',
            r'([A-Z][a-zA-Z]+)\s+(?:internship|interview|opportunity)',
            r'(?:internship|interview|opportunity).*?(?:with|at|for)\s+([A-Z][a-zA-Z]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                candidate = match.group(1)
                if self._is_valid_company_name(candidate):
                    return candidate
        
        # Pattern 2: Look for capitalized words (potential company names)
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', subject)
        for word in words:
            if (word.lower() not in ['interview', 'internship', 'opportunity', 'invitation', 'with', 'for', 'at', 'the', 'and'] 
                and len(word) > 2):
                return word
        
        return None
    
    def _extract_from_sender(self, sender: str) -> Optional[str]:
        """Extract company name from sender email"""
        if not sender or '@' not in sender:
            return None
        
        # Extract domain
        email_part = sender.split('<')[-1].split('>')[0] if '<' in sender else sender
        if '@' not in email_part:
            return None
        
        domain = email_part.split('@')[1].split('.')[0]
        
        # Skip common email providers
        if domain.lower() in self.ignore_domains:
            return None
        
        # Clean and capitalize domain name
        if len(domain) > 2 and domain.isalpha():
            return domain.capitalize()
        
        return None
    
    def _extract_from_body(self, body: str) -> Optional[str]:
        """Extract company name from email body"""
        if not body:
            return None
        
        # Look for company names in common patterns
        patterns = [
            r'(?:at|from|with)\s+([A-Z][a-zA-Z]+)(?:\s|$|\.)',
            r'([A-Z][a-zA-Z]+)\s+(?:team|internship|program|interview)',
            r'(?:welcome to|join)\s+([A-Z][a-zA-Z]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, body)
            for match in matches:
                if self._is_valid_company_name(match):
                    return match
        
        return None
    
    def _extract_from_llm(self, subject: str, sender: str, body: str) -> Optional[str]:
        """Use LLM to extract company name if other methods fail"""
        try:
            prompt = f"""
Extract the company name from this interview email. Return only the company name, nothing else.

Subject: {subject}
From: {sender}
Body: {body[:500]}...

Company name:"""

            response = call_llm(prompt, model="gpt-3.5-turbo", max_tokens=50)
            
            if response and response.strip():
                # Clean the response
                company_name = response.strip().strip('"').strip("'")
                # Take only the first word if multiple words
                company_name = company_name.split()[0]
                
                if self._is_valid_company_name(company_name):
                    return company_name
        
        except Exception as e:
            print(f"⚠️ LLM extraction failed: {str(e)}")
        
        return None
    
    def _is_valid_company_name(self, name: str) -> bool:
        """Check if a string is a valid company name"""
        if not name or len(name) < 2:
            return False
        
        # Must start with capital letter
        if not name[0].isupper():
            return False
        
        # Must be alphabetic
        if not name.isalpha():
            return False
        
        # Exclude common words
        common_words = [
            'interview', 'internship', 'opportunity', 'invitation', 'team',
            'program', 'position', 'role', 'application', 'hiring', 'recruitment',
            'hello', 'dear', 'welcome', 'congratulations', 'thank', 'please',
            'with', 'from', 'the', 'and', 'for', 'at', 'to', 'we', 'you', 'your'
        ]
        
        if name.lower() in common_words:
            return False
        
        return True
    
    def _clean_keyword(self, keyword: str) -> str:
        """Clean and standardize the keyword"""
        if not keyword:
            return 'Interview'
        
        # Remove non-alphanumeric characters
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', keyword)
        
        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:].lower()
        
        # Ensure minimum length
        if len(cleaned) < 2:
            return 'Interview'
        
        return cleaned
    
    def extract_keywords_from_emails(self, emails: List[Dict[str, Any]]) -> List[str]:
        """
        Extract keywords from multiple emails
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            List of keywords (one per email)
        """
        keywords = []
        
        for email in emails:
            keyword = self.extract_keyword_from_email(email)
            keywords.append(keyword)
        
        # Ensure unique keywords with numbering for duplicates
        unique_keywords = []
        keyword_counts = {}
        
        for keyword in keywords:
            if keyword not in keyword_counts:
                keyword_counts[keyword] = 1
                unique_keywords.append(keyword)
            else:
                keyword_counts[keyword] += 1
                unique_keywords.append(f"{keyword}_{keyword_counts[keyword]}")
        
        return unique_keywords
    
    def save_keywords_to_file(self, keywords: List[str], output_file: str = "keywords.txt"):
        """
        Save extracted keywords to a file (overwrites previous file)
        
        Args:
            keywords: List of keywords to save
            output_file: Output filename
        """
        try:
            output_path = os.path.join(os.path.dirname(__file__), output_file)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for keyword in keywords:
                    f.write(f"{keyword}\n")
            
            print(f"💾 Saved {len(keywords)} keywords to {output_file}")
            
        except Exception as e:
            print(f"❌ Error saving keywords: {str(e)}")


def main():
    """Test the email keyword extractor with sample data"""
    
    # Sample email data for testing
    sample_emails = [
        {
            'subject': 'Interview Invitation for JUTEQ Internship Program',
            'sender': 'hr@juteq.com',
            'body': 'We are excited to invite you to interview for our internship position at JUTEQ...'
        },
        {
            'subject': '🌱 SEEDS Internship Interview Invitation – Let\'s Chat!',
            'sender': 'Olivve Log <olivvelog@gmail.com>',
            'body': 'Hello Seedling, We\'re so excited that you\'ve taken the time to apply for the Dandilyonn SEEDS Internship Program...'
        }
    ]
    
    extractor = EmailKeywordExtractor()
    
    print("🔍 Testing Email Keyword Extraction")
    print("=" * 50)
    
    for i, email in enumerate(sample_emails, 1):
        keyword = extractor.extract_keyword_from_email(email)
        print(f"Email {i}: '{email['subject'][:50]}...'")
        print(f"Keyword: {keyword}")
        print("-" * 30)
    
    # Test batch extraction
    keywords = extractor.extract_keywords_from_emails(sample_emails)
    print(f"Batch keywords: {keywords}")
    
    # Save to file
    extractor.save_keywords_to_file(keywords)


if __name__ == "__main__":
    main()
