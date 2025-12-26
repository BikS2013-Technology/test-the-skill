"""
Test 01: Basic Usage with create_react_agent

This test implements the basic ReAct agent example from the guide,
adapted to use Azure OpenAI instead of Anthropic.

Original example from guide (lines 122-146):
- Uses ChatAnthropic
- Uses TavilySearch with max_results=3
- Simple invoke pattern
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch

from config import get_azure_model, validate_environment


def test_basic_usage():
    """Test basic ReAct agent functionality."""
    print("=" * 60)
    print("Test 01: Basic Usage with create_react_agent")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # Initialize the LLM (Azure OpenAI instead of Anthropic)
    model = get_azure_model()
    print("[OK] Azure OpenAI model initialized")

    # Create the web search tool
    search_tool = TavilySearch(max_results=3)
    print("[OK] TavilySearch tool created")

    # Create the ReAct agent
    agent = create_react_agent(
        model=model,
        tools=[search_tool]
    )
    print("[OK] ReAct agent created")

    # Invoke the agent
    print("\n[QUERY] What are the latest AI news?")
    print("-" * 40)

    result = agent.invoke({
        "messages": [{"role": "user", "content": "What are the latest AI news?"}]
    })

    # Print the response
    final_response = result["messages"][-1].content
    print(f"\n[RESPONSE]\n{final_response}")

    print("\n" + "=" * 60)
    print("Test 01: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_basic_usage()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
