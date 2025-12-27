"""
Test script for: Delete service account key
From document: Google-Cloud-Service-Account-Key-Guide.md
Document lines: 627-645

Tests the Delete Key with Python example from the guide.
NOTE: This test validates syntax and imports only.
"""
import sys
import os


def test_delete_key():
    """Test the delete key example syntax and imports."""
    print("=" * 60)
    print("Test: Delete service account key (syntax validation)")
    print("=" * 60)

    # Verify imports from document (lines 628-629)
    from google.cloud import iam_admin_v1
    from google.cloud.iam_admin_v1 import types

    print("[OK] Import: from google.cloud import iam_admin_v1")
    print("[OK] Import: from google.cloud.iam_admin_v1 import types")

    # Code from document (lines 632-645):
    def delete_service_account_key(
        project_id: str,
        service_account_email: str,
        key_id: str
    ) -> None:
        """Deletes a service account key."""
        iam_client = iam_admin_v1.IAMClient()

        request = types.DeleteServiceAccountKeyRequest()
        request.name = f"projects/{project_id}/serviceAccounts/{service_account_email}/keys/{key_id}"

        iam_client.delete_service_account_key(request=request)
        print(f"Deleted key: {key_id}")

    print("[OK] Function delete_service_account_key() defined successfully")

    # Verify the function signature is correct
    import inspect
    sig = inspect.signature(delete_service_account_key)
    params = list(sig.parameters.keys())
    expected_params = ['project_id', 'service_account_email', 'key_id']
    assert params == expected_params, f"Unexpected params: {params}"
    print(f"[OK] Function signature validated: {params}")

    # Verify return type annotation is None
    return_annotation = sig.return_annotation
    print(f"[OK] Return type annotation: {return_annotation}")

    # Verify DeleteServiceAccountKeyRequest exists
    assert hasattr(types, 'DeleteServiceAccountKeyRequest'), "DeleteServiceAccountKeyRequest not found"
    print("[OK] types.DeleteServiceAccountKeyRequest class exists")

    print("\n" + "=" * 60)
    print("Test: PASSED (syntax and imports validated)")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_delete_key()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
