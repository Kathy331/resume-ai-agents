"""
Dual Gmail Services
===================
This module provides separate Gmail services for user and bot authentication.
- User service: For reading emails from user's Gmail account
- Bot service: For sending emails from the bot account (Inkyhelps@gmail.com)
"""

import os
from pathlib import Path
from .google_apis_start import create_service

class DualGmailServices:
    """Manages separate Gmail services for user and bot operations"""
    
    def __init__(self, credentials_path='shared/google_oauth/client_secret.json'):
        self.credentials_path = credentials_path
        self._user_service = None
        self._bot_service = None
    
    def get_user_service(self):
        """Get Gmail service for user email reading"""
        if self._user_service is None:
            print("🔄 Creating user Gmail service...")
            self._user_service = create_service(
                self.credentials_path,
                'gmail',
                'v1',
                ['https://www.googleapis.com/auth/gmail.readonly'],
                prefix='_user'
            )
            
            if self._user_service:
                print("✅ User Gmail service ready")
            else:
                print("❌ Failed to create user Gmail service")
                
        return self._user_service
    
    def get_bot_service(self):
        """Get Gmail service for bot email sending"""
        if self._bot_service is None:
            print("🔄 Creating bot Gmail service...")
            self._bot_service = create_service(
                self.credentials_path,
                'gmail',
                'v1',
                ['https://www.googleapis.com/auth/gmail.send'],
                prefix='_bot'
            )
            
            if self._bot_service:
                print("✅ Bot Gmail service ready")
            else:
                print("❌ Failed to create bot Gmail service")
                
        return self._bot_service
    
    def get_user_email(self):
        """Get the authenticated user's email address"""
        service = self.get_user_service()
        if service:
            try:
                profile = service.users().getProfile(userId='me').execute()
                return profile.get('emailAddress', 'Unknown')
            except Exception as e:
                print(f"❌ Error getting user email: {e}")
                return None
        return None
    
    def get_bot_email(self):
        """Get the authenticated bot's email address"""
        service = self.get_bot_service()
        if service:
            try:
                profile = service.users().getProfile(userId='me').execute()
                return profile.get('emailAddress', 'Unknown')
            except Exception as e:
                print(f"❌ Error getting bot email: {e}")
                return None
        return None
    
    def is_user_authenticated(self):
        """Check if user Gmail is authenticated"""
        token_path = Path('token_files/token_gmail_v1_user.json')
        return token_path.exists() and self.get_user_service() is not None
    
    def is_bot_authenticated(self):
        """Check if bot Gmail is authenticated"""
        token_path = Path('token_files/token_gmail_v1_bot.json')
        return token_path.exists() and self.get_bot_service() is not None
    
    def check_authentication_status(self):
        """Check authentication status for both user and bot"""
        status = {
            'user_authenticated': False,
            'bot_authenticated': False,
            'user_email': None,
            'bot_email': None
        }
        
        # Check user authentication
        if self.is_user_authenticated():
            status['user_authenticated'] = True
            status['user_email'] = self.get_user_email()
        
        # Check bot authentication
        if self.is_bot_authenticated():
            status['bot_authenticated'] = True
            status['bot_email'] = self.get_bot_email()
        
        return status

# Global instance for easy access
gmail_services = DualGmailServices()

# Convenience functions
def get_user_gmail_service():
    """Get the user Gmail service"""
    return gmail_services.get_user_service()

def get_bot_gmail_service():
    """Get the bot Gmail service"""
    return gmail_services.get_bot_service()

def check_gmail_authentication():
    """Check authentication status for both services"""
    return gmail_services.check_authentication_status()
