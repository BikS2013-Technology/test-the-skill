/**
 * Test script for: Authentication Module
 * From document: 102 - Google-Workspace-APIs-Integration-Guide-ts.md
 * Document lines: 2748-2903
 *
 * Tests the authentication functions from the guide.
 */
import { getDriveService, getDocsService, getSheetsService, getSlidesService, getAllServices } from './google-workspace-auth';

const CREDENTIALS_PATH = '/Users/giorgosmarinos/.google-skills/drive/DriveSkill-Credentials.json';
const TOKEN_PATH = '/Users/giorgosmarinos/.google-skills/drive/token.json';

async function testAuthentication(): Promise<void> {
  console.log('=' .repeat(60));
  console.log('Test: Authentication Module');
  console.log('=' .repeat(60));

  // Test 1: Get Drive service
  console.log('\n[Test 1] Getting Drive service...');
  const driveService = await getDriveService(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] Drive service obtained');

  // Verify it works by listing files
  const driveResponse = await driveService.files.list({
    pageSize: 3,
    fields: 'files(id, name)',
  });
  console.log(`[OK] Drive API works - found ${driveResponse.data.files?.length || 0} files`);

  // Test 2: Get Docs service
  console.log('\n[Test 2] Getting Docs service...');
  const docsService = await getDocsService(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] Docs service obtained');

  // Test 3: Get Sheets service
  console.log('\n[Test 3] Getting Sheets service...');
  const sheetsService = await getSheetsService(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] Sheets service obtained');

  // Test 4: Get Slides service
  console.log('\n[Test 4] Getting Slides service...');
  const slidesService = await getSlidesService(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] Slides service obtained');

  // Test 5: Get all services at once
  console.log('\n[Test 5] Getting all services...');
  const allServices = await getAllServices(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] All services obtained');
  console.log(`  - drive: ${allServices.drive ? 'OK' : 'FAIL'}`);
  console.log(`  - docs: ${allServices.docs ? 'OK' : 'FAIL'}`);
  console.log(`  - sheets: ${allServices.sheets ? 'OK' : 'FAIL'}`);
  console.log(`  - slides: ${allServices.slides ? 'OK' : 'FAIL'}`);

  console.log('\n' + '=' .repeat(60));
  console.log('Test: PASSED');
  console.log('=' .repeat(60));
}

// Run the test
testAuthentication().catch((error) => {
  console.error('\n[ERROR] Test failed:', error.message);
  process.exit(1);
});
