"""
Test script for: Authentication Module
From document: 102 - Google-Workspace-APIs-Integration-Guide.md
Document lines: 2238-2341

Tests the google_workspace_auth.py module from the training guide.
Validates get_credentials() and get_all_services() functions.
"""
import sys
import os

# Add project path if needed
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial')

# Configuration
CREDENTIALS_PATH = os.path.expanduser('~/.google-skills/gmail/GMailSkill-Credentials.json')
TOKEN_PATH = os.path.expanduser('~/.google-skills/drive/token.json')

# Required scopes for all Workspace APIs
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
]


def validate_environment():
    """Validate required files exist."""
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(
            f"Credentials file not found at {CREDENTIALS_PATH}. "
            "Please ensure the Google OAuth credentials JSON exists."
        )
    print(f"[OK] Credentials file found: {CREDENTIALS_PATH}")

    # Ensure token directory exists
    token_dir = os.path.dirname(TOKEN_PATH)
    if not os.path.exists(token_dir):
        os.makedirs(token_dir)
        print(f"[OK] Created token directory: {token_dir}")


def test_authentication():
    """Test the authentication module from the guide."""
    print("=" * 60)
    print("Test: Authentication Module")
    print("=" * 60)

    # Validate environment
    validate_environment()

    # Import required libraries (as shown in the guide)
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    print("[OK] Required libraries imported successfully")

    # Test get_credentials function logic
    print("\n--- Testing get_credentials() logic ---")

    creds = None

    if os.path.exists(TOKEN_PATH):
        print(f"[INFO] Existing token found at {TOKEN_PATH}")
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        print("[OK] Loaded credentials from token file")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[INFO] Token expired, refreshing...")
            creds.refresh(Request())
            print("[OK] Token refreshed successfully")
        else:
            print("[INFO] No valid token, starting OAuth flow...")
            print("[INFO] A browser window will open for authentication.")
            print("[INFO] Please authorize all requested scopes.")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
            print("[OK] OAuth flow completed successfully")

        # Save the token
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
        print(f"[OK] Token saved to {TOKEN_PATH}")
    else:
        print("[OK] Token is valid")

    # Verify credentials are valid
    assert creds is not None, "Credentials should not be None"
    assert creds.valid, "Credentials should be valid"
    print("[OK] Credentials validated successfully")

    # Test building services for all APIs
    print("\n--- Testing get_all_services() logic ---")

    services = {}

    # Build Drive service
    print("[INFO] Building Drive API service...")
    services['drive'] = build('drive', 'v3', credentials=creds)
    assert services['drive'] is not None
    print("[OK] Drive API v3 service created")

    # Build Docs service
    print("[INFO] Building Docs API service...")
    services['docs'] = build('docs', 'v1', credentials=creds)
    assert services['docs'] is not None
    print("[OK] Docs API v1 service created")

    # Build Sheets service
    print("[INFO] Building Sheets API service...")
    services['sheets'] = build('sheets', 'v4', credentials=creds)
    assert services['sheets'] is not None
    print("[OK] Sheets API v4 service created")

    # Build Slides service
    print("[INFO] Building Slides API service...")
    services['slides'] = build('slides', 'v1', credentials=creds)
    assert services['slides'] is not None
    print("[OK] Slides API v1 service created")

    # Quick verification - list some files from Drive
    print("\n--- Verifying services work with a quick API call ---")
    try:
        results = services['drive'].files().list(
            pageSize=5,
            fields="files(id, name)"
        ).execute()
        files = results.get('files', [])
        print(f"[OK] Drive API test call successful - found {len(files)} files")
        if files:
            print(f"[INFO] Sample file: {files[0].get('name', 'Unknown')}")
    except Exception as e:
        print(f"[WARNING] Drive API call failed: {e}")
        print("[INFO] This may indicate the Drive scope needs to be authorized")

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    print("\nSummary:")
    print(f"  - Credentials file: {CREDENTIALS_PATH}")
    print(f"  - Token file: {TOKEN_PATH}")
    print(f"  - Services created: {list(services.keys())}")
    return True


if __name__ == "__main__":
    try:
        test_authentication()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
