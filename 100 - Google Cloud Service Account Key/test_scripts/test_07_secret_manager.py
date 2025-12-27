"""
Test script for: Get key from Secret Manager
From document: Google-Cloud-Service-Account-Key-Guide.md
Document lines: 563-571

Tests the Secret Manager example from the guide.
NOTE: This test validates syntax and imports only.
"""
import sys
import os


def test_secret_manager():
    """Test the Secret Manager example syntax and imports."""
    print("=" * 60)
    print("Test: Secret Manager (syntax validation)")
    print("=" * 60)

    # Verify imports from document (line 564)
    from google.cloud import secretmanager
    import json

    print("[OK] Import: from google.cloud import secretmanager")
    print("[OK] Import: import json (implicit in code)")

    # Code from document (lines 566-571):
    def get_key_from_secret_manager(project_id: str, secret_id: str) -> dict:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return json.loads(response.payload.data.decode('UTF-8'))

    print("[OK] Function get_key_from_secret_manager() defined successfully")

    # Verify the function signature is correct
    import inspect
    sig = inspect.signature(get_key_from_secret_manager)
    params = list(sig.parameters.keys())
    expected_params = ['project_id', 'secret_id']
    assert params == expected_params, f"Unexpected params: {params}"
    print(f"[OK] Function signature validated: {params}")

    # Verify return type annotation
    return_annotation = sig.return_annotation
    assert return_annotation == dict, f"Expected dict, got {return_annotation}"
    print(f"[OK] Return type annotation: {return_annotation}")

    # Verify SecretManagerServiceClient class exists
    assert hasattr(secretmanager, 'SecretManagerServiceClient'), "SecretManagerServiceClient not found"
    print("[OK] secretmanager.SecretManagerServiceClient class exists")

    print("\n" + "=" * 60)
    print("Test: PASSED (syntax and imports validated)")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_secret_manager()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
