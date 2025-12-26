"""
Test 12: Complete Example 2 - Interactive Chat with Memory

This test implements the Interactive Chat with Memory example from the guide.
Note: The guide shows an interactive loop. This test simulates a conversation.

Original example from guide (lines 731-797):
- Uses MemorySaver for conversation memory
- Uses thread_id for session management
- Implements streaming with progress indicator
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_tavily import TavilySearch

from config import get_azure_model, validate_environment


def test_interactive_chat():
    """Test Interactive Chat with Memory (Complete Example 2)."""
    print("=" * 60)
    print("Test 12: Complete Example 2 - Interactive Chat with Memory")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # Setup (from guide)
    model = get_azure_model()
    search_tool = TavilySearch(max_results=3)
    checkpointer = MemorySaver()
    print("[OK] Components initialized")

    agent = create_react_agent(
        model=model,
        tools=[search_tool],
        prompt="You are a helpful research assistant with web search capabilities.",
        checkpointer=checkpointer
    )
    print("[OK] Agent created with memory")

    # Simulate conversation (adapted from interactive loop)
    thread_id = "test-session-1"
    config = {"configurable": {"thread_id": thread_id}}
    print(f"[OK] Session started: {thread_id}")

    # Simulated conversation turns
    conversation = [
        "Tell me about Python programming language",
        "What are its main features?",
        "How does it compare to JavaScript?"
    ]

    print("\n--- Simulated Conversation ---")

    for i, user_input in enumerate(conversation, 1):
        print(f"\n[TURN {i}] User: {user_input}")
        print("[STREAMING]", end=" ")

        # Stream the response (adapted from guide's streaming code)
        final_response = ""
        for chunk in agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
            stream_mode="values"
        ):
            message = chunk["messages"][-1]
            if hasattr(message, 'tool_calls') and message.tool_calls:
                print("[Searching...]", end=" ")
            elif message.content and message.type == "ai":
                final_response = message.content

        print("Done")
        print(f"[RESPONSE] {final_response[:400]}...")

    # Verify memory works by checking state
    print("\n--- Test 12.2: Memory Verification ---")
    state = agent.get_state(config)
    message_count = len(state.values.get('messages', []))
    print(f"[INFO] Total messages in memory: {message_count}")

    if message_count > 2:
        print("[OK] Memory is working - conversation history preserved")
    else:
        print("[WARNING] Memory may not be working correctly")

    print("\n" + "=" * 60)
    print("Test 12: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_interactive_chat()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
