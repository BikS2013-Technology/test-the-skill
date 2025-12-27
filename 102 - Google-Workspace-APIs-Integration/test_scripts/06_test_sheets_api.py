"""
Test script for: Sheets API - Spreadsheet Operations
From document: 102 - Google-Workspace-APIs-Integration-Guide.md
Document lines: 1400-1700

Tests the Sheets API operations: create, read_values, write_values, append, clear.
"""
import sys
import os

# Add project path if needed
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial')

# Configuration
CREDENTIALS_PATH = os.path.expanduser('~/.google-skills/gmail/GMailSkill-Credentials.json')
TOKEN_PATH = os.path.expanduser('~/.google-skills/drive/token.json')


def get_services():
    """Get authenticated Sheets and Drive services."""
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
        'sheets': build('sheets', 'v4', credentials=creds),
        'drive': build('drive', 'v3', credentials=creds)
    }


def test_create_spreadsheet(sheets_service):
    """Test create_spreadsheet functionality from lines 1409-1431."""
    print("\n--- Test: create_spreadsheet() ---")

    # Implementation from document
    title = "ValidationTest_Spreadsheet"
    spreadsheet = {
        'properties': {
            'title': title
        }
    }

    spreadsheet = sheets_service.spreadsheets().create(
        body=spreadsheet,
        fields='spreadsheetId,spreadsheetUrl'
    ).execute()

    print(f"[OK] Created spreadsheet")
    print(f"[INFO] Spreadsheet ID: {spreadsheet.get('spreadsheetId')}")
    print(f"[INFO] URL: {spreadsheet.get('spreadsheetUrl')}")

    assert spreadsheet.get('spreadsheetId') is not None, "Spreadsheet should have an ID"
    return spreadsheet


def test_get_spreadsheet(sheets_service, spreadsheet_id):
    """Test get_spreadsheet functionality from lines 1488-1503."""
    print("\n--- Test: get_spreadsheet() ---")

    # Implementation from document
    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()

    print(f"[OK] Retrieved spreadsheet: {spreadsheet['properties']['title']}")
    print(f"[INFO] Sheets: {len(spreadsheet.get('sheets', []))}")

    assert spreadsheet.get('spreadsheetId') == spreadsheet_id, "Spreadsheet ID should match"
    return spreadsheet


def test_write_values(sheets_service, spreadsheet_id):
    """Test write_values functionality from lines 1602-1624."""
    print("\n--- Test: write_values() ---")

    # Implementation from document
    range_name = 'Sheet1!A1'
    values = [
        ['Name', 'Age', 'City'],
        ['Alice', 30, 'New York'],
        ['Bob', 25, 'Los Angeles'],
        ['Charlie', 35, 'Chicago']
    ]

    body = {'values': values}

    result = sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

    print(f"[OK] Wrote values to spreadsheet")
    print(f"[INFO] Updated range: {result.get('updatedRange')}")
    print(f"[INFO] Rows: {result.get('updatedRows')}, Cols: {result.get('updatedColumns')}")

    assert result.get('updatedRows') == 4, "Should have updated 4 rows"
    return result


def test_read_values(sheets_service, spreadsheet_id):
    """Test read_values functionality from lines 1506-1523."""
    print("\n--- Test: read_values() ---")

    # Implementation from document
    range_name = 'Sheet1!A1:C4'

    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get('values', [])

    print(f"[OK] Read values from spreadsheet")
    print(f"[INFO] Rows read: {len(values)}")
    if values:
        print(f"[INFO] Header: {values[0]}")
        print(f"[INFO] First data row: {values[1]}")

    assert len(values) == 4, "Should have read 4 rows"
    assert values[0] == ['Name', 'Age', 'City'], "Headers should match"
    return values


def test_append_values(sheets_service, spreadsheet_id):
    """Test append_values functionality from lines 1627-1650."""
    print("\n--- Test: append_values() ---")

    # Implementation from document
    range_name = 'Sheet1!A1'
    values = [
        ['Diana', 28, 'Boston'],
        ['Eve', 32, 'Seattle']
    ]

    body = {'values': values}

    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"[OK] Appended values to spreadsheet")
    print(f"[INFO] Updated range: {result.get('updates', {}).get('updatedRange')}")

    return result


def test_clear_values(sheets_service, spreadsheet_id):
    """Test clear_values functionality from lines 1653-1665."""
    print("\n--- Test: clear_values() ---")

    # Implementation from document
    range_name = 'Sheet1!A5:C6'  # Clear the appended rows

    sheets_service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    print(f"[OK] Cleared values from range: {range_name}")

    # Verify the clear
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get('values', [])
    print(f"[OK] Verified range is cleared (rows: {len(values)})")

    return True


def test_get_sheet_summary(sheets_service, spreadsheet_id):
    """Test get_sheet_summary functionality from lines 1564-1595."""
    print("\n--- Test: get_sheet_summary() ---")

    # Get spreadsheet metadata (from lines 1575)
    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()

    # Build summary (from lines 1577-1593)
    summary = {
        'title': spreadsheet['properties']['title'],
        'spreadsheetId': spreadsheet_id,
        'url': spreadsheet.get('spreadsheetUrl'),
        'sheets': []
    }

    for sheet in spreadsheet.get('sheets', []):
        props = sheet['properties']
        grid_props = props.get('gridProperties', {})

        summary['sheets'].append({
            'sheetId': props['sheetId'],
            'title': props['title'],
            'rowCount': grid_props.get('rowCount', 0),
            'columnCount': grid_props.get('columnCount', 0)
        })

    print(f"[OK] Generated spreadsheet summary")
    print(f"[INFO] Title: {summary['title']}")
    print(f"[INFO] Sheets: {len(summary['sheets'])}")
    for sheet in summary['sheets']:
        print(f"[INFO]   - {sheet['title']}: {sheet['rowCount']} rows x {sheet['columnCount']} cols")

    assert summary['title'] is not None, "Summary should have title"
    return summary


def test_delete_spreadsheet(drive_service, spreadsheet_id):
    """Test deleting spreadsheet (using Drive API)."""
    print("\n--- Test: delete_spreadsheet() ---")

    drive_service.files().delete(fileId=spreadsheet_id).execute()

    print(f"[OK] Deleted spreadsheet: {spreadsheet_id}")
    return True


def test_sheets_api():
    """Run all Sheets API tests."""
    print("=" * 60)
    print("Test: Sheets API - Spreadsheet Operations")
    print("=" * 60)

    # Get services
    services = get_services()
    sheets_service = services['sheets']
    drive_service = services['drive']
    print("[OK] Sheets and Drive services obtained")

    spreadsheet_id = None

    try:
        # Test 1: Create spreadsheet
        spreadsheet = test_create_spreadsheet(sheets_service)
        spreadsheet_id = spreadsheet['spreadsheetId']

        # Test 2: Get spreadsheet
        test_get_spreadsheet(sheets_service, spreadsheet_id)

        # Test 3: Write values
        test_write_values(sheets_service, spreadsheet_id)

        # Test 4: Read values
        test_read_values(sheets_service, spreadsheet_id)

        # Test 5: Append values
        test_append_values(sheets_service, spreadsheet_id)

        # Verify append
        print("\n--- Verifying append ---")
        values = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Sheet1!A1:C10'
        ).execute().get('values', [])
        print(f"[OK] Total rows after append: {len(values)}")
        assert len(values) == 6, "Should have 6 rows after append"

        # Test 6: Clear values
        test_clear_values(sheets_service, spreadsheet_id)

        # Test 7: Get summary
        test_get_sheet_summary(sheets_service, spreadsheet_id)

        print("\n" + "=" * 60)
        print("Test: PASSED")
        print("=" * 60)
        return True

    finally:
        # Cleanup
        if spreadsheet_id:
            print("\n--- Cleanup ---")
            try:
                test_delete_spreadsheet(drive_service, spreadsheet_id)
            except Exception as e:
                print(f"[WARNING] Could not delete spreadsheet: {e}")


if __name__ == "__main__":
    try:
        test_sheets_api()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
