"""Gmail API - List Messages Module.

Test script for: Gmail API List Messages
From document: Gmail-API-Integration-Guide.md
Document lines: 932-1054

Tests the list messages module from the training guide.
"""
import os
import sys
from typing import Optional
from googleapiclient.errors import HttpError

# Import from local gmail_auth module
from gmail_auth import get_gmail_service, SCOPES

# Use credentials from parent directory
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '..', 'GMailSkill-Credentials.json')
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', 'gmail_token.json')


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
    service = get_gmail_service(
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH
    )
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
    service = get_gmail_service(
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH
    )
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


# Test execution
if __name__ == '__main__':
    print("=" * 60)
    print("Test: Gmail API List Messages Module")
    print("=" * 60)

    try:
        # Test 1: List basic messages
        print("\n[Test 1] Listing messages (max 5)...")
        messages = list_messages(max_results=5)
        print(f"[OK] Found {len(messages)} messages")
        if messages:
            print(f"     First message ID: {messages[0]['id']}")
            print(f"     Thread ID: {messages[0]['threadId']}")

        # Test 2: List with query
        print("\n[Test 2] Listing unread messages from last 7 days...")
        messages = list_messages(query='is:unread newer_than:7d', max_results=5)
        print(f"[OK] Found {len(messages)} unread messages")

        # Test 3: List with details
        print("\n[Test 3] Listing messages with details...")
        detailed = list_messages_with_details(
            query='newer_than:7d',
            max_results=3
        )
        print(f"[OK] Retrieved {len(detailed)} messages with details")

        for i, msg in enumerate(detailed, 1):
            print(f"\n  [{i}] Subject: {msg['subject'][:50]}...")
            print(f"      From: {msg['from'][:50]}...")
            print(f"      Date: {msg['date']}")

        # Test 4: List by label
        print("\n[Test 4] Listing INBOX messages...")
        messages = list_messages(label_ids=['INBOX'], max_results=3)
        print(f"[OK] Found {len(messages)} INBOX messages")

        print("\n" + "=" * 60)
        print("Test: PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
