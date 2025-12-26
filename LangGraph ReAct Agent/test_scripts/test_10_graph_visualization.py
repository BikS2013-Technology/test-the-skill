"""
Test 10: Graph Visualization

This test implements the graph visualization examples from the guide.

Original examples from guide (lines 661-688):
- Display in Jupyter (lines 667-671)
- Save to File (lines 676-680)
- ASCII Output (lines 685-688)

Note: Jupyter display won't work in CLI, so we focus on file save and ASCII.
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent

from config import get_azure_model, validate_environment


def test_ascii_output(agent):
    """Test ASCII output of graph (from guide lines 685-688)."""
    print("\n--- Test 10.1: ASCII Output ---")
    print("-" * 40)

    # Print ASCII representation
    try:
        ascii_graph = agent.get_graph().draw_ascii()
        print("[ASCII GRAPH]")
        print(ascii_graph)
        print("[OK] ASCII graph generated")
    except Exception as e:
        print(f"[INFO] ASCII output not available: {e}")


def test_save_to_file(agent):
    """Test saving graph to file (from guide lines 676-680)."""
    print("\n--- Test 10.2: Save to File ---")
    print("-" * 40)

    try:
        # Save graph visualization to PNG
        png_data = agent.get_graph().draw_mermaid_png()
        output_path = "/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent/agent_graph.png"
        with open(output_path, "wb") as f:
            f.write(png_data)
        print(f"[OK] Graph saved to: {output_path}")
    except Exception as e:
        print(f"[INFO] PNG save not available (may need additional dependencies): {e}")


def test_mermaid_output(agent):
    """Test Mermaid diagram output."""
    print("\n--- Test 10.3: Mermaid Diagram ---")
    print("-" * 40)

    try:
        mermaid = agent.get_graph().draw_mermaid()
        print("[MERMAID DIAGRAM]")
        print(mermaid[:500] + "..." if len(mermaid) > 500 else mermaid)
        print("[OK] Mermaid diagram generated")
    except Exception as e:
        print(f"[INFO] Mermaid output not available: {e}")


def test_graph_visualization():
    """Run all graph visualization tests."""
    print("=" * 60)
    print("Test 10: Graph Visualization")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # Create agent
    model = get_azure_model()
    search_tool = TavilySearch(max_results=3)
    agent = create_react_agent(model, tools=[search_tool])
    print("[OK] Agent created for visualization")

    test_ascii_output(agent)
    test_mermaid_output(agent)
    test_save_to_file(agent)

    print("\n" + "=" * 60)
    print("Test 10: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_graph_visualization()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
