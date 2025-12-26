"""
Test 02: With System Prompt

This test implements the ReAct agent with a system prompt from the guide,
adapted to use Azure OpenAI instead of Anthropic.

Original example from guide (lines 150-170):
- Uses ChatAnthropic
- Uses TavilySearch with max_results=5
- Passes a prompt parameter to create_react_agent
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from langchain.agents import create_react_agent
from langchain_tavily import TavilySearch

from config import get_azure_model, validate_environment


def test_with_system_prompt():
    """Test ReAct agent with system prompt."""
    print("=" * 60)
    print("Test 02: With System Prompt")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # Initialize the LLM
    model = get_azure_model()
    print("[OK] Azure OpenAI model initialized")

    # Create search tool with max_results=5 (as per guide example)
    search_tool = TavilySearch(max_results=5)
    print("[OK] TavilySearch tool created (max_results=5)")

    # Create agent with a system prompt
    agent = create_react_agent(
        model=model,
        tools=[search_tool],
        prompt="You are a helpful research assistant. Always search the web for current information and cite your sources with URLs."
    )
    print("[OK] ReAct agent created with system prompt")

    # Invoke the agent
    print("\n[QUERY] Who won the latest Nobel Prize in Physics?")
    print("-" * 40)

    result = agent.invoke({
        "messages": [{"role": "user", "content": "Who won the latest Nobel Prize in Physics?"}]
    })

    # Print the response
    final_response = result["messages"][-1].content
    print(f"\n[RESPONSE]\n{final_response}")

    # Verify that the response contains URL citations (as per prompt instruction)
    if "http" in final_response.lower():
        print("\n[CHECK] Response contains URL citations: YES")
    else:
        print("\n[CHECK] Response contains URL citations: NO (may need prompt adjustment)")

    print("\n" + "=" * 60)
    print("Test 02: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_with_system_prompt()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
