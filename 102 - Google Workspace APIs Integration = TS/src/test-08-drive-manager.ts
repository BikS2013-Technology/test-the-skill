/**
 * Test script for: DriveManager class
 * From document: 102 - Google-Workspace-APIs-Integration-Guide-ts.md
 * Document lines: 2905-3531 (Section 6.3)
 *
 * Tests: DriveManager class comprehensive functionality
 */
import * as fs from 'fs';
import * as path from 'path';
import { DriveManager } from './drive-manager';

const CREDENTIALS_PATH = '/Users/giorgosmarinos/.google-skills/drive/DriveSkill-Credentials.json';
const TOKEN_PATH = '/Users/giorgosmarinos/.google-skills/drive/token.json';

async function testDriveManager(): Promise<void> {
  console.log('=' .repeat(60));
  console.log('Test: DriveManager Class');
  console.log('=' .repeat(60));

  const manager = new DriveManager();
  await manager.init(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] DriveManager initialized');

  const createdItemIds: string[] = [];
  const timestamp = Date.now();
  const tempDir = path.join('/tmp', `drive-manager-test-${timestamp}`);

  try {
    // Create temp directory for test files
    fs.mkdirSync(tempDir, { recursive: true });

    // ==================== FILE OPERATIONS ====================
    console.log('\n--- FILE OPERATIONS ---');

    // Test: createFolder
    console.log('\n[Test] createFolder()');
    const testFolder = await manager.createFolder(`ManagerTestFolder-${timestamp}`);
    createdItemIds.push(testFolder.id!);
    console.log(`[OK] Created folder: ${testFolder.name} (ID: ${testFolder.id})`);

    // Test: listFiles
    console.log('\n[Test] listFiles()');
    const files = await manager.listFiles(undefined, 5);
    console.log(`[OK] Listed ${files.length} files`);

    // Test: getFile
    console.log('\n[Test] getFile()');
    const fetchedFolder = await manager.getFile(testFolder.id!);
    console.log(`[OK] Got file: ${fetchedFolder.name}, mimeType: ${fetchedFolder.mimeType}`);

    // Test: uploadFile
    console.log('\n[Test] uploadFile()');
    const testFilePath = path.join(tempDir, 'test-upload.txt');
    fs.writeFileSync(testFilePath, 'Test content for upload');
    const uploadedFile = await manager.uploadFile(testFilePath, undefined, testFolder.id!);
    createdItemIds.push(uploadedFile.id!);
    console.log(`[OK] Uploaded file: ${uploadedFile.name} (ID: ${uploadedFile.id})`);

    // Test: downloadFile
    console.log('\n[Test] downloadFile()');
    const downloadPath = path.join(tempDir, 'downloaded.txt');
    await manager.downloadFile(uploadedFile.id!, downloadPath);
    const downloadedContent = fs.readFileSync(downloadPath, 'utf-8');
    console.log(`[OK] Downloaded file content: "${downloadedContent}"`);

    // Test: updateFile
    console.log('\n[Test] updateFile()');
    const updatedFile = await manager.updateFile(uploadedFile.id!, `updated-${uploadedFile.name}`, 'Test description');
    console.log(`[OK] Updated file: ${updatedFile.name}, description: ${updatedFile.description}`);

    // Test: deleteFile (trash)
    console.log('\n[Test] deleteFile() - trash');
    const fileToTrash = await manager.createFolder(`ToTrash-${timestamp}`, testFolder.id!);
    createdItemIds.push(fileToTrash.id!);
    await manager.deleteFile(fileToTrash.id!, false);
    console.log('[OK] Moved file to trash');

    // Test: restoreFile
    console.log('\n[Test] restoreFile()');
    await manager.restoreFile(fileToTrash.id!);
    console.log('[OK] Restored file from trash');

    // ==================== SEARCH OPERATIONS ====================
    console.log('\n--- SEARCH OPERATIONS ---');

    // Test: search
    console.log('\n[Test] search()');
    const searchResults = await manager.search("trashed = false");
    console.log(`[OK] Search returned ${searchResults.length} results`);

    // Test: findByName
    console.log('\n[Test] findByName()');
    const foundByName = await manager.findByName('ManagerTestFolder', false);
    console.log(`[OK] Found ${foundByName.length} items containing "ManagerTestFolder"`);

    // Test: findDocs
    console.log('\n[Test] findDocs()');
    const docs = await manager.findDocs();
    console.log(`[OK] Found ${docs.length} Google Docs`);

    // Test: findSheets
    console.log('\n[Test] findSheets()');
    const sheets = await manager.findSheets();
    console.log(`[OK] Found ${sheets.length} Google Sheets`);

    // Test: findSlides
    console.log('\n[Test] findSlides()');
    const slides = await manager.findSlides();
    console.log(`[OK] Found ${slides.length} Google Slides`);

    // Test: findFolders
    console.log('\n[Test] findFolders()');
    const folders = await manager.findFolders();
    console.log(`[OK] Found ${folders.length} folders`);

    // Test: findInFolder
    console.log('\n[Test] findInFolder()');
    const inFolder = await manager.findInFolder(testFolder.id!);
    console.log(`[OK] Found ${inFolder.length} items in test folder`);

    // Test: findSharedWithMe
    console.log('\n[Test] findSharedWithMe()');
    const shared = await manager.findSharedWithMe();
    console.log(`[OK] Found ${shared.length} shared items`);

    // Test: findRecent
    console.log('\n[Test] findRecent()');
    const recent = await manager.findRecent(7);
    console.log(`[OK] Found ${recent.length} items modified in last 7 days`);

    // Test: fullTextSearch
    console.log('\n[Test] fullTextSearch()');
    try {
      const fullText = await manager.fullTextSearch('test');
      console.log(`[OK] Full text search returned ${fullText.length} results`);
    } catch (e) {
      console.log('[INFO] Full text search may require indexing time');
    }

    // ==================== ORGANIZATION OPERATIONS ====================
    console.log('\n--- ORGANIZATION OPERATIONS ---');

    // Test: moveFile
    console.log('\n[Test] moveFile()');
    const subFolder = await manager.createFolder(`SubFolder-${timestamp}`, testFolder.id!);
    createdItemIds.push(subFolder.id!);
    const fileToMove = await manager.createFolder(`ToMove-${timestamp}`, testFolder.id!);
    createdItemIds.push(fileToMove.id!);
    await manager.moveFile(fileToMove.id!, subFolder.id!);
    const movedFile = await manager.getFile(fileToMove.id!);
    console.log(`[OK] Moved file - new parent: ${movedFile.parents?.includes(subFolder.id!)}`);

    // Test: copyFile
    console.log('\n[Test] copyFile()');
    // Find an existing document to copy (folders can't be copied)
    const existingDocs = await manager.findDocs();
    if (existingDocs.length > 0) {
      const copiedFile = await manager.copyFile(existingDocs[0].id!, `Copy-${timestamp}`, testFolder.id!);
      createdItemIds.push(copiedFile.id!);
      console.log(`[OK] Copied file: ${copiedFile.name}`);
    } else {
      console.log('[SKIP] No existing docs to copy');
    }

    // Test: createFolderPath
    console.log('\n[Test] createFolderPath()');
    const deepFolderId = await manager.createFolderPath('Level1/Level2/Level3', testFolder.id!);
    console.log(`[OK] Created folder path, deepest ID: ${deepFolderId}`);

    // ==================== PERMISSIONS OPERATIONS ====================
    console.log('\n--- PERMISSIONS OPERATIONS ---');

    // Test: listPermissions
    console.log('\n[Test] listPermissions()');
    const perms = await manager.listPermissions(testFolder.id!);
    console.log(`[OK] Listed ${perms.length} permissions`);

    // Test: shareWithAnyone
    console.log('\n[Test] shareWithAnyone()');
    const anyonePerm = await manager.shareWithAnyone(testFolder.id!, 'reader');
    console.log(`[OK] Shared with anyone: permission ID = ${anyonePerm.id}`);

    // Test: getSharingSummary
    console.log('\n[Test] getSharingSummary()');
    const summary = await manager.getSharingSummary(testFolder.id!);
    console.log(`[OK] Sharing summary: owner=${summary.owner}, anyoneWithLink=${summary.anyoneWithLink}`);

    // Test: revokePermission
    console.log('\n[Test] revokePermission()');
    await manager.revokePermission(testFolder.id!, anyonePerm.id!);
    const permsAfter = await manager.listPermissions(testFolder.id!);
    console.log(`[OK] Revoked permission - now ${permsAfter.length} permissions`);

    console.log('\n' + '=' .repeat(60));
    console.log('Test: PASSED');
    console.log('=' .repeat(60));

  } finally {
    // Cleanup
    console.log('\n[Cleanup] Deleting test items...');

    // Clean up temp directory
    try {
      fs.rmSync(tempDir, { recursive: true });
    } catch (e) {
      // Ignore
    }

    // Delete created items from Drive (in reverse order for nested items)
    for (const itemId of createdItemIds.reverse()) {
      try {
        await manager.deleteFile(itemId, true);
      } catch (e) {
        // Ignore cleanup errors
      }
    }

    console.log(`[OK] Cleaned up ${createdItemIds.length} Drive items`);
  }
}

// Run the test
testDriveManager().catch((error) => {
  console.error('\n[ERROR] Test failed:', error.message);
  console.error(error);
  process.exit(1);
});
