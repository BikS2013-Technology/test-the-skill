"""
Test 08: Async Streaming

This test implements the async streaming example from the guide.

Original example from guide (lines 484-504):
- Uses asyncio for async streaming
- Uses agent.astream() method
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

import asyncio
from langchain.agents import create_react_agent
from langchain_tavily import TavilySearch

from config import get_azure_model, validate_environment


async def async_stream_agent():
    """Async streaming example from the guide."""
    model = get_azure_model()
    search_tool = TavilySearch(max_results=3)
    agent = create_react_agent(model, tools=[search_tool])

    print("[QUERY] Latest tech news")
    print("[ASYNC STREAMING]")

    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": "Latest tech news"}]},
        stream_mode="values"
    ):
        message = chunk["messages"][-1]
        if message.content:
            content_preview = str(message.content)[:200]
            print(f"  [CHUNK] {content_preview}...")


def test_async_streaming():
    """Run async streaming test."""
    print("=" * 60)
    print("Test 08: Async Streaming")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    print("\n--- Test 8.1: Async Streaming with astream() ---")
    print("-" * 40)

    # Run async
    asyncio.run(async_stream_agent())

    print("\n[OK] Async streaming completed")

    print("\n" + "=" * 60)
    print("Test 08: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_async_streaming()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
