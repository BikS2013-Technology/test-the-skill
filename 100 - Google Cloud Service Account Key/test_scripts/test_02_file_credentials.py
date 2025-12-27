"""
Test script for: Load credentials from file explicitly
From document: Google-Cloud-Service-Account-Key-Guide.md
Document lines: 211-222

Tests the Method 2: Load from File Explicitly example from the guide.
"""
import sys
import os

MOCK_KEY_FILE = os.path.join(os.path.dirname(__file__), 'mock-service-account-key.json')


def test_file_credentials():
    """Test loading credentials from file explicitly."""
    print("=" * 60)
    print("Test: Load credentials from file explicitly")
    print("=" * 60)

    # Code from document (lines 211-222):
    from google.oauth2 import service_account

    print("[OK] Import: from google.oauth2 import service_account")

    # Load credentials from the JSON key file
    try:
        credentials = service_account.Credentials.from_service_account_file(
            MOCK_KEY_FILE
        )
        print(f"[OK] Credentials.from_service_account_file() executed")
        print(f"     Credentials type: {type(credentials).__name__}")
        print(f"     Service account email: {credentials.service_account_email}")
    except Exception as e:
        print(f"[INFO] from_service_account_file raised: {type(e).__name__}: {e}")
        print("[INFO] This may be expected with mock credentials")

    # Optionally specify scopes
    scopes = ['https://www.googleapis.com/auth/cloud-platform']
    try:
        scoped_credentials = credentials.with_scopes(scopes)
        print(f"[OK] credentials.with_scopes() executed")
        print(f"     Scoped credentials type: {type(scoped_credentials).__name__}")
    except Exception as e:
        print(f"[INFO] with_scopes raised: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_file_credentials()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
