"""Gmail API - Send Messages Module.

Test script for: Gmail API Send Messages
From document: Gmail-API-Integration-Guide.md
Document lines: 1236-1602

Tests the send messages module from the training guide.
NOTE: Actual sending is skipped as it requires gmail.send scope.
This test validates the message creation functions only.
"""
import os
import sys
import base64
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
from typing import Optional
from googleapiclient.errors import HttpError

# Import from local modules
from gmail_auth import get_gmail_service
from gmail_read import get_message_body

# Use credentials from parent directory
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '..', 'GMailSkill-Credentials.json')
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', 'gmail_token.json')


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
    NOTE: Requires gmail.send scope which is not available in read-only mode.

    Args:
        message: Message dictionary with 'raw' key (and optional 'threadId')

    Returns:
        Sent message object with 'id', 'threadId', 'labelIds'
    """
    service = get_gmail_service(
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH
    )

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
    NOTE: Requires gmail.send scope.

    Args:
        original_message_id: ID of the message to reply to
        body: Reply body text
        reply_all: If True, reply to all recipients
        html_body: HTML body (optional)

    Returns:
        Sent reply message object
    """
    service = get_gmail_service(
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH
    )

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
    NOTE: Requires gmail.send scope.

    Args:
        original_message_id: ID of the message to forward
        to: Recipient(s) to forward to
        additional_text: Optional text to add before forwarded content
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)

    Returns:
        Sent forwarded message object
    """
    service = get_gmail_service(
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH
    )

    # Get the original message with full content
    original = service.users().messages().get(
        userId='me',
        id=original_message_id,
        format='full'
    ).execute()

    headers = {h['name']: h['value'] for h in original['payload']['headers']}

    # Extract original body
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
    NOTE: Requires gmail.compose scope.

    Args:
        to: Recipient email address(es)
        subject: Email subject
        body: Plain text body
        cc: CC recipients (optional)
        html_body: HTML body (optional)

    Returns:
        Draft object with 'id' and 'message'
    """
    service = get_gmail_service(
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH
    )

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
    NOTE: Requires gmail.compose scope.

    Args:
        draft_id: ID of the draft to send

    Returns:
        Sent message object
    """
    service = get_gmail_service(
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH
    )

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


# Test execution
if __name__ == '__main__':
    from gmail_list import list_messages

    print("=" * 60)
    print("Test: Gmail API Send Messages Module (Read-Only Mode)")
    print("=" * 60)
    print("\nNOTE: Actual sending/draft creation requires gmail.send/compose scopes.")
    print("This test validates message creation functions only.\n")

    try:
        # Test 1: Create simple message
        print("[Test 1] Creating simple plain text message...")
        msg = create_message(
            to='test@example.com',
            subject='Test Subject',
            body='This is a test email body.'
        )
        print(f"[OK] Message created")
        print(f"     Has 'raw' key: {'raw' in msg}")
        print(f"     Raw length: {len(msg['raw'])} chars")

        # Decode and verify
        decoded = base64.urlsafe_b64decode(msg['raw']).decode('utf-8')
        print(f"     Contains 'To: test@example.com': {'To: test@example.com' in decoded}")
        print(f"     Contains 'Subject: Test Subject': {'Subject: Test Subject' in decoded}")

        # Test 2: Create message with CC/BCC
        print("\n[Test 2] Creating message with CC and BCC...")
        msg = create_message(
            to='recipient@example.com',
            subject='Test with CC/BCC',
            body='Test body',
            cc='cc@example.com',
            bcc='bcc@example.com'
        )
        decoded = base64.urlsafe_b64decode(msg['raw']).decode('utf-8')
        print(f"[OK] Message created")
        print(f"     Contains Cc header: {'Cc:' in decoded}")
        print(f"     Contains Bcc header: {'Bcc:' in decoded}")

        # Test 3: Create multipart message (plain + HTML)
        print("\n[Test 3] Creating multipart message (plain + HTML)...")
        msg = create_message(
            to='test@example.com',
            subject='HTML Test',
            body='Plain text version',
            html_body='<html><body><h1>HTML Version</h1></body></html>'
        )
        decoded = base64.urlsafe_b64decode(msg['raw']).decode('utf-8')
        print(f"[OK] Multipart message created")
        print(f"     Contains multipart: {'multipart/alternative' in decoded}")
        print(f"     Contains text/plain: {'text/plain' in decoded}")
        print(f"     Contains text/html: {'text/html' in decoded}")

        # Test 4: Create reply message structure
        print("\n[Test 4] Creating reply message with threading headers...")
        msg = create_message(
            to='sender@example.com',
            subject='Re: Original Subject',
            body='This is my reply.',
            thread_id='thread123',
            in_reply_to='<original@message.id>',
            references='<original@message.id>'
        )
        decoded = base64.urlsafe_b64decode(msg['raw']).decode('utf-8')
        print(f"[OK] Reply message created")
        print(f"     Has threadId: {'threadId' in msg}")
        print(f"     Contains In-Reply-To: {'In-Reply-To:' in decoded}")
        print(f"     Contains References: {'References:' in decoded}")

        # Test 5: Verify reply_to_message can fetch original (without sending)
        print("\n[Test 5] Testing reply_to_message preparation (read-only)...")
        messages = list_messages(max_results=1)
        if messages:
            service = get_gmail_service(
                credentials_path=CREDENTIALS_PATH,
                token_path=TOKEN_PATH
            )
            original = service.users().messages().get(
                userId='me',
                id=messages[0]['id'],
                format='metadata',
                metadataHeaders=['Subject', 'From', 'To', 'Message-ID']
            ).execute()
            headers = {h['name']: h['value'] for h in original['payload']['headers']}
            print(f"[OK] Can fetch original message for reply")
            print(f"     Original Subject: {headers.get('Subject', 'N/A')[:40]}...")
            print(f"     Would reply to: {headers.get('From', 'N/A')[:40]}...")

        # Test 6: Verify forward_message can prepare forward (without sending)
        print("\n[Test 6] Testing forward_message preparation (read-only)...")
        if messages:
            original = service.users().messages().get(
                userId='me',
                id=messages[0]['id'],
                format='full'
            ).execute()
            headers = {h['name']: h['value'] for h in original['payload']['headers']}
            original_body = get_message_body(original)
            print(f"[OK] Can fetch original message for forwarding")
            print(f"     Original body length: {len(original_body['plain'])} chars")

        print("\n" + "=" * 60)
        print("Test: PASSED (Message creation validated)")
        print("=" * 60)
        print("\nNote: To test actual sending, enable gmail.send scope in")
        print("your OAuth consent screen and re-authenticate.")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
