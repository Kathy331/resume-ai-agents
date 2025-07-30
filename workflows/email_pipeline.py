# # workflows/email_pipeline.py

# from shared.google_oauth.google_email_setup import get_gmail_service
# from shared.google_oauth.google_email_functions import get_email_messages, get_email_message_details
# # from orchestrator.decision_tree import classify_email  # Uncomment when ready

# # Fetches and parses emails from a Gmail folder
# def fetch_and_parse_emails(service, folder_name='INBOX', max_results=10):
#     raw_emails = get_email_messages(service, folder_name=folder_name, max_results=max_results)
#     emails = [get_email_message_details(service, msg['id']) for msg in raw_emails]
#     return emails

# # Classifies and routes emails
# def classify_and_route_emails(emails):
#     classified = classify_email(emails)  # You can plug in your classifier here
#     route_emails(classified)

# # Prints routed email summaries
# def route_emails(classified_emails):
#     personal = classified_emails.get('Personal_sent', [])
#     invites = classified_emails.get('Interview_invite', [])
#     others = classified_emails.get('Others', [])

#     for email in invites:
#         print(f"📬 Interview invite: {email['subject']} from {email['sender']}")
#     for email in personal:
#         print(f"👤 Personal: {email['subject']} from {email['sender']}")
#     for email in others:
#         print(f"📎 Other: {email['subject']} from {email['sender']}")

# # Entrypoint for running the full pipeline with dynamic folder name
# def email_pipeline(folder_name='INBOX', max_results=10):
#     service = get_gmail_service()
#     emails = fetch_and_parse_emails(service, folder_name=folder_name, max_results=max_results)
#     classify_and_route_emails(emails)

# #use it like this:
# from workflows.email_pipeline import email_pipeline

# email_pipeline(folder_name='Label_1234567890')  # Custom label ID from Gmail



# workflows/email_pipeline.py
# core email processing steps
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from shared.google_oauth.google_email_setup import get_gmail_service
from shared.google_oauth.google_email_functions import get_email_messages, get_email_message_details

class EmailPipelineError(Exception):
    """Custom exception for email pipeline errors"""
    pass

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

# will be replaced later with an ai classifier
def classify_emails(emails):
    """
    Pure function: emails -> classified emails
    Returns structured data, doesn't print or route
    """
    classified = {
        'Personal_sent': [],
        'Interview_invite': [],
        'Others': []
    }
    
    for email in emails:
        subject = email.get('subject', '').lower()
        sender = email.get('sender', '').lower()
        
        if 'interview' in subject or 'invitation' in subject:
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

# Core pipeline steps as individual functions
def create_gmail_service():
    """Initialize Gmail service - can be mocked for testing"""
    return get_gmail_service()
