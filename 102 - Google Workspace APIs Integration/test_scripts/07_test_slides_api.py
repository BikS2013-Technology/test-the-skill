"""
Test script for: Slides API - Presentation Operations
From document: 102 - Google-Workspace-APIs-Integration-Guide.md
Document lines: 1878-2100

Tests the Slides API operations: create, get, add_slide, get_summary.
"""
import sys
import os

# Add project path if needed
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial')

# Configuration
CREDENTIALS_PATH = os.path.expanduser('~/.google-skills/gmail/GMailSkill-Credentials.json')
TOKEN_PATH = os.path.expanduser('~/.google-skills/drive/token.json')


def get_services():
    """Get authenticated Slides and Drive services."""
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
        'slides': build('slides', 'v1', credentials=creds),
        'drive': build('drive', 'v3', credentials=creds)
    }


def test_create_presentation(slides_service):
    """Test create_presentation functionality from lines 1886-1905."""
    print("\n--- Test: create_presentation() ---")

    # Implementation from document
    title = "ValidationTest_Presentation"
    presentation_body = {
        'title': title
    }

    presentation = slides_service.presentations().create(
        body=presentation_body
    ).execute()

    print(f"[OK] Created presentation: {presentation.get('title')}")
    print(f"[INFO] Presentation ID: {presentation.get('presentationId')}")

    assert presentation.get('presentationId') is not None, "Presentation should have an ID"
    assert presentation.get('title') == title, "Presentation title should match"
    return presentation


def test_get_presentation(slides_service, presentation_id):
    """Test get_presentation functionality from lines 1948-1963."""
    print("\n--- Test: get_presentation() ---")

    # Implementation from document
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    print(f"[OK] Retrieved presentation: {presentation.get('title')}")
    print(f"[INFO] Slides count: {len(presentation.get('slides', []))}")

    assert presentation.get('presentationId') == presentation_id, "Presentation ID should match"
    return presentation


def test_add_slide(slides_service, presentation_id):
    """Test add_slide functionality from lines 2076-2099."""
    print("\n--- Test: add_slide() ---")

    # Implementation from document
    request = {
        'createSlide': {
            'slideLayoutReference': {
                'predefinedLayout': 'BLANK'
            }
        }
    }

    result = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': [request]}
    ).execute()

    replies = result.get('replies', [])
    print(f"[OK] Added new slide")
    if replies and 'createSlide' in replies[0]:
        print(f"[INFO] New slide ID: {replies[0]['createSlide'].get('objectId')}")

    return result


def test_create_presentation_with_slides(slides_service):
    """Test create_presentation_with_slides functionality from lines 1908-1941."""
    print("\n--- Test: create_presentation_with_slides() ---")

    # Create presentation (from lines 1920-1921)
    title = "ValidationTest_MultiSlidePresentation"
    presentation_body = {'title': title}
    presentation = slides_service.presentations().create(
        body=presentation_body
    ).execute()
    presentation_id = presentation['presentationId']

    # Add additional slides (from lines 1923-1939)
    slide_count = 3
    requests = []
    for i in range(slide_count - 1):  # First slide is created automatically
        requests.append({
            'createSlide': {
                'insertionIndex': i + 1,
                'slideLayoutReference': {
                    'predefinedLayout': 'BLANK'
                }
            }
        })

    if requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

    # Verify
    result = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()
    actual_count = len(result.get('slides', []))

    print(f"[OK] Created presentation with {actual_count} slides")
    print(f"[INFO] Presentation ID: {presentation_id}")

    assert actual_count == slide_count, f"Should have {slide_count} slides"
    return presentation


def test_get_presentation_summary(slides_service, presentation_id):
    """Test get_presentation_summary functionality from lines 1966-2005."""
    print("\n--- Test: get_presentation_summary() ---")

    # Get presentation (from line 1977)
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    # Build summary (from lines 1979-2003)
    summary = {
        'title': presentation.get('title'),
        'presentationId': presentation_id,
        'slideCount': len(presentation.get('slides', [])),
        'slides': []
    }

    for idx, slide in enumerate(presentation.get('slides', [])):
        slide_info = {
            'slideNumber': idx + 1,
            'objectId': slide['objectId'],
            'textContent': []
        }

        # Extract text from slide elements (from lines 1993-2001)
        for element in slide.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                text_elements = element['shape']['text'].get('textElements', [])
                for text_el in text_elements:
                    if 'textRun' in text_el:
                        content = text_el['textRun'].get('content', '').strip()
                        if content:
                            slide_info['textContent'].append(content)

        summary['slides'].append(slide_info)

    print(f"[OK] Generated presentation summary")
    print(f"[INFO] Title: {summary['title']}")
    print(f"[INFO] Slide count: {summary['slideCount']}")
    for slide in summary['slides'][:3]:  # Show first 3 slides
        print(f"[INFO]   Slide {slide['slideNumber']}: {len(slide['textContent'])} text elements")

    assert summary['title'] is not None, "Summary should have title"
    return summary


def test_delete_presentation(drive_service, presentation_id):
    """Test deleting presentation (using Drive API)."""
    print("\n--- Test: delete_presentation() ---")

    drive_service.files().delete(fileId=presentation_id).execute()

    print(f"[OK] Deleted presentation: {presentation_id}")
    return True


def test_slides_api():
    """Run all Slides API tests."""
    print("=" * 60)
    print("Test: Slides API - Presentation Operations")
    print("=" * 60)

    # Get services
    services = get_services()
    slides_service = services['slides']
    drive_service = services['drive']
    print("[OK] Slides and Drive services obtained")

    created_presentations = []

    try:
        # Test 1: Create presentation
        pres1 = test_create_presentation(slides_service)
        created_presentations.append(pres1['presentationId'])

        # Test 2: Get presentation
        test_get_presentation(slides_service, pres1['presentationId'])

        # Test 3: Add slide
        test_add_slide(slides_service, pres1['presentationId'])

        # Verify slide was added
        print("\n--- Verifying slide addition ---")
        pres = slides_service.presentations().get(
            presentationId=pres1['presentationId']
        ).execute()
        print(f"[OK] Presentation now has {len(pres.get('slides', []))} slides")

        # Test 4: Create presentation with slides
        pres2 = test_create_presentation_with_slides(slides_service)
        created_presentations.append(pres2['presentationId'])

        # Test 5: Get presentation summary
        test_get_presentation_summary(slides_service, pres1['presentationId'])

        print("\n" + "=" * 60)
        print("Test: PASSED")
        print("=" * 60)
        return True

    finally:
        # Cleanup
        print("\n--- Cleanup ---")
        for pres_id in created_presentations:
            try:
                test_delete_presentation(drive_service, pres_id)
            except Exception as e:
                print(f"[WARNING] Could not delete {pres_id}: {e}")


if __name__ == "__main__":
    try:
        test_slides_api()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
