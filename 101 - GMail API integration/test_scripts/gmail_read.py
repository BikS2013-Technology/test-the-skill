"""Gmail API - Read Messages and Threads Module.

Test script for: Gmail API Read Messages
From document: Gmail-API-Integration-Guide.md
Document lines: 1060-1230

Tests the read messages module from the training guide.
"""
import os
import sys
import base64
from typing import Optional
from googleapiclient.errors import HttpError

# Import from local modules
from gmail_auth import get_gmail_service
from gmail_list import list_messages

# Use credentials from parent directory
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '..', 'GMailSkill-Credentials.json')
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', 'gmail_token.json')


def get_message(message_id: str, format: str = 'full') -> dict:
    """
    Get a specific message by ID.

    Args:
        message_id: The ID of the message to retrieve
        format: 'full', 'metadata', 'minimal', or 'raw'

    Returns:
        Message object with full details
    """
    service = get_gmail_service(
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH
    )

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
    service = get_gmail_service(
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH
    )

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


# Test execution
if __name__ == '__main__':
    print("=" * 60)
    print("Test: Gmail API Read Messages Module")
    print("=" * 60)

    try:
        # Get a message to test with
        print("\n[Setup] Getting a message to read...")
        messages = list_messages(max_results=1)
        if not messages:
            print("[ERROR] No messages found in mailbox")
            sys.exit(1)

        msg_id = messages[0]['id']
        thread_id = messages[0]['threadId']
        print(f"[OK] Using message ID: {msg_id}")
        print(f"     Thread ID: {thread_id}")

        # Test 1: Get message
        print("\n[Test 1] Getting full message...")
        message = get_message(msg_id)
        print(f"[OK] Retrieved message")
        print(f"     Snippet: {message.get('snippet', '')[:80]}...")

        # Test 2: Extract headers
        print("\n[Test 2] Extracting headers...")
        headers = get_message_headers(message)
        print(f"[OK] Headers extracted")
        print(f"     Subject: {headers.get('Subject', '(none)')[:50]}")
        print(f"     From: {headers.get('From', '(none)')[:50]}")
        print(f"     Date: {headers.get('Date', '(none)')}")

        # Test 3: Extract body
        print("\n[Test 3] Extracting message body...")
        body = get_message_body(message)
        print(f"[OK] Body extracted")
        print(f"     Plain text length: {len(body['plain'])} chars")
        print(f"     HTML length: {len(body['html'])} chars")
        if body['plain']:
            print(f"     Preview: {body['plain'][:100]}...")

        # Test 4: Get thread
        print("\n[Test 4] Getting thread...")
        thread = get_thread(thread_id)
        msg_count = len(thread.get('messages', []))
        print(f"[OK] Thread retrieved")
        print(f"     Messages in thread: {msg_count}")

        # Test 5: Get thread messages with details
        print("\n[Test 5] Getting thread messages with parsed content...")
        thread_messages = get_thread_messages(thread_id)
        print(f"[OK] Retrieved {len(thread_messages)} messages")

        for i, msg in enumerate(thread_messages, 1):
            print(f"\n  [Message {i}]")
            print(f"    Subject: {msg['subject'][:40] if msg['subject'] else '(none)'}...")
            print(f"    From: {msg['from'][:40] if msg['from'] else '(none)'}...")
            print(f"    Has plain text: {'Yes' if msg['body_plain'] else 'No'}")
            print(f"    Has HTML: {'Yes' if msg['body_html'] else 'No'}")

        print("\n" + "=" * 60)
        print("Test: PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
