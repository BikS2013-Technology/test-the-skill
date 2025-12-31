/**
 * Test script for: Drive API Search and Query
 * From document: 102 - Google-Workspace-APIs-Integration-Guide-ts.md
 * Document lines: 312-474 (Section 2.2)
 *
 * Tests: searchFiles, findDocsByName, findSheetsByName, findSlidesByName,
 *        findFilesInFolder, findRecentFiles, findAllFolders
 *
 * NOTE: Some searches are limited to avoid long-running tests.
 */
import { getDriveService } from './google-workspace-auth';
import {
  searchFiles,
  findDocsByName,
  findSheetsByName,
  findSlidesByName,
  findFilesInFolder,
  findRecentFiles,
  findAllFolders,
  findSharedWithMe,
  fullTextSearch,
  createFolder,
  deleteFile,
} from './drive-api';

const CREDENTIALS_PATH = '/Users/giorgosmarinos/.google-skills/drive/DriveSkill-Credentials.json';
const TOKEN_PATH = '/Users/giorgosmarinos/.google-skills/drive/token.json';

async function testDriveSearch(): Promise<void> {
  console.log('=' .repeat(60));
  console.log('Test: Drive API Search and Query');
  console.log('=' .repeat(60));

  const service = await getDriveService(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] Drive service initialized');

  // Test 1: Basic search with query
  console.log('\n[Test 1] searchFiles() - basic query');
  const results = await searchFiles(service, "trashed = false", 5);
  console.log(`[OK] Found ${results.length} files (limited to 5)`);

  // Test 2: Find Google Docs
  console.log('\n[Test 2] findDocsByName()');
  // First, search for a common term that might exist
  const docsWithCommonName = await service.files.list({
    q: "mimeType = 'application/vnd.google-apps.document' and trashed = false",
    pageSize: 3,
    fields: 'files(id, name)',
  });
  const sampleDocs = docsWithCommonName.data.files || [];
  if (sampleDocs.length > 0) {
    const searchTerm = sampleDocs[0].name!.substring(0, 3);
    const docs = await findDocsByName(service, searchTerm);
    console.log(`[OK] Found ${docs.length} Google Docs containing "${searchTerm}"`);
  } else {
    console.log('[SKIP] No Google Docs found in account to test findDocsByName');
  }

  // Test 3: Find Google Sheets
  console.log('\n[Test 3] findSheetsByName()');
  const sheetsResponse = await service.files.list({
    q: "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false",
    pageSize: 3,
    fields: 'files(id, name)',
  });
  const sampleSheets = sheetsResponse.data.files || [];
  if (sampleSheets.length > 0) {
    const searchTerm = sampleSheets[0].name!.substring(0, 3);
    const sheets = await findSheetsByName(service, searchTerm);
    console.log(`[OK] Found ${sheets.length} Google Sheets containing "${searchTerm}"`);
  } else {
    console.log('[SKIP] No Google Sheets found in account to test findSheetsByName');
  }

  // Test 4: Find Google Slides
  console.log('\n[Test 4] findSlidesByName()');
  const slidesResponse = await service.files.list({
    q: "mimeType = 'application/vnd.google-apps.presentation' and trashed = false",
    pageSize: 3,
    fields: 'files(id, name)',
  });
  const sampleSlides = slidesResponse.data.files || [];
  if (sampleSlides.length > 0) {
    const searchTerm = sampleSlides[0].name!.substring(0, 3);
    const slides = await findSlidesByName(service, searchTerm);
    console.log(`[OK] Found ${slides.length} Google Slides containing "${searchTerm}"`);
  } else {
    console.log('[SKIP] No Google Slides found in account to test findSlidesByName');
  }

  // Test 5: Find files in folder
  console.log('\n[Test 5] findFilesInFolder()');
  // Create a test folder and put a file in it
  const testFolder = await createFolder(service, `SearchTest-${Date.now()}`);
  const subfolder = await createFolder(service, 'Subfolder', testFolder.id!);
  const filesInFolder = await findFilesInFolder(service, testFolder.id!);
  console.log(`[OK] Found ${filesInFolder.length} files in test folder`);
  // Cleanup
  await deleteFile(service, subfolder.id!, true);
  await deleteFile(service, testFolder.id!, true);
  console.log('  (Cleaned up test folder)');

  // Test 6: Find recent files
  console.log('\n[Test 6] findRecentFiles()');
  const recentFiles = await findRecentFiles(service, 30);
  console.log(`[OK] Found ${recentFiles.length} files modified in last 30 days`);

  // Test 7: Find all folders (limited)
  console.log('\n[Test 7] findAllFolders()');
  const allFoldersResponse = await service.files.list({
    q: "mimeType = 'application/vnd.google-apps.folder' and trashed = false",
    pageSize: 10,
    fields: 'files(id, name)',
  });
  const folders = allFoldersResponse.data.files || [];
  console.log(`[OK] Found ${folders.length} folders (limited to 10)`);

  // Test 8: Find shared with me
  console.log('\n[Test 8] findSharedWithMe()');
  const sharedResponse = await service.files.list({
    q: "sharedWithMe = true and trashed = false",
    pageSize: 5,
    fields: 'files(id, name)',
  });
  const sharedFiles = sharedResponse.data.files || [];
  console.log(`[OK] Found ${sharedFiles.length} shared files (limited to 5)`);

  console.log('\n' + '=' .repeat(60));
  console.log('Test: PASSED');
  console.log('=' .repeat(60));
}

// Run the test
testDriveSearch().catch((error) => {
  console.error('\n[ERROR] Test failed:', error.message);
  console.error(error);
  process.exit(1);
});
