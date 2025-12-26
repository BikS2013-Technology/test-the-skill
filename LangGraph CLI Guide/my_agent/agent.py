# my_agent/agent.py
"""
Example agent using Azure OpenAI with LangGraph.

This example is based on the LangGraph CLI Guide document,
modified to use Azure OpenAI instead of regular OpenAI.
"""
import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class MyState(TypedDict):
    """State definition for the agent graph."""
    messages: list


def agent_node(state: MyState) -> dict:
    """
    Agent node that processes messages.

    This is a simple example that just adds a greeting.
    In a real application, you would use an LLM here.
    """
    return {"messages": state["messages"] + ["Hello from agent!"]}


# Create the graph
builder = StateGraph(MyState)
builder.add_node("agent", agent_node)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)

# Compile the graph - this is what langgraph.json references
graph = builder.compile()
