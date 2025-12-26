"""
Test 06: Custom Tools

This test implements the custom tools example from the guide,
combining web search with custom tools.

Original example from guide (lines 375-408):
- Uses @tool decorator to create custom tools
- Combines TavilySearch with custom tools
- Creates an agent with multiple tools
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain.agents import create_react_agent

from config import get_azure_model, validate_environment


# Custom tools from the guide
@tool
def get_current_date() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression like '2 + 2' or '10 * 5'
    """
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


def test_custom_tools():
    """Test ReAct agent with custom tools."""
    print("=" * 60)
    print("Test 06: Custom Tools")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # Initialize the LLM
    model = get_azure_model()
    print("[OK] Azure OpenAI model initialized")

    # Create web search tool
    search_tool = TavilySearch(max_results=3)
    print("[OK] TavilySearch tool created")

    # Combine all tools
    tools = [search_tool, get_current_date, calculate]
    print(f"[OK] Combined tools: {[t.name for t in tools]}")

    # Create agent with multiple tools
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt="You are a helpful assistant with web search, date/time, and calculation capabilities."
    )
    print("[OK] ReAct agent created with multiple tools")

    # Test 1: Date/Time tool
    print("\n--- Test 6.1: Date/Time Tool ---")
    print("[QUERY] What is the current date and time?")
    result = agent.invoke({
        "messages": [{"role": "user", "content": "What is the current date and time?"}]
    })
    print(f"[RESPONSE] {result['messages'][-1].content}")

    # Test 2: Calculate tool
    print("\n--- Test 6.2: Calculate Tool ---")
    print("[QUERY] What is 25 * 37 + 123?")
    result = agent.invoke({
        "messages": [{"role": "user", "content": "What is 25 * 37 + 123?"}]
    })
    print(f"[RESPONSE] {result['messages'][-1].content}")

    # Test 3: Combined tools (search + date)
    print("\n--- Test 6.3: Combined Query ---")
    print("[QUERY] What are the top tech news today? Also tell me the current date.")
    result = agent.invoke({
        "messages": [{"role": "user", "content": "What are the top tech news today? Also tell me the current date."}]
    })
    print(f"[RESPONSE] {result['messages'][-1].content[:800]}...")

    print("\n" + "=" * 60)
    print("Test 06: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_custom_tools()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
