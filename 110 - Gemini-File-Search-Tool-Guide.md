# Google Gemini File Search Tool: Complete Implementation Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites and Setup](#prerequisites-and-setup)
3. [Core Concepts](#core-concepts)
4. [Python Implementation](#python-implementation)
5. [TypeScript/npm Implementation](#typescriptnpm-implementation)
6. [Chunking Configuration](#chunking-configuration)
7. [Custom Metadata and Filtering](#custom-metadata-and-filtering)
8. [Accessing Citations and Grounding Metadata](#accessing-citations-and-grounding-metadata)
9. [Document Management Operations](#document-management-operations)
10. [Repository Maintenance: Incremental Indexing, Removing, and Replacing Documents](#repository-maintenance-incremental-indexing-removing-and-replacing-documents)
    - [Incremental Indexing (Adding New Documents)](#incremental-indexing-adding-new-documents)
    - [Removing Documents from the Index](#removing-documents-from-the-index)
    - [Replacing Documents (Version Updates)](#replacing-documents-version-updates)
    - [Complete Repository Manager Example](#complete-repository-manager-example)
11. [Manual Embeddings API](#manual-embeddings-api)
12. [Best Practices](#best-practices)
13. [Limitations and Considerations](#limitations-and-considerations)
14. [Pricing](#pricing)
15. [Resources](#resources)

---

## Overview

The **Gemini File Search Tool** is Google's fully managed Retrieval Augmented Generation (RAG) system built directly into the Gemini API. Released in November 2025, it abstracts away the complex RAG pipeline, allowing developers to focus on building applications rather than managing infrastructure.

### What File Search Does

The File Search tool:
- **Imports** your documents into a persistent store
- **Chunks** documents into optimal segments automatically
- **Generates embeddings** using the `gemini-embedding-001` model
- **Indexes** content for fast semantic retrieval
- **Retrieves** relevant information based on user prompts
- **Injects** context into model responses with automatic citations

### Key Benefits

| Feature | Description |
|---------|-------------|
| **Semantic Search** | Understands meaning and context, not just keywords |
| **Built-in Citations** | Responses include references to source documents |
| **Managed Infrastructure** | No need for external vector databases (Pinecone, ChromaDB, etc.) |
| **Wide Format Support** | PDF, DOCX, TXT, JSON, code files, and 50+ formats |
| **Persistent Storage** | Data stored indefinitely until manually deleted |

### Supported Models

File Search is compatible with:
- `gemini-3-pro-preview`
- `gemini-2.5-pro` and `gemini-2.5-pro-preview`
- `gemini-2.5-flash` and `gemini-2.5-flash-preview`
- `gemini-2.5-flash-lite` and `gemini-2.5-flash-lite-preview`

---

## Prerequisites and Setup

### Python Setup

**Requirements:**
- Python 3.10 or newer
- Google Gemini API key (from [Google AI Studio](https://aistudio.google.com/))

**Installation:**

```bash
# Create and activate virtual environment (using UV as per project standards)
uv venv
source .venv/bin/activate

# Install the google-genai package
uv add google-genai

# For async support (optional)
uv add "google-genai[aiohttp]"
```

**Environment Configuration:**

```bash
# Set your API key as environment variable
export GEMINI_API_KEY="your-api-key-here"
```

### TypeScript/npm Setup

**Requirements:**
- Node.js 18.x or newer
- npm or yarn package manager
- Google Gemini API key

**Installation:**

```bash
# Initialize a new project (if needed)
npm init -y

# Install the Google GenAI SDK
npm install @google/genai

# For TypeScript projects
npm install typescript @types/node --save-dev
```

**TypeScript Configuration (tsconfig.json):**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "esModuleInterop": true,
    "strict": true,
    "outDir": "./dist"
  },
  "include": ["src/**/*"]
}
```

---

## Core Concepts

### File Search Store

A **File Search Store** is a persistent container for your document embeddings. It:
- Holds chunked and embedded documents
- Supports up to 20 GB per store for optimal latency
- Persists data indefinitely (unlike raw files which expire in 48 hours)
- Has a unique resource name in format `fileSearchStores/{40-char-id}`

### Documents

Documents within a store have:
- **States**: `PENDING` (processing), `ACTIVE` (ready), `FAILED` (error)
- **Metadata**: Custom key-value pairs for filtering
- **Chunks**: Automatically segmented pieces with embeddings

### Workflow Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Create Store   │────▶│  Upload Files   │────▶│  Wait for       │
│                 │     │                 │     │  Processing     │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
┌─────────────────┐     ┌─────────────────┐              │
│  Get Response   │◀────│  Query with     │◀─────────────┘
│  + Citations    │     │  File Search    │
└─────────────────┘     └─────────────────┘
```

---

## Python Implementation

### Basic Example: Complete Workflow

```python
"""
Gemini File Search - Complete Python Example
Demonstrates creating a store, uploading documents, querying, and cleanup.
"""

from google import genai
from google.genai import types
import time
import os

# Initialize client (uses GEMINI_API_KEY environment variable by default)
client = genai.Client()

# Alternative: explicit API key
# client = genai.Client(api_key="your-api-key-here")


def create_document_store(display_name: str) -> str:
    """Create a new File Search store."""
    file_search_store = client.file_search_stores.create(
        config={'display_name': display_name}
    )
    print(f"Created store: {file_search_store.name}")
    return file_search_store.name


def upload_document(store_name: str, file_path: str, display_name: str = None) -> None:
    """Upload a document to the store and wait for processing."""
    if display_name is None:
        display_name = os.path.basename(file_path)

    print(f"Uploading: {file_path}")

    operation = client.file_search_stores.upload_to_file_search_store(
        file=file_path,
        file_search_store_name=store_name,
        config={'display_name': display_name}
    )

    # Wait for the upload and processing to complete
    while not operation.done:
        print("  Processing...")
        time.sleep(2)
        operation = client.operations.get(operation)

    print(f"  Completed: {display_name}")


def query_documents(store_name: str, question: str, model: str = "gemini-2.5-flash") -> dict:
    """Query documents using File Search and return response with citations."""
    response = client.models.generate_content(
        model=model,
        contents=question,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_name]
                    )
                )
            ]
        )
    )

    result = {
        'text': response.text,
        'grounding_metadata': None,
        'citations': []
    }

    # Extract grounding metadata if available
    if response.candidates and response.candidates[0].grounding_metadata:
        metadata = response.candidates[0].grounding_metadata
        result['grounding_metadata'] = metadata

        # Extract citations from grounding chunks
        if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                if hasattr(chunk, 'retrieved_context') and chunk.retrieved_context:
                    result['citations'].append({
                        'title': chunk.retrieved_context.title,
                        'text': chunk.retrieved_context.text
                    })

    return result


def delete_store(store_name: str, force: bool = True) -> None:
    """Delete a File Search store."""
    client.file_search_stores.delete(
        name=store_name,
        config={'force': force}
    )
    print(f"Deleted store: {store_name}")


# Main execution example
if __name__ == "__main__":
    # Create a store
    store_name = create_document_store("my-knowledge-base")

    try:
        # Upload documents
        upload_document(store_name, "documents/manual.pdf", "Product Manual")
        upload_document(store_name, "documents/faq.txt", "FAQ Document")

        # Query the documents
        result = query_documents(
            store_name,
            "How do I reset the device to factory settings?"
        )

        print("\n=== Response ===")
        print(result['text'])

        print("\n=== Citations ===")
        for citation in result['citations']:
            print(f"- {citation['title']}: {citation['text'][:100]}...")

    finally:
        # Clean up (comment out to keep the store)
        # delete_store(store_name)
        pass
```

### Uploading Multiple Files Concurrently

```python
"""Upload multiple files with concurrent processing monitoring."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List


def upload_file_sync(store_name: str, file_path: str) -> str:
    """Synchronous upload function for thread pool."""
    display_name = os.path.basename(file_path)

    operation = client.file_search_stores.upload_to_file_search_store(
        file=file_path,
        file_search_store_name=store_name,
        config={'display_name': display_name}
    )

    while not operation.done:
        time.sleep(2)
        operation = client.operations.get(operation)

    return display_name


def upload_multiple_files(store_name: str, file_paths: List[str], max_workers: int = 5) -> None:
    """Upload multiple files concurrently using thread pool."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(upload_file_sync, store_name, fp): fp
            for fp in file_paths
        }

        for future in futures:
            file_path = futures[future]
            try:
                result = future.result()
                print(f"Completed: {result}")
            except Exception as e:
                print(f"Failed: {file_path} - {e}")


# Usage
files = [
    "docs/chapter1.pdf",
    "docs/chapter2.pdf",
    "docs/appendix.txt"
]
upload_multiple_files(store_name, files)
```

### Using the Import Method (Pre-uploaded Files)

```python
"""Import files that were previously uploaded via the Files API."""

def upload_then_import(store_name: str, file_path: str) -> None:
    """Upload to Files API first, then import to store."""

    # Step 1: Upload to temporary Files API storage
    uploaded_file = client.files.upload(file=file_path)
    print(f"Uploaded to Files API: {uploaded_file.name}")

    # Step 2: Import into File Search store (creates persistent copy)
    operation = client.file_search_stores.import_file(
        file_search_store_name=store_name,
        file_name=uploaded_file.name
    )

    # Wait for import to complete
    while not operation.done:
        time.sleep(2)
        operation = client.operations.get(operation)

    print(f"Imported to store: {os.path.basename(file_path)}")

    # Note: Original file in Files API will be deleted after 48 hours,
    # but the imported data in the store persists indefinitely
```

---

## TypeScript/npm Implementation

### Basic Example: Complete Workflow

```typescript
/**
 * Gemini File Search - Complete TypeScript Example
 * Demonstrates creating a store, uploading documents, querying, and cleanup.
 */

import { GoogleGenAI } from '@google/genai';
import * as fs from 'fs';
import * as path from 'path';

// Initialize client (uses GEMINI_API_KEY environment variable)
const ai = new GoogleGenAI({});

// Alternative: explicit API key
// const ai = new GoogleGenAI({ apiKey: 'your-api-key-here' });


interface QueryResult {
    text: string;
    citations: Array<{
        title: string;
        text: string;
    }>;
}


async function createDocumentStore(displayName: string): Promise<string> {
    /**
     * Create a new File Search store.
     */
    const fileSearchStore = await ai.fileSearchStores.create({
        config: { displayName: displayName }
    });

    console.log(`Created store: ${fileSearchStore.name}`);
    return fileSearchStore.name;
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


// Main execution
async function main(): Promise<void> {
    // Create a store
    const storeName = await createDocumentStore('my-knowledge-base');

    try {
        // Upload documents
        await uploadDocument(storeName, 'documents/manual.pdf', 'Product Manual');
        await uploadDocument(storeName, 'documents/faq.txt', 'FAQ Document');

        // Query the documents
        const result = await queryDocuments(
            storeName,
            'How do I reset the device to factory settings?'
        );

        console.log('\n=== Response ===');
        console.log(result.text);

        console.log('\n=== Citations ===');
        for (const citation of result.citations) {
            console.log(`- ${citation.title}: ${citation.text.substring(0, 100)}...`);
        }
    } finally {
        // Clean up (comment out to keep the store)
        // await deleteStore(storeName);
    }
}

main().catch(console.error);
```

### Uploading Multiple Files Concurrently

```typescript
/**
 * Upload multiple files with concurrent processing.
 */

async function uploadMultipleFiles(
    storeName: string,
    filePaths: string[]
): Promise<void> {
    /**
     * Upload multiple files concurrently using Promise.all.
     */
    const uploadPromises = filePaths.map(async (filePath) => {
        const displayName = path.basename(filePath);

        let operation = await ai.fileSearchStores.uploadToFileSearchStore({
            file: filePath,
            fileSearchStoreName: storeName,
            config: { displayName: displayName }
        });

        while (!operation.done) {
            await new Promise(resolve => setTimeout(resolve, 2000));
            operation = await ai.operations.get({ operation });
        }

        console.log(`Completed: ${displayName}`);
        return displayName;
    });

    await Promise.all(uploadPromises);
    console.log('All files uploaded successfully');
}


// Usage
const files = [
    'docs/chapter1.pdf',
    'docs/chapter2.pdf',
    'docs/appendix.txt'
];
await uploadMultipleFiles(storeName, files);
```

### Finding Stores by Display Name

```typescript
/**
 * Find a store by its display name (since API assigns unique IDs).
 */

interface FileSearchStore {
    name: string;
    displayName?: string;
}


async function findStoreByDisplayName(displayName: string): Promise<FileSearchStore | null> {
    const pager = await ai.fileSearchStores.list({
        config: { pageSize: 10 }
    });

    let page = pager.page;

    while (true) {
        for (const store of page) {
            if (store.displayName === displayName) {
                return store as FileSearchStore;
            }
        }

        if (!pager.hasNextPage()) {
            break;
        }
        page = await pager.nextPage();
    }

    return null;
}


// Usage
const store = await findStoreByDisplayName('my-knowledge-base');
if (store) {
    console.log(`Found store: ${store.name}`);
} else {
    console.log('Store not found');
}
```

---

## Chunking Configuration

File Search automatically chunks documents, but you can customize the chunking behavior for optimal results.

### Chunking Options

```python
# Python - Custom chunking configuration
chunking_config = {
    'white_space_config': {
        'max_tokens_per_chunk': 500,    # Maximum tokens per chunk (default varies)
        'max_overlap_tokens': 50         # Overlap between chunks for context
    }
}

operation = client.file_search_stores.upload_to_file_search_store(
    file='technical-manual.pdf',
    file_search_store_name=store_name,
    config={
        'display_name': 'Technical Manual',
        'chunking_config': chunking_config
    }
)
```

```typescript
// TypeScript - Custom chunking configuration
const chunkingConfig = {
    whiteSpaceConfig: {
        maxTokensPerChunk: 500,    // Maximum tokens per chunk
        maxOverlapTokens: 50       // Overlap between chunks for context
    }
};

let operation = await ai.fileSearchStores.uploadToFileSearchStore({
    file: 'technical-manual.pdf',
    fileSearchStoreName: storeName,
    config: {
        displayName: 'Technical Manual',
        chunkingConfig: chunkingConfig
    }
});
```

### Chunking Guidelines

| Parameter | Recommended Value | Use Case |
|-----------|-------------------|----------|
| `max_tokens_per_chunk` = 200 | Small, focused retrieval | FAQ, short answers |
| `max_tokens_per_chunk` = 500 | Balanced (default-like) | General documents |
| `max_tokens_per_chunk` = 1000 | Larger context | Technical documentation |
| `max_overlap_tokens` = 20-50 | Standard overlap | Most documents |
| `max_overlap_tokens` = 100+ | High overlap | Highly interconnected content |

---

## Custom Metadata and Filtering

### Adding Metadata to Documents

Metadata enables filtering and organization of documents within a store.

```python
# Python - Adding custom metadata
custom_metadata = [
    {"key": "author", "string_value": "John Smith"},
    {"key": "department", "string_value": "Engineering"},
    {"key": "year", "numeric_value": 2025},
    {"key": "tags", "string_list_value": {"values": ["manual", "technical", "v2"]}}
]

operation = client.file_search_stores.upload_to_file_search_store(
    file='engineering-manual.pdf',
    file_search_store_name=store_name,
    config={
        'display_name': 'Engineering Manual v2',
        'custom_metadata': custom_metadata
    }
)
```

```typescript
// TypeScript - Adding custom metadata
const customMetadata = [
    { key: 'author', stringValue: 'John Smith' },
    { key: 'department', stringValue: 'Engineering' },
    { key: 'year', numericValue: 2025 },
    { key: 'tags', stringListValue: { values: ['manual', 'technical', 'v2'] } }
];

let operation = await ai.fileSearchStores.uploadToFileSearchStore({
    file: 'engineering-manual.pdf',
    fileSearchStoreName: storeName,
    config: {
        displayName: 'Engineering Manual v2',
        customMetadata: customMetadata
    }
});
```

### Querying with Metadata Filters

Use AIP-160 filter syntax to narrow search results.

```python
# Python - Query with metadata filter
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How do I calibrate the sensors?",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store_name],
                    metadata_filter='department="Engineering" AND year>=2024'
                )
            )
        ]
    )
)
```

```typescript
// TypeScript - Query with metadata filter
const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: 'How do I calibrate the sensors?',
    config: {
        tools: [{
            fileSearch: {
                fileSearchStoreNames: [storeName],
                metadataFilter: 'department="Engineering" AND year>=2024'
            }
        }]
    }
});
```

### Filter Syntax Examples

| Filter | Description |
|--------|-------------|
| `author="John Smith"` | Exact string match |
| `year>=2024` | Numeric comparison |
| `department="Sales" OR department="Marketing"` | OR condition |
| `year>=2023 AND author="Jane Doe"` | AND condition |
| `tags:"manual"` | Contains value in list |

---

## Accessing Citations and Grounding Metadata

### Understanding the Response Structure

When File Search retrieves context, the response includes grounding metadata with:
- **`grounding_chunks`**: Source content that was retrieved
- **`grounding_supports`**: Links between response text and source chunks

### Python - Extracting Citations

```python
"""Complete example of extracting and processing citations."""

def extract_citations_detailed(response) -> dict:
    """Extract detailed citation information from response."""
    result = {
        'text': response.text,
        'chunks': [],
        'supports': [],
        'inline_citations': []
    }

    candidate = response.candidates[0] if response.candidates else None
    if not candidate or not candidate.grounding_metadata:
        return result

    metadata = candidate.grounding_metadata

    # Extract grounding chunks (source content)
    if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
        for i, chunk in enumerate(metadata.grounding_chunks):
            chunk_info = {'index': i}

            if hasattr(chunk, 'retrieved_context') and chunk.retrieved_context:
                chunk_info['type'] = 'retrieved_context'
                chunk_info['title'] = chunk.retrieved_context.title
                chunk_info['text'] = chunk.retrieved_context.text
                chunk_info['uri'] = getattr(chunk.retrieved_context, 'uri', None)
            elif hasattr(chunk, 'web') and chunk.web:
                chunk_info['type'] = 'web'
                chunk_info['title'] = chunk.web.title
                chunk_info['uri'] = chunk.web.uri

            result['chunks'].append(chunk_info)

    # Extract grounding supports (maps response text to sources)
    if hasattr(metadata, 'grounding_supports') and metadata.grounding_supports:
        for support in metadata.grounding_supports:
            support_info = {
                'text_segment': {
                    'start': support.segment.start_index,
                    'end': support.segment.end_index,
                    'text': support.segment.text
                },
                'source_indices': list(support.grounding_chunk_indices),
                'confidence': getattr(support, 'confidence_scores', [])
            }
            result['supports'].append(support_info)

    return result


def format_response_with_citations(response) -> str:
    """Format response text with inline citation markers."""
    citations = extract_citations_detailed(response)

    if not citations['supports']:
        return citations['text']

    text = citations['text']

    # Sort supports by end index (descending) to avoid offset issues
    sorted_supports = sorted(
        citations['supports'],
        key=lambda x: x['text_segment']['end'],
        reverse=True
    )

    # Insert citation markers
    for support in sorted_supports:
        end_idx = support['text_segment']['end']
        source_refs = ', '.join(str(i + 1) for i in support['source_indices'])
        citation_marker = f" [{source_refs}]"
        text = text[:end_idx] + citation_marker + text[end_idx:]

    # Append source list
    text += "\n\n--- Sources ---\n"
    for chunk in citations['chunks']:
        text += f"[{chunk['index'] + 1}] {chunk.get('title', 'Unknown')}\n"

    return text


# Usage
response = query_documents(store_name, "What are the safety guidelines?")
formatted = format_response_with_citations(response)
print(formatted)
```

### TypeScript - Extracting Citations

```typescript
/**
 * Complete example of extracting and processing citations.
 */

interface ChunkInfo {
    index: number;
    type: string;
    title?: string;
    text?: string;
    uri?: string;
}

interface SupportInfo {
    textSegment: {
        start: number;
        end: number;
        text: string;
    };
    sourceIndices: number[];
    confidence: number[];
}

interface DetailedCitations {
    text: string;
    chunks: ChunkInfo[];
    supports: SupportInfo[];
}


function extractCitationsDetailed(response: any): DetailedCitations {
    const result: DetailedCitations = {
        text: response.text || '',
        chunks: [],
        supports: []
    };

    const candidate = response.candidates?.[0];
    if (!candidate?.groundingMetadata) {
        return result;
    }

    const metadata = candidate.groundingMetadata;

    // Extract grounding chunks
    if (metadata.groundingChunks) {
        metadata.groundingChunks.forEach((chunk: any, index: number) => {
            const chunkInfo: ChunkInfo = { index, type: 'unknown' };

            if (chunk.retrievedContext) {
                chunkInfo.type = 'retrieved_context';
                chunkInfo.title = chunk.retrievedContext.title;
                chunkInfo.text = chunk.retrievedContext.text;
                chunkInfo.uri = chunk.retrievedContext.uri;
            } else if (chunk.web) {
                chunkInfo.type = 'web';
                chunkInfo.title = chunk.web.title;
                chunkInfo.uri = chunk.web.uri;
            }

            result.chunks.push(chunkInfo);
        });
    }

    // Extract grounding supports
    if (metadata.groundingSupports) {
        for (const support of metadata.groundingSupports) {
            result.supports.push({
                textSegment: {
                    start: support.segment.startIndex,
                    end: support.segment.endIndex,
                    text: support.segment.text
                },
                sourceIndices: [...support.groundingChunkIndices],
                confidence: support.confidenceScores || []
            });
        }
    }

    return result;
}


function formatResponseWithCitations(response: any): string {
    const citations = extractCitationsDetailed(response);

    if (citations.supports.length === 0) {
        return citations.text;
    }

    let text = citations.text;

    // Sort supports by end index (descending)
    const sortedSupports = [...citations.supports].sort(
        (a, b) => b.textSegment.end - a.textSegment.end
    );

    // Insert citation markers
    for (const support of sortedSupports) {
        const endIdx = support.textSegment.end;
        const sourceRefs = support.sourceIndices.map(i => i + 1).join(', ');
        const citationMarker = ` [${sourceRefs}]`;
        text = text.slice(0, endIdx) + citationMarker + text.slice(endIdx);
    }

    // Append source list
    text += '\n\n--- Sources ---\n';
    for (const chunk of citations.chunks) {
        text += `[${chunk.index + 1}] ${chunk.title || 'Unknown'}\n`;
    }

    return text;
}
```

---

## Document Management Operations

### Listing Documents in a Store

```python
# Python - List all documents
def list_documents(store_name: str) -> list:
    """List all documents in a store."""
    documents = []

    pager = client.file_search_stores.documents.list(parent=store_name)

    for doc in pager:
        documents.append({
            'name': doc.name,
            'display_name': doc.display_name,
            'state': doc.state,
            'size_bytes': doc.size_bytes,
            'mime_type': doc.mime_type,
            'create_time': doc.create_time
        })

    return documents


# Usage
docs = list_documents(store_name)
for doc in docs:
    print(f"{doc['display_name']} - {doc['state']} ({doc['size_bytes']} bytes)")
```

```typescript
// TypeScript - List all documents
async function listDocuments(storeName: string): Promise<any[]> {
    const documents: any[] = [];

    const pager = await ai.fileSearchStores.documents.list({
        parent: storeName
    });

    for await (const doc of pager) {
        documents.push({
            name: doc.name,
            displayName: doc.displayName,
            state: doc.state,
            sizeBytes: doc.sizeBytes,
            mimeType: doc.mimeType,
            createTime: doc.createTime
        });
    }

    return documents;
}
```

### Deleting Documents

```python
# Python - Delete a document
def delete_document(document_name: str, force: bool = True) -> None:
    """Delete a document from the store."""
    client.file_search_stores.documents.delete(
        name=document_name,
        config={'force': force}  # force=True also deletes associated chunks
    )
    print(f"Deleted document: {document_name}")


# Find and delete by display name
def delete_document_by_name(store_name: str, display_name: str) -> bool:
    """Find and delete a document by its display name."""
    pager = client.file_search_stores.documents.list(parent=store_name)

    for doc in pager:
        if doc.display_name == display_name:
            delete_document(doc.name)
            return True

    return False
```

```typescript
// TypeScript - Delete a document
async function deleteDocument(documentName: string, force: boolean = true): Promise<void> {
    await ai.fileSearchStores.documents.delete({
        name: documentName,
        config: { force: force }
    });
    console.log(`Deleted document: ${documentName}`);
}
```

### Updating Documents (Delete + Re-upload)

Documents are immutable, so updating requires deleting and re-uploading.

```python
# Python - Update a document
def update_document(store_name: str, display_name: str, new_file_path: str) -> None:
    """Update a document by deleting the old version and uploading the new one."""

    # Find and delete existing document
    if delete_document_by_name(store_name, display_name):
        print(f"Deleted old version of: {display_name}")

    # Upload new version
    upload_document(store_name, new_file_path, display_name)
    print(f"Uploaded new version of: {display_name}")
```

---

## Repository Maintenance: Incremental Indexing, Removing, and Replacing Documents

This section provides comprehensive patterns for maintaining a document repository over time, including adding new documents, removing outdated ones, and replacing documents with updated versions.

### Key Concepts for Repository Maintenance

1. **Stores are persistent** - Data remains until explicitly deleted
2. **Documents are immutable** - You cannot modify a document; you must delete and re-upload
3. **Operations are asynchronous** - Uploads/imports return operations that must be polled
4. **Display names enable lookup** - Use consistent naming to find documents programmatically

### Incremental Indexing (Adding New Documents)

You can add new documents to an existing store at any time. The store continues to function during uploads, and new documents become searchable once they reach `ACTIVE` state.

#### Python - Incremental Document Addition

```python
"""
Repository maintenance: Adding new documents to an existing store.
Demonstrates incremental indexing patterns.
"""

from google import genai
from google.genai import types
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import time
import os

client = genai.Client()


@dataclass
class DocumentInfo:
    """Information about an indexed document."""
    name: str
    display_name: str
    state: str
    size_bytes: int
    indexed_at: datetime


class DocumentRepository:
    """Manages a File Search store as a document repository."""

    def __init__(self, store_name: str):
        self.store_name = store_name

    @classmethod
    def connect(cls, display_name: str) -> 'DocumentRepository':
        """Connect to an existing store by display name."""
        pager = client.file_search_stores.list()
        for store in pager:
            if store.display_name == display_name:
                return cls(store.name)
        raise ValueError(f"Store not found: {display_name}")

    @classmethod
    def create(cls, display_name: str) -> 'DocumentRepository':
        """Create a new store and return repository instance."""
        store = client.file_search_stores.create(
            config={'display_name': display_name}
        )
        return cls(store.name)

    def add_document(
        self,
        file_path: str,
        display_name: Optional[str] = None,
        metadata: Optional[list] = None,
        chunking_config: Optional[dict] = None
    ) -> DocumentInfo:
        """
        Add a single document to the repository.

        Args:
            file_path: Path to the file to upload
            display_name: Human-readable name (defaults to filename)
            metadata: Custom metadata key-value pairs
            chunking_config: Custom chunking configuration

        Returns:
            DocumentInfo with details about the indexed document
        """
        if display_name is None:
            display_name = os.path.basename(file_path)

        config = {'display_name': display_name}
        if metadata:
            config['custom_metadata'] = metadata
        if chunking_config:
            config['chunking_config'] = chunking_config

        operation = client.file_search_stores.upload_to_file_search_store(
            file=file_path,
            file_search_store_name=self.store_name,
            config=config
        )

        # Wait for processing to complete
        while not operation.done:
            time.sleep(2)
            operation = client.operations.get(operation)

        # Get the document info
        doc = self._find_document_by_display_name(display_name)
        if doc:
            return DocumentInfo(
                name=doc.name,
                display_name=doc.display_name,
                state=str(doc.state),
                size_bytes=doc.size_bytes,
                indexed_at=datetime.now()
            )
        raise RuntimeError(f"Document upload succeeded but document not found: {display_name}")

    def add_documents_batch(
        self,
        file_paths: list,
        metadata_map: Optional[dict] = None
    ) -> list:
        """
        Add multiple documents to the repository.

        Args:
            file_paths: List of file paths to upload
            metadata_map: Dict mapping filename to metadata list

        Returns:
            List of DocumentInfo for successfully indexed documents
        """
        results = []
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            metadata = metadata_map.get(filename) if metadata_map else None

            try:
                doc_info = self.add_document(file_path, metadata=metadata)
                results.append(doc_info)
                print(f"Indexed: {filename}")
            except Exception as e:
                print(f"Failed to index {filename}: {e}")

        return results

    def _find_document_by_display_name(self, display_name: str):
        """Find a document by its display name."""
        pager = client.file_search_stores.documents.list(parent=self.store_name)
        for doc in pager:
            if doc.display_name == display_name:
                return doc
        return None

    def list_documents(self) -> list:
        """List all documents in the repository."""
        documents = []
        pager = client.file_search_stores.documents.list(parent=self.store_name)
        for doc in pager:
            documents.append({
                'name': doc.name,
                'display_name': doc.display_name,
                'state': str(doc.state),
                'size_bytes': doc.size_bytes
            })
        return documents


# Usage Example: Incremental Indexing
if __name__ == "__main__":
    # Connect to existing repository or create new one
    try:
        repo = DocumentRepository.connect("my-knowledge-base")
        print("Connected to existing repository")
    except ValueError:
        repo = DocumentRepository.create("my-knowledge-base")
        print("Created new repository")

    # Add new documents incrementally
    new_documents = [
        "new_docs/guide_2025.pdf",
        "new_docs/release_notes.md",
        "new_docs/api_reference.txt"
    ]

    # Add with custom metadata
    metadata_map = {
        "guide_2025.pdf": [
            {"key": "doc_type", "string_value": "guide"},
            {"key": "year", "numeric_value": 2025}
        ],
        "release_notes.md": [
            {"key": "doc_type", "string_value": "release_notes"},
            {"key": "version", "string_value": "2.0"}
        ]
    }

    results = repo.add_documents_batch(new_documents, metadata_map)
    print(f"\nSuccessfully indexed {len(results)} new documents")

    # List all documents in repository
    print("\nRepository contents:")
    for doc in repo.list_documents():
        print(f"  - {doc['display_name']} ({doc['state']})")
```

#### TypeScript - Incremental Document Addition

```typescript
/**
 * Repository maintenance: Adding new documents to an existing store.
 * Demonstrates incremental indexing patterns.
 */

import { GoogleGenAI } from '@google/genai';
import * as path from 'path';

const ai = new GoogleGenAI({});


interface DocumentInfo {
    name: string;
    displayName: string;
    state: string;
    sizeBytes: number;
    indexedAt: Date;
}

interface CustomMetadata {
    key: string;
    stringValue?: string;
    numericValue?: number;
    stringListValue?: { values: string[] };
}


class DocumentRepository {
    private storeName: string;

    constructor(storeName: string) {
        this.storeName = storeName;
    }

    static async connect(displayName: string): Promise<DocumentRepository> {
        /**
         * Connect to an existing store by display name.
         */
        const pager = await ai.fileSearchStores.list({ config: { pageSize: 20 } });
        let page = pager.page;

        while (true) {
            for (const store of page) {
                if (store.displayName === displayName) {
                    return new DocumentRepository(store.name);
                }
            }
            if (!pager.hasNextPage()) break;
            page = await pager.nextPage();
        }

        throw new Error(`Store not found: ${displayName}`);
    }

    static async create(displayName: string): Promise<DocumentRepository> {
        /**
         * Create a new store and return repository instance.
         */
        const store = await ai.fileSearchStores.create({
            config: { displayName: displayName }
        });
        return new DocumentRepository(store.name);
    }

    async addDocument(
        filePath: string,
        displayName?: string,
        metadata?: CustomMetadata[],
        chunkingConfig?: any
    ): Promise<DocumentInfo> {
        /**
         * Add a single document to the repository.
         */
        const docDisplayName = displayName || path.basename(filePath);

        const config: any = { displayName: docDisplayName };
        if (metadata) config.customMetadata = metadata;
        if (chunkingConfig) config.chunkingConfig = chunkingConfig;

        let operation = await ai.fileSearchStores.uploadToFileSearchStore({
            file: filePath,
            fileSearchStoreName: this.storeName,
            config: config
        });

        // Wait for processing
        while (!operation.done) {
            await new Promise(resolve => setTimeout(resolve, 2000));
            operation = await ai.operations.get({ operation });
        }

        // Find and return document info
        const doc = await this.findDocumentByDisplayName(docDisplayName);
        if (doc) {
            return {
                name: doc.name,
                displayName: doc.displayName || docDisplayName,
                state: doc.state || 'UNKNOWN',
                sizeBytes: doc.sizeBytes || 0,
                indexedAt: new Date()
            };
        }

        throw new Error(`Document upload succeeded but not found: ${docDisplayName}`);
    }

    async addDocumentsBatch(
        filePaths: string[],
        metadataMap?: Map<string, CustomMetadata[]>
    ): Promise<DocumentInfo[]> {
        /**
         * Add multiple documents to the repository.
         */
        const results: DocumentInfo[] = [];

        for (const filePath of filePaths) {
            const filename = path.basename(filePath);
            const metadata = metadataMap?.get(filename);

            try {
                const docInfo = await this.addDocument(filePath, undefined, metadata);
                results.push(docInfo);
                console.log(`Indexed: ${filename}`);
            } catch (error) {
                console.error(`Failed to index ${filename}:`, error);
            }
        }

        return results;
    }

    private async findDocumentByDisplayName(displayName: string): Promise<any | null> {
        const pager = await ai.fileSearchStores.documents.list({
            parent: this.storeName
        });

        for await (const doc of pager) {
            if (doc.displayName === displayName) {
                return doc;
            }
        }
        return null;
    }

    async listDocuments(): Promise<any[]> {
        const documents: any[] = [];
        const pager = await ai.fileSearchStores.documents.list({
            parent: this.storeName
        });

        for await (const doc of pager) {
            documents.push({
                name: doc.name,
                displayName: doc.displayName,
                state: doc.state,
                sizeBytes: doc.sizeBytes
            });
        }
        return documents;
    }

    getStoreName(): string {
        return this.storeName;
    }
}


// Usage Example
async function main() {
    // Connect or create repository
    let repo: DocumentRepository;
    try {
        repo = await DocumentRepository.connect('my-knowledge-base');
        console.log('Connected to existing repository');
    } catch {
        repo = await DocumentRepository.create('my-knowledge-base');
        console.log('Created new repository');
    }

    // Add new documents incrementally
    const newDocuments = [
        'new_docs/guide_2025.pdf',
        'new_docs/release_notes.md'
    ];

    const metadataMap = new Map<string, CustomMetadata[]>([
        ['guide_2025.pdf', [
            { key: 'doc_type', stringValue: 'guide' },
            { key: 'year', numericValue: 2025 }
        ]]
    ]);

    const results = await repo.addDocumentsBatch(newDocuments, metadataMap);
    console.log(`\nSuccessfully indexed ${results.length} new documents`);
}

main().catch(console.error);
```

---

### Removing Documents from the Index

Remove documents when they become outdated, irrelevant, or need to be replaced.

#### Python - Document Removal

```python
"""
Repository maintenance: Removing documents from the index.
"""

class DocumentRepository:
    # ... (previous methods) ...

    def remove_document(self, display_name: str, force: bool = True) -> bool:
        """
        Remove a document from the repository by display name.

        Args:
            display_name: The display name of the document to remove
            force: If True, also deletes associated chunks (recommended)

        Returns:
            True if document was found and deleted, False if not found
        """
        doc = self._find_document_by_display_name(display_name)
        if not doc:
            print(f"Document not found: {display_name}")
            return False

        client.file_search_stores.documents.delete(
            name=doc.name,
            config={'force': force}
        )
        print(f"Removed document: {display_name}")
        return True

    def remove_documents_batch(self, display_names: list) -> dict:
        """
        Remove multiple documents from the repository.

        Args:
            display_names: List of document display names to remove

        Returns:
            Dict with 'removed' and 'not_found' lists
        """
        results = {'removed': [], 'not_found': []}

        for display_name in display_names:
            if self.remove_document(display_name):
                results['removed'].append(display_name)
            else:
                results['not_found'].append(display_name)

        return results

    def remove_documents_by_metadata(self, filter_key: str, filter_value) -> list:
        """
        Remove all documents matching a metadata filter.

        Args:
            filter_key: Metadata key to filter on
            filter_value: Value to match

        Returns:
            List of removed document display names
        """
        removed = []
        pager = client.file_search_stores.documents.list(parent=self.store_name)

        for doc in pager:
            # Check if document has matching metadata
            if hasattr(doc, 'custom_metadata') and doc.custom_metadata:
                for meta in doc.custom_metadata:
                    if meta.key == filter_key:
                        # Check string value
                        if hasattr(meta, 'string_value') and meta.string_value == filter_value:
                            self.remove_document(doc.display_name)
                            removed.append(doc.display_name)
                            break
                        # Check numeric value
                        if hasattr(meta, 'numeric_value') and meta.numeric_value == filter_value:
                            self.remove_document(doc.display_name)
                            removed.append(doc.display_name)
                            break

        return removed

    def remove_all_documents(self) -> int:
        """
        Remove all documents from the repository.
        Use with caution!

        Returns:
            Number of documents removed
        """
        count = 0
        pager = client.file_search_stores.documents.list(parent=self.store_name)

        for doc in pager:
            client.file_search_stores.documents.delete(
                name=doc.name,
                config={'force': True}
            )
            count += 1
            print(f"Removed: {doc.display_name}")

        return count


# Usage Example: Removing Documents
if __name__ == "__main__":
    repo = DocumentRepository.connect("my-knowledge-base")

    # Remove a single document
    repo.remove_document("old_guide_2023.pdf")

    # Remove multiple documents
    outdated_docs = [
        "deprecated_api.txt",
        "legacy_manual.pdf",
        "old_faq.md"
    ]
    results = repo.remove_documents_batch(outdated_docs)
    print(f"Removed: {len(results['removed'])}, Not found: {len(results['not_found'])}")

    # Remove all documents from a specific year
    removed = repo.remove_documents_by_metadata("year", 2023)
    print(f"Removed {len(removed)} documents from 2023")
```

#### TypeScript - Document Removal

```typescript
/**
 * Repository maintenance: Removing documents from the index.
 */

class DocumentRepository {
    // ... (previous methods) ...

    async removeDocument(displayName: string, force: boolean = true): Promise<boolean> {
        /**
         * Remove a document from the repository by display name.
         */
        const doc = await this.findDocumentByDisplayName(displayName);
        if (!doc) {
            console.log(`Document not found: ${displayName}`);
            return false;
        }

        await ai.fileSearchStores.documents.delete({
            name: doc.name,
            config: { force: force }
        });

        console.log(`Removed document: ${displayName}`);
        return true;
    }

    async removeDocumentsBatch(displayNames: string[]): Promise<{removed: string[], notFound: string[]}> {
        /**
         * Remove multiple documents from the repository.
         */
        const results = { removed: [] as string[], notFound: [] as string[] };

        for (const displayName of displayNames) {
            if (await this.removeDocument(displayName)) {
                results.removed.push(displayName);
            } else {
                results.notFound.push(displayName);
            }
        }

        return results;
    }

    async removeAllDocuments(): Promise<number> {
        /**
         * Remove all documents from the repository.
         * Use with caution!
         */
        let count = 0;
        const pager = await ai.fileSearchStores.documents.list({
            parent: this.storeName
        });

        for await (const doc of pager) {
            await ai.fileSearchStores.documents.delete({
                name: doc.name,
                config: { force: true }
            });
            count++;
            console.log(`Removed: ${doc.displayName}`);
        }

        return count;
    }
}


// Usage Example
async function removeOutdatedDocuments() {
    const repo = await DocumentRepository.connect('my-knowledge-base');

    // Remove single document
    await repo.removeDocument('old_guide_2023.pdf');

    // Remove multiple documents
    const outdatedDocs = ['deprecated_api.txt', 'legacy_manual.pdf'];
    const results = await repo.removeDocumentsBatch(outdatedDocs);
    console.log(`Removed: ${results.removed.length}, Not found: ${results.notFound.length}`);
}
```

---

### Replacing Documents (Version Updates)

When a document is updated, you must delete the old version and upload the new one. This section provides patterns for safe document replacement with version tracking.

#### Python - Document Replacement with Version Tracking

```python
"""
Repository maintenance: Replacing documents with new versions.
Includes version tracking and rollback capabilities.
"""

from datetime import datetime
from typing import Optional
import json
import os


class VersionedDocumentRepository(DocumentRepository):
    """Repository with version tracking for document updates."""

    def __init__(self, store_name: str, version_log_path: str = "version_log.json"):
        super().__init__(store_name)
        self.version_log_path = version_log_path
        self._load_version_log()

    def _load_version_log(self):
        """Load version history from disk."""
        if os.path.exists(self.version_log_path):
            with open(self.version_log_path, 'r') as f:
                self.version_log = json.load(f)
        else:
            self.version_log = {}

    def _save_version_log(self):
        """Save version history to disk."""
        with open(self.version_log_path, 'w') as f:
            json.dump(self.version_log, f, indent=2, default=str)

    def replace_document(
        self,
        display_name: str,
        new_file_path: str,
        version: Optional[str] = None,
        metadata: Optional[list] = None,
        chunking_config: Optional[dict] = None
    ) -> DocumentInfo:
        """
        Replace an existing document with a new version.

        Args:
            display_name: The display name of the document to replace
            new_file_path: Path to the new version of the file
            version: Version identifier (auto-generated if not provided)
            metadata: Custom metadata for the new version
            chunking_config: Custom chunking configuration

        Returns:
            DocumentInfo for the newly indexed document
        """
        # Generate version if not provided
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Record the replacement in version log
        if display_name not in self.version_log:
            self.version_log[display_name] = []

        # Check if document exists and remove it
        existing_doc = self._find_document_by_display_name(display_name)
        if existing_doc:
            # Store info about the old version before deletion
            old_version_info = {
                'version': self.version_log[display_name][-1]['version'] if self.version_log[display_name] else 'initial',
                'replaced_at': datetime.now().isoformat(),
                'size_bytes': existing_doc.size_bytes
            }
            self.version_log[display_name].append({
                'action': 'replaced',
                'old_version': old_version_info,
                'new_version': version,
                'timestamp': datetime.now().isoformat()
            })

            # Delete old version
            client.file_search_stores.documents.delete(
                name=existing_doc.name,
                config={'force': True}
            )
            print(f"Removed old version of: {display_name}")
        else:
            # New document
            self.version_log[display_name].append({
                'action': 'created',
                'version': version,
                'timestamp': datetime.now().isoformat()
            })

        # Add version to metadata
        version_metadata = [{"key": "version", "string_value": version}]
        if metadata:
            version_metadata.extend(metadata)

        # Upload new version
        doc_info = self.add_document(
            file_path=new_file_path,
            display_name=display_name,
            metadata=version_metadata,
            chunking_config=chunking_config
        )

        self._save_version_log()
        print(f"Uploaded new version ({version}) of: {display_name}")
        return doc_info

    def replace_documents_batch(
        self,
        replacements: list  # List of dicts: {'display_name': str, 'file_path': str, 'metadata': list}
    ) -> list:
        """
        Replace multiple documents with new versions.

        Args:
            replacements: List of replacement specifications

        Returns:
            List of DocumentInfo for successfully replaced documents
        """
        results = []
        for replacement in replacements:
            try:
                doc_info = self.replace_document(
                    display_name=replacement['display_name'],
                    new_file_path=replacement['file_path'],
                    metadata=replacement.get('metadata')
                )
                results.append(doc_info)
            except Exception as e:
                print(f"Failed to replace {replacement['display_name']}: {e}")
        return results

    def get_version_history(self, display_name: str) -> list:
        """Get the version history for a document."""
        return self.version_log.get(display_name, [])

    def sync_directory(
        self,
        directory_path: str,
        file_extensions: list = None,
        metadata_generator: callable = None
    ) -> dict:
        """
        Sync a directory with the repository.
        Adds new files, updates modified files (based on display name).

        Args:
            directory_path: Path to directory to sync
            file_extensions: List of extensions to include (e.g., ['.pdf', '.txt'])
            metadata_generator: Function that takes filename and returns metadata list

        Returns:
            Dict with 'added', 'updated', 'unchanged' counts
        """
        results = {'added': 0, 'updated': 0, 'unchanged': 0, 'failed': 0}

        # Get existing documents
        existing_docs = {doc['display_name']: doc for doc in self.list_documents()}

        # Scan directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            # Skip directories
            if os.path.isdir(file_path):
                continue

            # Filter by extension
            if file_extensions:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in file_extensions:
                    continue

            # Generate metadata if generator provided
            metadata = metadata_generator(filename) if metadata_generator else None

            try:
                if filename in existing_docs:
                    # Document exists - replace it
                    self.replace_document(filename, file_path, metadata=metadata)
                    results['updated'] += 1
                else:
                    # New document - add it
                    self.add_document(file_path, display_name=filename, metadata=metadata)
                    results['added'] += 1
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
                results['failed'] += 1

        return results


# Usage Example: Document Replacement
if __name__ == "__main__":
    # Create versioned repository
    repo = VersionedDocumentRepository.connect("my-knowledge-base")
    repo.version_log_path = "my_kb_versions.json"
    repo._load_version_log()

    # Replace a single document
    repo.replace_document(
        display_name="Product Manual",
        new_file_path="manuals/product_manual_v2.pdf",
        version="2.0",
        metadata=[
            {"key": "doc_type", "string_value": "manual"},
            {"key": "updated_by", "string_value": "admin"}
        ]
    )

    # Replace multiple documents
    replacements = [
        {
            'display_name': 'API Reference',
            'file_path': 'docs/api_v3.pdf',
            'metadata': [{"key": "api_version", "string_value": "3.0"}]
        },
        {
            'display_name': 'FAQ',
            'file_path': 'docs/faq_updated.md'
        }
    ]
    repo.replace_documents_batch(replacements)

    # Sync an entire directory
    def generate_metadata(filename):
        return [
            {"key": "source_dir", "string_value": "docs"},
            {"key": "sync_date", "string_value": datetime.now().isoformat()}
        ]

    results = repo.sync_directory(
        directory_path="docs/",
        file_extensions=['.pdf', '.txt', '.md'],
        metadata_generator=generate_metadata
    )
    print(f"Sync complete: {results}")

    # View version history
    history = repo.get_version_history("Product Manual")
    print(f"\nVersion history for 'Product Manual':")
    for entry in history:
        print(f"  - {entry['action']} at {entry['timestamp']}")
```

#### TypeScript - Document Replacement with Version Tracking

```typescript
/**
 * Repository maintenance: Replacing documents with new versions.
 * Includes version tracking.
 */

import * as fs from 'fs';

interface VersionLogEntry {
    action: string;
    version?: string;
    oldVersion?: any;
    newVersion?: string;
    timestamp: string;
}

interface ReplacementSpec {
    displayName: string;
    filePath: string;
    metadata?: CustomMetadata[];
}


class VersionedDocumentRepository extends DocumentRepository {
    private versionLogPath: string;
    private versionLog: Map<string, VersionLogEntry[]>;

    constructor(storeName: string, versionLogPath: string = 'version_log.json') {
        super(storeName);
        this.versionLogPath = versionLogPath;
        this.versionLog = new Map();
        this.loadVersionLog();
    }

    static async connectVersioned(
        displayName: string,
        versionLogPath?: string
    ): Promise<VersionedDocumentRepository> {
        const pager = await ai.fileSearchStores.list({ config: { pageSize: 20 } });
        let page = pager.page;

        while (true) {
            for (const store of page) {
                if (store.displayName === displayName) {
                    return new VersionedDocumentRepository(store.name, versionLogPath);
                }
            }
            if (!pager.hasNextPage()) break;
            page = await pager.nextPage();
        }

        throw new Error(`Store not found: ${displayName}`);
    }

    private loadVersionLog(): void {
        if (fs.existsSync(this.versionLogPath)) {
            const data = JSON.parse(fs.readFileSync(this.versionLogPath, 'utf-8'));
            this.versionLog = new Map(Object.entries(data));
        }
    }

    private saveVersionLog(): void {
        const data = Object.fromEntries(this.versionLog);
        fs.writeFileSync(this.versionLogPath, JSON.stringify(data, null, 2));
    }

    async replaceDocument(
        displayName: string,
        newFilePath: string,
        version?: string,
        metadata?: CustomMetadata[]
    ): Promise<DocumentInfo> {
        /**
         * Replace an existing document with a new version.
         */
        // Generate version if not provided
        if (!version) {
            version = new Date().toISOString().replace(/[:-]/g, '').slice(0, 15);
        }

        // Initialize version history for this document
        if (!this.versionLog.has(displayName)) {
            this.versionLog.set(displayName, []);
        }
        const history = this.versionLog.get(displayName)!;

        // Check if document exists and remove it
        const existingDoc = await this.findDocumentByDisplayName(displayName);
        if (existingDoc) {
            history.push({
                action: 'replaced',
                oldVersion: history.length > 0 ? history[history.length - 1].version : 'initial',
                newVersion: version,
                timestamp: new Date().toISOString()
            });

            await ai.fileSearchStores.documents.delete({
                name: existingDoc.name,
                config: { force: true }
            });
            console.log(`Removed old version of: ${displayName}`);
        } else {
            history.push({
                action: 'created',
                version: version,
                timestamp: new Date().toISOString()
            });
        }

        // Add version to metadata
        const versionMetadata: CustomMetadata[] = [
            { key: 'version', stringValue: version }
        ];
        if (metadata) {
            versionMetadata.push(...metadata);
        }

        // Upload new version
        const docInfo = await this.addDocument(newFilePath, displayName, versionMetadata);

        this.saveVersionLog();
        console.log(`Uploaded new version (${version}) of: ${displayName}`);
        return docInfo;
    }

    async replaceDocumentsBatch(replacements: ReplacementSpec[]): Promise<DocumentInfo[]> {
        /**
         * Replace multiple documents with new versions.
         */
        const results: DocumentInfo[] = [];

        for (const replacement of replacements) {
            try {
                const docInfo = await this.replaceDocument(
                    replacement.displayName,
                    replacement.filePath,
                    undefined,
                    replacement.metadata
                );
                results.push(docInfo);
            } catch (error) {
                console.error(`Failed to replace ${replacement.displayName}:`, error);
            }
        }

        return results;
    }

    getVersionHistory(displayName: string): VersionLogEntry[] {
        return this.versionLog.get(displayName) || [];
    }
}


// Usage Example
async function replaceDocuments() {
    const repo = await VersionedDocumentRepository.connectVersioned(
        'my-knowledge-base',
        'my_kb_versions.json'
    );

    // Replace a single document
    await repo.replaceDocument(
        'Product Manual',
        'manuals/product_manual_v2.pdf',
        '2.0',
        [{ key: 'doc_type', stringValue: 'manual' }]
    );

    // Replace multiple documents
    const replacements: ReplacementSpec[] = [
        {
            displayName: 'API Reference',
            filePath: 'docs/api_v3.pdf',
            metadata: [{ key: 'api_version', stringValue: '3.0' }]
        },
        {
            displayName: 'FAQ',
            filePath: 'docs/faq_updated.md'
        }
    ];

    await repo.replaceDocumentsBatch(replacements);

    // View version history
    const history = repo.getVersionHistory('Product Manual');
    console.log('\nVersion history for "Product Manual":');
    for (const entry of history) {
        console.log(`  - ${entry.action} at ${entry.timestamp}`);
    }
}

replaceDocuments().catch(console.error);
```

---

### Complete Repository Manager Example

Here's a complete, production-ready repository manager that combines all maintenance operations:

```python
"""
Complete Document Repository Manager
Combines incremental indexing, removal, and replacement operations.
"""

from google import genai
from google.genai import types
from datetime import datetime
from typing import Optional, Callable
import json
import os
import time

client = genai.Client()


class DocumentRepositoryManager:
    """
    Complete repository manager for Gemini File Search stores.
    Supports incremental indexing, document removal, and version-tracked replacements.
    """

    def __init__(self, store_name: str, version_log_path: Optional[str] = None):
        self.store_name = store_name
        self.version_log_path = version_log_path or f"{store_name}_versions.json"
        self._load_version_log()

    @classmethod
    def connect_or_create(cls, display_name: str) -> 'DocumentRepositoryManager':
        """Connect to existing store or create new one."""
        # Try to find existing store
        pager = client.file_search_stores.list()
        for store in pager:
            if store.display_name == display_name:
                print(f"Connected to existing store: {display_name}")
                return cls(store.name)

        # Create new store
        store = client.file_search_stores.create(
            config={'display_name': display_name}
        )
        print(f"Created new store: {display_name}")
        return cls(store.name)

    def _load_version_log(self):
        if os.path.exists(self.version_log_path):
            with open(self.version_log_path, 'r') as f:
                self.version_log = json.load(f)
        else:
            self.version_log = {}

    def _save_version_log(self):
        with open(self.version_log_path, 'w') as f:
            json.dump(self.version_log, f, indent=2, default=str)

    def _find_document(self, display_name: str):
        pager = client.file_search_stores.documents.list(parent=self.store_name)
        for doc in pager:
            if doc.display_name == display_name:
                return doc
        return None

    def _wait_for_operation(self, operation):
        while not operation.done:
            time.sleep(2)
            operation = client.operations.get(operation)
        return operation

    # ==================== INCREMENTAL INDEXING ====================

    def add(
        self,
        file_path: str,
        display_name: Optional[str] = None,
        metadata: Optional[list] = None,
        chunking_config: Optional[dict] = None
    ) -> dict:
        """Add a new document to the repository."""
        display_name = display_name or os.path.basename(file_path)

        config = {'display_name': display_name}
        if metadata:
            config['custom_metadata'] = metadata
        if chunking_config:
            config['chunking_config'] = chunking_config

        operation = client.file_search_stores.upload_to_file_search_store(
            file=file_path,
            file_search_store_name=self.store_name,
            config=config
        )
        self._wait_for_operation(operation)

        # Log the addition
        self.version_log[display_name] = [{
            'action': 'added',
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path
        }]
        self._save_version_log()

        print(f"Added: {display_name}")
        return {'display_name': display_name, 'status': 'added'}

    def add_batch(self, files: list) -> list:
        """Add multiple documents. files: list of dicts with 'path' and optional 'name', 'metadata'."""
        results = []
        for f in files:
            try:
                result = self.add(
                    file_path=f['path'],
                    display_name=f.get('name'),
                    metadata=f.get('metadata')
                )
                results.append(result)
            except Exception as e:
                results.append({'path': f['path'], 'status': 'failed', 'error': str(e)})
        return results

    # ==================== DOCUMENT REMOVAL ====================

    def remove(self, display_name: str) -> bool:
        """Remove a document from the repository."""
        doc = self._find_document(display_name)
        if not doc:
            print(f"Not found: {display_name}")
            return False

        client.file_search_stores.documents.delete(
            name=doc.name,
            config={'force': True}
        )

        # Log the removal
        if display_name in self.version_log:
            self.version_log[display_name].append({
                'action': 'removed',
                'timestamp': datetime.now().isoformat()
            })
            self._save_version_log()

        print(f"Removed: {display_name}")
        return True

    def remove_batch(self, display_names: list) -> dict:
        """Remove multiple documents."""
        results = {'removed': [], 'not_found': []}
        for name in display_names:
            if self.remove(name):
                results['removed'].append(name)
            else:
                results['not_found'].append(name)
        return results

    def clear_all(self) -> int:
        """Remove all documents from the repository."""
        count = 0
        pager = client.file_search_stores.documents.list(parent=self.store_name)
        for doc in pager:
            client.file_search_stores.documents.delete(
                name=doc.name,
                config={'force': True}
            )
            count += 1
        print(f"Cleared {count} documents")
        return count

    # ==================== DOCUMENT REPLACEMENT ====================

    def replace(
        self,
        display_name: str,
        new_file_path: str,
        version: Optional[str] = None,
        metadata: Optional[list] = None
    ) -> dict:
        """Replace a document with a new version."""
        version = version or datetime.now().strftime("%Y%m%d_%H%M%S")

        # Remove existing if present
        existing = self._find_document(display_name)
        if existing:
            client.file_search_stores.documents.delete(
                name=existing.name,
                config={'force': True}
            )

        # Add version metadata
        version_metadata = [{"key": "version", "string_value": version}]
        if metadata:
            version_metadata.extend(metadata)

        # Upload new version
        config = {
            'display_name': display_name,
            'custom_metadata': version_metadata
        }
        operation = client.file_search_stores.upload_to_file_search_store(
            file=new_file_path,
            file_search_store_name=self.store_name,
            config=config
        )
        self._wait_for_operation(operation)

        # Log the replacement
        if display_name not in self.version_log:
            self.version_log[display_name] = []
        self.version_log[display_name].append({
            'action': 'replaced' if existing else 'added',
            'version': version,
            'timestamp': datetime.now().isoformat()
        })
        self._save_version_log()

        print(f"{'Replaced' if existing else 'Added'}: {display_name} (v{version})")
        return {'display_name': display_name, 'version': version}

    # ==================== SYNC OPERATIONS ====================

    def sync_directory(
        self,
        directory: str,
        extensions: list = None,
        metadata_fn: Callable = None
    ) -> dict:
        """Sync a directory with the repository."""
        results = {'added': 0, 'updated': 0, 'failed': 0}
        existing = {d['display_name'] for d in self.list()}

        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isdir(filepath):
                continue

            if extensions:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in extensions:
                    continue

            metadata = metadata_fn(filename) if metadata_fn else None

            try:
                if filename in existing:
                    self.replace(filename, filepath, metadata=metadata)
                    results['updated'] += 1
                else:
                    self.add(filepath, display_name=filename, metadata=metadata)
                    results['added'] += 1
            except Exception as e:
                print(f"Failed: {filename} - {e}")
                results['failed'] += 1

        return results

    # ==================== QUERY & INFO ====================

    def list(self) -> list:
        """List all documents in the repository."""
        documents = []
        pager = client.file_search_stores.documents.list(parent=self.store_name)
        for doc in pager:
            documents.append({
                'name': doc.name,
                'display_name': doc.display_name,
                'state': str(doc.state),
                'size_bytes': doc.size_bytes
            })
        return documents

    def get_history(self, display_name: str) -> list:
        """Get version history for a document."""
        return self.version_log.get(display_name, [])

    def query(self, question: str, model: str = "gemini-2.5-flash", metadata_filter: str = None) -> dict:
        """Query the repository."""
        file_search_config = types.FileSearch(file_search_store_names=[self.store_name])
        if metadata_filter:
            file_search_config.metadata_filter = metadata_filter

        response = client.models.generate_content(
            model=model,
            contents=question,
            config=types.GenerateContentConfig(
                tools=[types.Tool(file_search=file_search_config)]
            )
        )
        return {'text': response.text, 'response': response}


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Initialize repository
    repo = DocumentRepositoryManager.connect_or_create("my-knowledge-base")

    # Add new documents
    repo.add("docs/getting_started.pdf", metadata=[
        {"key": "category", "string_value": "tutorial"}
    ])

    # Add batch of documents
    repo.add_batch([
        {"path": "docs/api.pdf", "name": "API Reference"},
        {"path": "docs/faq.md", "metadata": [{"key": "category", "string_value": "support"}]}
    ])

    # Replace a document with new version
    repo.replace("API Reference", "docs/api_v2.pdf", version="2.0")

    # Sync a directory
    repo.sync_directory("docs/", extensions=[".pdf", ".md", ".txt"])

    # Remove outdated documents
    repo.remove_batch(["old_doc.pdf", "deprecated.txt"])

    # Query the repository
    result = repo.query("How do I get started?")
    print(result['text'])

    # View document list
    print("\nRepository contents:")
    for doc in repo.list():
        print(f"  - {doc['display_name']} ({doc['state']})")

    # View version history
    print("\nVersion history for 'API Reference':")
    for entry in repo.get_history("API Reference"):
        print(f"  - {entry['action']} v{entry.get('version', 'N/A')} at {entry['timestamp']}")
```

---

## Manual Embeddings API

For cases where you need more control than File Search provides, you can use the Embeddings API directly.

### Embedding Configuration

| Parameter | Options | Default |
|-----------|---------|---------|
| `model` | `gemini-embedding-001` | Required |
| `task_type` | See table below | `RETRIEVAL_DOCUMENT` |
| `output_dimensionality` | 128-3072 | 3072 |

**Task Types:**

| Task Type | Use Case |
|-----------|----------|
| `RETRIEVAL_DOCUMENT` | Indexing documents for search |
| `RETRIEVAL_QUERY` | Encoding search queries |
| `SEMANTIC_SIMILARITY` | Comparing text similarity |
| `CLASSIFICATION` | Text categorization |
| `CLUSTERING` | Grouping similar documents |
| `QUESTION_ANSWERING` | QA system optimization |
| `CODE_RETRIEVAL_QUERY` | Code search queries |
| `FACT_VERIFICATION` | Evidence retrieval |

### Python - Manual Embeddings

```python
"""Manual embeddings for custom RAG implementations."""

from google import genai
from google.genai import types
import numpy as np

client = genai.Client()


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT", dimensions: int = 768) -> list:
    """Generate embedding for a single text."""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=dimensions
        )
    )
    return result.embeddings[0].values


def embed_batch(texts: list, task_type: str = "RETRIEVAL_DOCUMENT", dimensions: int = 768) -> list:
    """Generate embeddings for multiple texts."""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=dimensions
        )
    )
    return [emb.values for emb in result.embeddings]


def cosine_similarity(vec1: list, vec2: list) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(vec1)
    b = np.array(vec2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def normalize_embedding(embedding: list) -> list:
    """L2 normalize embedding (required for dimensions < 3072)."""
    vec = np.array(embedding)
    norm = np.linalg.norm(vec)
    if norm == 0:
        return embedding
    return (vec / norm).tolist()


# Example: Simple document search
documents = [
    "The quick brown fox jumps over the lazy dog",
    "Machine learning is a subset of artificial intelligence",
    "Python is a popular programming language",
    "Neural networks are inspired by biological neurons"
]

# Embed documents (using RETRIEVAL_DOCUMENT task type)
doc_embeddings = embed_batch(documents, task_type="RETRIEVAL_DOCUMENT", dimensions=768)
doc_embeddings = [normalize_embedding(emb) for emb in doc_embeddings]

# Embed query (using RETRIEVAL_QUERY task type)
query = "What is AI?"
query_embedding = embed_text(query, task_type="RETRIEVAL_QUERY", dimensions=768)
query_embedding = normalize_embedding(query_embedding)

# Find most similar document
similarities = [cosine_similarity(query_embedding, doc_emb) for doc_emb in doc_embeddings]
best_match_idx = np.argmax(similarities)

print(f"Query: {query}")
print(f"Best match: {documents[best_match_idx]}")
print(f"Similarity: {similarities[best_match_idx]:.4f}")
```

### TypeScript - Manual Embeddings

```typescript
/**
 * Manual embeddings for custom RAG implementations.
 */

import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({});


async function embedText(
    text: string,
    taskType: string = 'RETRIEVAL_DOCUMENT',
    dimensions: number = 768
): Promise<number[]> {
    const response = await ai.models.embedContent({
        model: 'gemini-embedding-001',
        contents: [text],
        taskType: taskType,
        outputDimensionality: dimensions
    });
    return response.embeddings[0].values;
}


async function embedBatch(
    texts: string[],
    taskType: string = 'RETRIEVAL_DOCUMENT',
    dimensions: number = 768
): Promise<number[][]> {
    const response = await ai.models.embedContent({
        model: 'gemini-embedding-001',
        contents: texts,
        taskType: taskType,
        outputDimensionality: dimensions
    });
    return response.embeddings.map(emb => emb.values);
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


// Example usage
async function searchDocuments() {
    const documents = [
        'The quick brown fox jumps over the lazy dog',
        'Machine learning is a subset of artificial intelligence',
        'Python is a popular programming language',
        'Neural networks are inspired by biological neurons'
    ];

    // Embed documents
    const docEmbeddings = await embedBatch(documents, 'RETRIEVAL_DOCUMENT', 768);
    const normalizedDocs = docEmbeddings.map(normalizeEmbedding);

    // Embed query
    const query = 'What is AI?';
    const queryEmbedding = await embedText(query, 'RETRIEVAL_QUERY', 768);
    const normalizedQuery = normalizeEmbedding(queryEmbedding);

    // Find best match
    const similarities = normalizedDocs.map(doc => cosineSimilarity(normalizedQuery, doc));
    const bestMatchIdx = similarities.indexOf(Math.max(...similarities));

    console.log(`Query: ${query}`);
    console.log(`Best match: ${documents[bestMatchIdx]}`);
    console.log(`Similarity: ${similarities[bestMatchIdx].toFixed(4)}`);
}
```

---

## Best Practices

### Store Management

1. **Use descriptive display names** for stores and documents to enable lookup
2. **Limit store size to 20 GB** for optimal query latency
3. **Clean up development stores** - there's a limit of 10 stores per project
4. **Use separate stores** for different document categories when metadata filtering isn't sufficient

### Document Organization

1. **Add meaningful metadata** to documents for filtering capabilities
2. **Use consistent naming conventions** for document display names
3. **Track document versions** through metadata or naming schemes
4. **Monitor document states** - check for FAILED status after uploads

### Chunking Strategy

1. **Smaller chunks (200-300 tokens)** for:
   - FAQ documents
   - Short, self-contained answers
   - High-precision retrieval needs

2. **Larger chunks (500-1000 tokens)** for:
   - Technical documentation
   - Narrative content
   - Complex explanations requiring context

3. **Increase overlap** when documents have interconnected concepts

### Query Optimization

1. **Be specific in queries** - semantic search benefits from clear intent
2. **Use metadata filters** to narrow search scope and improve relevance
3. **Query multiple stores** (up to 5) when information spans categories
4. **Iterate on chunk sizes** based on response quality

### Error Handling

```python
# Python - Robust error handling
import time
from google.api_core import exceptions

def upload_with_retry(store_name: str, file_path: str, max_retries: int = 3) -> bool:
    """Upload with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            operation = client.file_search_stores.upload_to_file_search_store(
                file=file_path,
                file_search_store_name=store_name,
                config={'display_name': os.path.basename(file_path)}
            )

            while not operation.done:
                time.sleep(2)
                operation = client.operations.get(operation)

            if hasattr(operation, 'error') and operation.error:
                raise Exception(f"Operation failed: {operation.error}")

            return True

        except exceptions.ResourceExhausted:
            wait_time = (2 ** attempt) * 5  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise

    return False
```

---

## Limitations and Considerations

### Technical Limits

| Limit | Value |
|-------|-------|
| Maximum file size | 100 MB per document |
| Maximum stores per query | 5 |
| Maximum stores per project | 10 (soft limit) |
| Maximum metadata entries | 20 per document |
| Display name length | 512 characters |
| Recommended store size | < 20 GB for optimal latency |

### Storage Tier Limits

| Tier | Storage Limit |
|------|--------------|
| Free | 1 GB |
| Tier 1 | 10 GB |
| Tier 2 | 100 GB |
| Tier 3 | 1 TB |

### Supported File Formats

**Documents:**
- PDF, DOCX, XLSX, PPTX
- ODT, RTF
- JSON, XML

**Text:**
- TXT, CSV, TSV
- Markdown (MD)
- HTML, YAML

**Code (50+ languages):**
- Python, JavaScript, TypeScript
- Java, C++, C#, Go, Rust
- SQL, Shell scripts
- And many more

### Known Limitations

1. **Black box nature** - Limited control over chunking and retrieval algorithms
2. **No custom embeddings** - Must use Gemini's embedding model
3. **Immutable documents** - Updates require delete + re-upload
4. **Processing time** - Large files may take time to index
5. **File expiration** - Files API uploads expire in 48 hours (but imported data persists)

---

## Pricing

### File Search Pricing Model

| Component | Cost |
|-----------|------|
| **Indexing (embedding generation)** | $0.15 per 1M tokens |
| **Storage** | Free |
| **Query-time embeddings** | Free |
| **Retrieved document tokens** | Standard input token rate |

### Cost Estimation Example

For a knowledge base with:
- 100 documents averaging 10,000 tokens each = 1M tokens total
- Indexing cost: 1M tokens × $0.15 = **$0.15 one-time**

Query costs depend on the model used:
- Retrieved context counts against input token costs
- Model output counts against output token costs

---

## Resources

### Official Documentation

- [File Search Overview](https://ai.google.dev/gemini-api/docs/file-search)
- [File Search Stores API Reference](https://ai.google.dev/api/file-search/file-search-stores)
- [Documents API Reference](https://ai.google.dev/api/file-search/documents)
- [Embeddings API](https://ai.google.dev/gemini-api/docs/embeddings)
- [Google AI Studio](https://aistudio.google.com/)

### SDKs and Libraries

- [Python SDK (google-genai)](https://pypi.org/project/google-genai/) | [GitHub](https://github.com/googleapis/python-genai)
- [TypeScript/JavaScript SDK (@google/genai)](https://www.npmjs.com/package/@google/genai) | [GitHub](https://github.com/googleapis/js-genai)

### Tutorials and Examples

- [Google Blog: Introducing File Search](https://blog.google/technology/developers/file-search-gemini-api/)
- [Gemini File Search JavaScript Tutorial](https://www.philschmid.de/gemini-file-search-javascript)
- [Google Document Search Notebook](https://github.com/google/generative-ai-docs/blob/main/site/en/gemini-api/tutorials/document_search.ipynb)

---

*Document created: December 28, 2025*
*Last updated: December 28, 2025*
