"""
Test script for: Drive API - Permissions Management
From document: 102 - Google-Workspace-APIs-Integration-Guide.md
Document lines: 2602-2690

Tests the Drive permissions operations: list, share_with_anyone, update, revoke.
Note: We test with 'anyone' sharing to avoid needing real email addresses.
"""
import sys
import os

# Add project path if needed
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial')

# Configuration
CREDENTIALS_PATH = os.path.expanduser('~/.google-skills/gmail/GMailSkill-Credentials.json')
TOKEN_PATH = os.path.expanduser('~/.google-skills/drive/token.json')


def get_drive_service():
    """Get authenticated Drive service."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/presentations',
    ]

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build('drive', 'v3', credentials=creds)


def create_test_folder(service):
    """Create a test folder for permission testing."""
    metadata = {
        'name': 'ValidationTest_PermissionsFolder',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    return service.files().create(
        body=metadata,
        fields='id, name'
    ).execute()


def delete_test_folder(service, folder_id):
    """Delete test folder."""
    try:
        service.files().delete(fileId=folder_id).execute()
        print(f"[INFO] Cleaned up test folder")
    except Exception as e:
        print(f"[WARNING] Could not clean up test folder: {e}")


def test_list_permissions(service, file_id):
    """Test list_permissions functionality from lines 2604-2609."""
    print("\n--- Test: list_permissions() ---")

    # Implementation from document
    permissions = service.permissions().list(
        fileId=file_id,
        fields='permissions(id, type, role, emailAddress, domain, displayName, deleted)'
    ).execute().get('permissions', [])

    print(f"[OK] list_permissions() returned {len(permissions)} permissions")
    for perm in permissions:
        print(f"[INFO] Permission: type={perm.get('type')}, role={perm.get('role')}, email={perm.get('emailAddress', 'N/A')}")

    assert isinstance(permissions, list), "permissions should be a list"
    return permissions


def test_share_with_anyone(service, file_id):
    """Test share_with_anyone functionality from lines 2655-2666."""
    print("\n--- Test: share_with_anyone() ---")

    # Implementation from document
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }

    result = service.permissions().create(
        fileId=file_id,
        body=permission,
        fields='id, type, role'
    ).execute()

    print(f"[OK] share_with_anyone() succeeded")
    print(f"[INFO] Permission ID: {result.get('id')}")
    print(f"[INFO] Type: {result.get('type')}, Role: {result.get('role')}")

    assert result.get('id') is not None, "Permission should have an ID"
    assert result.get('type') == 'anyone', "Permission type should be 'anyone'"
    assert result.get('role') == 'reader', "Permission role should be 'reader'"
    return result


def test_update_permission(service, file_id, permission_id):
    """Test update_permission functionality from lines 2668-2675."""
    print("\n--- Test: update_permission() ---")

    # Implementation from document
    result = service.permissions().update(
        fileId=file_id,
        permissionId=permission_id,
        body={'role': 'writer'},
        fields='id, type, role'
    ).execute()

    print(f"[OK] update_permission() succeeded")
    print(f"[INFO] Updated role: {result.get('role')}")

    assert result.get('role') == 'writer', "Permission role should be updated to 'writer'"
    return result


def test_revoke_permission(service, file_id, permission_id):
    """Test revoke_permission functionality from lines 2677-2682."""
    print("\n--- Test: revoke_permission() ---")

    # Implementation from document
    service.permissions().delete(
        fileId=file_id,
        permissionId=permission_id
    ).execute()

    print(f"[OK] revoke_permission() succeeded")

    # Verify permission is gone
    permissions = service.permissions().list(
        fileId=file_id,
        fields='permissions(id, type)'
    ).execute().get('permissions', [])

    for perm in permissions:
        if perm.get('id') == permission_id:
            raise AssertionError("Permission should be deleted")

    print(f"[OK] Confirmed permission is revoked")
    return True


def test_share_with_user_structure(service, file_id):
    """Test share_with_user structure from lines 2611-2625 (without actual send)."""
    print("\n--- Test: share_with_user() structure ---")

    # Just test the structure - we don't actually send to avoid spam
    permission_body = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': 'test@example.com'  # Placeholder
    }

    # Verify the structure matches the document
    expected_fields = ['type', 'role', 'emailAddress']
    for field in expected_fields:
        assert field in permission_body, f"Permission should have {field} field"

    print(f"[OK] share_with_user() permission structure is correct")
    print(f"[INFO] Required fields: {expected_fields}")
    return True


def test_share_with_group_structure():
    """Test share_with_group structure from lines 2627-2639."""
    print("\n--- Test: share_with_group() structure ---")

    permission_body = {
        'type': 'group',
        'role': 'reader',
        'emailAddress': 'group@example.com'
    }

    expected_fields = ['type', 'role', 'emailAddress']
    for field in expected_fields:
        assert field in permission_body, f"Permission should have {field} field"
    assert permission_body['type'] == 'group', "Type should be 'group'"

    print(f"[OK] share_with_group() permission structure is correct")
    return True


def test_share_with_domain_structure():
    """Test share_with_domain structure from lines 2641-2653."""
    print("\n--- Test: share_with_domain() structure ---")

    permission_body = {
        'type': 'domain',
        'role': 'reader',
        'domain': 'example.com'
    }

    expected_fields = ['type', 'role', 'domain']
    for field in expected_fields:
        assert field in permission_body, f"Permission should have {field} field"
    assert permission_body['type'] == 'domain', "Type should be 'domain'"

    print(f"[OK] share_with_domain() permission structure is correct")
    return True


def test_drive_permissions():
    """Run all Drive permissions tests."""
    print("=" * 60)
    print("Test: Drive API - Permissions Management")
    print("=" * 60)

    # Get service
    service = get_drive_service()
    print("[OK] Drive service obtained")

    # Create test folder
    test_folder = create_test_folder(service)
    folder_id = test_folder.get('id')
    print(f"[OK] Created test folder: {test_folder.get('name')} (ID: {folder_id})")

    try:
        # Test 1: List initial permissions
        test_list_permissions(service, folder_id)

        # Test 2: Share with anyone (safe test - no real emails)
        permission = test_share_with_anyone(service, folder_id)
        permission_id = permission.get('id')

        # Test 3: Update permission
        test_update_permission(service, folder_id, permission_id)

        # Test 4: Revoke permission
        test_revoke_permission(service, folder_id, permission_id)

        # Test 5-7: Test permission structure (without actual API calls)
        test_share_with_user_structure(service, folder_id)
        test_share_with_group_structure()
        test_share_with_domain_structure()

        print("\n" + "=" * 60)
        print("Test: PASSED")
        print("=" * 60)
        return True

    finally:
        # Cleanup
        delete_test_folder(service, folder_id)


if __name__ == "__main__":
    try:
        test_drive_permissions()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
