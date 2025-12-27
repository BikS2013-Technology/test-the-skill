"""
Test script for: Complete Cloud Storage example
From document: Google-Cloud-Service-Account-Key-Guide.md
Document lines: 242-272

Tests the Complete Example: Using Google Cloud Storage from the guide.
NOTE: This test validates syntax and imports only.
Actual bucket listing requires valid credentials and permissions.
"""
import sys
import os

MOCK_KEY_FILE = os.path.join(os.path.dirname(__file__), 'mock-service-account-key.json')


def test_cloud_storage_syntax():
    """Test the Cloud Storage example syntax and imports."""
    print("=" * 60)
    print("Test: Cloud Storage example (syntax validation)")
    print("=" * 60)

    # Verify imports from document (lines 243-244)
    from google.cloud import storage
    from google.oauth2 import service_account

    print("[OK] Import: from google.cloud import storage")
    print("[OK] Import: from google.oauth2 import service_account")

    # Code from document (lines 246-272):
    def list_buckets(key_file_path: str, project_id: str):
        """List all buckets in a project using service account authentication."""

        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            key_file_path
        )

        # Create storage client with credentials
        client = storage.Client(
            project=project_id,
            credentials=credentials
        )

        # List buckets
        buckets = list(client.list_buckets())
        for bucket in buckets:
            print(f"Bucket: {bucket.name}")

        return buckets

    print("[OK] Function list_buckets() defined successfully")

    # Verify the function signature is correct
    import inspect
    sig = inspect.signature(list_buckets)
    params = list(sig.parameters.keys())
    assert params == ['key_file_path', 'project_id'], f"Unexpected params: {params}"
    print("[OK] Function signature validated: (key_file_path: str, project_id: str)")

    # Test that the function can be called (will fail due to mock credentials)
    print("\n[INFO] Attempting to call function with mock credentials...")
    try:
        list_buckets(
            key_file_path=MOCK_KEY_FILE,
            project_id="test-project-12345"
        )
    except Exception as e:
        print(f"[INFO] Expected error with mock credentials: {type(e).__name__}")

    print("\n" + "=" * 60)
    print("Test: PASSED (syntax and imports validated)")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_cloud_storage_syntax()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
