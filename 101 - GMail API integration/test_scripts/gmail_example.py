"""Complete Gmail API Example Script.

Test script for: Gmail API Complete Example
From document: Gmail-API-Integration-Guide.md
Document lines: 1608-1707

Tests the complete example script from the training guide.
"""
import sys
import os

# Import from local modules
from gmail_list import list_messages, list_messages_with_details
from gmail_read import get_message, get_thread_messages, get_message_body, get_message_headers
from gmail_send import create_draft, create_message


def example_list_recent_unread():
    """List recent unread messages."""
    print("\n=== Recent Unread Messages ===")
    messages = list_messages_with_details(
        query='is:unread newer_than:7d',
        max_results=5
    )

    if not messages:
        print("No unread messages in the last 7 days.")
        return

    for i, msg in enumerate(messages, 1):
        print(f"\n[{i}] {msg['subject'][:60]}")
        print(f"    From: {msg['from'][:50]}")
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
        print(f"From: {msg['from'][:50] if msg['from'] else '(none)'}")
        print(f"Date: {msg['date']}")
        print(f"Subject: {msg['subject'][:50] if msg['subject'] else '(none)'}")
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

    print(f"Would reply to: {headers.get('Subject', '(No Subject)')[:50]}")
    print(f"From: {headers.get('From', '')[:50]}")

    # Note: Creating draft requires gmail.compose scope
    # Uncommenting below would create an actual draft:
    # draft = create_draft(
    #     to=headers.get('From', ''),
    #     subject=f"Re: {headers.get('Subject', '')}",
    #     body="Thank you for your message. I will get back to you soon.",
    # )
    # print(f"Draft created with ID: {draft['id']}")

    print("\n(Draft creation skipped - requires gmail.compose scope)")


# Test execution
if __name__ == '__main__':
    print("=" * 60)
    print("Test: Gmail API Complete Example")
    print("=" * 60)

    try:
        example_list_recent_unread()
        example_search_messages()
        example_read_thread()
        example_create_draft_reply()

        print("\n" + "=" * 60)
        print("Test: PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
