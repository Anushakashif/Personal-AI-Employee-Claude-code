"""
Gmail Watcher for AI Employee Vault

Monitors Gmail inbox for unread important emails every 2 minutes.
Creates files in Needs_Action/ folder for processing by the orchestrator.

Requirements:
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

Setup:
    1. Enable Gmail API at https://console.cloud.google.com/apis/library/gmail.googleapis.com
    2. Download credentials.json to the project root
    3. First run will open browser for OAuth authorization
"""

import os
import time
import traceback
import base64
from datetime import datetime
from pathlib import Path
from email import message_from_bytes

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Polling interval in seconds
POLL_INTERVAL = 120  # 2 minutes

# Directory configuration
BASE_DIR = Path.cwd()
NEEDS_ACTION_DIR = BASE_DIR / "Needs_Action"
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


class GmailWatcher:
    def __init__(self):
        self.service = None
        self.processed_emails = set()
        self.needs_action_dir = NEEDS_ACTION_DIR
        
        # Ensure Needs_Action directory exists
        self.needs_action_dir.mkdir(parents=True, exist_ok=True)
        
        # Track seen message IDs to avoid duplicates
        self.seen_message_ids = set()

    def authenticate(self):
        """Authenticate with Gmail API and build the service."""
        creds = None
        
        # Load existing token if available
        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        
        # Refresh or obtain new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"[GMAIL] Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                if not CREDENTIALS_FILE.exists():
                    print(f"[GMAIL ERROR] credentials.json not found at {CREDENTIALS_FILE}")
                    print("Please download credentials.json from Google Cloud Console.")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(CREDENTIALS_FILE), SCOPES
                    )
                    creds = flow.run_local_server(port=0, open_browser=True)
                    
                    # Save credentials for future use
                    with open(TOKEN_FILE, "w") as token:
                        token.write(creds.to_json())
                    print("[GMAIL] Authentication successful. Token saved.")
                except Exception as e:
                    print(f"[GMAIL ERROR] Authentication failed: {e}")
                    return False
        
        # Build the Gmail API service
        try:
            self.service = build("gmail", "v1", credentials=creds)
            print("[GMAIL] Service initialized successfully.")
            return True
        except Exception as e:
            print(f"[GMAIL ERROR] Failed to build service: {e}")
            return False

    def decode_message(self, message_data):
        """Decode Gmail message parts."""
        try:
            msg_bytes = base64.urlsafe_b64decode(message_data["raw"])
            msg = message_from_bytes(msg_bytes)
            
            subject = ""
            from_email = ""
            snippet = message_data.get("snippet", "")
            
            # Extract headers
            headers = msg.get("headers", [])
            if isinstance(headers, list):
                for header in headers:
                    name = header.get("name", "")
                    value = header.get("value", "")
                    if name.lower() == "subject":
                        subject = value
                    elif name.lower() == "from":
                        from_email = value
            
            # Try to get body content
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body = part.get_payload(decode=True).decode()
                            break
                        except:
                            pass
            else:
                try:
                    body = msg.get_payload(decode=True).decode()
                except:
                    pass
            
            return {
                "subject": subject,
                "from": from_email,
                "snippet": snippet,
                "body": body[:500] if body else snippet  # Limit body length
            }
        except Exception as e:
            print(f"[GMAIL] Error decoding message: {e}")
            return {
                "subject": "Error decoding subject",
                "from": "Unknown",
                "snippet": "Error decoding message",
                "body": ""
            }

    def get_unread_emails(self, max_results=10):
        """Fetch unread emails from Gmail."""
        if not self.service:
            return []
        
        try:
            # Search for unread emails
            results = self.service.users().messages().list(
                userId="me",
                q="is:unread",
                maxResults=max_results
            ).execute()
            
            messages = results.get("messages", [])
            return messages
        except HttpError as error:
            print(f"[GMAIL ERROR] API error: {error}")
            return []
        except Exception as e:
            print(f"[GMAIL ERROR] Error fetching emails: {e}")
            return []

    def get_message_details(self, message_id):
        """Get full message details from Gmail."""
        if not self.service:
            return None
        
        try:
            message = self.service.users().messages().get(
                userId="me",
                id=message_id,
                format="raw"
            ).execute()
            return message
        except Exception as e:
            print(f"[GMAIL ERROR] Error fetching message {message_id}: {e}")
            return None

    def determine_priority(self, subject, from_email, snippet):
        """Determine email priority based on content."""
        priority_keywords = ["urgent", "important", "asap", "priority", "action required"]
        action_keywords = ["review", "approve", "respond", "meeting", "deadline", "task", "please"]
        
        text = f"{subject} {from_email} {snippet}".lower()
        
        priority = "normal"
        suggested_actions = []
        
        # Check for priority indicators
        for keyword in priority_keywords:
            if keyword in text:
                priority = "high"
                break
        
        # Determine suggested actions
        if "meeting" in text:
            suggested_actions.append("Respond to meeting request")
        if "review" in text or "approve" in text:
            suggested_actions.append("Review and provide feedback")
        if "deadline" in text or "asap" in text:
            suggested_actions.append("Handle with urgency")
        if "task" in text or "please" in text:
            suggested_actions.append("Complete requested task")
        
        if not suggested_actions:
            suggested_actions.append("Read and respond appropriately")
        
        return priority, suggested_actions

    def create_needs_action_file(self, email_data):
        """Create a file in Needs_Action folder for the email."""
        try:
            email_id = email_data["id"]
            filename = f"EMAIL_{email_id}.md"
            file_path = self.needs_action_dir / filename
            
            # Create metadata filename
            metadata_filename = f"EMAIL_{email_id}_metadata.md"
            metadata_path = self.needs_action_dir / metadata_filename
            
            # Determine priority and actions
            priority, suggested_actions = self.determine_priority(
                email_data["subject"],
                email_data["from"],
                email_data["snippet"]
            )
            
            # Create main email file
            content = f"""From : {email_data["from"]}
Subject : {email_data["subject"]}
Priority : {priority}
Message : {email_data["snippet"]}

---
Suggested Actions:
{chr(10).join(f'- {action}' for action in suggested_actions)}

---
Full Content:
{email_data["body"]}
"""
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Create metadata file
            metadata_content = f"""---
type: gmail_email
email_id: "{email_id}"
thread_id: "{email_data.get("threadId", "")}"
from: "{email_data["from"]}"
subject: "{email_data["subject"]}"
received_at: "{email_data["received_at"]}"
priority: "{priority}"
snippet: "{email_data["snippet"]}"
---

# Gmail Email Metadata

- **Email ID:** {email_id}
- **Thread ID:** {email_data.get("threadId", "")}
- **From:** {email_data["from"]}
- **Subject:** {email_data["subject"]}
- **Received:** {email_data["received_at"]}
- **Priority:** {priority}
- **Snippet:** {email_data["snippet"]}

## Suggested Actions
{chr(10).join(f'- {action}' for action in suggested_actions)}
"""
            
            with open(metadata_path, "w", encoding="utf-8") as f:
                f.write(metadata_content)
            
            print(f"[GMAIL] Created Needs_Action file: {filename}")
            return True
            
        except Exception as e:
            print(f"[GMAIL ERROR] Error creating file: {e}")
            print(traceback.format_exc())
            return False

    def check_emails(self):
        """Check for new unread emails and create Needs_Action files."""
        if not self.service:
            return
        
        print(f"[GMAIL] Checking for unread emails...")
        
        messages = self.get_unread_emails(max_results=10)
        
        if not messages:
            print("[GMAIL] No unread emails found.")
            return
        
        new_emails_count = 0
        for message in messages:
            msg_id = message["id"]
            
            # Skip already processed emails
            if msg_id in self.seen_message_ids:
                continue
            
            # Get full message details
            msg_data = self.get_message_details(msg_id)
            if not msg_data:
                continue
            
            # Decode message content
            decoded = self.decode_message(msg_data)
            
            # Prepare email data
            email_data = {
                "id": msg_id,
                "threadId": msg_data.get("threadId", ""),
                "from": decoded["from"],
                "subject": decoded["subject"],
                "snippet": decoded["snippet"],
                "body": decoded["body"],
                "received_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Create Needs_Action file
            if self.create_needs_action_file(email_data):
                self.seen_message_ids.add(msg_id)
                new_emails_count += 1
        
        if new_emails_count > 0:
            print(f"[GMAIL] Processed {new_emails_count} new email(s).")
        else:
            print("[GMAIL] No new emails to process.")

    def run(self):
        """Main watcher loop."""
        print("=" * 60)
        print("Gmail Watcher for AI Employee Vault")
        print("=" * 60)
        print(f"Poll interval: {POLL_INTERVAL} seconds ({POLL_INTERVAL // 60} minutes)")
        print(f"Needs_Action directory: {self.needs_action_dir}")
        print("Press Ctrl+C to stop.")
        print("=" * 60)
        
        # Authenticate
        if not self.authenticate():
            print("[GMAIL] Failed to authenticate. Exiting.")
            return
        
        # Initial check
        self.check_emails()
        
        # Main polling loop
        try:
            while True:
                time.sleep(POLL_INTERVAL)
                self.check_emails()
        except KeyboardInterrupt:
            print("\n\n[GMAIL] Gmail watcher stopped by user.")


def main():
    watcher = GmailWatcher()
    watcher.run()


if __name__ == "__main__":
    main()
