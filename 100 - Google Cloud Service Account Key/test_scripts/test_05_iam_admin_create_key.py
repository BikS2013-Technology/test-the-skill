"""
Test script for: Create key with google-cloud-iam
From document: Google-Cloud-Service-Account-Key-Guide.md
Document lines: 403-463

Tests the Method 1: Using google-cloud-iam example from the guide.
NOTE: This test validates syntax and imports only.
"""
import sys
import os


def test_iam_admin_create_key():
    """Test the IAM admin create key example syntax and imports."""
    print("=" * 60)
    print("Test: IAM Admin create key (syntax validation)")
    print("=" * 60)

    # Verify imports from document (lines 412-414)
    import json
    from google.cloud import iam_admin_v1
    from google.cloud.iam_admin_v1 import types

    print("[OK] Import: import json")
    print("[OK] Import: from google.cloud import iam_admin_v1")
    print("[OK] Import: from google.cloud.iam_admin_v1 import types")

    # Code from document (lines 417-454):
    def create_service_account_key(
        project_id: str,
        service_account_email: str,
        output_file: str
    ) -> types.ServiceAccountKey:
        """
        Creates a key for a service account and saves it to a file.

        Args:
            project_id: ID of the Google Cloud project
            service_account_email: Email of the service account
            output_file: Path where to save the JSON key file

        Returns:
            ServiceAccountKey object
        """
        # Create IAM client
        iam_client = iam_admin_v1.IAMClient()

        # Build the request
        request = types.CreateServiceAccountKeyRequest()
        request.name = f"projects/{project_id}/serviceAccounts/{service_account_email}"

        # Create the key
        key = iam_client.create_service_account_key(request=request)

        # The private_key_data contains the base64-encoded JSON key
        # Decode and save to file
        import base64
        key_data = base64.b64decode(key.private_key_data).decode('utf-8')

        with open(output_file, 'w') as f:
            f.write(key_data)

        print(f"Key created and saved to: {output_file}")
        print(f"Key ID: {key.name.split('/')[-1]}")

        return key

    print("[OK] Function create_service_account_key() defined successfully")

    # Verify the function signature is correct
    import inspect
    sig = inspect.signature(create_service_account_key)
    params = list(sig.parameters.keys())
    expected_params = ['project_id', 'service_account_email', 'output_file']
    assert params == expected_params, f"Unexpected params: {params}"
    print(f"[OK] Function signature validated: {params}")

    # Verify return type annotation
    return_annotation = sig.return_annotation
    print(f"[OK] Return type annotation: {return_annotation}")

    # Verify IAMClient class exists
    assert hasattr(iam_admin_v1, 'IAMClient'), "IAMClient not found"
    print("[OK] iam_admin_v1.IAMClient class exists")

    # Verify CreateServiceAccountKeyRequest exists
    assert hasattr(types, 'CreateServiceAccountKeyRequest'), "CreateServiceAccountKeyRequest not found"
    print("[OK] types.CreateServiceAccountKeyRequest class exists")

    print("\n" + "=" * 60)
    print("Test: PASSED (syntax and imports validated)")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_iam_admin_create_key()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
