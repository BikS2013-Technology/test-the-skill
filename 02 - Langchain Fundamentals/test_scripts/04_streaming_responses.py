"""
Test Script 04: Streaming Responses Examples
Tests streaming capabilities from the LangChain Fundamentals Guide.
"""

import os
import asyncio
from langchain_openai import AzureChatOpenAI

# Validate required environment variables
required_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT"
]

for var in required_vars:
    if not os.environ.get(var):
        raise ValueError(f"{var} environment variable is required")


def get_model():
    """Get configured Azure OpenAI model."""
    return AzureChatOpenAI(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"]
    )


def test_basic_streaming():
    """
    Test Example: Basic Streaming (Document Section: Streaming Responses)
    From lines 592-595
    """
    print("\n=== Test: Basic Streaming ===")

    model = get_model()

    # Stream token by token
    print("Streaming response: ", end="")
    for chunk in model.stream("Why do parrots talk? Answer in one sentence."):
        print(chunk.content, end="", flush=True)
    print("\n")
    return True


async def test_async_streaming_with_events():
    """
    Test Example: Async Streaming with Events (Document Section: Streaming Responses)
    From lines 602-611

    NOTE: The document shows event["data"]["chunk"].text but in the current LangChain version
    it should be event["data"]["chunk"].content
    """
    print("\n=== Test: Async Streaming with Events ===")

    model = get_model()

    print("Event stream:")
    async for event in model.astream_events("Hello, say hi back briefly", version="v2"):
        if event["event"] == "on_chat_model_start":
            print(f"  [START] Input: {event['data'].get('input', 'N/A')}")

        elif event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            # NOTE: Document uses .text but should be .content
            content = getattr(chunk, 'content', getattr(chunk, 'text', ''))
            if content:
                print(f"  [CHUNK] Token: {content}")

        elif event["event"] == "on_chat_model_end":
            output = event["data"].get("output")
            if output:
                # NOTE: Document uses .text but should be .content
                content = getattr(output, 'content', getattr(output, 'text', ''))
                print(f"  [END] Full message: {content}")

    return True


def test_aggregating_streamed_chunks():
    """
    Test Example: Aggregating Streamed Chunks (Document Section: Streaming Responses)
    From lines 630-645

    NOTE: The document shows full.text but in the current LangChain version
    it should be full.content
    """
    print("\n=== Test: Aggregating Streamed Chunks ===")

    model = get_model()

    full = None
    print("Progressive aggregation:")
    for chunk in model.stream("What color is the sky? Answer briefly."):
        full = chunk if full is None else full + chunk
        # NOTE: Document uses full.text but should be full.content
        content = getattr(full, 'content', getattr(full, 'text', ''))
        print(f"  {content}")

    print(f"\nFinal content: {full.content}")

    # NOTE: Document mentions content_blocks but this may not exist in all versions
    if hasattr(full, 'content_blocks'):
        print(f"Content blocks: {full.content_blocks}")
    else:
        print("Note: content_blocks attribute not available in this version")

    return True


def test_batch_processing():
    """
    Test Example: Batch Processing (Document Section: Streaming Responses)
    From lines 652-666
    """
    print("\n=== Test: Batch Processing ===")

    model = get_model()

    # Standard batch (waits for all to complete)
    print("Standard batch:")
    responses = model.batch([
        "Why do parrots have colorful feathers? One sentence.",
        "How do airplanes fly? One sentence.",
        "What is quantum computing? One sentence."
    ])

    for i, response in enumerate(responses, 1):
        print(f"  Response {i}: {response.content}")

    print("\nBatch as completed:")
    # Batch as completed (returns results as they finish)
    for idx, response in model.batch_as_completed([
        "Why do parrots have colorful feathers? One sentence.",
        "How do airplanes fly? One sentence.",
        "What is quantum computing? One sentence."
    ]):
        print(f"  Response (idx={idx}): {response.content}")

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Fundamentals - Streaming Responses Tests")
    print("=" * 60)

    tests = [
        ("Basic Streaming", test_basic_streaming),
        ("Async Streaming with Events", lambda: asyncio.run(test_async_streaming_with_events())),
        ("Aggregating Streamed Chunks", test_aggregating_streamed_chunks),
        ("Batch Processing", test_batch_processing),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, "PASSED" if success else "FAILED"))
        except Exception as e:
            results.append((name, f"ERROR: {e}"))

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    for name, result in results:
        print(f"{name}: {result}")
