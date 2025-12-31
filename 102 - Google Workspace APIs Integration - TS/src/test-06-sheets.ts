/**
 * Test script for: Sheets API Functions
 * From document: 102 - Google-Workspace-APIs-Integration-Guide-ts.md
 * Document lines: 1697-2280 (Section 4)
 *
 * Tests: Create, Read, Update, Search/Query Spreadsheets
 */
import { getDriveService, getSheetsService } from './google-workspace-auth';
import { deleteFile } from './drive-api';
import {
  createSpreadsheet,
  createSpreadsheetWithSheets,
  createSpreadsheetWithData,
  getSpreadsheet,
  readValues,
  readAllValues,
  readMultipleRanges,
  getSheetSummary,
  writeValues,
  appendValues,
  clearValues,
  updateMultipleRanges,
  addSheet,
  deleteSheet,
  findInSheet,
  querySheet,
  getColumnValues,
  findRowByValue,
} from './sheets-api';

const CREDENTIALS_PATH = '/Users/giorgosmarinos/.google-skills/drive/DriveSkill-Credentials.json';
const TOKEN_PATH = '/Users/giorgosmarinos/.google-skills/drive/token.json';

async function testSheetsAPI(): Promise<void> {
  console.log('=' .repeat(60));
  console.log('Test: Sheets API Functions');
  console.log('=' .repeat(60));

  const driveService = await getDriveService(CREDENTIALS_PATH, TOKEN_PATH);
  const sheetsService = await getSheetsService(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] Drive and Sheets services initialized');

  const createdSpreadsheetIds: string[] = [];

  try {
    // ==================== CREATE SPREADSHEETS (Section 4.1) ====================
    console.log('\n--- CREATE SPREADSHEETS (Section 4.1) ---');

    // Test: createSpreadsheet
    console.log('\n[Test] createSpreadsheet()');
    const timestamp = Date.now();
    const sheet1 = await createSpreadsheet(sheetsService, `TestSheet-${timestamp}`);
    createdSpreadsheetIds.push(sheet1.spreadsheetId!);
    console.log(`[OK] Created spreadsheet: ${sheet1.spreadsheetId}`);
    console.log(`     URL: ${sheet1.spreadsheetUrl}`);

    // Test: createSpreadsheetWithSheets
    console.log('\n[Test] createSpreadsheetWithSheets()');
    const sheet2 = await createSpreadsheetWithSheets(sheetsService, `MultiSheetTest-${timestamp}`, [
      'Data',
      'Summary',
      'Charts',
    ]);
    createdSpreadsheetIds.push(sheet2.spreadsheetId!);
    console.log(`[OK] Created spreadsheet with ${sheet2.sheets?.length} sheets`);
    for (const s of sheet2.sheets || []) {
      console.log(`     - ${s.properties?.title}`);
    }

    // Test: createSpreadsheetWithData
    console.log('\n[Test] createSpreadsheetWithData()');
    const testData = [
      ['Name', 'Age', 'City', 'Department'],
      ['Alice', 30, 'New York', 'Engineering'],
      ['Bob', 25, 'San Francisco', 'Marketing'],
      ['Charlie', 35, 'Chicago', 'Engineering'],
      ['Diana', 28, 'Boston', 'Sales'],
    ];
    const sheet3 = await createSpreadsheetWithData(sheetsService, `DataSheet-${timestamp}`, testData);
    createdSpreadsheetIds.push(sheet3.spreadsheetId!);
    console.log(`[OK] Created spreadsheet with data: ${sheet3.spreadsheetId}`);

    // ==================== READ DATA (Section 4.2) ====================
    console.log('\n--- READ DATA (Section 4.2) ---');

    // Test: getSpreadsheet
    console.log('\n[Test] getSpreadsheet()');
    const fetchedSheet = await getSpreadsheet(sheetsService, sheet3.spreadsheetId!);
    console.log(`[OK] Fetched spreadsheet: ${fetchedSheet.properties?.title}`);

    // Test: readValues
    console.log('\n[Test] readValues()');
    const values = await readValues(sheetsService, sheet3.spreadsheetId!, 'Sheet1!A1:D3');
    console.log(`[OK] Read ${values.length} rows from range A1:D3`);
    for (const row of values) {
      console.log(`     ${row.join(', ')}`);
    }

    // Test: readAllValues
    console.log('\n[Test] readAllValues()');
    const allValues = await readAllValues(sheetsService, sheet3.spreadsheetId!);
    console.log(`[OK] Read all ${allValues.length} rows from sheet`);

    // Test: readMultipleRanges
    console.log('\n[Test] readMultipleRanges()');
    const multiRangeData = await readMultipleRanges(sheetsService, sheet3.spreadsheetId!, [
      'Sheet1!A:A',
      'Sheet1!C:C',
    ]);
    console.log(`[OK] Read ${Object.keys(multiRangeData).length} ranges`);
    for (const [range, vals] of Object.entries(multiRangeData)) {
      console.log(`     ${range}: ${vals.length} rows`);
    }

    // Test: getSheetSummary
    console.log('\n[Test] getSheetSummary()');
    const summary = await getSheetSummary(sheetsService, sheet3.spreadsheetId!);
    console.log(`[OK] Spreadsheet summary: "${summary.title}"`);
    for (const s of summary.sheets) {
      console.log(`     - ${s.title}: ${s.rowCount}x${s.columnCount}`);
    }

    // ==================== UPDATE DATA (Section 4.3) ====================
    console.log('\n--- UPDATE DATA (Section 4.3) ---');

    // Test: writeValues
    console.log('\n[Test] writeValues()');
    const writeResult = await writeValues(sheetsService, sheet3.spreadsheetId!, 'Sheet1!E1', [
      ['Status'],
      ['Active'],
      ['Inactive'],
      ['Active'],
      ['Active'],
    ]);
    console.log(`[OK] Wrote values to ${writeResult.updatedRange}`);

    // Test: appendValues
    console.log('\n[Test] appendValues()');
    const appendResult = await appendValues(sheetsService, sheet3.spreadsheetId!, 'Sheet1!A1', [
      ['Eve', 32, 'Seattle', 'HR', 'Active'],
      ['Frank', 29, 'Austin', 'Engineering', 'Active'],
    ]);
    console.log(`[OK] Appended rows to ${appendResult.updates?.updatedRange}`);

    // Test: clearValues
    console.log('\n[Test] clearValues()');
    // First add data to clear
    await writeValues(sheetsService, sheet3.spreadsheetId!, 'Sheet1!G1:G3', [
      ['ToClear'],
      ['Value1'],
      ['Value2'],
    ]);
    await clearValues(sheetsService, sheet3.spreadsheetId!, 'Sheet1!G1:G3');
    const afterClear = await readValues(sheetsService, sheet3.spreadsheetId!, 'Sheet1!G1:G3');
    console.log(`[OK] Cleared range - now has ${afterClear.length} rows`);

    // Test: updateMultipleRanges
    console.log('\n[Test] updateMultipleRanges()');
    const multiUpdateResult = await updateMultipleRanges(sheetsService, sheet3.spreadsheetId!, {
      'Sheet1!F1': [['Score']],
      'Sheet1!F2': [[85]],
      'Sheet1!F3': [[92]],
      'Sheet1!F4': [[78]],
      'Sheet1!F5': [[88]],
    });
    console.log(`[OK] Updated ${multiUpdateResult.totalUpdatedRows} rows across multiple ranges`);

    // Test: addSheet
    console.log('\n[Test] addSheet()');
    const newSheet = await addSheet(sheetsService, sheet3.spreadsheetId!, 'NewSheet');
    console.log(`[OK] Added sheet: ${newSheet.title} (ID: ${newSheet.sheetId})`);

    // Test: deleteSheet
    console.log('\n[Test] deleteSheet()');
    await deleteSheet(sheetsService, sheet3.spreadsheetId!, newSheet.sheetId!);
    const afterDelete = await getSpreadsheet(sheetsService, sheet3.spreadsheetId!);
    console.log(`[OK] Deleted sheet - now ${afterDelete.sheets?.length} sheets remain`);

    // ==================== SEARCH AND QUERY DATA (Section 4.4) ====================
    console.log('\n--- SEARCH AND QUERY DATA (Section 4.4) ---');

    // Test: findInSheet
    console.log('\n[Test] findInSheet()');
    const searchMatches = await findInSheet(sheetsService, sheet3.spreadsheetId!, 'Engineering');
    console.log(`[OK] Found ${searchMatches.length} cells containing "Engineering"`);
    for (const m of searchMatches) {
      console.log(`     Cell ${m.cell}: "${m.value}"`);
    }

    // Test: querySheet
    console.log('\n[Test] querySheet()');
    // Filter by Department column (index 3) = "Engineering"
    const queryResults = await querySheet(sheetsService, sheet3.spreadsheetId!, { 3: 'Engineering' });
    console.log(`[OK] Query returned ${queryResults.length} matching rows`);
    for (const row of queryResults) {
      console.log(`     ${row['Name']}, ${row['Department']}`);
    }

    // Test: getColumnValues
    console.log('\n[Test] getColumnValues()');
    const nameColumn = await getColumnValues(sheetsService, sheet3.spreadsheetId!, 'A');
    console.log(`[OK] Column A has ${nameColumn.length} values: ${nameColumn.slice(0, 5).join(', ')}...`);

    // Test: findRowByValue
    console.log('\n[Test] findRowByValue()');
    const foundRow = await findRowByValue(sheetsService, sheet3.spreadsheetId!, 'A', 'Bob');
    if (foundRow) {
      console.log(`[OK] Found Bob: City=${foundRow['City']}, Department=${foundRow['Department']}`);
    } else {
      console.log('[WARN] Row not found for "Bob"');
    }

    console.log('\n' + '=' .repeat(60));
    console.log('Test: PASSED');
    console.log('=' .repeat(60));

  } finally {
    // Cleanup - delete all test spreadsheets
    console.log('\n[Cleanup] Deleting test spreadsheets...');

    for (const spreadsheetId of createdSpreadsheetIds) {
      try {
        await deleteFile(driveService, spreadsheetId, true);
      } catch (e) {
        // Ignore cleanup errors
      }
    }

    console.log(`[OK] Cleaned up ${createdSpreadsheetIds.length} spreadsheets`);
  }
}

// Run the test
testSheetsAPI().catch((error) => {
  console.error('\n[ERROR] Test failed:', error.message);
  console.error(error);
  process.exit(1);
});
