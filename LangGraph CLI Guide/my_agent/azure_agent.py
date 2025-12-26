# my_agent/azure_agent.py
"""
Agent using Azure OpenAI with LangGraph.

This example demonstrates using Azure OpenAI with LangGraph
instead of the regular OpenAI API.
"""
import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import AzureChatOpenAI


class AgentState(TypedDict):
    """State definition for the agent graph with message handling."""
    messages: Annotated[list, add_messages]


def get_azure_llm() -> AzureChatOpenAI:
    """
    Create and return an Azure OpenAI chat model.

    Raises:
        ValueError: If required environment variables are not set.
    """
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set")
    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set")
    if not api_version:
        raise ValueError("AZURE_OPENAI_API_VERSION environment variable is not set")
    if not deployment:
        raise ValueError("AZURE_OPENAI_DEPLOYMENT environment variable is not set")

    return AzureChatOpenAI(
        azure_endpoint=endpoint,
        azure_deployment=deployment,
        api_version=api_version,
        api_key=api_key,
    )


def chatbot_node(state: AgentState) -> dict:
    """
    Chatbot node that uses Azure OpenAI to generate responses.
    """
    llm = get_azure_llm()
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


# Create the graph
builder = StateGraph(AgentState)
builder.add_node("chatbot", chatbot_node)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# Compile the graph - this is what langgraph.json references
azure_graph = builder.compile()
