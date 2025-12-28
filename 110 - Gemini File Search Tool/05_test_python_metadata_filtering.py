"""
Test script for: Python Metadata and Filtering
From document: Gemini-File-Search-Tool-Guide.md
Document lines: 689-762

Tests custom metadata addition and metadata filtering in queries.
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


def test_python_metadata_filtering():
    """Test Python metadata and filtering from the guide."""
    print("=" * 60)
    print("Test: Python Metadata and Filtering (Lines 689-762)")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    from google import genai
    from google.genai import types

    client = genai.Client()
    print("[OK] Client initialized")

    # Get the test documents path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_docs_dir = os.path.join(script_dir, "test_documents")

    # Create a store
    store = client.file_search_stores.create(
        config={'display_name': 'test-metadata-filtering'}
    )
    store_name = store.name
    print(f"[OK] Store created: {store_name}")

    try:
        # ============ CODE FROM DOCUMENT: Adding custom metadata ============
        print("\n--- Testing Custom Metadata Upload ---")

        # Python - Adding custom metadata (adapted for test)
        custom_metadata = [
            {"key": "author", "string_value": "John Smith"},
            {"key": "department", "string_value": "Engineering"},
            {"key": "year", "numeric_value": 2025},
            {"key": "tags", "string_list_value": {"values": ["manual", "technical", "v2"]}}
        ]

        manual_path = os.path.join(test_docs_dir, "sample_manual.txt")

        operation = client.file_search_stores.upload_to_file_search_store(
            file=manual_path,
            file_search_store_name=store_name,
            config={
                'display_name': 'Engineering Manual v2',
                'custom_metadata': custom_metadata
            }
        )

        while not operation.done:
            print("  Processing...")
            time.sleep(2)
            operation = client.operations.get(operation)

        print("[OK] Document uploaded with custom metadata")

        # Upload another document with different metadata for filtering test
        faq_metadata = [
            {"key": "author", "string_value": "Jane Doe"},
            {"key": "department", "string_value": "Support"},
            {"key": "year", "numeric_value": 2024}
        ]

        faq_path = os.path.join(test_docs_dir, "faq.txt")

        operation = client.file_search_stores.upload_to_file_search_store(
            file=faq_path,
            file_search_store_name=store_name,
            config={
                'display_name': 'Support FAQ 2024',
                'custom_metadata': faq_metadata
            }
        )

        while not operation.done:
            print("  Processing...")
            time.sleep(2)
            operation = client.operations.get(operation)

        print("[OK] Second document uploaded with different metadata")

        # ============ CODE FROM DOCUMENT: Query with metadata filter ============
        print("\n--- Testing Query with Metadata Filter ---")

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

        print(f"[OK] Query with filter executed")
        print(f"Response (first 200 chars): {response.text[:200]}...")

        # Test that we got a response
        assert response.text, "Expected non-empty response"
        print("[OK] Response received for filtered query")

        # Test with another filter
        print("\n--- Testing Query with Different Filter ---")

        response2 = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="How do I reset my password?",
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store_name],
                            metadata_filter='department="Support"'
                        )
                    )
                ]
            )
        )

        print(f"[OK] Query with Support filter executed")
        print(f"Response (first 200 chars): {response2.text[:200]}...")
        assert response2.text, "Expected non-empty response"
        print("[OK] Response received for Support filter query")

    finally:
        # Clean up
        client.file_search_stores.delete(
            name=store_name,
            config={'force': True}
        )
        print(f"\n[OK] Store cleaned up: {store_name}")

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_python_metadata_filtering()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
