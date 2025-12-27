# Gmail API Integration Guide - Part 2: Implementation

This guide provides detailed instructions for accessing Gmail programmatically using Python and Node.js. It covers listing messages, reading messages/threads, creating replies, sending emails, forwarding messages, and service account implementation for Google Workspace.

> **Prerequisites:** Before using this guide, complete the OAuth setup in [Part 1: OAuth Setup](./101%20-%20Gmail-API-Integration-Guide-OAuth%20part.md), which covers creating a Google Cloud project, configuring the OAuth consent screen, creating credentials, and understanding scopes.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Python Implementation](#2-python-implementation)
3. [Node.js Implementation](#3-nodejs-implementation)
4. [Common Search Query Operators](#4-common-search-query-operators)
5. [Error Handling](#5-error-handling)
6. [Service Account Implementation (Google Workspace Only)](#6-service-account-implementation-google-workspace-only)
7. [Quick Reference: API Endpoints](#quick-reference-api-endpoints)
8. [Sources](#sources)

---

## 1. Prerequisites

Before implementing Gmail API access, ensure you have completed the OAuth setup from **Part 1** of this guide:

> **Required:** Complete all steps in [Part 1: OAuth Setup](./101%20-%20Gmail-API-Integration-Guide-OAuth%20part.md) before proceeding.

### 1.1 Checklist

Verify you have completed the following:

| Step | Description | Document Reference |
|------|-------------|-------------------|
| ✅ | Created a Google Cloud project | Part 1, Section 1.1 |
| ✅ | Enabled the Gmail API | Part 1, Section 1.1 |
| ✅ | Configured the OAuth consent screen | Part 1, Section 1.2 |
| ✅ | Created OAuth 2.0 credentials | Part 1, Section 1.3 |
| ✅ | Downloaded `credentials.json` | Part 1, Section 1.3 |
| ✅ | Selected appropriate scopes | Part 1, Section 2 |

### 1.2 Required Files

Ensure you have the following file in your project directory:

```
your-project/
├── credentials.json    # OAuth 2.0 client credentials (from Part 1)
└── token.json          # Generated automatically on first authentication
```

### 1.3 Authentication Summary

For personal Gmail accounts (@gmail.com), you must use **OAuth 2.0 Client ID** authentication, which requires user consent through a browser-based flow.

For Google Workspace accounts, you have two options:
- **OAuth 2.0 Client ID** - Same as personal accounts
- **Service Account** - Server-to-server authentication with domain-wide delegation (see [Section 6](#6-service-account-implementation-google-workspace-only))

### 1.4 Security Reminders

```gitignore
# Add to .gitignore - NEVER commit these files
credentials.json
client_secret*.json
token.json
*.pickle
service-account.json
```

---

## 2. Python Implementation


### 2.1 Environment Setup

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install required packages
uv add google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2.2 Authentication Module

Create `gmail_auth.py`:

```python
"""Gmail API Authentication Module."""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define your scopes - modify based on your needs
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
]

def get_gmail_service(credentials_path: str = 'credentials.json',
                      token_path: str = 'token.json'):
    """
    Authenticate and return Gmail API service.

    Args:
        credentials_path: Path to OAuth credentials JSON file
        token_path: Path to store/retrieve access tokens

    Returns:
        Gmail API service instance

    Raises:
        FileNotFoundError: If credentials file is not found
    """
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"Credentials file not found at {credentials_path}. "
            "Download it from Google Cloud Console."
        )

    creds = None

    # Load existing token if available
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)
```

### 2.3 List Messages with Criteria

Create `gmail_list.py`:

```python
"""Gmail API - List Messages Module."""
from typing import Optional
from googleapiclient.errors import HttpError
from gmail_auth import get_gmail_service


def list_messages(
    query: str = '',
    label_ids: Optional[list] = None,
    max_results: int = 100,
    include_spam_trash: bool = False
) -> list:
    """
    List messages matching the specified criteria.

    Args:
        query: Gmail search query (same syntax as Gmail search box)
        label_ids: List of label IDs to filter by (e.g., ['INBOX', 'UNREAD'])
        max_results: Maximum number of messages to return (max 500)
        include_spam_trash: Include messages from SPAM and TRASH

    Returns:
        List of message objects with 'id' and 'threadId'

    Example queries:
        - 'from:user@example.com' - Messages from specific sender
        - 'is:unread' - Unread messages
        - 'subject:meeting' - Messages with 'meeting' in subject
        - 'after:2024/01/01 before:2024/12/31' - Date range
        - 'has:attachment' - Messages with attachments
    """
    service = get_gmail_service()
    messages = []
    page_token = None

    try:
        while True:
            # Build request parameters
            params = {
                'userId': 'me',
                'maxResults': min(max_results - len(messages), 500),
                'includeSpamTrash': include_spam_trash,
            }

            if query:
                params['q'] = query
            if label_ids:
                params['labelIds'] = label_ids
            if page_token:
                params['pageToken'] = page_token

            # Execute request
            result = service.users().messages().list(**params).execute()

            if 'messages' in result:
                messages.extend(result['messages'])

            # Check for more pages
            page_token = result.get('nextPageToken')
            if not page_token or len(messages) >= max_results:
                break

        return messages[:max_results]

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise


def list_messages_with_details(query: str = '', max_results: int = 10) -> list:
    """
    List messages with full details (subject, from, snippet).

    Args:
        query: Gmail search query
        max_results: Maximum number of messages to return

    Returns:
        List of dictionaries with message details
    """
    service = get_gmail_service()
    messages = list_messages(query=query, max_results=max_results)
    detailed_messages = []

    for msg in messages:
        full_msg = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From', 'To', 'Date']
        ).execute()

        headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}

        detailed_messages.append({
            'id': full_msg['id'],
            'threadId': full_msg['threadId'],
            'subject': headers.get('Subject', '(No Subject)'),
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'date': headers.get('Date', ''),
            'snippet': full_msg.get('snippet', ''),
            'labelIds': full_msg.get('labelIds', []),
        })

    return detailed_messages


# Example usage
if __name__ == '__main__':
    # List unread messages from last 7 days
    messages = list_messages_with_details(
        query='is:unread newer_than:7d',
        max_results=5
    )

    for msg in messages:
        print(f"\nSubject: {msg['subject']}")
        print(f"From: {msg['from']}")
        print(f"Date: {msg['date']}")
        print(f"Snippet: {msg['snippet'][:100]}...")
```

### 2.4 Read Message and Thread

Create `gmail_read.py`:

```python
"""Gmail API - Read Messages and Threads Module."""
import base64
from typing import Optional
from googleapiclient.errors import HttpError
from gmail_auth import get_gmail_service


def get_message(message_id: str, format: str = 'full') -> dict:
    """
    Get a specific message by ID.

    Args:
        message_id: The ID of the message to retrieve
        format: 'full', 'metadata', 'minimal', or 'raw'

    Returns:
        Message object with full details
    """
    service = get_gmail_service()

    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format=format
        ).execute()
        return message

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise


def get_message_body(message: dict) -> dict:
    """
    Extract the body content from a message.

    Args:
        message: Full message object from get_message()

    Returns:
        Dictionary with 'plain' and 'html' body content
    """
    body = {'plain': '', 'html': ''}

    def extract_parts(payload):
        """Recursively extract body parts."""
        if 'body' in payload and payload['body'].get('data'):
            mime_type = payload.get('mimeType', '')
            data = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

            if 'text/plain' in mime_type:
                body['plain'] = data
            elif 'text/html' in mime_type:
                body['html'] = data

        if 'parts' in payload:
            for part in payload['parts']:
                extract_parts(part)

    if 'payload' in message:
        extract_parts(message['payload'])

    return body


def get_message_headers(message: dict) -> dict:
    """
    Extract headers from a message.

    Args:
        message: Full message object

    Returns:
        Dictionary of header name -> value
    """
    headers = {}
    if 'payload' in message and 'headers' in message['payload']:
        for header in message['payload']['headers']:
            headers[header['name']] = header['value']
    return headers


def get_thread(thread_id: str, format: str = 'full') -> dict:
    """
    Get a complete thread (conversation) by ID.

    Args:
        thread_id: The ID of the thread to retrieve
        format: 'full', 'metadata', or 'minimal'

    Returns:
        Thread object with all messages in the conversation
    """
    service = get_gmail_service()

    try:
        thread = service.users().threads().get(
            userId='me',
            id=thread_id,
            format=format
        ).execute()
        return thread

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise


def get_thread_messages(thread_id: str) -> list:
    """
    Get all messages in a thread with parsed content.

    Args:
        thread_id: The ID of the thread

    Returns:
        List of parsed message dictionaries
    """
    thread = get_thread(thread_id, format='full')
    parsed_messages = []

    for message in thread.get('messages', []):
        headers = get_message_headers(message)
        body = get_message_body(message)

        parsed_messages.append({
            'id': message['id'],
            'threadId': message['threadId'],
            'subject': headers.get('Subject', ''),
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'date': headers.get('Date', ''),
            'body_plain': body['plain'],
            'body_html': body['html'],
            'snippet': message.get('snippet', ''),
            'labelIds': message.get('labelIds', []),
        })

    return parsed_messages


# Example usage
if __name__ == '__main__':
    from gmail_list import list_messages

    # Get latest message
    messages = list_messages(max_results=1)
    if messages:
        msg_id = messages[0]['id']
        thread_id = messages[0]['threadId']

        # Read single message
        message = get_message(msg_id)
        headers = get_message_headers(message)
        body = get_message_body(message)

        print(f"Subject: {headers.get('Subject')}")
        print(f"From: {headers.get('From')}")
        print(f"Body Preview: {body['plain'][:200]}...")

        # Read entire thread
        print(f"\n--- Thread Messages ({thread_id}) ---")
        thread_messages = get_thread_messages(thread_id)
        for i, msg in enumerate(thread_messages, 1):
            print(f"\n[Message {i}]")
            print(f"From: {msg['from']}")
            print(f"Date: {msg['date']}")
            print(f"Snippet: {msg['snippet']}")
```

### 2.5 Create and Send Replies

Create `gmail_send.py`:

```python
"""Gmail API - Send Messages Module."""
import base64
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
import os
from typing import Optional
from googleapiclient.errors import HttpError
from gmail_auth import get_gmail_service


def create_message(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None,
    thread_id: Optional[str] = None,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None,
) -> dict:
    """
    Create an email message.

    Args:
        to: Recipient email address(es), comma-separated for multiple
        subject: Email subject
        body: Plain text body
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html_body: HTML body (optional, for multipart messages)
        thread_id: Thread ID for replies (optional)
        in_reply_to: Message-ID header of message being replied to
        references: References header for threading

    Returns:
        Message dictionary ready for sending
    """
    if html_body:
        # Create multipart message with both plain and HTML
        message = MIMEMultipart('alternative')
        message.attach(MIMEText(body, 'plain'))
        message.attach(MIMEText(html_body, 'html'))
    else:
        message = EmailMessage()
        message.set_content(body)

    message['To'] = to
    message['Subject'] = subject

    if cc:
        message['Cc'] = cc
    if bcc:
        message['Bcc'] = bcc
    if in_reply_to:
        message['In-Reply-To'] = in_reply_to
    if references:
        message['References'] = references

    # Encode the message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    result = {'raw': encoded_message}
    if thread_id:
        result['threadId'] = thread_id

    return result


def send_message(message: dict) -> dict:
    """
    Send an email message.

    Args:
        message: Message dictionary with 'raw' key (and optional 'threadId')

    Returns:
        Sent message object with 'id', 'threadId', 'labelIds'
    """
    service = get_gmail_service()

    try:
        sent_message = service.users().messages().send(
            userId='me',
            body=message
        ).execute()

        print(f"Message sent successfully. ID: {sent_message['id']}")
        return sent_message

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise


def send_email(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None,
) -> dict:
    """
    Convenience function to create and send an email in one call.

    Args:
        to: Recipient email address(es)
        subject: Email subject
        body: Plain text body
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html_body: HTML body (optional)

    Returns:
        Sent message object
    """
    message = create_message(
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        html_body=html_body,
    )
    return send_message(message)


def reply_to_message(
    original_message_id: str,
    body: str,
    reply_all: bool = False,
    html_body: Optional[str] = None,
) -> dict:
    """
    Reply to an existing message.

    Args:
        original_message_id: ID of the message to reply to
        body: Reply body text
        reply_all: If True, reply to all recipients
        html_body: HTML body (optional)

    Returns:
        Sent reply message object
    """
    service = get_gmail_service()

    # Get the original message
    original = service.users().messages().get(
        userId='me',
        id=original_message_id,
        format='metadata',
        metadataHeaders=['Subject', 'From', 'To', 'Cc', 'Message-ID', 'References']
    ).execute()

    headers = {h['name']: h['value'] for h in original['payload']['headers']}

    # Build reply headers
    original_from = headers.get('From', '')
    original_to = headers.get('To', '')
    original_cc = headers.get('Cc', '')
    original_subject = headers.get('Subject', '')
    message_id = headers.get('Message-ID', '')
    references = headers.get('References', '')

    # Determine recipients
    if reply_all:
        # Reply to sender and all original recipients
        to = original_from
        cc = f"{original_to}, {original_cc}".strip(', ')
    else:
        to = original_from
        cc = None

    # Build subject (add Re: if not present)
    if not original_subject.lower().startswith('re:'):
        subject = f"Re: {original_subject}"
    else:
        subject = original_subject

    # Build References header
    if references:
        new_references = f"{references} {message_id}"
    else:
        new_references = message_id

    message = create_message(
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        html_body=html_body,
        thread_id=original['threadId'],
        in_reply_to=message_id,
        references=new_references,
    )

    return send_message(message)


def forward_message(
    original_message_id: str,
    to: str,
    additional_text: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
) -> dict:
    """
    Forward an existing message to new recipients.

    Args:
        original_message_id: ID of the message to forward
        to: Recipient(s) to forward to
        additional_text: Optional text to add before forwarded content
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)

    Returns:
        Sent forwarded message object
    """
    service = get_gmail_service()

    # Get the original message with full content
    original = service.users().messages().get(
        userId='me',
        id=original_message_id,
        format='full'
    ).execute()

    headers = {h['name']: h['value'] for h in original['payload']['headers']}

    # Extract original body
    from gmail_read import get_message_body
    original_body = get_message_body(original)

    # Build forwarded message body
    forward_header = (
        f"\n\n---------- Forwarded message ----------\n"
        f"From: {headers.get('From', '')}\n"
        f"Date: {headers.get('Date', '')}\n"
        f"Subject: {headers.get('Subject', '')}\n"
        f"To: {headers.get('To', '')}\n\n"
    )

    if additional_text:
        body = f"{additional_text}{forward_header}{original_body['plain']}"
    else:
        body = f"{forward_header}{original_body['plain']}"

    # Build subject
    original_subject = headers.get('Subject', '')
    if not original_subject.lower().startswith('fwd:'):
        subject = f"Fwd: {original_subject}"
    else:
        subject = original_subject

    message = create_message(
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
    )

    return send_message(message)


def create_draft(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    html_body: Optional[str] = None,
) -> dict:
    """
    Create a draft email (not sent).

    Args:
        to: Recipient email address(es)
        subject: Email subject
        body: Plain text body
        cc: CC recipients (optional)
        html_body: HTML body (optional)

    Returns:
        Draft object with 'id' and 'message'
    """
    service = get_gmail_service()

    message = create_message(
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        html_body=html_body,
    )

    try:
        draft = service.users().drafts().create(
            userId='me',
            body={'message': message}
        ).execute()

        print(f"Draft created. ID: {draft['id']}")
        return draft

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise


def send_draft(draft_id: str) -> dict:
    """
    Send an existing draft.

    Args:
        draft_id: ID of the draft to send

    Returns:
        Sent message object
    """
    service = get_gmail_service()

    try:
        sent_message = service.users().drafts().send(
            userId='me',
            body={'id': draft_id}
        ).execute()

        print(f"Draft sent successfully. Message ID: {sent_message['id']}")
        return sent_message

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise


# Example usage
if __name__ == '__main__':
    # Example: Send a simple email
    # result = send_email(
    #     to='recipient@example.com',
    #     subject='Test Email',
    #     body='This is a test email sent via Gmail API.',
    # )

    # Example: Reply to a message
    # reply_to_message(
    #     original_message_id='MESSAGE_ID_HERE',
    #     body='Thank you for your email. This is my reply.',
    # )

    # Example: Forward a message
    # forward_message(
    #     original_message_id='MESSAGE_ID_HERE',
    #     to='forward-to@example.com',
    #     additional_text='FYI - Please see the message below.',
    # )

    print("Gmail send module loaded. Import functions to use.")
```

### 2.6 Complete Example Script

Create `gmail_example.py`:

```python
"""Complete Gmail API Example Script."""
from gmail_list import list_messages, list_messages_with_details
from gmail_read import get_message, get_thread_messages, get_message_body, get_message_headers
from gmail_send import send_email, reply_to_message, forward_message, create_draft


def example_list_recent_unread():
    """List recent unread messages."""
    print("\n=== Recent Unread Messages ===")
    messages = list_messages_with_details(
        query='is:unread newer_than:7d',
        max_results=5
    )

    for i, msg in enumerate(messages, 1):
        print(f"\n[{i}] {msg['subject']}")
        print(f"    From: {msg['from']}")
        print(f"    Date: {msg['date']}")


def example_search_messages():
    """Search messages with various criteria."""
    print("\n=== Search Examples ===")

    # Search by sender
    print("\nMessages from a specific domain:")
    messages = list_messages(query='from:@gmail.com', max_results=3)
    print(f"  Found {len(messages)} messages")

    # Search by subject
    print("\nMessages with 'meeting' in subject:")
    messages = list_messages(query='subject:meeting', max_results=3)
    print(f"  Found {len(messages)} messages")

    # Search with date range
    print("\nMessages from last month:")
    messages = list_messages(query='newer_than:30d', max_results=3)
    print(f"  Found {len(messages)} messages")


def example_read_thread():
    """Read a complete email thread."""
    print("\n=== Read Thread Example ===")

    # Get the latest message
    messages = list_messages(max_results=1)
    if not messages:
        print("No messages found.")
        return

    thread_id = messages[0]['threadId']
    print(f"Reading thread: {thread_id}")

    thread_messages = get_thread_messages(thread_id)
    print(f"Thread contains {len(thread_messages)} message(s):\n")

    for i, msg in enumerate(thread_messages, 1):
        print(f"--- Message {i} ---")
        print(f"From: {msg['from']}")
        print(f"Date: {msg['date']}")
        print(f"Subject: {msg['subject']}")
        print(f"Preview: {msg['snippet'][:100]}...")
        print()


def example_create_draft_reply():
    """Create a draft reply to the latest message."""
    print("\n=== Create Draft Reply Example ===")

    messages = list_messages(max_results=1)
    if not messages:
        print("No messages to reply to.")
        return

    msg_id = messages[0]['id']
    message = get_message(msg_id, format='metadata')
    headers = get_message_headers(message)

    print(f"Would reply to: {headers.get('Subject', '(No Subject)')}")
    print(f"From: {headers.get('From', '')}")

    # Uncomment to actually create draft:
    # draft = create_draft(
    #     to=headers.get('From', ''),
    #     subject=f"Re: {headers.get('Subject', '')}",
    #     body="Thank you for your message. I will get back to you soon.",
    # )
    # print(f"Draft created with ID: {draft['id']}")


if __name__ == '__main__':
    print("Gmail API Complete Example")
    print("=" * 50)

    example_list_recent_unread()
    example_search_messages()
    example_read_thread()
    example_create_draft_reply()
```

---

## 3. Node.js Implementation

### 3.1 Environment Setup

```bash
# Initialize project
npm init -y

# Install required packages
npm install @googleapis/gmail googleapis @google-cloud/local-auth
```

### 3.2 Authentication Module

Create `gmail-auth.js`:

```javascript
/**
 * Gmail API Authentication Module for Node.js
 */
const fs = require('fs').promises;
const path = require('path');
const { authenticate } = require('@google-cloud/local-auth');
const { google } = require('googleapis');

// Define your scopes - modify based on your needs
const SCOPES = [
  'https://www.googleapis.com/auth/gmail.readonly',
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/gmail.compose',
  'https://www.googleapis.com/auth/gmail.modify',
];

const TOKEN_PATH = path.join(process.cwd(), 'token.json');
const CREDENTIALS_PATH = path.join(process.cwd(), 'credentials.json');

/**
 * Reads previously authorized credentials from the save file.
 * @returns {Promise<OAuth2Client|null>}
 */
async function loadSavedCredentialsIfExist() {
  try {
    const content = await fs.readFile(TOKEN_PATH);
    const credentials = JSON.parse(content);
    return google.auth.fromJSON(credentials);
  } catch (err) {
    return null;
  }
}

/**
 * Serializes credentials to a file.
 * @param {OAuth2Client} client
 */
async function saveCredentials(client) {
  const content = await fs.readFile(CREDENTIALS_PATH);
  const keys = JSON.parse(content);
  const key = keys.installed || keys.web;
  const payload = JSON.stringify({
    type: 'authorized_user',
    client_id: key.client_id,
    client_secret: key.client_secret,
    refresh_token: client.credentials.refresh_token,
  });
  await fs.writeFile(TOKEN_PATH, payload);
}

/**
 * Load or request authorization to call APIs.
 * @returns {Promise<OAuth2Client>}
 */
async function authorize() {
  let client = await loadSavedCredentialsIfExist();
  if (client) {
    return client;
  }
  client = await authenticate({
    scopes: SCOPES,
    keyfilePath: CREDENTIALS_PATH,
  });
  if (client.credentials) {
    await saveCredentials(client);
  }
  return client;
}

/**
 * Get Gmail API service instance.
 * @returns {Promise<gmail_v1.Gmail>}
 */
async function getGmailService() {
  const auth = await authorize();
  return google.gmail({ version: 'v1', auth });
}

module.exports = {
  authorize,
  getGmailService,
  SCOPES,
};
```

### 3.3 List Messages

Create `gmail-list.js`:

```javascript
/**
 * Gmail API - List Messages Module for Node.js
 */
const { getGmailService } = require('./gmail-auth');

/**
 * List messages matching the specified criteria.
 * @param {Object} options - Search options
 * @param {string} options.query - Gmail search query
 * @param {string[]} options.labelIds - Label IDs to filter by
 * @param {number} options.maxResults - Maximum messages to return
 * @param {boolean} options.includeSpamTrash - Include spam/trash
 * @returns {Promise<Array>} Array of message objects
 */
async function listMessages(options = {}) {
  const {
    query = '',
    labelIds = null,
    maxResults = 100,
    includeSpamTrash = false,
  } = options;

  const gmail = await getGmailService();
  const messages = [];
  let pageToken = null;

  try {
    do {
      const params = {
        userId: 'me',
        maxResults: Math.min(maxResults - messages.length, 500),
        includeSpamTrash,
      };

      if (query) params.q = query;
      if (labelIds) params.labelIds = labelIds;
      if (pageToken) params.pageToken = pageToken;

      const response = await gmail.users.messages.list(params);

      if (response.data.messages) {
        messages.push(...response.data.messages);
      }

      pageToken = response.data.nextPageToken;
    } while (pageToken && messages.length < maxResults);

    return messages.slice(0, maxResults);
  } catch (error) {
    console.error('Error listing messages:', error.message);
    throw error;
  }
}

/**
 * List messages with full details.
 * @param {string} query - Gmail search query
 * @param {number} maxResults - Maximum messages to return
 * @returns {Promise<Array>} Array of detailed message objects
 */
async function listMessagesWithDetails(query = '', maxResults = 10) {
  const gmail = await getGmailService();
  const messages = await listMessages({ query, maxResults });
  const detailedMessages = [];

  for (const msg of messages) {
    const fullMsg = await gmail.users.messages.get({
      userId: 'me',
      id: msg.id,
      format: 'metadata',
      metadataHeaders: ['Subject', 'From', 'To', 'Date'],
    });

    const headers = {};
    fullMsg.data.payload.headers.forEach((h) => {
      headers[h.name] = h.value;
    });

    detailedMessages.push({
      id: fullMsg.data.id,
      threadId: fullMsg.data.threadId,
      subject: headers.Subject || '(No Subject)',
      from: headers.From || '',
      to: headers.To || '',
      date: headers.Date || '',
      snippet: fullMsg.data.snippet || '',
      labelIds: fullMsg.data.labelIds || [],
    });
  }

  return detailedMessages;
}

module.exports = {
  listMessages,
  listMessagesWithDetails,
};

// Example usage
if (require.main === module) {
  (async () => {
    const messages = await listMessagesWithDetails('is:unread newer_than:7d', 5);
    console.log('Recent unread messages:');
    messages.forEach((msg, i) => {
      console.log(`\n[${i + 1}] ${msg.subject}`);
      console.log(`    From: ${msg.from}`);
      console.log(`    Date: ${msg.date}`);
    });
  })();
}
```

### 3.4 Read Messages and Threads

Create `gmail-read.js`:

```javascript
/**
 * Gmail API - Read Messages and Threads Module for Node.js
 */
const { getGmailService } = require('./gmail-auth');

/**
 * Get a specific message by ID.
 * @param {string} messageId - Message ID
 * @param {string} format - 'full', 'metadata', 'minimal', or 'raw'
 * @returns {Promise<Object>} Message object
 */
async function getMessage(messageId, format = 'full') {
  const gmail = await getGmailService();

  try {
    const response = await gmail.users.messages.get({
      userId: 'me',
      id: messageId,
      format,
    });
    return response.data;
  } catch (error) {
    console.error('Error getting message:', error.message);
    throw error;
  }
}

/**
 * Extract body content from a message.
 * @param {Object} message - Full message object
 * @returns {Object} Object with 'plain' and 'html' body content
 */
function getMessageBody(message) {
  const body = { plain: '', html: '' };

  function extractParts(payload) {
    if (payload.body && payload.body.data) {
      const data = Buffer.from(payload.body.data, 'base64').toString('utf-8');
      const mimeType = payload.mimeType || '';

      if (mimeType.includes('text/plain')) {
        body.plain = data;
      } else if (mimeType.includes('text/html')) {
        body.html = data;
      }
    }

    if (payload.parts) {
      payload.parts.forEach((part) => extractParts(part));
    }
  }

  if (message.payload) {
    extractParts(message.payload);
  }

  return body;
}

/**
 * Extract headers from a message.
 * @param {Object} message - Message object
 * @returns {Object} Headers as key-value pairs
 */
function getMessageHeaders(message) {
  const headers = {};
  if (message.payload && message.payload.headers) {
    message.payload.headers.forEach((h) => {
      headers[h.name] = h.value;
    });
  }
  return headers;
}

/**
 * Get a complete thread by ID.
 * @param {string} threadId - Thread ID
 * @param {string} format - 'full', 'metadata', or 'minimal'
 * @returns {Promise<Object>} Thread object with all messages
 */
async function getThread(threadId, format = 'full') {
  const gmail = await getGmailService();

  try {
    const response = await gmail.users.threads.get({
      userId: 'me',
      id: threadId,
      format,
    });
    return response.data;
  } catch (error) {
    console.error('Error getting thread:', error.message);
    throw error;
  }
}

/**
 * Get all messages in a thread with parsed content.
 * @param {string} threadId - Thread ID
 * @returns {Promise<Array>} Array of parsed message objects
 */
async function getThreadMessages(threadId) {
  const thread = await getThread(threadId, 'full');
  const parsedMessages = [];

  for (const message of thread.messages || []) {
    const headers = getMessageHeaders(message);
    const body = getMessageBody(message);

    parsedMessages.push({
      id: message.id,
      threadId: message.threadId,
      subject: headers.Subject || '',
      from: headers.From || '',
      to: headers.To || '',
      date: headers.Date || '',
      bodyPlain: body.plain,
      bodyHtml: body.html,
      snippet: message.snippet || '',
      labelIds: message.labelIds || [],
    });
  }

  return parsedMessages;
}

module.exports = {
  getMessage,
  getMessageBody,
  getMessageHeaders,
  getThread,
  getThreadMessages,
};

// Example usage
if (require.main === module) {
  const { listMessages } = require('./gmail-list');

  (async () => {
    const messages = await listMessages({ maxResults: 1 });
    if (messages.length > 0) {
      const threadId = messages[0].threadId;
      console.log(`Reading thread: ${threadId}\n`);

      const threadMessages = await getThreadMessages(threadId);
      threadMessages.forEach((msg, i) => {
        console.log(`--- Message ${i + 1} ---`);
        console.log(`From: ${msg.from}`);
        console.log(`Subject: ${msg.subject}`);
        console.log(`Preview: ${msg.snippet.substring(0, 100)}...\n`);
      });
    }
  })();
}
```

### 3.5 Send Messages, Reply, and Forward

Create `gmail-send.js`:

```javascript
/**
 * Gmail API - Send Messages Module for Node.js
 */
const { getGmailService } = require('./gmail-auth');
const { getMessage, getMessageBody, getMessageHeaders } = require('./gmail-read');

/**
 * Create an email message.
 * @param {Object} options - Message options
 * @returns {Object} Message object ready for sending
 */
function createMessage(options) {
  const {
    to,
    subject,
    body,
    cc = null,
    bcc = null,
    htmlBody = null,
    threadId = null,
    inReplyTo = null,
    references = null,
  } = options;

  // Build email headers and body
  const boundary = `boundary_${Date.now()}`;
  let email = '';

  email += `To: ${to}\r\n`;
  email += `Subject: ${subject}\r\n`;
  if (cc) email += `Cc: ${cc}\r\n`;
  if (bcc) email += `Bcc: ${bcc}\r\n`;
  if (inReplyTo) email += `In-Reply-To: ${inReplyTo}\r\n`;
  if (references) email += `References: ${references}\r\n`;

  if (htmlBody) {
    // Multipart message
    email += `Content-Type: multipart/alternative; boundary="${boundary}"\r\n\r\n`;
    email += `--${boundary}\r\n`;
    email += `Content-Type: text/plain; charset="UTF-8"\r\n\r\n`;
    email += `${body}\r\n\r\n`;
    email += `--${boundary}\r\n`;
    email += `Content-Type: text/html; charset="UTF-8"\r\n\r\n`;
    email += `${htmlBody}\r\n\r\n`;
    email += `--${boundary}--`;
  } else {
    email += `Content-Type: text/plain; charset="UTF-8"\r\n\r\n`;
    email += body;
  }

  const encodedMessage = Buffer.from(email)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');

  const result = { raw: encodedMessage };
  if (threadId) result.threadId = threadId;

  return result;
}

/**
 * Send an email message.
 * @param {Object} message - Message object with 'raw' key
 * @returns {Promise<Object>} Sent message object
 */
async function sendMessage(message) {
  const gmail = await getGmailService();

  try {
    const response = await gmail.users.messages.send({
      userId: 'me',
      requestBody: message,
    });

    console.log(`Message sent successfully. ID: ${response.data.id}`);
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error.message);
    throw error;
  }
}

/**
 * Convenience function to create and send an email.
 * @param {Object} options - Email options (to, subject, body, cc, bcc, htmlBody)
 * @returns {Promise<Object>} Sent message object
 */
async function sendEmail(options) {
  const message = createMessage(options);
  return sendMessage(message);
}

/**
 * Reply to an existing message.
 * @param {string} originalMessageId - ID of message to reply to
 * @param {string} body - Reply body text
 * @param {boolean} replyAll - If true, reply to all recipients
 * @param {string} htmlBody - Optional HTML body
 * @returns {Promise<Object>} Sent reply message object
 */
async function replyToMessage(originalMessageId, body, replyAll = false, htmlBody = null) {
  const original = await getMessage(originalMessageId);
  const headers = getMessageHeaders(original);

  const originalFrom = headers.From || '';
  const originalTo = headers.To || '';
  const originalCc = headers.Cc || '';
  const originalSubject = headers.Subject || '';
  const messageId = headers['Message-ID'] || '';
  const existingReferences = headers.References || '';

  // Determine recipients
  let to = originalFrom;
  let cc = null;
  if (replyAll) {
    cc = [originalTo, originalCc].filter(Boolean).join(', ');
  }

  // Build subject
  let subject = originalSubject;
  if (!originalSubject.toLowerCase().startsWith('re:')) {
    subject = `Re: ${originalSubject}`;
  }

  // Build References header
  const newReferences = existingReferences
    ? `${existingReferences} ${messageId}`
    : messageId;

  const message = createMessage({
    to,
    subject,
    body,
    cc,
    htmlBody,
    threadId: original.threadId,
    inReplyTo: messageId,
    references: newReferences,
  });

  return sendMessage(message);
}

/**
 * Forward a message to new recipients.
 * @param {string} originalMessageId - ID of message to forward
 * @param {string} to - Recipient(s) to forward to
 * @param {string} additionalText - Optional text to add before forwarded content
 * @param {string} cc - Optional CC recipients
 * @param {string} bcc - Optional BCC recipients
 * @returns {Promise<Object>} Sent forwarded message object
 */
async function forwardMessage(originalMessageId, to, additionalText = null, cc = null, bcc = null) {
  const original = await getMessage(originalMessageId);
  const headers = getMessageHeaders(original);
  const originalBody = getMessageBody(original);

  // Build forwarded message body
  const forwardHeader = `\n\n---------- Forwarded message ----------\n` +
    `From: ${headers.From || ''}\n` +
    `Date: ${headers.Date || ''}\n` +
    `Subject: ${headers.Subject || ''}\n` +
    `To: ${headers.To || ''}\n\n`;

  let body;
  if (additionalText) {
    body = `${additionalText}${forwardHeader}${originalBody.plain}`;
  } else {
    body = `${forwardHeader}${originalBody.plain}`;
  }

  // Build subject
  const originalSubject = headers.Subject || '';
  let subject = originalSubject;
  if (!originalSubject.toLowerCase().startsWith('fwd:')) {
    subject = `Fwd: ${originalSubject}`;
  }

  const message = createMessage({
    to,
    subject,
    body,
    cc,
    bcc,
  });

  return sendMessage(message);
}

/**
 * Create a draft email.
 * @param {Object} options - Email options
 * @returns {Promise<Object>} Draft object
 */
async function createDraft(options) {
  const gmail = await getGmailService();
  const message = createMessage(options);

  try {
    const response = await gmail.users.drafts.create({
      userId: 'me',
      requestBody: {
        message,
      },
    });

    console.log(`Draft created. ID: ${response.data.id}`);
    return response.data;
  } catch (error) {
    console.error('Error creating draft:', error.message);
    throw error;
  }
}

/**
 * Send an existing draft.
 * @param {string} draftId - ID of draft to send
 * @returns {Promise<Object>} Sent message object
 */
async function sendDraft(draftId) {
  const gmail = await getGmailService();

  try {
    const response = await gmail.users.drafts.send({
      userId: 'me',
      requestBody: {
        id: draftId,
      },
    });

    console.log(`Draft sent successfully. Message ID: ${response.data.id}`);
    return response.data;
  } catch (error) {
    console.error('Error sending draft:', error.message);
    throw error;
  }
}

module.exports = {
  createMessage,
  sendMessage,
  sendEmail,
  replyToMessage,
  forwardMessage,
  createDraft,
  sendDraft,
};

// Example usage
if (require.main === module) {
  console.log('Gmail send module loaded.');
  console.log('Import functions to use:');
  console.log('  const { sendEmail, replyToMessage, forwardMessage } = require("./gmail-send");');
}
```

---

## 4. Common Search Query Operators

Use these operators in the `query` parameter:

| Operator | Description | Example |
|----------|-------------|---------|
| `from:` | Sender | `from:user@example.com` |
| `to:` | Recipient | `to:me@example.com` |
| `subject:` | Subject line | `subject:meeting` |
| `is:` | Status | `is:unread`, `is:starred`, `is:important` |
| `has:` | Content type | `has:attachment`, `has:drive`, `has:youtube` |
| `in:` | Location | `in:inbox`, `in:sent`, `in:trash`, `in:spam` |
| `after:` | After date | `after:2024/01/01` |
| `before:` | Before date | `before:2024/12/31` |
| `newer_than:` | Relative time | `newer_than:7d`, `newer_than:1m`, `newer_than:1y` |
| `older_than:` | Relative time | `older_than:30d` |
| `label:` | Label name | `label:work` |
| `filename:` | Attachment name | `filename:report.pdf` |
| `larger:` | Size | `larger:5M` |
| `smaller:` | Size | `smaller:1M` |
| `OR` | Boolean OR | `from:alice OR from:bob` |
| `-` | Exclude | `-is:spam` |
| `""` | Exact phrase | `"project update"` |

### Combined Examples

```
# Unread emails from specific sender in last week
from:boss@company.com is:unread newer_than:7d

# Emails with PDF attachments larger than 2MB
has:attachment filename:pdf larger:2M

# Important emails not in inbox (archived)
is:important -in:inbox

# Emails about meetings from last month
subject:meeting newer_than:30d older_than:7d
```

---

## 5. Error Handling

### Common Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| 400 | Bad Request | Check request parameters and format |
| 401 | Unauthorized | Token expired - delete token.json and re-authenticate |
| 403 | Forbidden | Insufficient scopes or API not enabled |
| 404 | Not Found | Invalid message/thread ID |
| 429 | Rate Limit | Implement exponential backoff |
| 500 | Server Error | Retry with exponential backoff |

### Python Error Handling Pattern

```python
from googleapiclient.errors import HttpError
import time

def with_retry(func, max_retries=3):
    """Execute function with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return func()
        except HttpError as error:
            if error.resp.status in [429, 500, 503]:
                wait_time = (2 ** attempt) + 1
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception(f"Failed after {max_retries} retries")
```

### Node.js Error Handling Pattern

```javascript
async function withRetry(func, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await func();
    } catch (error) {
      if ([429, 500, 503].includes(error.code) && attempt < maxRetries - 1) {
        const waitTime = Math.pow(2, attempt) * 1000;
        console.log(`Retrying in ${waitTime / 1000} seconds...`);
        await new Promise((resolve) => setTimeout(resolve, waitTime));
      } else {
        throw error;
      }
    }
  }
}
```

---

## 6. Service Account Implementation (Google Workspace Only)

> **Important:** This section applies ONLY to Google Workspace accounts. Service accounts cannot be used with personal Gmail accounts (@gmail.com). See Section 1.3 for details.

### 6.1 Prerequisites for Service Account Authentication

Before implementing service account authentication, ensure you have:

1. A **Google Workspace** account (not a personal @gmail.com account)
2. **Super admin** access to your Google Workspace organization
3. A Google Cloud project with the Gmail API enabled

### 6.2 Create a Service Account

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **IAM & Admin > Service Accounts**
4. Click **Create Service Account**
5. Enter a name and description for the service account
6. Click **Create and Continue**
7. (Optional) Grant roles if needed, then click **Continue**
8. Click **Done**

### 6.3 Create and Download Service Account Key

1. In the Service Accounts list, click on your newly created service account
2. Go to the **Keys** tab
3. Click **Add Key > Create new key**
4. Select **JSON** format
5. Click **Create**
6. Save the downloaded JSON file as `service-account.json` in your project directory

**Important:** Never commit `service-account.json` to source control!

### 6.4 Enable Domain-Wide Delegation

1. In the Service Account details page, click **Show Advanced Settings**
2. Under **Domain-wide delegation**, click **Enable Google Workspace Domain-wide Delegation**
3. Note the **Client ID** (you'll need this for the admin console)

### 6.5 Grant Domain-Wide Delegation in Google Workspace Admin Console

1. Sign in to the [Google Workspace Admin Console](https://admin.google.com/) as a super admin
2. Navigate to **Security > Access and data control > API controls**
3. In the **Domain-wide delegation** section, click **Manage Domain Wide Delegation**
4. Click **Add new**
5. Enter the **Client ID** from step 7.4
6. Enter the required OAuth scopes (comma-separated):
   ```
   https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.compose,https://www.googleapis.com/auth/gmail.modify
   ```
7. Click **Authorize**

### 6.6 Python Implementation with Service Account

#### Environment Setup

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install required packages
uv add google-api-python-client google-auth
```

#### Authentication Module

Create `gmail_service_account_auth.py`:

```python
"""Gmail API Service Account Authentication Module (Google Workspace Only)."""
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define your scopes - modify based on your needs
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
]


def get_gmail_service_for_user(
    user_email: str,
    service_account_file: str = 'service-account.json'
):
    """
    Get Gmail API service using service account with domain-wide delegation.

    This function creates a Gmail API service that impersonates the specified
    user within your Google Workspace organization.

    Args:
        user_email: The email address of the user to impersonate
                   (must be in your Google Workspace domain)
        service_account_file: Path to the service account JSON key file

    Returns:
        Gmail API service instance authorized to act as the specified user

    Raises:
        FileNotFoundError: If service account file is not found
        google.auth.exceptions.RefreshError: If delegation is not properly configured

    Note:
        This only works for Google Workspace accounts. Personal Gmail accounts
        (@gmail.com) do not support service account authentication.
    """
    # Load service account credentials
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=SCOPES
    )

    # Create delegated credentials for the target user
    delegated_credentials = credentials.with_subject(user_email)

    # Build and return the Gmail service
    return build('gmail', 'v1', credentials=delegated_credentials)


def list_user_messages(user_email: str, max_results: int = 10) -> list:
    """
    List messages for a specific user using service account.

    Args:
        user_email: The email address of the user
        max_results: Maximum number of messages to return

    Returns:
        List of message objects
    """
    service = get_gmail_service_for_user(user_email)

    results = service.users().messages().list(
        userId='me',  # 'me' refers to the impersonated user
        maxResults=max_results
    ).execute()

    return results.get('messages', [])


def send_email_as_user(
    user_email: str,
    to: str,
    subject: str,
    body: str
) -> dict:
    """
    Send an email as a specific user using service account.

    Args:
        user_email: The email address of the user to send as
        to: Recipient email address
        subject: Email subject
        body: Email body text

    Returns:
        Sent message object
    """
    import base64
    from email.message import EmailMessage

    service = get_gmail_service_for_user(user_email)

    # Create the email message
    message = EmailMessage()
    message.set_content(body)
    message['To'] = to
    message['Subject'] = subject

    # Encode the message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Send the message
    sent_message = service.users().messages().send(
        userId='me',
        body={'raw': encoded_message}
    ).execute()

    return sent_message


# Example usage
if __name__ == '__main__':
    # Replace with a user email from your Google Workspace domain
    WORKSPACE_USER = 'user@your-workspace-domain.com'

    try:
        # List messages for the user
        messages = list_user_messages(WORKSPACE_USER, max_results=5)
        print(f"Found {len(messages)} messages for {WORKSPACE_USER}")

        for msg in messages:
            print(f"  Message ID: {msg['id']}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nCommon issues:")
        print("  - Service account file not found")
        print("  - Domain-wide delegation not enabled")
        print("  - Scopes not authorized in Admin Console")
        print("  - User email not in your Workspace domain")
```

### 6.7 Node.js Implementation with Service Account

#### Environment Setup

```bash
# Initialize project
npm init -y

# Install required packages
npm install googleapis
```

#### Authentication Module

Create `gmail-service-account-auth.js`:

```javascript
/**
 * Gmail API Service Account Authentication Module (Google Workspace Only)
 */
const { google } = require('googleapis');
const path = require('path');

// Define your scopes
const SCOPES = [
  'https://www.googleapis.com/auth/gmail.readonly',
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/gmail.compose',
  'https://www.googleapis.com/auth/gmail.modify',
];

const SERVICE_ACCOUNT_FILE = path.join(process.cwd(), 'service-account.json');

/**
 * Get Gmail API service using service account with domain-wide delegation.
 * @param {string} userEmail - The email of the user to impersonate
 * @returns {Promise<gmail_v1.Gmail>} Gmail API service instance
 */
async function getGmailServiceForUser(userEmail) {
  const auth = new google.auth.GoogleAuth({
    keyFile: SERVICE_ACCOUNT_FILE,
    scopes: SCOPES,
    clientOptions: {
      subject: userEmail, // User to impersonate
    },
  });

  const authClient = await auth.getClient();
  return google.gmail({ version: 'v1', auth: authClient });
}

/**
 * List messages for a specific user using service account.
 * @param {string} userEmail - The email of the user
 * @param {number} maxResults - Maximum messages to return
 * @returns {Promise<Array>} Array of message objects
 */
async function listUserMessages(userEmail, maxResults = 10) {
  const gmail = await getGmailServiceForUser(userEmail);

  const response = await gmail.users.messages.list({
    userId: 'me',
    maxResults,
  });

  return response.data.messages || [];
}

/**
 * Send an email as a specific user using service account.
 * @param {string} userEmail - The email of the user to send as
 * @param {string} to - Recipient email
 * @param {string} subject - Email subject
 * @param {string} body - Email body
 * @returns {Promise<Object>} Sent message object
 */
async function sendEmailAsUser(userEmail, to, subject, body) {
  const gmail = await getGmailServiceForUser(userEmail);

  // Build the email
  const email = [
    `To: ${to}`,
    `Subject: ${subject}`,
    'Content-Type: text/plain; charset="UTF-8"',
    '',
    body,
  ].join('\r\n');

  // Encode to base64url
  const encodedMessage = Buffer.from(email)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');

  const response = await gmail.users.messages.send({
    userId: 'me',
    requestBody: {
      raw: encodedMessage,
    },
  });

  return response.data;
}

module.exports = {
  getGmailServiceForUser,
  listUserMessages,
  sendEmailAsUser,
};

// Example usage
if (require.main === module) {
  const WORKSPACE_USER = 'user@your-workspace-domain.com';

  (async () => {
    try {
      const messages = await listUserMessages(WORKSPACE_USER, 5);
      console.log(`Found ${messages.length} messages for ${WORKSPACE_USER}`);

      messages.forEach((msg) => {
        console.log(`  Message ID: ${msg.id}`);
      });
    } catch (error) {
      console.error('Error:', error.message);
      console.log('\nCommon issues:');
      console.log('  - Service account file not found');
      console.log('  - Domain-wide delegation not enabled');
      console.log('  - Scopes not authorized in Admin Console');
      console.log('  - User email not in your Workspace domain');
    }
  })();
}
```

### 6.8 Troubleshooting Service Account Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `unauthorized_client` | Domain-wide delegation not enabled | Enable delegation in Service Account settings |
| `access_denied` | Scopes not authorized | Add scopes in Google Workspace Admin Console |
| `invalid_grant` | User not in Workspace domain | Verify user belongs to your organization |
| `File not found` | Missing service account key | Download key from Cloud Console |
| `RefreshError` | Delegation not configured | Complete steps 6.4 and 6.5 |

### 6.9 Security Best Practices for Service Accounts

1. **Principle of least privilege**: Only request the scopes you actually need
2. **Secure key storage**: Never commit service account keys to version control
3. **Key rotation**: Regularly rotate service account keys
4. **Audit logging**: Monitor service account usage in Cloud Console
5. **Limit impersonation**: Only impersonate users when necessary
6. **Environment variables**: Consider storing the service account path in environment variables

```python
import os

SERVICE_ACCOUNT_FILE = os.environ.get(
    'GMAIL_SERVICE_ACCOUNT_FILE',
    'service-account.json'
)
```

---

## Quick Reference: API Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List messages | GET | `/gmail/v1/users/{userId}/messages` |
| Get message | GET | `/gmail/v1/users/{userId}/messages/{id}` |
| Send message | POST | `/gmail/v1/users/{userId}/messages/send` |
| Delete message | DELETE | `/gmail/v1/users/{userId}/messages/{id}` |
| Trash message | POST | `/gmail/v1/users/{userId}/messages/{id}/trash` |
| List threads | GET | `/gmail/v1/users/{userId}/threads` |
| Get thread | GET | `/gmail/v1/users/{userId}/threads/{id}` |
| Create draft | POST | `/gmail/v1/users/{userId}/drafts` |
| Send draft | POST | `/gmail/v1/users/{userId}/drafts/send` |
| List labels | GET | `/gmail/v1/users/{userId}/labels` |

---

## Sources

### Gmail API

- [Gmail API Documentation](https://developers.google.com/workspace/gmail/api)
- [Gmail API Reference](https://developers.google.com/workspace/gmail/api/reference/rest)
- [Gmail API Authentication Overview](https://developers.google.com/workspace/gmail/api/auth/about-auth)

### Client Libraries

- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [Google API Node.js Client](https://github.com/googleapis/google-api-nodejs-client)

### Service Accounts (Google Workspace Only)

- [Understanding Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Domain-Wide Delegation](https://developers.google.com/workspace/guides/create-credentials#service-account)

### OAuth Setup (Part 1)

For OAuth configuration, consent screen setup, credentials creation, and scope selection, see [Part 1: OAuth Setup](./101%20-%20Gmail-API-Integration-Guide-OAuth%20part.md).
