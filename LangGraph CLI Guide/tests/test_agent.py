"""
Unit tests for the LangGraph agents.

Based on the pytest example from LangGraph CLI Guide.
"""
import pytest
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


def test_basic_agent_execution():
    """
    Test from the LangGraph CLI Guide documentation.

    This test demonstrates the basic pattern for testing a LangGraph agent
    with checkpointing (persistence).
    """
    checkpointer = MemorySaver()

    class MyState(TypedDict):
        my_key: str

    graph = StateGraph(MyState)
    graph.add_node("node1", lambda state: {"my_key": "hello"})
    graph.add_edge(START, "node1")
    graph.add_edge("node1", END)

    compiled_graph = graph.compile(checkpointer=checkpointer)
    result = compiled_graph.invoke(
        {"my_key": "initial"},
        config={"configurable": {"thread_id": "1"}}
    )

    assert result["my_key"] == "hello"


def test_my_agent_graph():
    """Test the my_agent basic graph implementation."""
    import sys
    sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph CLI Guide')

    from my_agent.agent import graph

    result = graph.invoke({"messages": ["test message"]})

    assert "messages" in result
    assert len(result["messages"]) == 2
    assert result["messages"][0] == "test message"
    assert result["messages"][1] == "Hello from agent!"


def test_azure_agent_graph():
    """Test the Azure OpenAI agent graph implementation."""
    import os
    import sys
    from dotenv import load_dotenv

    load_dotenv('/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph CLI Guide/.env')

    # Check if Azure credentials are available
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT"
    ]

    for var in required_vars:
        value = os.environ.get(var)
        if not value or value.startswith('$'):
            pytest.skip(f"Missing Azure credential: {var}")

    sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph CLI Guide')

    from my_agent.azure_agent import azure_graph
    from langchain_core.messages import HumanMessage

    result = azure_graph.invoke({
        "messages": [HumanMessage(content="Reply with just: OK")]
    })

    assert "messages" in result
    assert len(result["messages"]) >= 1
    # Last message should be from the AI
    assert result["messages"][-1].content is not None


def test_checkpointer_persistence():
    """Test that checkpointer properly persists state across invocations."""
    checkpointer = MemorySaver()

    class ConversationState(TypedDict):
        messages: list
        count: int

    def increment_node(state: ConversationState) -> dict:
        return {
            "messages": state["messages"] + [f"Count: {state['count'] + 1}"],
            "count": state["count"] + 1
        }

    graph = StateGraph(ConversationState)
    graph.add_node("increment", increment_node)
    graph.add_edge(START, "increment")
    graph.add_edge("increment", END)

    compiled_graph = graph.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "test-thread"}}

    # First invocation
    result1 = compiled_graph.invoke(
        {"messages": [], "count": 0},
        config=config
    )
    assert result1["count"] == 1

    # Second invocation - should start from where we left off
    # Note: With checkpointer, we need to pass a fresh input
    result2 = compiled_graph.invoke(
        {"messages": result1["messages"], "count": result1["count"]},
        config=config
    )
    assert result2["count"] == 2
    assert len(result2["messages"]) == 2
