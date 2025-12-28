"""
Test script for: Python Manual Embeddings
From document: Gemini-File-Search-Tool-Guide.md
Document lines: 2553-2628

Tests the manual embeddings API for custom RAG implementations.
"""
import sys
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def validate_environment():
    """Validate required environment variables."""
    required_vars = ["GEMINI_API_KEY"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")


def test_python_manual_embeddings():
    """Test the Python manual embeddings from the guide."""
    print("=" * 60)
    print("Test: Python Manual Embeddings (Lines 2553-2628)")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # ============ CODE FROM DOCUMENT ============

    from google import genai
    from google.genai import types
    import numpy as np

    client = genai.Client()
    print("[OK] Client initialized")

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

    # ============ EXECUTE THE TEST ============

    # Test single embedding
    print("\n--- Testing Single Embedding ---")
    test_text = "Machine learning is a subset of artificial intelligence"
    embedding = embed_text(test_text, task_type="RETRIEVAL_DOCUMENT", dimensions=768)
    print(f"[OK] Generated embedding with {len(embedding)} dimensions")
    assert len(embedding) == 768, f"Expected 768 dimensions, got {len(embedding)}"

    # Test batch embedding
    print("\n--- Testing Batch Embeddings ---")
    documents = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Python is a popular programming language",
        "Neural networks are inspired by biological neurons"
    ]

    # Embed documents (using RETRIEVAL_DOCUMENT task type)
    doc_embeddings = embed_batch(documents, task_type="RETRIEVAL_DOCUMENT", dimensions=768)
    print(f"[OK] Generated {len(doc_embeddings)} document embeddings")
    assert len(doc_embeddings) == 4, f"Expected 4 embeddings, got {len(doc_embeddings)}"

    # Normalize embeddings
    doc_embeddings = [normalize_embedding(emb) for emb in doc_embeddings]
    print("[OK] Normalized document embeddings")

    # Embed query (using RETRIEVAL_QUERY task type)
    print("\n--- Testing Query Embedding ---")
    query = "What is AI?"
    query_embedding = embed_text(query, task_type="RETRIEVAL_QUERY", dimensions=768)
    query_embedding = normalize_embedding(query_embedding)
    print(f"[OK] Generated query embedding with {len(query_embedding)} dimensions")

    # Find most similar document
    print("\n--- Testing Cosine Similarity ---")
    similarities = [cosine_similarity(query_embedding, doc_emb) for doc_emb in doc_embeddings]
    best_match_idx = np.argmax(similarities)

    print(f"Query: {query}")
    print(f"Best match: {documents[best_match_idx]}")
    print(f"Similarity: {similarities[best_match_idx]:.4f}")

    # Verify the best match is the AI-related document
    expected_best = "Machine learning is a subset of artificial intelligence"
    assert documents[best_match_idx] == expected_best, \
        f"Expected best match to be '{expected_best}', got '{documents[best_match_idx]}'"
    print("[OK] Semantic search returned correct best match")

    print("\n" + "=" * 60)
    print("Test: PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        test_python_manual_embeddings()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
