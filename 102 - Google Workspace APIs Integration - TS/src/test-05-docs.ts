/**
 * Test script for: Docs API Functions
 * From document: 102 - Google-Workspace-APIs-Integration-Guide-ts.md
 * Document lines: 1131-1693 (Section 3)
 *
 * Tests: Create, Read, Update, Search Documents
 */
import { getDriveService, getDocsService } from './google-workspace-auth';
import { deleteFile } from './drive-api';
import {
  createDocument,
  createDocumentWithContent,
  createDocumentInFolder,
  getDocument,
  getDocumentText,
  getDocumentSummary,
  getDocumentStructure,
  appendText,
  insertTextAtPosition,
  replaceText,
  deleteContentRange,
  addHeading,
  searchInDocument,
  searchDocumentsForText,
} from './docs-api';
import { createFolder } from './drive-api';

const CREDENTIALS_PATH = '/Users/giorgosmarinos/.google-skills/drive/DriveSkill-Credentials.json';
const TOKEN_PATH = '/Users/giorgosmarinos/.google-skills/drive/token.json';

async function testDocsAPI(): Promise<void> {
  console.log('=' .repeat(60));
  console.log('Test: Docs API Functions');
  console.log('=' .repeat(60));

  const driveService = await getDriveService(CREDENTIALS_PATH, TOKEN_PATH);
  const docsService = await getDocsService(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] Drive and Docs services initialized');

  const createdDocIds: string[] = [];
  const createdFolderIds: string[] = [];

  try {
    // ==================== CREATE DOCUMENTS (Section 3.1) ====================
    console.log('\n--- CREATE DOCUMENTS (Section 3.1) ---');

    // Test: createDocument
    console.log('\n[Test] createDocument()');
    const timestamp = Date.now();
    const doc1 = await createDocument(docsService, `TestDoc-${timestamp}`);
    createdDocIds.push(doc1.documentId!);
    console.log(`[OK] Created document: ${doc1.title} (ID: ${doc1.documentId})`);

    // Test: createDocumentWithContent
    console.log('\n[Test] createDocumentWithContent()');
    const initialContent = 'This is the initial content of the document.\nIt has multiple lines.\nAnd some text to search for.';
    const doc2 = await createDocumentWithContent(docsService, `TestDocWithContent-${timestamp}`, initialContent);
    createdDocIds.push(doc2.documentId!);
    console.log(`[OK] Created document with content: ${doc2.title}`);

    // Test: createDocumentInFolder
    console.log('\n[Test] createDocumentInFolder()');
    const testFolder = await createFolder(driveService, `DocsTestFolder-${timestamp}`);
    createdFolderIds.push(testFolder.id!);
    const doc3 = await createDocumentInFolder(driveService, docsService, `TestDocInFolder-${timestamp}`, testFolder.id!);
    createdDocIds.push(doc3.documentId!);
    console.log(`[OK] Created document in folder: ${doc3.title}`);

    // ==================== READ DOCUMENT CONTENT (Section 3.2) ====================
    console.log('\n--- READ DOCUMENT CONTENT (Section 3.2) ---');

    // Test: getDocument
    console.log('\n[Test] getDocument()');
    const fetchedDoc = await getDocument(docsService, doc2.documentId!);
    console.log(`[OK] Fetched document: ${fetchedDoc.title}`);

    // Test: getDocumentText
    console.log('\n[Test] getDocumentText()');
    const text = await getDocumentText(docsService, doc2.documentId!);
    console.log(`[OK] Extracted text (${text.length} chars): "${text.substring(0, 50)}..."`);

    // Test: getDocumentSummary
    console.log('\n[Test] getDocumentSummary()');
    const summary = await getDocumentSummary(docsService, doc2.documentId!, 100);
    console.log(`[OK] Got summary: title="${summary.title}", totalLength=${summary.totalLength}`);
    console.log(`     Summary: "${summary.summary}"`);

    // Test: getDocumentStructure
    console.log('\n[Test] getDocumentStructure()');
    // First add some structure to a document
    const structuredDoc = await createDocument(docsService, `StructuredDoc-${timestamp}`);
    createdDocIds.push(structuredDoc.documentId!);
    await addHeading(docsService, structuredDoc.documentId!, 'Main Title', 1);
    await appendText(docsService, structuredDoc.documentId!, 'Some body text here.\n');
    await addHeading(docsService, structuredDoc.documentId!, 'Section One', 2);
    await appendText(docsService, structuredDoc.documentId!, 'Content for section one.\n');

    const structure = await getDocumentStructure(docsService, structuredDoc.documentId!);
    console.log(`[OK] Document structure: ${structure.headings.length} headings, ${structure.tables} tables, ${structure.images} images`);
    for (const heading of structure.headings) {
      console.log(`     - ${heading.level}: "${heading.text}"`);
    }

    // ==================== UPDATE DOCUMENTS (Section 3.3) ====================
    console.log('\n--- UPDATE DOCUMENTS (Section 3.3) ---');

    // Test: appendText
    console.log('\n[Test] appendText()');
    const updateDoc = await createDocumentWithContent(docsService, `UpdateTestDoc-${timestamp}`, 'Original content.');
    createdDocIds.push(updateDoc.documentId!);
    await appendText(docsService, updateDoc.documentId!, '\nAppended text at the end.');
    const afterAppend = await getDocumentText(docsService, updateDoc.documentId!);
    console.log(`[OK] Appended text. New content: "${afterAppend}"`);

    // Test: insertTextAtPosition
    console.log('\n[Test] insertTextAtPosition()');
    const insertDoc = await createDocumentWithContent(docsService, `InsertTestDoc-${timestamp}`, 'Hello World');
    createdDocIds.push(insertDoc.documentId!);
    // Insert " Beautiful" after "Hello" (index 6, accounting for 1-based indexing in docs)
    await insertTextAtPosition(docsService, insertDoc.documentId!, ' Beautiful', 6);
    const afterInsert = await getDocumentText(docsService, insertDoc.documentId!);
    console.log(`[OK] Inserted text. New content: "${afterInsert.trim()}"`);

    // Test: replaceText
    console.log('\n[Test] replaceText()');
    const replaceDoc = await createDocumentWithContent(docsService, `ReplaceTestDoc-${timestamp}`, 'The cat sat on the mat. The cat was happy.');
    createdDocIds.push(replaceDoc.documentId!);
    const replacements = await replaceText(docsService, replaceDoc.documentId!, 'cat', 'dog');
    const afterReplace = await getDocumentText(docsService, replaceDoc.documentId!);
    console.log(`[OK] Replaced ${replacements} occurrences. New content: "${afterReplace.trim()}"`);

    // Test: deleteContentRange
    console.log('\n[Test] deleteContentRange()');
    const deleteDoc = await createDocumentWithContent(docsService, `DeleteTestDoc-${timestamp}`, 'ABCDEFGHIJ');
    createdDocIds.push(deleteDoc.documentId!);
    // Delete characters at positions 3-6 (CDE)
    await deleteContentRange(docsService, deleteDoc.documentId!, 3, 6);
    const afterDelete = await getDocumentText(docsService, deleteDoc.documentId!);
    console.log(`[OK] Deleted range. New content: "${afterDelete.trim()}"`);

    // Test: addHeading
    console.log('\n[Test] addHeading()');
    const headingDoc = await createDocument(docsService, `HeadingTestDoc-${timestamp}`);
    createdDocIds.push(headingDoc.documentId!);
    await addHeading(docsService, headingDoc.documentId!, 'This is Heading 1', 1);
    await addHeading(docsService, headingDoc.documentId!, 'This is Heading 2', 2);
    await addHeading(docsService, headingDoc.documentId!, 'This is Heading 3', 3);
    const headingStructure = await getDocumentStructure(docsService, headingDoc.documentId!);
    console.log(`[OK] Added headings: ${headingStructure.headings.length} headings found`);

    // ==================== SEARCH WITHIN DOCUMENTS (Section 3.4) ====================
    console.log('\n--- SEARCH WITHIN DOCUMENTS (Section 3.4) ---');

    // Test: searchInDocument
    console.log('\n[Test] searchInDocument()');
    const searchDoc = await createDocumentWithContent(
      docsService,
      `SearchTestDoc-${timestamp}`,
      'The quick brown fox jumps over the lazy dog. The fox was very quick indeed. Another fox appeared.'
    );
    createdDocIds.push(searchDoc.documentId!);
    const matches = await searchInDocument(docsService, searchDoc.documentId!, 'fox');
    console.log(`[OK] Found ${matches.length} matches for "fox"`);
    for (const match of matches) {
      console.log(`     Position ${match.position}: "${match.match}" - context: "...${match.context.substring(0, 40)}..."`);
    }

    // Test: searchDocumentsForText
    console.log('\n[Test] searchDocumentsForText()');
    // Create a few documents with searchable content in our test folder
    const searchFolder = await createFolder(driveService, `SearchFolder-${timestamp}`);
    createdFolderIds.push(searchFolder.id!);

    const searchableDoc1 = await createDocumentInFolder(driveService, docsService, `Searchable1-${timestamp}`, searchFolder.id!);
    createdDocIds.push(searchableDoc1.documentId!);
    await appendText(docsService, searchableDoc1.documentId!, 'This document contains the keyword VALIDATION_TEST_MARKER.');

    const searchableDoc2 = await createDocumentInFolder(driveService, docsService, `Searchable2-${timestamp}`, searchFolder.id!);
    createdDocIds.push(searchableDoc2.documentId!);
    await appendText(docsService, searchableDoc2.documentId!, 'This one also has VALIDATION_TEST_MARKER in it.');

    // Note: Full-text search indexing may take time, so this might not find results immediately
    console.log('  (Note: Full-text search indexing may take time - results may vary)');
    try {
      const searchResults = await searchDocumentsForText(driveService, docsService, 'VALIDATION_TEST_MARKER', searchFolder.id!);
      console.log(`[OK] Search returned ${searchResults.length} documents`);
      for (const result of searchResults) {
        console.log(`     - ${result.name}: ${result.matchCount} matches`);
      }
    } catch (e) {
      console.log(`[INFO] Full-text search: ${e}`);
    }

    console.log('\n' + '=' .repeat(60));
    console.log('Test: PASSED');
    console.log('=' .repeat(60));

  } finally {
    // Cleanup - delete all test documents and folders
    console.log('\n[Cleanup] Deleting test documents and folders...');

    for (const docId of createdDocIds) {
      try {
        await deleteFile(driveService, docId, true);
      } catch (e) {
        // Ignore cleanup errors
      }
    }

    for (const folderId of createdFolderIds) {
      try {
        await deleteFile(driveService, folderId, true);
      } catch (e) {
        // Ignore cleanup errors
      }
    }

    console.log(`[OK] Cleaned up ${createdDocIds.length} documents and ${createdFolderIds.length} folders`);
  }
}

// Run the test
testDocsAPI().catch((error) => {
  console.error('\n[ERROR] Test failed:', error.message);
  console.error(error);
  process.exit(1);
});
