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





# temporary code for email pipeline workflow
from shared.google_oauth.google_email_setup import get_gmail_service
from shared.google_oauth.google_email_functions import get_email_messages, get_email_message_details

# Fetches and parses emails from a Gmail folder
def fetch_and_parse_emails(service, folder_name, max_results=10):
    raw_emails = get_email_messages(service, folder_name=folder_name, max_results=max_results)
    emails = [get_email_message_details(service, msg['id']) for msg in raw_emails]
    return emails

# Simple keyword-based classifier for email categorization
def simple_keyword_classifier(emails):
    classified = {
        'Personal_sent': [],
        'Interview_invite': [],
        'Others': []
    }

    for email in emails:
        subject = email.get('subject', '').lower()
        sender = email.get('sender', '').lower()

        # Customize keywords as needed
        if 'interview' in subject or 'invitation' in subject:
            classified['Interview_invite'].append(email)
        elif 'dinner' in subject or 'plans' in subject or 'from kathy' in subject:
            classified['Personal_sent'].append(email)
        else:
            classified['Others'].append(email)

    return classified

# Classifies and routes emails using the simple keyword classifier
def classify_and_route_emails(emails):
    classified = simple_keyword_classifier(emails)
    route_emails(classified)

# Prints routed email summaries
def route_emails(classified_emails):
    personal = classified_emails.get('Personal_sent', [])
    invites = classified_emails.get('Interview_invite', [])
    others = classified_emails.get('Others', [])

    for email in invites:
        print(f"📬 Interview invite: {email['subject']} from {email['sender']}")
    for email in personal:
        print(f"👤 Personal: {email['subject']} from {email['sender']}")
    for email in others:
        print(f"📎 Other: {email['subject']} from {email['sender']}")

# Entrypoint for running the full pipeline — folder_name is required
def email_pipeline(folder_name, max_results=10):
    if not folder_name:
        raise ValueError("folder_name argument is required and cannot be empty.")
    service = get_gmail_service()
    emails = fetch_and_parse_emails(service, folder_name=folder_name, max_results=max_results)
    classify_and_route_emails(emails)


# Example usage (if you want to test locally):
# if __name__ == "__main__":
#     email_pipeline(folder_name='test')