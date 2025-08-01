# shared/google_oauth/google_email_playground.py
from shared.google_oauth.google_email_functions import (
    init_gmail_service, create_draft_email, list_draft_email_messages,
    get_draft_email_details, send_draft_email, get_email_messages, get_email_message_details
)
# pressing the "run python file" button doesn't work for me, so
# I just changed the imports. Now to run this file, you have to run this:
# python -m shared.google_oauth.google_email_playground

### (C-Testing Emails)
### THIS FILE IS CONNECTED TO google_api_all_functions.py
### (maybe I can make this the main function for google_api_read.py?)
### NEED TO RUN google_email_setup.py FIRST AND THEN YOU CAN USE THIS FILE (this is basically testing the functions lol)
client_file = 'client_secret.json'
service = init_gmail_service(client_file)

# the folder name here determines which label to read emails from
messages = get_email_messages(service, folder_name='test', max_results=10)
for msg in messages:
    details = get_email_message_details(service, msg['id'])
    if details:
        print(f"Message ID: {msg['id']}")
        print(f"Subject: {details['subject']}")
        print(f"From: {details['sender']}")
        print(f"Recipients: {details['recipients']}")
        print(f"Body: {details['body'][:100]}...")  # Print first 100 characters of body
        print(f"Snippet: {details['snippet']}")
        print(f"Has Attachments: {details['has_attachments']}")
        print(f"Date: {details['date']}")
        print(f"Star: {details['star']}")
        print(f"Label: {details['label']}")
        print('-' * 50)

# CREATING A DRAFT EMAIL
to_address = 'liveinthemoment780@gmail.com'
email_subject = 'Test Email from Grace'
email_body = 'This is a test email sent using the Gmail API!!! First it was draft, then I send it...'
response = create_draft_email(
    service, to_address, email_subject, email_body
)
print(response)

# SENDING ALL DRAFT EMAILS
drafts = list_draft_email_messages(service)
for draft in drafts:
    draft_message_detail = get_draft_email_details(service, draft['id'])
    send_draft_email(service, draft['id'])
    print(f'Draft email: {draft_message_detail["subject"]} sent successfully!')

# SENDING ONE DRAFT EMAIL
send_draft_email(service, 'r-3249868396202777246')  # draft id is found from before

# GET SPECIFIC EMAIL DETAILS
email_id = '198587a3f3fe94fb'  # replace with a valid email ID
email_details = get_email_message_details(service, email_id)
if email_details:
    print(f"Message ID: {email_details['id']}")
    print(f"Subject: {email_details['subject']}")
    print(f"From: {email_details['sender']}")
    print(f"Recipients: {email_details['recipients']}")
    print(f"Body: {email_details['body'][:100]}...")  # Print first 100 characters of body
    print(f"Snippet: {email_details['snippet']}")
    print(f"Has Attachments: {email_details['has_attachments']}")
    print(f"Date: {email_details['date']}")
    print(f"Star: {email_details['star']}")
    print(f"Label: {email_details['label']}")
    print('-' * 50)
else:
    print(f"No details found for Email ID {email_id}")