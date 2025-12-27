"""
Test script for: Drive API - Search Functions
From document: 102 - Google-Workspace-APIs-Integration-Guide.md
Document lines: 2489-2538

Tests the Drive search operations: search, find_by_name, find_docs, find_sheets,
find_slides, find_folders, find_in_folder, find_shared_with_me.
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


def list_files_with_query(service, query=None, page_size=100):
    """Base search implementation from document lines 2491-2493."""
    files = []
    page_token = None

    params = {
        'pageSize': min(page_size, 1000),
        'fields': 'nextPageToken, files(id, name, mimeType, parents, createdTime, modifiedTime)',
        'supportsAllDrives': True,
    }

    if query:
        params['q'] = query

    results = service.files().list(**params).execute()
    files = results.get('files', [])

    return files


def test_search_custom_query(service):
    """Test search with custom query from lines 2491-2493."""
    print("\n--- Test: search() with custom query ---")

    # Implementation from document
    query = "trashed = false"
    files = list_files_with_query(service, query=query, page_size=10)

    print(f"[OK] Custom query search returned {len(files)} files")
    assert isinstance(files, list), "search should return a list"
    return files


def test_find_by_name(service):
    """Test find_by_name functionality from lines 2495-2501."""
    print("\n--- Test: find_by_name() ---")

    # Test contains search (from document line 2500)
    name = "test"  # Common pattern that might exist
    query = f"name contains '{name}' and trashed = false"
    files = list_files_with_query(service, query=query)

    print(f"[OK] find_by_name(contains) returned {len(files)} files")
    if files:
        print(f"[INFO] Sample: {files[0].get('name')}")

    # Test exact search (from document line 2498)
    # We won't assert on results as the name might not exist
    query_exact = f"name = 'NonExistentFile12345' and trashed = false"
    files_exact = list_files_with_query(service, query=query_exact)
    print(f"[OK] find_by_name(exact) query executed successfully")

    return True


def test_find_docs(service):
    """Test find_docs functionality from lines 2503-2508."""
    print("\n--- Test: find_docs() ---")

    # Implementation from document
    query = "mimeType = 'application/vnd.google-apps.document' and trashed = false"
    files = list_files_with_query(service, query=query)

    print(f"[OK] find_docs() returned {len(files)} Google Docs")
    if files:
        print(f"[INFO] Sample doc: {files[0].get('name')}")

    # All returned files should be documents
    for f in files:
        assert f.get('mimeType') == 'application/vnd.google-apps.document', \
            f"Expected document, got {f.get('mimeType')}"

    return files


def test_find_sheets(service):
    """Test find_sheets functionality from lines 2510-2515."""
    print("\n--- Test: find_sheets() ---")

    # Implementation from document
    query = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    files = list_files_with_query(service, query=query)

    print(f"[OK] find_sheets() returned {len(files)} Google Sheets")
    if files:
        print(f"[INFO] Sample sheet: {files[0].get('name')}")

    # All returned files should be spreadsheets
    for f in files:
        assert f.get('mimeType') == 'application/vnd.google-apps.spreadsheet', \
            f"Expected spreadsheet, got {f.get('mimeType')}"

    return files


def test_find_slides(service):
    """Test find_slides functionality from lines 2517-2522."""
    print("\n--- Test: find_slides() ---")

    # Implementation from document
    query = "mimeType = 'application/vnd.google-apps.presentation' and trashed = false"
    files = list_files_with_query(service, query=query)

    print(f"[OK] find_slides() returned {len(files)} Google Slides")
    if files:
        print(f"[INFO] Sample presentation: {files[0].get('name')}")

    # All returned files should be presentations
    for f in files:
        assert f.get('mimeType') == 'application/vnd.google-apps.presentation', \
            f"Expected presentation, got {f.get('mimeType')}"

    return files


def test_find_folders(service):
    """Test find_folders functionality from lines 2524-2529."""
    print("\n--- Test: find_folders() ---")

    # Implementation from document
    query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    files = list_files_with_query(service, query=query)

    print(f"[OK] find_folders() returned {len(files)} folders")
    if files:
        print(f"[INFO] Sample folder: {files[0].get('name')}")

    # All returned files should be folders
    for f in files:
        assert f.get('mimeType') == 'application/vnd.google-apps.folder', \
            f"Expected folder, got {f.get('mimeType')}"

    return files


def test_find_in_folder(service):
    """Test find_in_folder functionality from lines 2531-2534."""
    print("\n--- Test: find_in_folder() ---")

    # First, get a folder to search in
    folders = list_files_with_query(
        service,
        query="mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        page_size=5
    )

    if folders:
        folder_id = folders[0].get('id')
        folder_name = folders[0].get('name')

        # Implementation from document
        query = f"'{folder_id}' in parents and trashed = false"
        files = list_files_with_query(service, query=query)

        print(f"[OK] find_in_folder() for '{folder_name}' returned {len(files)} items")
        if files:
            print(f"[INFO] Sample item: {files[0].get('name')}")
    else:
        print("[INFO] No folders found to test find_in_folder()")

    return True


def test_find_shared_with_me(service):
    """Test find_shared_with_me functionality from lines 2536-2538."""
    print("\n--- Test: find_shared_with_me() ---")

    # Implementation from document
    query = "sharedWithMe = true and trashed = false"
    files = list_files_with_query(service, query=query)

    print(f"[OK] find_shared_with_me() returned {len(files)} shared files")
    if files:
        print(f"[INFO] Sample shared file: {files[0].get('name')}")

    return files


def test_drive_search_functions():
    """Run all Drive search function tests."""
    print("=" * 60)
    print("Test: Drive API - Search Functions")
    print("=" * 60)

    # Get service
    service = get_drive_service()
    print("[OK] Drive service obtained")

    # Run all search tests
    test_search_custom_query(service)
    test_find_by_name(service)
    test_find_docs(service)
    test_find_sheets(service)
    test_find_slides(service)
    test_find_folders(service)
    test_find_in_folder(service)
    test_find_shared_with_me(service)

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_drive_search_functions()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
