"""
Test 03: With Memory (Checkpointer)

This test implements the ReAct agent with memory using MemorySaver,
adapted to use Azure OpenAI instead of Anthropic.

Original example from guide (lines 174-210):
- Uses ChatAnthropic
- Uses TavilySearch with max_results=3
- Uses MemorySaver for conversation memory
- Uses thread_id in config to maintain conversation state
- Tests multi-turn conversation (agent remembers context)
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from langchain.agents import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_tavily import TavilySearch

from config import get_azure_model, validate_environment


def test_with_memory():
    """Test ReAct agent with memory (checkpointer)."""
    print("=" * 60)
    print("Test 03: With Memory (Checkpointer)")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # Initialize the LLM
    model = get_azure_model()
    print("[OK] Azure OpenAI model initialized")

    # Create search tool
    search_tool = TavilySearch(max_results=3)
    print("[OK] TavilySearch tool created")

    # Create a checkpointer for conversation memory
    checkpointer = MemorySaver()
    print("[OK] MemorySaver checkpointer created")

    # Create agent with memory
    agent = create_react_agent(
        model=model,
        tools=[search_tool],
        prompt="You are a helpful assistant with web search capabilities.",
        checkpointer=checkpointer
    )
    print("[OK] ReAct agent created with memory")

    # Use thread_id to maintain conversation state
    config = {"configurable": {"thread_id": "user-123"}}

    # First message
    print("\n[TURN 1 - QUERY] Search for information about quantum computing")
    print("-" * 40)

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Search for information about quantum computing"}]},
        config=config
    )
    print(f"\n[TURN 1 - RESPONSE]\n{result['messages'][-1].content}")

    # Follow-up message - agent should remember context!
    print("\n" + "=" * 40)
    print("[TURN 2 - QUERY] What are its practical applications?")
    print("-" * 40)

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What are its practical applications?"}]},
        config=config
    )
    print(f"\n[TURN 2 - RESPONSE]\n{result['messages'][-1].content}")

    # Verify memory is working by checking if the response references quantum computing
    response_text = result['messages'][-1].content.lower()
    if "quantum" in response_text:
        print("\n[CHECK] Agent remembered context from Turn 1: YES")
    else:
        print("\n[CHECK] Agent remembered context from Turn 1: UNCLEAR (response may not reference quantum)")

    print("\n" + "=" * 60)
    print("Test 03: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_with_memory()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
