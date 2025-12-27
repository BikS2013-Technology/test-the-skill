"""
Test script for: Drive API - File Operations
From document: 102 - Google-Workspace-APIs-Integration-Guide.md
Document lines: 2365-2488

Tests the Drive file operations: list, create, get, update, delete, restore.
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


def test_list_files(service):
    """Test list_files functionality from lines 2365-2390."""
    print("\n--- Test: list_files() ---")

    # Implementation from document
    files = []
    page_size = 10
    params = {
        'pageSize': min(page_size, 1000),
        'fields': 'nextPageToken, files(id, name, mimeType, parents, createdTime, modifiedTime, owners, size, webViewLink)',
        'orderBy': 'modifiedTime desc',
        'supportsAllDrives': True,
    }

    results = service.files().list(**params).execute()
    files = results.get('files', [])

    print(f"[OK] Listed {len(files)} files")
    if files:
        print(f"[INFO] First file: {files[0].get('name')} (ID: {files[0].get('id')})")

    assert isinstance(files, list), "files should be a list"
    return files


def test_create_folder(service):
    """Test create_folder functionality from lines 2400-2412."""
    print("\n--- Test: create_folder() ---")

    # Implementation from document
    folder_name = 'ValidationTest_Folder'
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    folder = service.files().create(
        body=metadata,
        fields='id, name, webViewLink'
    ).execute()

    print(f"[OK] Created folder: {folder.get('name')}")
    print(f"[INFO] Folder ID: {folder.get('id')}")
    print(f"[INFO] Web link: {folder.get('webViewLink')}")

    assert folder.get('id') is not None, "Folder should have an ID"
    assert folder.get('name') == folder_name, "Folder name should match"
    return folder


def test_get_file(service, file_id):
    """Test get_file functionality from lines 2392-2398."""
    print("\n--- Test: get_file() ---")

    # Implementation from document
    file_info = service.files().get(
        fileId=file_id,
        fields='*',
        supportsAllDrives=True
    ).execute()

    print(f"[OK] Retrieved file metadata")
    print(f"[INFO] Name: {file_info.get('name')}")
    print(f"[INFO] MIME Type: {file_info.get('mimeType')}")
    print(f"[INFO] Created: {file_info.get('createdTime')}")

    assert file_info.get('id') == file_id, "File ID should match"
    return file_info


def test_update_file(service, file_id):
    """Test update_file functionality from lines 2458-2470."""
    print("\n--- Test: update_file() ---")

    # Implementation from document
    metadata = {
        'name': 'ValidationTest_Folder_Updated',
        'description': 'Updated by validation test script'
    }

    updated_file = service.files().update(
        fileId=file_id,
        body=metadata,
        fields='id, name, description'
    ).execute()

    print(f"[OK] Updated file metadata")
    print(f"[INFO] New name: {updated_file.get('name')}")
    print(f"[INFO] Description: {updated_file.get('description')}")

    assert updated_file.get('name') == 'ValidationTest_Folder_Updated', "Name should be updated"
    return updated_file


def test_delete_file_to_trash(service, file_id):
    """Test delete_file (to trash) functionality from lines 2472-2480."""
    print("\n--- Test: delete_file() to trash ---")

    # Implementation from document (trash, not permanent delete)
    service.files().update(
        fileId=file_id,
        body={'trashed': True}
    ).execute()

    # Verify file is trashed
    file_info = service.files().get(
        fileId=file_id,
        fields='id, name, trashed'
    ).execute()

    print(f"[OK] File moved to trash")
    print(f"[INFO] Trashed: {file_info.get('trashed')}")

    assert file_info.get('trashed') == True, "File should be in trash"
    return True


def test_restore_file(service, file_id):
    """Test restore_file functionality from lines 2482-2487."""
    print("\n--- Test: restore_file() ---")

    # Implementation from document
    service.files().update(
        fileId=file_id,
        body={'trashed': False}
    ).execute()

    # Verify file is restored
    file_info = service.files().get(
        fileId=file_id,
        fields='id, name, trashed'
    ).execute()

    print(f"[OK] File restored from trash")
    print(f"[INFO] Trashed: {file_info.get('trashed')}")

    assert file_info.get('trashed') == False, "File should not be in trash"
    return True


def test_permanent_delete(service, file_id):
    """Test permanent delete functionality from lines 2474-2475."""
    print("\n--- Test: delete_file() permanent ---")

    # Implementation from document
    service.files().delete(fileId=file_id).execute()

    print(f"[OK] File permanently deleted")

    # Verify file no longer exists
    try:
        service.files().get(fileId=file_id).execute()
        raise AssertionError("File should not exist after permanent delete")
    except Exception as e:
        if 'File not found' in str(e) or '404' in str(e):
            print(f"[OK] Confirmed file no longer exists")
            return True
        raise


def test_drive_file_operations():
    """Run all Drive file operation tests."""
    print("=" * 60)
    print("Test: Drive API - File Operations")
    print("=" * 60)

    # Get service
    service = get_drive_service()
    print("[OK] Drive service obtained")

    # Run tests in sequence (they depend on each other)
    test_folder = None
    try:
        # Test 1: List files
        test_list_files(service)

        # Test 2: Create folder
        test_folder = test_create_folder(service)
        folder_id = test_folder.get('id')

        # Test 3: Get file metadata
        test_get_file(service, folder_id)

        # Test 4: Update file metadata
        test_update_file(service, folder_id)

        # Test 5: Delete to trash
        test_delete_file_to_trash(service, folder_id)

        # Test 6: Restore from trash
        test_restore_file(service, folder_id)

        # Test 7: Permanent delete (cleanup)
        test_permanent_delete(service, folder_id)

        print("\n" + "=" * 60)
        print("Test: PASSED")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        # Cleanup: try to delete the test folder if it was created
        if test_folder:
            try:
                service.files().delete(fileId=test_folder.get('id')).execute()
                print("[INFO] Cleaned up test folder")
            except:
                pass
        raise


if __name__ == "__main__":
    try:
        test_drive_file_operations()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
