/**
 * Google Docs API Functions - Implementation from document lines 1131-1693
 *
 * This module implements all Docs API functions from Section 3 of the guide.
 */
import { docs_v1, drive_v3 } from 'googleapis';
import { moveFile, searchFiles } from './drive-api';

// ==================== CREATE DOCUMENTS (Section 3.1) ====================

/**
 * Create a new Google Document.
 *
 * @param docsService - Docs API service instance
 * @param title - Document title
 * @returns Created document metadata
 */
export async function createDocument(
  docsService: docs_v1.Docs,
  title: string
): Promise<docs_v1.Schema$Document> {
  const response = await docsService.documents.create({
    requestBody: { title },
  });

  return response.data;
}

/**
 * Create a new Google Document with initial content.
 *
 * @param docsService - Docs API service instance
 * @param title - Document title
 * @param content - Initial text content
 * @returns Created document metadata
 */
export async function createDocumentWithContent(
  docsService: docs_v1.Docs,
  title: string,
  content: string
): Promise<docs_v1.Schema$Document> {
  // Create the document
  const document = await createDocument(docsService, title);
  const documentId = document.documentId!;

  // Insert content
  const requests: docs_v1.Schema$Request[] = [
    {
      insertText: {
        location: { index: 1 },
        text: content,
      },
    },
  ];

  await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });

  return document;
}

/**
 * Create a document in a specific folder.
 *
 * @param driveService - Drive API service instance
 * @param docsService - Docs API service instance
 * @param title - Document title
 * @param folderId - Parent folder ID
 * @returns Created document metadata
 */
export async function createDocumentInFolder(
  driveService: drive_v3.Drive,
  docsService: docs_v1.Docs,
  title: string,
  folderId: string
): Promise<docs_v1.Schema$Document> {
  // Create the document
  const document = await createDocument(docsService, title);
  const documentId = document.documentId!;

  // Move to folder
  await moveFile(driveService, documentId, folderId);

  return document;
}

// ==================== READ DOCUMENT CONTENT (Section 3.2) ====================

/**
 * Get a document's full content.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @returns Document object with content
 */
export async function getDocument(
  docsService: docs_v1.Docs,
  documentId: string
): Promise<docs_v1.Schema$Document> {
  const response = await docsService.documents.get({
    documentId,
  });

  return response.data;
}

/**
 * Extract plain text from a document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @returns Plain text content of the document
 */
export async function getDocumentText(
  docsService: docs_v1.Docs,
  documentId: string
): Promise<string> {
  const document = await getDocument(docsService, documentId);
  const textContent: string[] = [];

  function extractText(elements: docs_v1.Schema$StructuralElement[]): void {
    for (const element of elements) {
      if (element.paragraph) {
        for (const paraElement of element.paragraph.elements || []) {
          if (paraElement.textRun) {
            textContent.push(paraElement.textRun.content || '');
          }
        }
      } else if (element.table) {
        for (const row of element.table.tableRows || []) {
          for (const cell of row.tableCells || []) {
            extractText(cell.content || []);
          }
        }
      }
    }
  }

  const body = document.body;
  if (body?.content) {
    extractText(body.content);
  }

  return textContent.join('');
}

export interface DocumentSummary {
  title: string | null | undefined;
  documentId: string;
  summary: string;
  totalLength: number;
}

/**
 * Get a summary of document content (first N characters).
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param maxChars - Maximum characters to return
 * @returns Dictionary with title and summary
 */
export async function getDocumentSummary(
  docsService: docs_v1.Docs,
  documentId: string,
  maxChars: number = 500
): Promise<DocumentSummary> {
  const document = await getDocument(docsService, documentId);
  const text = await getDocumentText(docsService, documentId);

  let summary = text.slice(0, maxChars).trim();
  if (text.length > maxChars) {
    summary += '...';
  }

  return {
    title: document.title,
    documentId,
    summary,
    totalLength: text.length,
  };
}

export interface HeadingInfo {
  level: string;
  text: string;
}

export interface DocumentStructure {
  title: string | null | undefined;
  headings: HeadingInfo[];
  lists: number;
  tables: number;
  images: number;
}

/**
 * Get the structural elements of a document (headings, lists, tables).
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @returns Dictionary with document structure
 */
export async function getDocumentStructure(
  docsService: docs_v1.Docs,
  documentId: string
): Promise<DocumentStructure> {
  const document = await getDocument(docsService, documentId);

  const structure: DocumentStructure = {
    title: document.title,
    headings: [],
    lists: 0,
    tables: 0,
    images: 0,
  };

  const body = document.body;

  for (const element of body?.content || []) {
    if (element.paragraph) {
      const paragraph = element.paragraph;
      const style = paragraph.paragraphStyle?.namedStyleType || '';

      if (style.startsWith('HEADING')) {
        let text = '';
        for (const paraElement of paragraph.elements || []) {
          if (paraElement.textRun) {
            text += paraElement.textRun.content || '';
          }
        }

        structure.headings.push({
          level: style,
          text: text.trim(),
        });
      }

      // Check for inline objects (images)
      for (const paraElement of paragraph.elements || []) {
        if (paraElement.inlineObjectElement) {
          structure.images += 1;
        }
      }
    } else if (element.table) {
      structure.tables += 1;
    }
  }

  return structure;
}

// ==================== UPDATE DOCUMENTS (Section 3.3) ====================

/**
 * Append text to the end of a document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param text - Text to append
 */
export async function appendText(
  docsService: docs_v1.Docs,
  documentId: string,
  text: string
): Promise<void> {
  // Get the document to find the end index
  const document = await getDocument(docsService, documentId);
  const content = document.body?.content || [];
  const endIndex = content[content.length - 1]?.endIndex || 1;
  const insertIndex = endIndex - 1;

  const requests: docs_v1.Schema$Request[] = [
    {
      insertText: {
        location: { index: insertIndex },
        text,
      },
    },
  ];

  await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });
}

/**
 * Insert text at a specific position in the document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param text - Text to insert
 * @param index - Position to insert at (1-based)
 */
export async function insertTextAtPosition(
  docsService: docs_v1.Docs,
  documentId: string,
  text: string,
  index: number
): Promise<void> {
  const requests: docs_v1.Schema$Request[] = [
    {
      insertText: {
        location: { index },
        text,
      },
    },
  ];

  await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });
}

/**
 * Replace all occurrences of text in a document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param oldText - Text to find
 * @param newText - Replacement text
 * @returns Number of replacements made
 */
export async function replaceText(
  docsService: docs_v1.Docs,
  documentId: string,
  oldText: string,
  newText: string
): Promise<number> {
  const requests: docs_v1.Schema$Request[] = [
    {
      replaceAllText: {
        containsText: {
          text: oldText,
          matchCase: true,
        },
        replaceText: newText,
      },
    },
  ];

  const response = await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });

  const replies = response.data.replies || [];
  if (replies.length > 0) {
    return replies[0].replaceAllText?.occurrencesChanged || 0;
  }
  return 0;
}

/**
 * Delete content in a specific range.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param startIndex - Start index (1-based)
 * @param endIndex - End index
 */
export async function deleteContentRange(
  docsService: docs_v1.Docs,
  documentId: string,
  startIndex: number,
  endIndex: number
): Promise<void> {
  const requests: docs_v1.Schema$Request[] = [
    {
      deleteContentRange: {
        range: {
          startIndex,
          endIndex,
        },
      },
    },
  ];

  await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });
}

/**
 * Add a heading to the end of the document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param text - Heading text
 * @param headingLevel - Heading level (1-6)
 */
export async function addHeading(
  docsService: docs_v1.Docs,
  documentId: string,
  text: string,
  headingLevel: 1 | 2 | 3 | 4 | 5 | 6 = 1
): Promise<void> {
  // Get the document to find the end index
  const document = await getDocument(docsService, documentId);
  const content = document.body?.content || [];
  const endIndex = content[content.length - 1]?.endIndex || 1;
  const insertIndex = endIndex - 1;

  const headingStyles: Record<number, string> = {
    1: 'HEADING_1',
    2: 'HEADING_2',
    3: 'HEADING_3',
    4: 'HEADING_4',
    5: 'HEADING_5',
    6: 'HEADING_6',
  };

  const requests: docs_v1.Schema$Request[] = [
    {
      insertText: {
        location: { index: insertIndex },
        text: text + '\n',
      },
    },
    {
      updateParagraphStyle: {
        range: {
          startIndex: insertIndex,
          endIndex: insertIndex + text.length + 1,
        },
        paragraphStyle: {
          namedStyleType: headingStyles[headingLevel],
        },
        fields: 'namedStyleType',
      },
    },
  ];

  await docsService.documents.batchUpdate({
    documentId,
    requestBody: { requests },
  });
}

// ==================== SEARCH WITHIN DOCUMENTS (Section 3.4) ====================

export interface TextMatch {
  position: number;
  context: string;
  match: string;
}

/**
 * Search for text within a document.
 *
 * @param docsService - Docs API service instance
 * @param documentId - ID of the document
 * @param searchText - Text to search for
 * @returns List of matches with context
 */
export async function searchInDocument(
  docsService: docs_v1.Docs,
  documentId: string,
  searchText: string
): Promise<TextMatch[]> {
  const text = await getDocumentText(docsService, documentId);

  const matches: TextMatch[] = [];
  const searchLower = searchText.toLowerCase();
  const textLower = text.toLowerCase();

  let start = 0;
  while (true) {
    const index = textLower.indexOf(searchLower, start);
    if (index === -1) {
      break;
    }

    // Get context (50 chars before and after)
    const contextStart = Math.max(0, index - 50);
    const contextEnd = Math.min(text.length, index + searchText.length + 50);

    matches.push({
      position: index,
      context: text.slice(contextStart, contextEnd),
      match: text.slice(index, index + searchText.length),
    });

    start = index + 1;
  }

  return matches;
}

export interface DocumentSearchResult {
  documentId: string;
  name: string;
  matchCount: number;
  matches: TextMatch[];
}

/**
 * Search across multiple documents for specific text.
 *
 * @param driveService - Drive API service instance
 * @param docsService - Docs API service instance
 * @param searchText - Text to search for
 * @param folderId - Optional folder to limit search
 * @returns List of documents containing the text
 */
export async function searchDocumentsForText(
  driveService: drive_v3.Drive,
  docsService: docs_v1.Docs,
  searchText: string,
  folderId?: string
): Promise<DocumentSearchResult[]> {
  // First, use Drive's fullText search for efficiency
  let query = `fullText contains '${searchText}' and mimeType = 'application/vnd.google-apps.document' and trashed = false`;

  if (folderId) {
    query += ` and '${folderId}' in parents`;
  }

  const files = await searchFiles(driveService, query);

  const results: DocumentSearchResult[] = [];
  for (const file of files) {
    try {
      const matches = await searchInDocument(docsService, file.id!, searchText);
      if (matches.length > 0) {
        results.push({
          documentId: file.id!,
          name: file.name!,
          matchCount: matches.length,
          matches: matches.slice(0, 5), // First 5 matches
        });
      }
    } catch (e) {
      console.error(`Error searching ${file.name}: ${e}`);
    }
  }

  return results;
}
