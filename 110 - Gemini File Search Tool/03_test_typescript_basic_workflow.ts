/**
 * Test script for: TypeScript Basic Workflow
 * From document: Gemini-File-Search-Tool-Guide.md
 * Document lines: 379-531
 *
 * Tests the complete workflow example: create store, upload documents, query, and cleanup.
 */

import { GoogleGenAI } from '@google/genai';
import * as fs from 'fs';
import * as path from 'path';
import { config } from 'dotenv';
import { fileURLToPath } from 'url';

// Load environment variables
config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function validateEnvironment(): void {
    const requiredVars = ['GEMINI_API_KEY'];
    const missing = requiredVars.filter(v => !process.env[v]);
    if (missing.length > 0) {
        throw new Error(`Missing environment variables: ${missing.join(', ')}`);
    }
}

// ============ CODE FROM DOCUMENT (adapted) ============

interface QueryResult {
    text: string;
    citations: Array<{
        title: string;
        text: string;
    }>;
}

// Initialize client (uses GEMINI_API_KEY environment variable)
const ai = new GoogleGenAI({});

async function createDocumentStore(displayName: string): Promise<string> {
    /**
     * Create a new File Search store.
     */
    const fileSearchStore = await ai.fileSearchStores.create({
        config: { displayName: displayName }
    });

    console.log(`Created store: ${fileSearchStore.name}`);
    return fileSearchStore.name!;
}

async function uploadDocument(
    storeName: string,
    filePath: string,
    displayName?: string
): Promise<void> {
    /**
     * Upload a document to the store and wait for processing.
     */
    const docDisplayName = displayName || path.basename(filePath);

    console.log(`Uploading: ${filePath}`);

    let operation = await ai.fileSearchStores.uploadToFileSearchStore({
        file: filePath,
        fileSearchStoreName: storeName,
        config: { displayName: docDisplayName }
    });

    // Wait for the upload and processing to complete
    while (!operation.done) {
        console.log('  Processing...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        operation = await ai.operations.get({ operation });
    }

    console.log(`  Completed: ${docDisplayName}`);
}

async function queryDocuments(
    storeName: string,
    question: string,
    model: string = 'gemini-2.5-flash'
): Promise<QueryResult> {
    /**
     * Query documents using File Search and return response with citations.
     */
    const response = await ai.models.generateContent({
        model: model,
        contents: question,
        config: {
            tools: [{
                fileSearch: {
                    fileSearchStoreNames: [storeName]
                }
            }]
        }
    });

    const result: QueryResult = {
        text: response.text || '',
        citations: []
    };

    // Extract citations from grounding metadata
    const candidate = response.candidates?.[0];
    if (candidate?.groundingMetadata?.groundingChunks) {
        for (const chunk of candidate.groundingMetadata.groundingChunks) {
            if (chunk.retrievedContext) {
                result.citations.push({
                    title: chunk.retrievedContext.title || 'Unknown',
                    text: chunk.retrievedContext.text || ''
                });
            }
        }
    }

    return result;
}

async function deleteStore(storeName: string, force: boolean = true): Promise<void> {
    /**
     * Delete a File Search store.
     */
    await ai.fileSearchStores.delete({
        name: storeName,
        config: { force: force }
    });
    console.log(`Deleted store: ${storeName}`);
}

// ============ MAIN TEST ============

async function testTypescriptBasicWorkflow(): Promise<boolean> {
    console.log('='.repeat(60));
    console.log('Test: TypeScript Basic Workflow (Lines 379-531)');
    console.log('='.repeat(60));

    // Validate environment
    validateEnvironment();
    console.log('[OK] Environment validated');

    // Get test documents path
    const testDocsDir = path.join(__dirname, 'test_documents');

    // Create a store
    const storeName = await createDocumentStore('test-knowledge-base-ts');
    console.log(`[OK] Store created: ${storeName}`);

    try {
        // Upload documents
        const manualPath = path.join(testDocsDir, 'sample_manual.txt');
        const faqPath = path.join(testDocsDir, 'faq.txt');

        await uploadDocument(storeName, manualPath, 'Product Manual');
        console.log('[OK] Product Manual uploaded');

        await uploadDocument(storeName, faqPath, 'FAQ Document');
        console.log('[OK] FAQ Document uploaded');

        // Query the documents
        const result = await queryDocuments(
            storeName,
            'How do I reset the device to factory settings?'
        );

        console.log('\n=== Response ===');
        console.log(result.text);

        console.log('\n=== Citations ===');
        if (result.citations.length > 0) {
            for (const citation of result.citations) {
                const textPreview = citation.text.substring(0, 100);
                console.log(`- ${citation.title}: ${textPreview}...`);
            }
        } else {
            console.log('No citations returned (this may be normal depending on the response)');
        }

        console.log('\n[OK] Query executed successfully');

    } finally {
        // Clean up
        await deleteStore(storeName);
        console.log('[OK] Store cleaned up');
    }

    console.log('\n' + '='.repeat(60));
    console.log('Test: PASSED');
    console.log('='.repeat(60));
    return true;
}

// Run the test
testTypescriptBasicWorkflow()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(`\n[ERROR] Test failed: ${error.message}`);
        console.error(error.stack);
        process.exit(1);
    });
