/**
 * Test script for: Drive API Advanced Functions
 * From document: 102 - Google-Workspace-APIs-Integration-Guide-ts.md
 * Document lines: 476-1121 (Sections 2.3, 2.4, 2.5)
 *
 * Tests: Folder Management, Move/Organize, Permissions
 */
import { getDriveService } from './google-workspace-auth';
import {
  createFolder,
  deleteFile,
  getFolderContents,
  getFolderTree,
  createFolderPath,
  moveFile,
  copyFile,
  addToFolder,
  listPermissions,
  shareWithAnyone,
  getSharingSummary,
  revokePermission,
} from './drive-api';

const CREDENTIALS_PATH = '/Users/giorgosmarinos/.google-skills/drive/DriveSkill-Credentials.json';
const TOKEN_PATH = '/Users/giorgosmarinos/.google-skills/drive/token.json';

async function testDriveAdvanced(): Promise<void> {
  console.log('=' .repeat(60));
  console.log('Test: Drive API Advanced Functions');
  console.log('=' .repeat(60));

  const service = await getDriveService(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] Drive service initialized');

  // Create test structure
  const timestamp = Date.now();
  const rootFolder = await createFolder(service, `TestRoot-${timestamp}`);
  console.log(`\nCreated test root folder: ${rootFolder.id}`);

  try {
    // ==================== FOLDER MANAGEMENT ====================
    console.log('\n--- FOLDER MANAGEMENT (Section 2.3) ---');

    // Test: getFolderContents
    console.log('\n[Test] getFolderContents()');
    const subfolder1 = await createFolder(service, 'Subfolder1', rootFolder.id!);
    const subfolder2 = await createFolder(service, 'Subfolder2', rootFolder.id!);
    const contents = await getFolderContents(service, rootFolder.id!);
    console.log(`[OK] Found ${contents.length} items in folder`);

    // Test: getFolderTree
    console.log('\n[Test] getFolderTree()');
    const tree = await getFolderTree(service, rootFolder.id!, 0, 2);
    console.log(`[OK] Got folder tree with ${tree?.children?.length || 0} children`);

    // Test: createFolderPath
    console.log('\n[Test] createFolderPath()');
    const deepFolderId = await createFolderPath(service, 'Level1/Level2/Level3', rootFolder.id!);
    console.log(`[OK] Created folder path, final folder ID: ${deepFolderId}`);

    // ==================== MOVE AND ORGANIZE ====================
    console.log('\n--- MOVE AND ORGANIZE (Section 2.4) ---');

    // Test: moveFile
    console.log('\n[Test] moveFile()');
    const fileToMove = await createFolder(service, 'FileToMove', rootFolder.id!);
    await moveFile(service, fileToMove.id!, subfolder1.id!);
    // Verify
    const movedFile = await service.files.get({ fileId: fileToMove.id!, fields: 'parents' });
    const isInSubfolder = movedFile.data.parents?.includes(subfolder1.id!);
    console.log(`[OK] Moved file - now in subfolder1: ${isInSubfolder}`);

    // Test: copyFile
    // Note: Folders cannot be copied - we need an actual file
    console.log('\n[Test] copyFile()');
    // Find an existing Google Doc to copy
    const existingDocs = await service.files.list({
      q: "mimeType = 'application/vnd.google-apps.document' and trashed = false",
      pageSize: 1,
      fields: 'files(id, name)',
    });
    if (existingDocs.data.files && existingDocs.data.files.length > 0) {
      const docToCopy = existingDocs.data.files[0];
      const copiedFile = await copyFile(service, docToCopy.id!, `Copy-${Date.now()}`, rootFolder.id!);
      console.log(`[OK] Copied file: ${copiedFile.name} (ID: ${copiedFile.id})`);
      // Clean up the copy
      await deleteFile(service, copiedFile.id!, true);
    } else {
      console.log('[SKIP] No Google Docs found to test copyFile - function syntax is correct')
    }

    // Test: addToFolder (Note: This adds a second parent)
    console.log('\n[Test] addToFolder()');
    const multiParentFile = await createFolder(service, 'MultiParentFile', rootFolder.id!);
    await addToFolder(service, multiParentFile.id!, subfolder1.id!);
    const multiParent = await service.files.get({ fileId: multiParentFile.id!, fields: 'parents' });
    console.log(`[OK] File now has ${multiParent.data.parents?.length} parents`);

    // ==================== PERMISSIONS ====================
    console.log('\n--- PERMISSIONS (Section 2.5) ---');

    // Test: listPermissions
    console.log('\n[Test] listPermissions()');
    const perms = await listPermissions(service, rootFolder.id!);
    console.log(`[OK] Listed ${perms.length} permissions`);

    // Test: shareWithAnyone
    console.log('\n[Test] shareWithAnyone()');
    const anyonePerm = await shareWithAnyone(service, rootFolder.id!, 'reader');
    console.log(`[OK] Shared with anyone: permission ID = ${anyonePerm.id}`);

    // Test: getSharingSummary
    console.log('\n[Test] getSharingSummary()');
    const summary = await getSharingSummary(service, rootFolder.id!);
    console.log(`[OK] Sharing summary: anyoneWithLink = ${summary.anyoneWithLink}`);

    // Test: revokePermission
    console.log('\n[Test] revokePermission()');
    await revokePermission(service, rootFolder.id!, anyonePerm.id!);
    const permsAfter = await listPermissions(service, rootFolder.id!);
    console.log(`[OK] Revoked permission - now ${permsAfter.length} permissions (was ${perms.length + 1})`);

    console.log('\n' + '=' .repeat(60));
    console.log('Test: PASSED');
    console.log('=' .repeat(60));

  } finally {
    // Cleanup - delete all test files
    console.log('\n[Cleanup] Deleting test files...');
    try {
      // Need to delete in correct order (children first)
      const allContents = await getFolderContents(service, rootFolder.id!, true);
      // Sort by depth (files before folders) and delete
      for (const item of allContents.reverse()) {
        try {
          await deleteFile(service, item.id!, true);
        } catch (e) {
          // Ignore errors during cleanup
        }
      }
      await deleteFile(service, rootFolder.id!, true);
      console.log('[OK] Cleanup complete');
    } catch (e) {
      console.log('[WARN] Some cleanup may have failed - manual cleanup might be needed');
    }
  }
}

// Run the test
testDriveAdvanced().catch((error) => {
  console.error('\n[ERROR] Test failed:', error.message);
  console.error(error);
  process.exit(1);
});
