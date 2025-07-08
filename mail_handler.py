# -*- coding: utf-8 -*-
"""
Mail handler module: Fetch new emails, parse parameters, send replies.
"""
import os
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import mailparser
from config import GMAIL_ADDRESS
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Authenticate and get Gmail service object
def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# Fetch new (unread) emails, return body parameters and image path
def fetch_new_emails():
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()
        raw = base64.urlsafe_b64decode(msg_data['raw'].encode('ASCII')) if 'raw' in msg_data else None
        if raw:
            mail = mailparser.parse_from_bytes(raw)
            print("DEBUG: mail.from_ =", mail.from_)
            print("DEBUG: mail.headers =", mail.headers)
            params = parse_token_params(mail.body)
            image_path = None
            for att in mail.attachments:
                if att['mail_content_type'].startswith('image/'):
                    ext = att['mail_content_type'].split('/')[-1]
                    image_path = f"tmp_{msg['id']}.{ext}"
                    with open(image_path, 'wb') as f:
                        payload = att['payload']
                        if isinstance(payload, str):
                            try:
                                payload = base64.b64decode(payload)
                            except Exception:
                                payload = payload.encode('utf-8')
                        f.write(payload)
                    break
            emails.append({'id': msg['id'], 'from': mail.from_[0][1], 'params': params, 'image_path': image_path})
            # Mark as read
            service.users().messages().modify(userId='me', id=msg['id'], body={'removeLabelIds': ['UNREAD']}).execute()
    return emails

# Parse email body, only extract name and ticker
def parse_token_params(body):
    params = {}
    for line in body.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if key in ['name', 'ticker']:
                params[key] = value
    if 'name' in params and 'ticker' in params:
        return params
    return None

# Send email reply
def send_reply(to_email, content):
    service = get_gmail_service()
    message = MIMEText(content, "plain", "utf-8")
    message['to'] = to_email
    message['from'] = GMAIL_ADDRESS
    message['subject'] = "Pump.fun Token Creation Result Notification"
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw}
    service.users().messages().send(userId='me', body=body).execute() 