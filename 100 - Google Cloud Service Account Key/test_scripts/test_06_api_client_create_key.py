"""
Test script for: Create key with google-api-python-client
From document: Google-Cloud-Service-Account-Key-Guide.md
Document lines: 467-537

Tests the Method 2: Using google-api-python-client example from the guide.
NOTE: This test validates syntax and imports only.
"""
import sys
import os


def test_api_client_create_key():
    """Test the API client create key example syntax and imports."""
    print("=" * 60)
    print("Test: API Python Client create key (syntax validation)")
    print("=" * 60)

    # Verify imports from document (lines 475-479)
    import json
    import base64
    from googleapiclient import discovery
    from google.oauth2 import service_account
    import google.auth

    print("[OK] Import: import json")
    print("[OK] Import: import base64")
    print("[OK] Import: from googleapiclient import discovery")
    print("[OK] Import: from google.oauth2 import service_account")
    print("[OK] Import: import google.auth")

    # Code from document (lines 482-537):
    def create_key_with_api_client(
        service_account_email: str,
        output_file: str,
        project_id: str = None
    ) -> dict:
        """
        Creates a service account key using the IAM API.

        Args:
            service_account_email: Email of the service account
            output_file: Path to save the JSON key
            project_id: Optional project ID (uses '-' wildcard if not specified)

        Returns:
            The API response dictionary
        """
        # Get default credentials
        credentials, default_project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )

        # Build IAM service
        service = discovery.build('iam', 'v1', credentials=credentials)

        # Build resource name
        if project_id:
            name = f'projects/{project_id}/serviceAccounts/{service_account_email}'
        else:
            name = f'projects/-/serviceAccounts/{service_account_email}'

        # Create the key
        request = service.projects().serviceAccounts().keys().create(
            name=name,
            body={}  # Empty body uses defaults (JSON format, RSA 2048)
        )
        response = request.execute()

        # Decode and save the private key data
        private_key_data = base64.b64decode(response['privateKeyData']).decode('utf-8')

        with open(output_file, 'w') as f:
            f.write(private_key_data)

        print(f"Key created successfully!")
        print(f"Key name: {response['name']}")
        print(f"Saved to: {output_file}")

        return response

    print("[OK] Function create_key_with_api_client() defined successfully")

    # Verify the function signature is correct
    import inspect
    sig = inspect.signature(create_key_with_api_client)
    params = list(sig.parameters.keys())
    expected_params = ['service_account_email', 'output_file', 'project_id']
    assert params == expected_params, f"Unexpected params: {params}"
    print(f"[OK] Function signature validated: {params}")

    # Verify return type annotation
    return_annotation = sig.return_annotation
    assert return_annotation == dict, f"Expected dict, got {return_annotation}"
    print(f"[OK] Return type annotation: {return_annotation}")

    # Verify discovery.build exists
    assert hasattr(discovery, 'build'), "discovery.build not found"
    print("[OK] discovery.build function exists")

    print("\n" + "=" * 60)
    print("Test: PASSED (syntax and imports validated)")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_api_client_create_key()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
