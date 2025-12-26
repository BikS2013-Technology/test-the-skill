"""
Test 07: Streaming Responses

This test implements the streaming examples from the guide.

Original examples from guide (lines 418-480):
- Stream State Values (lines 418-435)
- Stream State Updates (lines 439-450)
- Stream with Progress Indicator (lines 454-480)
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch

from config import get_azure_model, validate_environment


def test_stream_values():
    """Test streaming with stream_mode='values'."""
    print("\n--- Test 7.1: Stream State Values ---")
    print("-" * 40)

    model = get_azure_model()
    search_tool = TavilySearch(max_results=3)
    agent = create_react_agent(model, tools=[search_tool])

    print("[QUERY] What is quantum computing?")
    print("[STREAMING VALUES]")

    # Stream complete state at each step
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "What is quantum computing?"}]},
        stream_mode="values"
    ):
        # Get the latest message
        message = chunk["messages"][-1]
        print(f"  [MSG TYPE] {message.type}")
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"  [TOOL CALLS] {len(message.tool_calls)} tool(s)")
        if message.content:
            content_preview = str(message.content)[:100]
            print(f"  [CONTENT] {content_preview}...")

    print("[OK] Stream values completed")


def test_stream_updates():
    """Test streaming with stream_mode='updates'."""
    print("\n--- Test 7.2: Stream State Updates ---")
    print("-" * 40)

    model = get_azure_model()
    search_tool = TavilySearch(max_results=3)
    agent = create_react_agent(model, tools=[search_tool])

    print("[QUERY] Search for AI news")
    print("[STREAMING UPDATES]")

    # Stream only the changes at each step
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "Search for AI news"}]},
        stream_mode="updates"
    ):
        for node_name, update in chunk.items():
            print(f"\n  --- Update from: {node_name} ---")
            if "messages" in update:
                for msg in update["messages"]:
                    print(f"    [MSG TYPE] {msg.type}")
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tc in msg.tool_calls:
                            print(f"    [TOOL] {tc['name']}")
                    if msg.content:
                        content_preview = str(msg.content)[:100]
                        print(f"    [CONTENT] {content_preview}...")

    print("\n[OK] Stream updates completed")


def stream_with_progress(agent, question: str):
    """Stream agent response with progress updates (from guide lines 454-480)."""
    print(f"\n[QUERY] {question}")
    print("[PROGRESS]")

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values"
    ):
        message = chunk["messages"][-1]

        # Check if it's a tool call
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tc in message.tool_calls:
                query = tc['args'].get('query', 'N/A')
                print(f"  [Searching: {query}]")

        # Check if it's a tool response
        elif message.type == "tool":
            print(f"  [Received search results]")

        # Final response
        elif message.type == "ai" and message.content:
            print(f"\n[ANSWER]\n{message.content[:500]}...")


def test_stream_progress():
    """Test streaming with progress indicator."""
    print("\n--- Test 7.3: Stream with Progress Indicator ---")
    print("-" * 40)

    model = get_azure_model()
    search_tool = TavilySearch(max_results=3)
    agent = create_react_agent(model, tools=[search_tool])

    stream_with_progress(agent, "What are the latest breakthroughs in fusion energy?")

    print("\n[OK] Stream with progress completed")


def test_streaming():
    """Run all streaming tests."""
    print("=" * 60)
    print("Test 07: Streaming Responses")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    test_stream_values()
    test_stream_updates()
    test_stream_progress()

    print("\n" + "=" * 60)
    print("Test 07: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_streaming()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
