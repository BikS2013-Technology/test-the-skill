"""
Test script for the basic agent example from LangGraph CLI Guide.
"""
import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph CLI Guide')

from my_agent.agent import graph


def test_basic_agent():
    """Test the basic agent graph execution."""
    # Initial state
    initial_state = {"messages": ["Hello, world!"]}

    # Invoke the graph
    result = graph.invoke(initial_state)

    print("Input state:", initial_state)
    print("Output state:", result)

    # Verify the result
    assert "messages" in result, "Result should contain 'messages' key"
    assert len(result["messages"]) == 2, "Should have 2 messages"
    assert result["messages"][0] == "Hello, world!", "First message should be preserved"
    assert result["messages"][1] == "Hello from agent!", "Second message should be from agent"

    print("Test passed!")
    return True


if __name__ == "__main__":
    test_basic_agent()
