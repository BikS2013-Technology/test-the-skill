/**
 * Test script for: TypeScript Manual Embeddings
 * From document: Gemini-File-Search-Tool-Guide.md
 * Document lines: 2633-2713
 *
 * Tests the manual embeddings API for custom RAG implementations.
 */

import { GoogleGenAI } from '@google/genai';
import { config } from 'dotenv';

// Load environment variables
config();

function validateEnvironment(): void {
    const requiredVars = ['GEMINI_API_KEY'];
    const missing = requiredVars.filter(v => !process.env[v]);
    if (missing.length > 0) {
        throw new Error(`Missing environment variables: ${missing.join(', ')}`);
    }
}

// ============ CODE FROM DOCUMENT ============

const ai = new GoogleGenAI({});

async function embedText(
    text: string,
    taskType: string = 'RETRIEVAL_DOCUMENT',
    dimensions: number = 768
): Promise<number[]> {
    const response = await ai.models.embedContent({
        model: 'gemini-embedding-001',
        contents: [text],
        config: {
            taskType: taskType,
            outputDimensionality: dimensions
        }
    });
    return response.embeddings![0].values!;
}

async function embedBatch(
    texts: string[],
    taskType: string = 'RETRIEVAL_DOCUMENT',
    dimensions: number = 768
): Promise<number[][]> {
    const response = await ai.models.embedContent({
        model: 'gemini-embedding-001',
        contents: texts,
        config: {
            taskType: taskType,
            outputDimensionality: dimensions
        }
    });
    return response.embeddings!.map(emb => emb.values!);
}

function cosineSimilarity(vec1: number[], vec2: number[]): number {
    const dotProduct = vec1.reduce((sum, a, i) => sum + a * vec2[i], 0);
    const norm1 = Math.sqrt(vec1.reduce((sum, a) => sum + a * a, 0));
    const norm2 = Math.sqrt(vec2.reduce((sum, a) => sum + a * a, 0));
    return dotProduct / (norm1 * norm2);
}

function normalizeEmbedding(embedding: number[]): number[] {
    const norm = Math.sqrt(embedding.reduce((sum, a) => sum + a * a, 0));
    if (norm === 0) return embedding;
    return embedding.map(x => x / norm);
}

// ============ MAIN TEST ============

async function testTypescriptManualEmbeddings(): Promise<boolean> {
    console.log('='.repeat(60));
    console.log('Test: TypeScript Manual Embeddings (Lines 2633-2713)');
    console.log('='.repeat(60));

    // Validate environment
    validateEnvironment();
    console.log('[OK] Environment validated');
    console.log('[OK] Client initialized');

    // Test single embedding
    console.log('\n--- Testing Single Embedding ---');
    const testText = 'Machine learning is a subset of artificial intelligence';
    const embedding = await embedText(testText, 'RETRIEVAL_DOCUMENT', 768);
    console.log(`[OK] Generated embedding with ${embedding.length} dimensions`);

    if (embedding.length !== 768) {
        throw new Error(`Expected 768 dimensions, got ${embedding.length}`);
    }

    // Test batch embedding
    console.log('\n--- Testing Batch Embeddings ---');
    const documents = [
        'The quick brown fox jumps over the lazy dog',
        'Machine learning is a subset of artificial intelligence',
        'Python is a popular programming language',
        'Neural networks are inspired by biological neurons'
    ];

    // Embed documents
    let docEmbeddings = await embedBatch(documents, 'RETRIEVAL_DOCUMENT', 768);
    console.log(`[OK] Generated ${docEmbeddings.length} document embeddings`);

    if (docEmbeddings.length !== 4) {
        throw new Error(`Expected 4 embeddings, got ${docEmbeddings.length}`);
    }

    // Normalize embeddings
    const normalizedDocs = docEmbeddings.map(normalizeEmbedding);
    console.log('[OK] Normalized document embeddings');

    // Embed query
    console.log('\n--- Testing Query Embedding ---');
    const query = 'What is AI?';
    const queryEmbedding = await embedText(query, 'RETRIEVAL_QUERY', 768);
    const normalizedQuery = normalizeEmbedding(queryEmbedding);
    console.log(`[OK] Generated query embedding with ${queryEmbedding.length} dimensions`);

    // Find best match
    console.log('\n--- Testing Cosine Similarity ---');
    const similarities = normalizedDocs.map(doc => cosineSimilarity(normalizedQuery, doc));
    const bestMatchIdx = similarities.indexOf(Math.max(...similarities));

    console.log(`Query: ${query}`);
    console.log(`Best match: ${documents[bestMatchIdx]}`);
    console.log(`Similarity: ${similarities[bestMatchIdx].toFixed(4)}`);

    // Verify the best match
    const expectedBest = 'Machine learning is a subset of artificial intelligence';
    if (documents[bestMatchIdx] !== expectedBest) {
        throw new Error(`Expected best match to be '${expectedBest}', got '${documents[bestMatchIdx]}'`);
    }
    console.log('[OK] Semantic search returned correct best match');

    console.log('\n' + '='.repeat(60));
    console.log('Test: PASSED');
    console.log('='.repeat(60));
    return true;
}

// Run the test
testTypescriptManualEmbeddings()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(`\n[ERROR] Test failed: ${error.message}`);
        console.error(error.stack);
        process.exit(1);
    });
