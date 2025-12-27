"""
Test script for: Docs API - Document Operations
From document: 102 - Google-Workspace-APIs-Integration-Guide.md
Document lines: 940-1200

Tests the Docs API operations: create, read, get_text, append, delete.
"""
import sys
import os

# Add project path if needed
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial')

# Configuration
CREDENTIALS_PATH = os.path.expanduser('~/.google-skills/gmail/GMailSkill-Credentials.json')
TOKEN_PATH = os.path.expanduser('~/.google-skills/drive/token.json')


def get_services():
    """Get authenticated Docs and Drive services."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/presentations',
    ]

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return {
        'docs': build('docs', 'v1', credentials=creds),
        'drive': build('drive', 'v3', credentials=creds)
    }


def test_create_document(docs_service):
    """Test create_document functionality from lines 942-957."""
    print("\n--- Test: create_document() ---")

    # Implementation from document
    title = "ValidationTest_Document"
    document = docs_service.documents().create(
        body={'title': title}
    ).execute()

    print(f"[OK] Created document: {document.get('title')}")
    print(f"[INFO] Document ID: {document.get('documentId')}")

    assert document.get('documentId') is not None, "Document should have an ID"
    assert document.get('title') == title, "Document title should match"
    return document


def test_create_document_with_content(docs_service):
    """Test create_document_with_content functionality from lines 960-991."""
    print("\n--- Test: create_document_with_content() ---")

    # Create the document (from lines 972-974)
    title = "ValidationTest_DocumentWithContent"
    document = docs_service.documents().create(
        body={'title': title}
    ).execute()
    document_id = document['documentId']

    # Insert content (from lines 977-989)
    content = "This is test content for validation.\nSecond paragraph here."
    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()

    print(f"[OK] Created document with content: {title}")
    print(f"[INFO] Document ID: {document_id}")
    print(f"[INFO] Content length: {len(content)} chars")

    assert document_id is not None, "Document should have an ID"
    return document


def test_get_document(docs_service, document_id):
    """Test get_document functionality from lines 1021-1036."""
    print("\n--- Test: get_document() ---")

    # Implementation from document
    document = docs_service.documents().get(
        documentId=document_id
    ).execute()

    print(f"[OK] Retrieved document: {document.get('title')}")
    print(f"[INFO] Revision ID: {document.get('revisionId')}")

    assert document.get('documentId') == document_id, "Document ID should match"
    assert 'body' in document, "Document should have body"
    return document


def test_get_document_text(docs_service, document_id):
    """Test get_document_text functionality from lines 1039-1068."""
    print("\n--- Test: get_document_text() ---")

    # Get document (from lines 1050)
    document = docs_service.documents().get(
        documentId=document_id
    ).execute()

    # Extract text (from lines 1052-1067)
    text_content = []

    def extract_text(elements):
        for element in elements:
            if 'paragraph' in element:
                for para_element in element['paragraph'].get('elements', []):
                    if 'textRun' in para_element:
                        text_content.append(para_element['textRun'].get('content', ''))
            elif 'table' in element:
                for row in element['table'].get('tableRows', []):
                    for cell in row.get('tableCells', []):
                        extract_text(cell.get('content', []))

    body = document.get('body', {})
    extract_text(body.get('content', []))

    text = ''.join(text_content)
    print(f"[OK] Extracted text from document")
    print(f"[INFO] Text length: {len(text)} chars")
    print(f"[INFO] Preview: {text[:50]}...")

    assert isinstance(text, str), "Text should be a string"
    return text


def test_append_text(docs_service, document_id):
    """Test append_text functionality from lines 1152-1177."""
    print("\n--- Test: append_text() ---")

    # Get the document to find the end index (from lines 1162-1163)
    document = docs_service.documents().get(
        documentId=document_id
    ).execute()
    end_index = document['body']['content'][-1]['endIndex'] - 1

    # Append text (from lines 1165-1177)
    text = "\n\nAppended text by validation test."
    requests = [
        {
            'insertText': {
                'location': {'index': end_index},
                'text': text
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()

    print(f"[OK] Appended text to document")
    print(f"[INFO] Appended {len(text)} chars at index {end_index}")

    return True


def test_delete_document(drive_service, document_id):
    """Test deleting document (using Drive API)."""
    print("\n--- Test: delete_document() ---")

    drive_service.files().delete(fileId=document_id).execute()

    print(f"[OK] Deleted document: {document_id}")
    return True


def test_docs_api():
    """Run all Docs API tests."""
    print("=" * 60)
    print("Test: Docs API - Document Operations")
    print("=" * 60)

    # Get services
    services = get_services()
    docs_service = services['docs']
    drive_service = services['drive']
    print("[OK] Docs and Drive services obtained")

    created_docs = []

    try:
        # Test 1: Create document
        doc1 = test_create_document(docs_service)
        created_docs.append(doc1['documentId'])

        # Test 2: Create document with content
        doc2 = test_create_document_with_content(docs_service)
        created_docs.append(doc2['documentId'])

        # Test 3: Get document
        test_get_document(docs_service, doc2['documentId'])

        # Test 4: Get document text
        test_get_document_text(docs_service, doc2['documentId'])

        # Test 5: Append text
        test_append_text(docs_service, doc2['documentId'])

        # Verify append worked
        print("\n--- Verifying append ---")
        text = test_get_document_text(docs_service, doc2['documentId'])
        assert "Appended text" in text, "Appended text should be in document"
        print("[OK] Appended text verified in document")

        print("\n" + "=" * 60)
        print("Test: PASSED")
        print("=" * 60)
        return True

    finally:
        # Cleanup - delete created documents
        print("\n--- Cleanup ---")
        for doc_id in created_docs:
            try:
                test_delete_document(drive_service, doc_id)
            except Exception as e:
                print(f"[WARNING] Could not delete {doc_id}: {e}")


if __name__ == "__main__":
    try:
        test_docs_api()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
