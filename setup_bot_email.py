#!/usr/bin/env python3
"""
Dual Gmail Authentication Setup
==============================
This script sets up Gmail authentication for both:
1. User Gmail account (for reading emails)  
2. Bot Gmail account (Inkyhelps@gmail.com for sending emails)

This allows users to authenticate with their own Gmail while the bot sends from a dedicated account.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from shared.google_oauth.google_apis_start import create_service

def setup_user_email():
    """Set up Gmail authentication for user's personal Gmail account"""
    print("👤 Setting up User Email Authentication")
    print("=" * 50)
    
    try:
        # Get credentials file path
        credentials_path = 'shared/google_oauth/client_secret.json'
        
        if not os.path.exists(credentials_path):
            print(f"❌ Credentials file not found: {credentials_path}")
            return False, None
            
        print(f"✅ Found credentials file: {credentials_path}")
        
        # Create Gmail service with read permissions for user
        print("🔄 Authenticating User Gmail API...")
        print("📧 Please authenticate with YOUR Gmail account when browser opens...")
        
        service = create_service(
            credentials_path,
            'gmail', 
            'v1', 
            ['https://www.googleapis.com/auth/gmail.readonly'],
            prefix='_user'  # This creates token_gmail_v1_user.json
        )
        
        if service:
            print("✅ User Gmail service created successfully!")
            
            # Test the service by getting user profile
            try:
                profile = service.users().getProfile(userId='me').execute()
                email_address = profile.get('emailAddress', 'Unknown')
                print(f"📧 User authenticated email: {email_address}")
                return True, email_address
                    
            except Exception as e:
                print(f"❌ Error getting profile: {e}")
                return False, None
                
        else:
            print("❌ Failed to create User Gmail service")
            return False, None
            
    except Exception as e:
        print(f"❌ Error during user setup: {e}")
        return False, None

def setup_bot_email():
    """Set up Gmail authentication for the bot email account (Inkyhelps@gmail.com)"""
    print("\n🤖 Setting up Bot Email Authentication")
    print("=" * 50)
    
    try:
        # Get credentials file path
        credentials_path = 'shared/google_oauth/client_secret.json'
        
        if not os.path.exists(credentials_path):
            print(f"❌ Credentials file not found: {credentials_path}")
            return False, None
            
        print(f"✅ Found credentials file: {credentials_path}")
        
        # Create Gmail service with send permissions for bot
        print("🔄 Authenticating Bot Gmail API...")
        print("🤖 Please authenticate with INKYHELPS@GMAIL.COM when browser opens...")
        
        service = create_service(
            credentials_path,
            'gmail', 
            'v1', 
            ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly'],
            prefix='_bot'  # This creates token_gmail_v1_bot.json
        )
        
        if service:
            print("✅ Bot Gmail service created successfully!")
            
            # Test the service by getting user profile
            try:
                profile = service.users().getProfile(userId='me').execute()
                email_address = profile.get('emailAddress', 'Unknown')
                print(f"📧 Bot authenticated email: {email_address}")
                
                if 'inkyhelps@gmail.com' in email_address.lower():
                    print("✅ Bot email authenticated successfully!")
                    return True, email_address
                else:
                    print(f"⚠️  Warning: Expected inkyhelps@gmail.com but got {email_address}")
                    print("ℹ️  Please make sure you authenticate with the correct Bot account")
                    return True, email_address  # Still functional, just different account
                    
            except Exception as e:
                print(f"❌ Error getting bot profile: {e}")
                return False, None
                
        else:
            print("❌ Failed to create Bot Gmail service")
            return False, None
            
    except Exception as e:
        print(f"❌ Error during bot setup: {e}")
        return False, None

def check_existing_tokens():
    """Check what tokens already exist"""
    print("🔍 Checking existing authentication tokens...")
    print("=" * 50)
    
    token_dir = 'token_files'
    tokens_found = []
    
    if os.path.exists(token_dir):
        for file in os.listdir(token_dir):
            if file.startswith('token_gmail_v1'):
                tokens_found.append(file)
                print(f"✅ Found: {file}")
    
    if not tokens_found:
        print("📭 No Gmail tokens found")
    
    return tokens_found

def clean_bot_token():
    """Remove existing bot token to force re-authentication with new scopes"""
    token_file = 'token_files/token_gmail_v1_bot.json'
    if os.path.exists(token_file):
        os.remove(token_file)
        print(f"🧹 Removed existing bot token: {token_file}")
        print("ℹ️  This will force re-authentication with expanded scopes")
        return True
    else:
        print("📭 No existing bot token found")
        return False

def clean_user_token():
    """Remove existing user token to force re-authentication with different account"""
    token_file = 'token_files/token_gmail_v1_user.json'
    if os.path.exists(token_file):
        os.remove(token_file)
        print(f"🧹 Removed existing user token: {token_file}")
        print("ℹ️  This will force re-authentication with your personal Gmail account")
        return True
    else:
        print("📭 No existing user token found")
        return False

def main():
    """Main setup function"""
    print("🚀 DUAL GMAIL AUTHENTICATION SETUP")
    print("=" * 60)
    print("This will set up authentication for:")
    print("👤 1. User Gmail (for reading emails)")
    print("🤖 2. Bot Gmail (Inkyhelps@gmail.com for sending)")
    print("=" * 60)
    
    # Check existing tokens
    existing_tokens = check_existing_tokens()
    
    print("\nChoose setup option:")
    print("1. Setup User Gmail Authentication")
    print("2. Setup Bot Gmail Authentication") 
    print("3. Setup Both (Full Setup)")
    print("4. Check Current Authentication Status")
    print("5. Clean Bot Token (Force Re-authentication)")
    print("6. Clean User Token (Force Re-authentication)")
    
    try:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            success, email = setup_user_email()
            if success:
                print(f"\n🎉 User authentication completed! ({email})")
            else:
                print("\n❌ User authentication failed!")
                
        elif choice == '2':
            success, email = setup_bot_email()
            if success:
                print(f"\n🎉 Bot authentication completed! ({email})")
            else:
                print("\n❌ Bot authentication failed!")
                
        elif choice == '3':
            print("\n🚀 Starting Full Setup...")
            
            # Setup user first
            user_success, user_email = setup_user_email()
            
            # Setup bot second
            bot_success, bot_email = setup_bot_email()
            
            print("\n" + "=" * 60)
            print("📊 SETUP SUMMARY")
            print("=" * 60)
            print(f"👤 User Gmail: {'✅ ' + user_email if user_success else '❌ Failed'}")
            print(f"🤖 Bot Gmail: {'✅ ' + bot_email if bot_success else '❌ Failed'}")
            
            if user_success and bot_success:
                print("\n🎉 Full setup completed successfully!")
                print("💡 You can now use both user email reading and bot email sending!")
            else:
                print("\n⚠️ Partial setup completed. Some authentication may need retry.")
                
        elif choice == '4':
            # Check authentication status
            print("\n🔍 Checking Authentication Status...")
            
            # Try to create services and check
            try:
                # Check user service
                user_service = create_service(
                    'shared/google_oauth/client_secret.json',
                    'gmail', 'v1', 
                    ['https://www.googleapis.com/auth/gmail.readonly'],
                    prefix='_user'
                )
                if user_service:
                    user_profile = user_service.users().getProfile(userId='me').execute()
                    user_email = user_profile.get('emailAddress', 'Unknown')
                    print(f"👤 User Gmail: ✅ {user_email}")
                else:
                    print("👤 User Gmail: ❌ Not authenticated")
            except:
                print("👤 User Gmail: ❌ Not authenticated")
            
            try:
                # Check bot service  
                bot_service = create_service(
                    'shared/google_oauth/client_secret.json',
                    'gmail', 'v1',
                    ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly'],
                    prefix='_bot'
                )
                if bot_service:
                    bot_profile = bot_service.users().getProfile(userId='me').execute()
                    bot_email = bot_profile.get('emailAddress', 'Unknown')
                    print(f"🤖 Bot Gmail: ✅ {bot_email}")
                else:
                    print("🤖 Bot Gmail: ❌ Not authenticated")
            except:
                print("🤖 Bot Gmail: ❌ Not authenticated")
        
        elif choice == '5':
            # Clean bot token
            print("\n🧹 Cleaning Bot Token...")
            cleaned = clean_bot_token()
            if cleaned:
                print("✅ Bot token cleaned successfully!")
                print("💡 Now run option 2 to re-authenticate bot with expanded scopes")
            else:
                print("ℹ️  No bot token to clean")
        
        elif choice == '6':
            # Clean user token
            print("\n🧹 Cleaning User Token...")
            cleaned = clean_user_token()
            if cleaned:
                print("✅ User token cleaned successfully!")
                print("💡 Now run option 1 to authenticate with your personal Gmail account")
                print("📧 Make sure to authenticate with YOUR Gmail, not the bot account")
            else:
                print("ℹ️  No user token to clean")
        
        else:
            print("❌ Invalid choice!")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")

if __name__ == "__main__":
    main()
