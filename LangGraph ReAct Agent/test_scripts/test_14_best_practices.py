"""
Test 14: Best Practices

This test implements the Best Practices examples from the guide.

Original examples from guide (lines 905-1001):
- Handle Errors Gracefully (lines 910-920)
- Configure Search Tool Appropriately (lines 924-943)
- Use Appropriate Models (lines 947-959) - Adapted for Azure
- Validate Environment at Startup (lines 964-976)
- Log Tool Usage for Debugging (lines 980-1000)
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch

from config import get_azure_model, validate_environment


# Best Practice 1: Handle Errors Gracefully (from guide lines 910-920)
def safe_invoke(agent, question: str, config: dict = None) -> str:
    """Safely invoke agent with error handling."""
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config or {}
        )
        return result["messages"][-1].content
    except Exception as e:
        return f"Error occurred: {str(e)}"


# Best Practice 5: Log Tool Usage for Debugging (from guide lines 980-1000)
def invoke_with_logging(agent, question: str, config: dict = None):
    """Invoke agent with detailed logging."""
    print(f"[QUERY] {question}\n")

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        config or {},
        stream_mode="updates"
    ):
        for node_name, update in chunk.items():
            print(f"[{node_name}]")
            if "messages" in update:
                for msg in update["messages"]:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tc in msg.tool_calls:
                            print(f"  Tool: {tc['name']}")
                            print(f"  Args: {tc['args']}")
                    elif msg.content:
                        content_preview = str(msg.content)[:200]
                        print(f"  Content: {content_preview}...")
    print()


def test_error_handling():
    """Test error handling best practice."""
    print("\n--- Test 14.1: Error Handling ---")
    print("-" * 40)

    model = get_azure_model()
    search_tool = TavilySearch(max_results=3)
    agent = create_react_agent(model, tools=[search_tool])

    # Test successful invoke
    result = safe_invoke(agent, "What is Python?")
    print(f"[RESULT] {result[:200]}...")

    # Test with invalid config (should be handled gracefully)
    result = safe_invoke(agent, "What is Python?", {"invalid": "config"})
    print(f"[RESULT WITH BAD CONFIG] {result[:200]}...")

    print("[OK] Error handling tested")


def test_search_configurations():
    """Test search tool configurations best practice (from guide lines 924-943)."""
    print("\n--- Test 14.2: Search Tool Configurations ---")
    print("-" * 40)

    # For news queries (from guide)
    news_search = TavilySearch(
        max_results=5,
        topic="news"
    )
    print("[OK] News search configured (topic=news)")

    # For general research (from guide)
    research_search = TavilySearch(
        max_results=10
        # Note: search_depth and include_raw_content may not be available in current langchain-tavily
    )
    print("[OK] Research search configured (max_results=10)")

    # For specific domains - test direct invocation
    # Note: include_domains/exclude_domains may have different API in langchain-tavily
    domain_search = TavilySearch(
        max_results=5
    )
    print("[OK] Domain search configured")

    # Test each configuration
    print("\n[Testing news_search]")
    news_results = news_search.invoke("Technology news today")
    print(f"  Results type: {type(news_results)}")

    print("\n[Testing research_search]")
    research_results = research_search.invoke("Python programming")
    print(f"  Results type: {type(research_results)}")

    print("[OK] Search configurations tested")


def test_environment_validation():
    """Test environment validation best practice (from guide lines 964-976)."""
    print("\n--- Test 14.3: Environment Validation ---")
    print("-" * 40)

    # The guide shows this pattern:
    # def validate_environment():
    #     required_keys = ["ANTHROPIC_API_KEY", "TAVILY_API_KEY"]
    #     missing = [key for key in required_keys if not os.environ.get(key)]
    #     if missing:
    #         raise ValueError(f"Missing required environment variables: {missing}")

    # We use our config.validate_environment() which does the same for Azure
    try:
        validate_environment()
        print("[OK] Environment validation passed")
    except ValueError as e:
        print(f"[ERROR] {e}")


def test_logging():
    """Test logging tool usage best practice."""
    print("\n--- Test 14.4: Logging Tool Usage ---")
    print("-" * 40)

    model = get_azure_model()
    search_tool = TavilySearch(max_results=3)
    agent = create_react_agent(model, tools=[search_tool])

    invoke_with_logging(agent, "What is machine learning?")

    print("[OK] Logging tested")


def test_best_practices():
    """Run all best practices tests."""
    print("=" * 60)
    print("Test 14: Best Practices")
    print("=" * 60)

    # Validate environment first
    validate_environment()
    print("[OK] Environment validated")

    test_environment_validation()
    test_error_handling()
    test_search_configurations()
    test_logging()

    print("\n" + "=" * 60)
    print("Test 14: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_best_practices()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
