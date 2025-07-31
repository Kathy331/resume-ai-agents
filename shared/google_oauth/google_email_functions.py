### shared/google_oauth/google_email_functions.py
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from shared.google_oauth.google_apis_start import create_service
### (B-Email Functions)

### READING EMAILS
def init_gmail_service(client_file, api_name='gmail', api_version='v1', scopes=['https://mail.google.com/']):
    return create_service(client_file, api_name, api_version, scopes)

def extract_body(payload):
    body = '<Text body not found>'
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'multipart/alternative':
                for subpart in part['parts']:
                    if subpart['mimeType'] == 'text/plain' and 'data' in subpart['body']:
                        body = base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8')
                        break
            elif part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    return body

def get_email_messages(service, user_id='me', label_ids=None, folder_name='INBOX', max_results=5):
    messages = []
    next_page_token = None

    if folder_name:
        label_results = service.users().labels().list(userId=user_id).execute()
        labels = label_results.get('labels', [])
        folder_label_id = next((label['id'] for label in labels if (label['name']).lower() == folder_name.lower()), None)
        if folder_label_id:
            if label_ids:
                label_ids.append(folder_label_id)
            else:
                label_ids = [folder_label_id]
        else:
            raise ValueError(f"Folder '{folder_name}' not found in labels.")
        
    while True:
        response = service.users().messages().list(
            userId=user_id,
            labelIds=label_ids,
            pageToken=next_page_token,
            maxResults=min(500, max_results - len(messages)) if max_results else 500
        ).execute()

        messages.extend(response.get('messages', []))

        next_page_token = response.get('nextPageToken')

        if not next_page_token or (max_results and len(messages) >= max_results):
            break

    return messages[:max_results] if max_results else messages

def get_email_message_details(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = message['payload']
    headers = payload.get('headers', [])
    # headers = {header['name']: header['value'] for header in message['payload']['headers']}
    # body = extract_body(message['payload'])

    subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), None)
    if not subject:
        subject = message.get('subject', 'No subject')

    sender = next((header['value'] for header in headers if header['name'] == 'From'), 'No sender')
    recipients = next((header['value'] for header in headers if header['name'] == 'To'), 'No recipients')
    snippet = message.get('snippet', 'No snippet')
    has_attachments = any(part.get('filename') for part in payload.get('parts', []) if part.get('filename'))
    date = next((header['value'] for header in headers if header['name'] == 'Date'), 'No date') 
    star = message.get('labelIds', []).count('STARRED') > 0
    label = ', '.join(message.get('labelIds', [])) # not sure how to get label name, so just return label IDs

    body = extract_body(payload)

    return {
        'id': msg_id,
        'subject': subject,
        'sender': sender,
        'recipients': recipients,
        'body': body,
        'snippet': snippet,
        'has_attachments': has_attachments,
        'date': date,
        'star': star,
        'label': label
    }

def download_attachments_parent(service, user_id, msg_id, target_dir):
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    for part in message['payload']['parts']:
        if part['filename']:
            att_id = part['body']['attachmentId']
            att = service.users().messages().attachments().get(
                userId=user_id, messageId=msg_id, id=att_id).execute()
            data = att['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            file_path = os.path.join(target_dir, part['filename'])
            print('Saving attachment to: ', file_path)
            with open(file_path, 'wb') as f:
                f.write(file_data)

def download_attachments_all(service, user_id, msg_id, target_dir):
    thread = service.users().threads().get(userId=user_id, id=msg_id).execute()
    for message in thread['messages']:
        for part in message['payload']['parts']:
            if part['filename']:
                att_id = part['body']['attachmentId']
                att = service.users().messages().attachments().get(
                    userId=user_id, messageId=message['id'], id=att_id).execute()
                data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                file_path = os.path.join(target_dir, part['filename'])
                print('Saving attachment to: ', file_path)
                with open(file_path, 'wb') as f:
                    f.write(file_data)

### READING ALL THE LABELS SOMEONE HAS
def list_labels(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    # return [label['name'] for label in labels] will return a list of label names
    return labels

### CREATING AND SENDING DRAFT EMAILS
def list_draft_email_messages(service, user_id='me', max_results=5):
    drafts = []
    next_page_token = None

    while True:
        response = service.users().drafts().list(
            userId=user_id,
            pageToken=next_page_token,
            maxResults=min(500, max_results - len(drafts)) if max_results else 500
        ).execute()

        drafts.extend(response.get('drafts', []))

        next_page_token = response.get('nextPageToken')

        if not next_page_token or (max_results and len(drafts) >= max_results):
            break

    return drafts[:max_results] if max_results else drafts

# body types & attachments are optional
def create_draft_email(service, to, subject, body, body_type='plain', attachment_paths=None):
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject

    if body_type.lower() not in ['plain', 'html']:
        raise ValueError("body_type must be either 'plain' or 'html'")
    
    message.attach(MIMEText(body, body_type.lower()))

    if attachment_paths:
        for attachment_path in attachment_paths:
            if os.path.exists(attachment_path):
                filename = os.path.basename(attachment_path)

                with open(attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)

                part.add_header(
                    'Content-Disposition',
                    f"attachment; filename={filename}"
                )

                message.attach(part)
            else:
                raise FileNotFoundError(f"File not found: {attachment_path}")
            
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    draft = service.users().drafts().create(
        userId='me',
        body={'message': {'raw': raw_message}}
    ).execute()

    return draft

def get_draft_email_details(service, draft_id, format='full'):
    draft_details = service.users().drafts().get(userId='me', id=draft_id, format=format).execute()
    draft_id = draft_details['id']
    draft_message = draft_details['message']
    draft_payload = draft_message['payload']
    headers = draft_payload.get('headers', [])
    subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No subject')
    sender = next((header['value'] for header in headers if header['name'] == 'From'), 'No sender')
    recipients = next((header['value'] for header in headers if header['name'] == 'To'), 'No recipients')
    snippet = draft_message.get('snippet', 'No snippet')
    has_attachments = any(part.get('filename') for part in draft_payload.get('parts', []) if part.get('filename'))
    date = next((header['value'] for header in headers if header['name'] == 'Date'), 'No date')
    star = draft_message.get('labelIds', []).count('STARRED') > 0
    label = ', '.join(draft_message.get('labelIds', []))

    body = '<Text body not found>'
    if 'parts' in draft_payload:
        for part in draft_payload['parts']:
            if part['mimeType'] == 'multipart/alternative':
                for subpart in part['parts']:
                    if subpart['mimeType'] == 'text/plain' and 'data' in subpart['body']:
                        body = base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8')
                        break
            elif part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break

    return {
        'subject': subject,
        'sender': sender,
        'recipients': recipients,
        'body': body,
        'snippet': snippet,
        'has_attachments': has_attachments,
        'date': date,
        'star': star,
        'label': label,
    }

def send_draft_email(service, draft_id):
    draft = service.users().drafts().send(userId='me', body={'id': draft_id}).execute()
    return draft

def delete_draft_email(service, draft_id):
    service.users().drafts().delete(userId='me', id=draft_id).execute()

### READ A SPECIFIC EMAIL THREAD
# This is for one message and all its replies in the same thread
def get_message_and_replies(service, message_id):
    message = service.users().messages().get(userId='me',id=message_id, format='minimal').execute()
    thread_id = message['threadId']
    thread = service.users().threads().get(userId='me', id=thread_id).execute()

    processed_messages = []
    for msg in thread['messages']:
        subject = next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'), 'No subject')
        from_header = next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'From'), 'No sender')
        date = next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'Date'), 'No date')

        content = extract_body(msg['payload'])

        processed_messages.append({
            'id': msg['id'],
            'subject': subject,
            'from': from_header,
            'date': date,
            'content': content
        })

        return processed_messages