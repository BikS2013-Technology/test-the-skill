"""
Test script for: Python DocumentRepositoryManager
From document: Gemini-File-Search-Tool-Guide.md
Document lines: 2193-2522

Tests the complete DocumentRepositoryManager class for repository maintenance.
"""
import sys
import os
import time
import json
from datetime import datetime
from typing import Optional, Callable

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def validate_environment():
    """Validate required environment variables."""
    required_vars = ["GEMINI_API_KEY"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")


# ============ CODE FROM DOCUMENT (lines 2193-2522) ============

from google import genai
from google.genai import types

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


# ============ TEST EXECUTION ============

def test_document_repository_manager():
    """Test the DocumentRepositoryManager class from the guide."""
    print("=" * 60)
    print("Test: Python DocumentRepositoryManager (Lines 2193-2522)")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # Get the test documents path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_docs_dir = os.path.join(script_dir, "test_documents")

    # Set version log path to test directory
    version_log_path = os.path.join(script_dir, "test_repo_versions.json")

    # Clean up any existing version log
    if os.path.exists(version_log_path):
        os.remove(version_log_path)

    # Initialize repository
    print("\n--- Testing Repository Creation ---")
    repo = DocumentRepositoryManager.connect_or_create("test-repo-manager")
    repo.version_log_path = version_log_path
    repo._load_version_log()
    print(f"[OK] Repository initialized: {repo.store_name}")

    try:
        # Test add() method
        print("\n--- Testing add() method ---")
        manual_path = os.path.join(test_docs_dir, "sample_manual.txt")
        result = repo.add(manual_path, display_name="Product Manual", metadata=[
            {"key": "category", "string_value": "tutorial"}
        ])
        assert result['status'] == 'added', f"Expected 'added' status, got {result['status']}"
        print("[OK] Single document added")

        # Test add_batch() method
        print("\n--- Testing add_batch() method ---")
        faq_path = os.path.join(test_docs_dir, "faq.txt")
        api_path = os.path.join(test_docs_dir, "api_reference.txt")
        batch_results = repo.add_batch([
            {"path": faq_path, "name": "FAQ Document"},
            {"path": api_path, "metadata": [{"key": "category", "string_value": "reference"}]}
        ])
        assert len(batch_results) == 2, f"Expected 2 results, got {len(batch_results)}"
        print(f"[OK] Batch added {len(batch_results)} documents")

        # Test list() method
        print("\n--- Testing list() method ---")
        docs = repo.list()
        assert len(docs) == 3, f"Expected 3 documents, got {len(docs)}"
        print(f"[OK] Listed {len(docs)} documents:")
        for doc in docs:
            print(f"  - {doc['display_name']} ({doc['state']})")

        # Test replace() method
        print("\n--- Testing replace() method ---")
        replace_result = repo.replace("Product Manual", manual_path, version="2.0")
        assert replace_result['version'] == "2.0", f"Expected version '2.0', got {replace_result['version']}"
        print(f"[OK] Document replaced with version {replace_result['version']}")

        # Test get_history() method
        print("\n--- Testing get_history() method ---")
        history = repo.get_history("Product Manual")
        assert len(history) >= 2, f"Expected at least 2 history entries, got {len(history)}"
        print(f"[OK] History has {len(history)} entries:")
        for entry in history:
            print(f"  - {entry['action']} at {entry['timestamp']}")

        # Test query() method
        print("\n--- Testing query() method ---")
        query_result = repo.query("How do I reset the device?")
        assert query_result['text'], "Expected non-empty response"
        print(f"[OK] Query returned response (first 100 chars): {query_result['text'][:100]}...")

        # Test remove() method
        print("\n--- Testing remove() method ---")
        removed = repo.remove("FAQ Document")
        assert removed, "Expected document to be removed"
        print("[OK] Document removed")

        # Test remove_batch() method
        print("\n--- Testing remove_batch() method ---")
        remove_results = repo.remove_batch(["api_reference.txt", "nonexistent.txt"])
        assert "api_reference.txt" in remove_results['removed'], "Expected api_reference.txt to be removed"
        assert "nonexistent.txt" in remove_results['not_found'], "Expected nonexistent.txt in not_found"
        print(f"[OK] Batch remove: {len(remove_results['removed'])} removed, {len(remove_results['not_found'])} not found")

        # Test clear_all() method
        print("\n--- Testing clear_all() method ---")
        cleared = repo.clear_all()
        print(f"[OK] Cleared {cleared} remaining documents")

    finally:
        # Clean up the store
        print("\n--- Cleanup ---")
        client.file_search_stores.delete(
            name=repo.store_name,
            config={'force': True}
        )
        print(f"[OK] Store deleted: {repo.store_name}")

        # Clean up version log
        if os.path.exists(version_log_path):
            os.remove(version_log_path)
            print(f"[OK] Version log cleaned up")

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_document_repository_manager()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
