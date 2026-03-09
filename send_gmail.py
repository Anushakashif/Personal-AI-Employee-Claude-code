#!/usr/bin/env python3
"""
Send Approved Email via Gmail

Usage:
    python send_gmail.py

This script:
1. Checks Approved/ folder for email draft files
2. Sends each email via Gmail API
3. Moves sent emails to Done/ folder
4. Updates Dashboard.md
"""

import base64
from email.message import EmailMessage
from pathlib import Path
import re
from datetime import datetime

# Gmail API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying scopes, delete token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_FILE = Path("token.json")
CREDENTIALS_FILE = Path("credentials.json")

APPROVED_DIR = Path("./Approved")
DONE_DIR = Path("./Done")

def get_gmail_service():
    """Authenticate and build Gmail service."""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def send_email(to: str, subject: str, body: str) -> dict:
    """Send email via Gmail API."""
    try:
        service = get_gmail_service()
        
        message = EmailMessage()
        message['To'] = to
        message['Subject'] = subject
        message.set_content(body)
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': encoded_message}
        
        sent_message = service.users().messages().send(userId='me', body=body).execute()
        return {'success': True, 'message_id': sent_message['id']}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

def process_approved_emails():
    """Find and send approved email drafts."""
    
    approved_files = list(APPROVED_DIR.glob("Email_*.md"))
    if not approved_files:
        print("No approved email drafts found in Approved/ folder")
        return
    
    for approved_file in approved_files:
        content = approved_file.read_text(encoding='utf-8')
        
        # Extract email details
        to_match = re.search(r'\*\*To\*\*\s*\|\s*([^\s|]+)', content)
        subject_match = re.search(r'\*\*Subject\*\*\s*\|\s*([^\n]+)', content)
        body_match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
        
        if not all([to_match, subject_match, body_match]):
            print(f"Could not extract email details from {approved_file.name}")
            continue
        
        to_email = to_match.group(1).strip()
        subject = subject_match.group(1).strip()
        body = body_match.group(1).strip()
        
        approval_id = re.search(r'approval_id: "([^"]+)"', content)
        approval_id = approval_id.group(1) if approval_id else "UNKNOWN"
        
        print(f"\nSending: {approval_id}")
        print("-" * 50)
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body preview: {body[:80]}...")
        
        result = send_email(to_email, subject, body)
        
        if result['success']:
            print(f"✓ Email sent successfully (Message ID: {result['message_id']})")
            
            # Move to Done folder
            DONE_DIR.mkdir(exist_ok=True)
            new_name = f"Email_Sent_{to_email.split('@')[0]}_{datetime.now().strftime('%Y%m%d')}.md"
            approved_file.rename(DONE_DIR / new_name)
            print(f"✓ Moved to Done/: {new_name}")
            
            # Update Dashboard
            dashboard_file = Path("Dashboard.md")
            if dashboard_file.exists():
                dash_content = dashboard_file.read_text(encoding='utf-8')
                dash_content += f"\n- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] Email sent to {to_email}: {subject}\n"
                dashboard_file.write_text(dash_content, encoding='utf-8')
                print("✓ Dashboard updated")
        else:
            print(f"✗ Failed to send: {result.get('error')}")
            print("Check credentials.json and token.json")

if __name__ == "__main__":
    process_approved_emails()
