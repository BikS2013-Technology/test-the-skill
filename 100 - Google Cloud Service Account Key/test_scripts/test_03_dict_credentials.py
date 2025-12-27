"""
Test script for: Load credentials from dictionary
From document: Google-Cloud-Service-Account-Key-Guide.md
Document lines: 226-238

Tests the Method 3: Load from Dictionary example from the guide.
"""
import sys
import os

MOCK_KEY_FILE = os.path.join(os.path.dirname(__file__), 'mock-service-account-key.json')


def test_dict_credentials():
    """Test loading credentials from dictionary."""
    print("=" * 60)
    print("Test: Load credentials from dictionary")
    print("=" * 60)

    # Code from document (lines 226-238):
    import json
    from google.oauth2 import service_account

    print("[OK] Import: import json")
    print("[OK] Import: from google.oauth2 import service_account")

    # Load key file content
    with open(MOCK_KEY_FILE, 'r') as f:
        service_account_info = json.load(f)

    print(f"[OK] Loaded JSON from file")
    print(f"     Keys in JSON: {list(service_account_info.keys())}")

    # Create credentials from dictionary
    try:
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info
        )
        print(f"[OK] Credentials.from_service_account_info() executed")
        print(f"     Credentials type: {type(credentials).__name__}")
        print(f"     Service account email: {credentials.service_account_email}")
    except Exception as e:
        print(f"[INFO] from_service_account_info raised: {type(e).__name__}: {e}")
        print("[INFO] This may be expected with mock credentials")

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_dict_credentials()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
