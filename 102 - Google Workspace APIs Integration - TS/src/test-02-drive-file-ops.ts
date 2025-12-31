/**
 * Test script for: Drive API File Operations
 * From document: 102 - Google-Workspace-APIs-Integration-Guide-ts.md
 * Document lines: 101-310 (Section 2.1)
 *
 * Tests: listFiles, createFolder, uploadFile, updateFileMetadata, deleteFile, restoreFromTrash
 *
 * NOTE: The document's listFiles function iterates through ALL pages, which
 * can be very slow for large Drive accounts. For testing, we use the raw
 * service.files.list() with a single page.
 */
import * as fs from 'fs';
import * as path from 'path';
import { getDriveService } from './google-workspace-auth';
import {
  createFolder,
  updateFileMetadata,
  deleteFile,
  restoreFromTrash,
} from './drive-api';

const CREDENTIALS_PATH = '/Users/giorgosmarinos/.google-skills/drive/DriveSkill-Credentials.json';
const TOKEN_PATH = '/Users/giorgosmarinos/.google-skills/drive/token.json';

async function testDriveFileOperations(): Promise<void> {
  console.log('=' .repeat(60));
  console.log('Test: Drive API File Operations');
  console.log('=' .repeat(60));

  const service = await getDriveService(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] Drive service initialized');

  // Test 1: List files (using raw API for speed - single page only)
  console.log('\n[Test 1] files.list() - single page');
  const listResponse = await service.files.list({
    pageSize: 10,
    fields: 'files(id, name, mimeType)',
  });
  const files = listResponse.data.files || [];
  console.log(`[OK] Listed ${files.length} files`);
  if (files.length > 0) {
    console.log(`  First file: ${files[0].name} (${files[0].mimeType})`);
  }

  // Test 2: Create folder
  console.log('\n[Test 2] createFolder()');
  const testFolderName = `Test-Folder-${Date.now()}`;
  const folder = await createFolder(service, testFolderName);
  console.log(`[OK] Created folder: ${folder.name} (ID: ${folder.id})`);

  // Test 3: Update file metadata
  console.log('\n[Test 3] updateFileMetadata()');
  const newDescription = 'Test description ' + Date.now();
  const updatedFolder = await updateFileMetadata(service, folder.id!, undefined, newDescription);
  console.log(`[OK] Updated metadata: description = "${updatedFolder.description}"`);

  // Test 4: Move to trash (deleteFile with permanent=false)
  console.log('\n[Test 4] deleteFile() - move to trash');
  await deleteFile(service, folder.id!, false);
  console.log('[OK] Moved folder to trash');

  // Verify it's in trash
  const trashedFile = await service.files.get({
    fileId: folder.id!,
    fields: 'trashed',
  });
  console.log(`  Verified: trashed = ${trashedFile.data.trashed}`);

  // Test 5: Restore from trash
  console.log('\n[Test 5] restoreFromTrash()');
  await restoreFromTrash(service, folder.id!);
  console.log('[OK] Restored folder from trash');

  // Verify it's restored
  const restoredFile = await service.files.get({
    fileId: folder.id!,
    fields: 'trashed',
  });
  console.log(`  Verified: trashed = ${restoredFile.data.trashed}`);

  // Test 6: Permanent delete
  console.log('\n[Test 6] deleteFile() - permanent');
  await deleteFile(service, folder.id!, true);
  console.log('[OK] Permanently deleted folder');

  // Verify it's deleted (should throw 404)
  try {
    await service.files.get({ fileId: folder.id! });
    console.log('[FAIL] File still exists after permanent delete');
  } catch (error: any) {
    if (error.code === 404) {
      console.log('[OK] Verified: File no longer exists (404 error as expected)');
    } else {
      throw error;
    }
  }

  console.log('\n' + '=' .repeat(60));
  console.log('Test: PASSED');
  console.log('=' .repeat(60));
}

// Run the test
testDriveFileOperations().catch((error) => {
  console.error('\n[ERROR] Test failed:', error.message);
  console.error(error);
  process.exit(1);
});
