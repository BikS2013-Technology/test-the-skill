"""Gmail API Authentication Module.

Test script for: Gmail API Authentication
From document: Gmail-API-Integration-Guide.md
Document lines: 868-926

Tests the authentication module from the training guide.
"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define your scopes - IMPORTANT: Only request scopes that are configured
# in your OAuth Consent Screen's Data Access section
# For this test, we use only gmail.readonly which is commonly configured
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
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


if __name__ == '__main__':
    import sys

    # Use credentials from parent directory
    CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '..', 'GMailSkill-Credentials.json')
    TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', 'gmail_token.json')

    print("=" * 60)
    print("Test: Gmail API Authentication Module")
    print("=" * 60)

    # Validate credentials file exists
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"[ERROR] Credentials file not found: {CREDENTIALS_PATH}")
        sys.exit(1)
    print(f"[OK] Credentials file found: {CREDENTIALS_PATH}")

    try:
        # Attempt to authenticate
        print("\nAttempting Gmail API authentication...")
        print("(This may open a browser window for first-time authentication)")

        service = get_gmail_service(
            credentials_path=CREDENTIALS_PATH,
            token_path=TOKEN_PATH
        )

        # Verify by getting profile
        profile = service.users().getProfile(userId='me').execute()

        print(f"\n[OK] Authentication successful!")
        print(f"Email: {profile.get('emailAddress', 'N/A')}")
        print(f"Messages Total: {profile.get('messagesTotal', 'N/A')}")
        print(f"Threads Total: {profile.get('threadsTotal', 'N/A')}")

        print("\n" + "=" * 60)
        print("Test: PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
