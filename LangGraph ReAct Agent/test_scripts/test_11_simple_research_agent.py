"""
Test 11: Complete Example 1 - Simple Research Agent

This test implements the Simple Research Agent example from the guide.

Original example from guide (lines 696-727):
- Complete working example
- Includes environment setup, agent creation, and ask() function
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch

from config import get_azure_model, validate_environment


def test_simple_research_agent():
    """Test Simple Research Agent (Complete Example 1)."""
    print("=" * 60)
    print("Test 11: Complete Example 1 - Simple Research Agent")
    print("=" * 60)

    # Validate environment (replaces os.environ setup in the guide)
    validate_environment()
    print("[OK] Environment validated")

    # Initialize components
    model = get_azure_model()
    print("[OK] Azure OpenAI model initialized")

    search_tool = TavilySearch(max_results=3)
    print("[OK] TavilySearch tool created")

    # Create agent (from guide)
    agent = create_react_agent(
        model=model,
        tools=[search_tool],
        prompt="You are a research assistant. Search for accurate information and cite sources."
    )
    print("[OK] Research agent created")

    # Define ask() function from guide
    def ask(question: str) -> str:
        result = agent.invoke({
            "messages": [{"role": "user", "content": question}]
        })
        return result["messages"][-1].content

    # Test queries from the guide
    print("\n--- Test 11.1: Population Query ---")
    print("[QUERY] What is the population of Japan in 2024?")
    response1 = ask("What is the population of Japan in 2024?")
    print(f"[RESPONSE] {response1[:400]}...")

    print("\n--- Test 11.2: CEO Query ---")
    print("[QUERY] Who is the current CEO of Tesla?")
    response2 = ask("Who is the current CEO of Tesla?")
    print(f"[RESPONSE] {response2[:400]}...")

    print("\n" + "=" * 60)
    print("Test 11: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_simple_research_agent()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
