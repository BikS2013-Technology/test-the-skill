"""
Test script for: Python Basic Workflow
From document: Gemini-File-Search-Tool-Guide.md
Document lines: 165-289

Tests the complete workflow example: create store, upload documents, query, and cleanup.
"""
import sys
import os
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def validate_environment():
    """Validate required environment variables."""
    required_vars = ["GEMINI_API_KEY"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")


def test_python_basic_workflow():
    """Test the Python basic workflow from the guide."""
    print("=" * 60)
    print("Test: Python Basic Workflow (Lines 165-289)")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # Import the library
    from google import genai
    from google.genai import types
    print("[OK] Imports successful")

    # Initialize client
    client = genai.Client()
    print("[OK] Client initialized")

    # ============ CODE FROM DOCUMENT (adapted) ============

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

    # ============ EXECUTE THE TEST ============

    # Get the test documents path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_docs_dir = os.path.join(script_dir, "test_documents")

    # Create a store
    store_name = create_document_store("test-knowledge-base-basic")
    print(f"[OK] Store created: {store_name}")

    try:
        # Upload documents
        manual_path = os.path.join(test_docs_dir, "sample_manual.txt")
        faq_path = os.path.join(test_docs_dir, "faq.txt")

        upload_document(store_name, manual_path, "Product Manual")
        print("[OK] Product Manual uploaded")

        upload_document(store_name, faq_path, "FAQ Document")
        print("[OK] FAQ Document uploaded")

        # Query the documents
        result = query_documents(
            store_name,
            "How do I reset the device to factory settings?"
        )

        print("\n=== Response ===")
        print(result['text'])

        print("\n=== Citations ===")
        if result['citations']:
            for citation in result['citations']:
                text_preview = citation['text'][:100] if citation['text'] else 'N/A'
                print(f"- {citation['title']}: {text_preview}...")
        else:
            print("No citations returned (this may be normal depending on the response)")

        print("\n[OK] Query executed successfully")

    finally:
        # Clean up
        delete_store(store_name)
        print("[OK] Store cleaned up")

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_python_basic_workflow()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
