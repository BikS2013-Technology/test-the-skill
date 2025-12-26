"""
Test 09: Dynamic Prompts

This test implements the dynamic prompt examples from the guide.

Original examples from guide (lines 585-657):
- Static Prompt (lines 585-590)
- Dynamic Prompt Function (lines 595-618)
- Custom State with User Information (lines 624-657)
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from langchain_core.messages import AnyMessage
from langchain_tavily import TavilySearch
from langchain.agents import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState

from config import get_azure_model, validate_environment


def test_static_prompt():
    """Test static prompt (from guide lines 585-590)."""
    print("\n--- Test 9.1: Static Prompt ---")
    print("-" * 40)

    model = get_azure_model()
    search_tool = TavilySearch(max_results=3)

    agent = create_react_agent(
        model=model,
        tools=[search_tool],
        prompt="You are a research assistant specializing in technology news. Always cite sources."
    )
    print("[OK] Agent created with static prompt")

    result = agent.invoke({
        "messages": [{"role": "user", "content": "What are the latest AI developments?"}]
    })
    print(f"[RESPONSE] {result['messages'][-1].content[:300]}...")


def test_dynamic_prompt():
    """Test dynamic prompt function (from guide lines 595-618)."""
    print("\n--- Test 9.2: Dynamic Prompt Function ---")
    print("-" * 40)

    model = get_azure_model()
    search_tool = TavilySearch(max_results=3)

    def dynamic_prompt(state) -> list[AnyMessage]:
        """Generate dynamic system prompt based on state."""
        user_context = state.get("user_context", "general user")

        system_content = f"""You are a helpful research assistant.
User context: {user_context}

Guidelines:
1. Always search for current, accurate information
2. Cite sources with URLs
3. Be concise but comprehensive
4. If uncertain, search again with different terms
"""
        return [{"role": "system", "content": system_content}] + state["messages"]

    agent = create_react_agent(
        model=model,
        tools=[search_tool],
        prompt=dynamic_prompt
    )
    print("[OK] Agent created with dynamic prompt function")

    result = agent.invoke({
        "messages": [{"role": "user", "content": "What is machine learning?"}],
        "user_context": "beginner in AI"
    })
    print(f"[RESPONSE] {result['messages'][-1].content[:300]}...")


def test_custom_state():
    """Test custom state with user information (from guide lines 624-657)."""
    print("\n--- Test 9.3: Custom State with User Information ---")
    print("-" * 40)

    model = get_azure_model()
    search_tool = TavilySearch(max_results=3)

    class CustomState(AgentState):
        """Extended state with user information."""
        user_name: str
        user_preferences: dict

    def personalized_prompt(state: CustomState) -> list[AnyMessage]:
        """Create personalized prompt based on user state."""
        name = state.get("user_name", "User")
        prefs = state.get("user_preferences", {})

        system_msg = f"""You are a personal research assistant for {name}.
User preferences: {prefs}
Search the web to provide accurate, personalized responses."""

        return [{"role": "system", "content": system_msg}] + state["messages"]

    agent = create_react_agent(
        model=model,
        tools=[search_tool],
        state_schema=CustomState,
        prompt=personalized_prompt
    )
    print("[OK] Agent created with custom state schema")

    # Invoke with custom state
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Find me some good restaurants"}],
        "user_name": "Alice",
        "user_preferences": {"cuisine": "Italian", "location": "NYC"}
    })
    print(f"[RESPONSE] {result['messages'][-1].content[:400]}...")


def test_dynamic_prompts():
    """Run all dynamic prompt tests."""
    print("=" * 60)
    print("Test 09: Dynamic Prompts")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    test_static_prompt()
    test_dynamic_prompt()
    test_custom_state()

    print("\n" + "=" * 60)
    print("Test 09: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_dynamic_prompts()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
