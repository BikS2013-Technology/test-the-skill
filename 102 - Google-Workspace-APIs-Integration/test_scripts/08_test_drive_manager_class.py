"""
Test script for: DriveManager Complete Class
From document: 102 - Google-Workspace-APIs-Integration-Guide.md
Document lines: 2344-2700

Tests the DriveManager class as a complete unit - verifying that the class
pattern works correctly and all methods can be called through a class instance.
"""
import sys
import os

# Add project path if needed
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial')

# Configuration
CREDENTIALS_PATH = os.path.expanduser('~/.google-skills/gmail/GMailSkill-Credentials.json')
TOKEN_PATH = os.path.expanduser('~/.google-skills/drive/token.json')


# =====================================================
# DriveManager Class Implementation (from document)
# =====================================================

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
]


class DriveManager:
    """Manager class for Google Drive operations (from document lines 2356-2700)."""

    def __init__(self, credentials_path=CREDENTIALS_PATH, token_path=TOKEN_PATH):
        """Initialize with credentials."""
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        self.service = build('drive', 'v3', credentials=creds)

    # ==================== FILE OPERATIONS ====================

    def list_files(self, query=None, page_size=100, order_by='modifiedTime desc'):
        """List files with optional query filter."""
        files = []
        page_token = None

        while True:
            params = {
                'pageSize': min(page_size, 1000),
                'fields': 'nextPageToken, files(id, name, mimeType, parents, createdTime, modifiedTime, owners, size, webViewLink)',
                'orderBy': order_by,
                'supportsAllDrives': True,
            }

            if query:
                params['q'] = query
            if page_token:
                params['pageToken'] = page_token

            results = self.service.files().list(**params).execute()
            files.extend(results.get('files', []))

            page_token = results.get('nextPageToken')
            if not page_token or len(files) >= page_size:
                break

        return files[:page_size]

    def get_file(self, file_id):
        """Get file metadata."""
        return self.service.files().get(
            fileId=file_id,
            fields='*',
            supportsAllDrives=True
        ).execute()

    def create_folder(self, name, parent_id=None):
        """Create a folder."""
        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            metadata['parents'] = [parent_id]

        return self.service.files().create(
            body=metadata,
            fields='id, name, webViewLink'
        ).execute()

    def update_file(self, file_id, name=None, description=None):
        """Update file metadata."""
        metadata = {}
        if name:
            metadata['name'] = name
        if description:
            metadata['description'] = description

        return self.service.files().update(
            fileId=file_id,
            body=metadata,
            fields='id, name, description'
        ).execute()

    def delete_file(self, file_id, permanent=False):
        """Delete or trash a file."""
        if permanent:
            self.service.files().delete(fileId=file_id).execute()
        else:
            self.service.files().update(
                fileId=file_id,
                body={'trashed': True}
            ).execute()

    # ==================== SEARCH OPERATIONS ====================

    def search(self, query):
        """Search with custom query."""
        return self.list_files(query=query)

    def find_by_name(self, name, exact=False):
        """Find files by name."""
        if exact:
            query = f"name = '{name}' and trashed = false"
        else:
            query = f"name contains '{name}' and trashed = false"
        return self.search(query)

    def find_docs(self, name_contains=None):
        """Find Google Docs."""
        query = "mimeType = 'application/vnd.google-apps.document' and trashed = false"
        if name_contains:
            query = f"name contains '{name_contains}' and " + query
        return self.search(query)

    def find_sheets(self, name_contains=None):
        """Find Google Sheets."""
        query = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
        if name_contains:
            query = f"name contains '{name_contains}' and " + query
        return self.search(query)

    def find_folders(self, name_contains=None):
        """Find folders."""
        query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if name_contains:
            query = f"name contains '{name_contains}' and " + query
        return self.search(query)

    # ==================== PERMISSIONS OPERATIONS ====================

    def list_permissions(self, file_id):
        """List all permissions for a file."""
        return self.service.permissions().list(
            fileId=file_id,
            fields='permissions(id, type, role, emailAddress, domain, displayName, deleted)'
        ).execute().get('permissions', [])

    def share_with_anyone(self, file_id, role='reader'):
        """Share with anyone (public link)."""
        permission = {
            'type': 'anyone',
            'role': role
        }

        return self.service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id, type, role'
        ).execute()

    def revoke_permission(self, file_id, permission_id):
        """Revoke a permission."""
        self.service.permissions().delete(
            fileId=file_id,
            permissionId=permission_id
        ).execute()


# =====================================================
# Tests
# =====================================================

def test_drive_manager_initialization():
    """Test DriveManager class initialization."""
    print("\n--- Test: DriveManager.__init__() ---")

    manager = DriveManager()

    assert manager.service is not None, "Service should be initialized"
    print("[OK] DriveManager initialized successfully")
    print(f"[INFO] Service type: {type(manager.service).__name__}")

    return manager


def test_drive_manager_list_files(manager):
    """Test DriveManager.list_files() method."""
    print("\n--- Test: DriveManager.list_files() ---")

    files = manager.list_files(page_size=5)

    print(f"[OK] list_files() returned {len(files)} files")
    if files:
        print(f"[INFO] First file: {files[0].get('name')}")

    assert isinstance(files, list), "list_files should return a list"
    return files


def test_drive_manager_folder_operations(manager):
    """Test DriveManager folder create/update/delete operations."""
    print("\n--- Test: DriveManager folder operations ---")

    # Create folder
    folder = manager.create_folder("DriveManagerTest_Folder")
    folder_id = folder.get('id')
    print(f"[OK] create_folder() - Created: {folder.get('name')}")

    # Get file metadata
    metadata = manager.get_file(folder_id)
    print(f"[OK] get_file() - Retrieved metadata")

    # Update file
    updated = manager.update_file(folder_id, name="DriveManagerTest_Folder_Updated")
    print(f"[OK] update_file() - Updated name to: {updated.get('name')}")

    # Delete (permanent)
    manager.delete_file(folder_id, permanent=True)
    print(f"[OK] delete_file() - Permanently deleted folder")

    return True


def test_drive_manager_search_methods(manager):
    """Test DriveManager search methods."""
    print("\n--- Test: DriveManager search methods ---")

    # Test find_by_name
    results = manager.find_by_name("test", exact=False)
    print(f"[OK] find_by_name() returned {len(results)} files")

    # Test find_docs
    docs = manager.find_docs()
    print(f"[OK] find_docs() returned {len(docs)} documents")

    # Test find_sheets
    sheets = manager.find_sheets()
    print(f"[OK] find_sheets() returned {len(sheets)} spreadsheets")

    # Test find_folders
    folders = manager.find_folders()
    print(f"[OK] find_folders() returned {len(folders)} folders")

    return True


def test_drive_manager_permissions(manager):
    """Test DriveManager permission methods."""
    print("\n--- Test: DriveManager permission methods ---")

    # Create a test folder
    folder = manager.create_folder("DriveManagerTest_PermFolder")
    folder_id = folder.get('id')

    try:
        # List permissions
        perms = manager.list_permissions(folder_id)
        print(f"[OK] list_permissions() returned {len(perms)} permissions")

        # Share with anyone
        perm = manager.share_with_anyone(folder_id, role='reader')
        print(f"[OK] share_with_anyone() - Created permission ID: {perm.get('id')}")

        # Revoke permission
        manager.revoke_permission(folder_id, perm.get('id'))
        print(f"[OK] revoke_permission() - Revoked permission")

    finally:
        # Cleanup
        manager.delete_file(folder_id, permanent=True)
        print(f"[INFO] Cleaned up test folder")

    return True


def test_drive_manager_class():
    """Run all DriveManager class tests."""
    print("=" * 60)
    print("Test: DriveManager Complete Class")
    print("=" * 60)

    # Test 1: Initialize
    manager = test_drive_manager_initialization()

    # Test 2: List files
    test_drive_manager_list_files(manager)

    # Test 3: Folder operations
    test_drive_manager_folder_operations(manager)

    # Test 4: Search methods
    test_drive_manager_search_methods(manager)

    # Test 5: Permission methods
    test_drive_manager_permissions(manager)

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    print("\nSummary: DriveManager class works as documented")
    print("  - Initialization: OK")
    print("  - File operations: OK")
    print("  - Search operations: OK")
    print("  - Permission operations: OK")
    return True


if __name__ == "__main__":
    try:
        test_drive_manager_class()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
