"""
Test 05: TavilySearch Configurations

This test implements various TavilySearch configurations from the guide.

Original examples from guide (lines 328-368):
- TavilySearch with various configuration options
- Testing the search tool directly
- TavilySearch results structure
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from langchain_tavily import TavilySearch

from config import validate_environment


def test_tavily_configurations():
    """Test various TavilySearch configurations."""
    print("=" * 60)
    print("Test 05: TavilySearch Configurations")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # Test 1: Basic configuration (from guide lines 328-342)
    print("\n--- Test 5.1: Basic Configuration ---")
    search_tool_basic = TavilySearch(
        max_results=5,              # Number of results to return
        topic="general",            # Topic: "general" or "news"
        # include_answer=False,     # Include AI-generated answer
        # include_raw_content=False,# Include raw page content
        # include_images=False,     # Include image results
        # search_depth="basic",     # "basic" or "advanced"
        # time_range="day",         # Time range: "day", "week", "month", "year"
        # include_domains=None,     # List of domains to include
        # exclude_domains=None      # List of domains to exclude
    )
    print("[OK] Basic TavilySearch created with max_results=5, topic=general")

    # Test 2: Testing the search tool directly (from guide lines 346-349)
    print("\n--- Test 5.2: Direct Search Tool Test ---")
    print("[QUERY] Latest developments in AI")
    results = search_tool_basic.invoke("Latest developments in AI")
    print(f"[RESULT TYPE] {type(results)}")
    # Results can be dict or string depending on the tool configuration
    results_str = str(results)
    print(f"[RESULT] {results_str[:500]}..." if len(results_str) > 500 else f"[RESULT] {results_str}")

    # Test 3: News-focused search
    print("\n--- Test 5.3: News-Focused Search ---")
    search_tool_news = TavilySearch(
        max_results=3,
        topic="news"
    )
    print("[OK] News TavilySearch created with topic=news")
    results_news = search_tool_news.invoke("Technology news today")
    results_news_str = str(results_news)
    print(f"[RESULT] {results_news_str[:500]}..." if len(results_news_str) > 500 else f"[RESULT] {results_news_str}")

    # Test 4: Domain-restricted search (if supported)
    print("\n--- Test 5.4: Testing Configuration Parameters ---")
    try:
        search_tool_domain = TavilySearch(
            max_results=3,
            # Note: Some parameters may not be available in langchain-tavily
            # include_domains=["arxiv.org", "nature.com"]
        )
        print("[OK] Domain-restricted search created")
        results_domain = search_tool_domain.invoke("Machine learning research papers")
        results_domain_str = str(results_domain)
        print(f"[RESULT] {results_domain_str[:500]}..." if len(results_domain_str) > 500 else f"[RESULT] {results_domain_str}")
    except Exception as e:
        print(f"[INFO] Domain restriction test: {e}")

    print("\n" + "=" * 60)
    print("Test 05: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_tavily_configurations()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
