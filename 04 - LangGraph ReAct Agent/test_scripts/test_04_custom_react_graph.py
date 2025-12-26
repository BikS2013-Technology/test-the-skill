"""
Test 04: Custom ReAct Graph (Manual Build)

This test implements a custom ReAct agent graph manually,
adapted to use Azure OpenAI instead of Anthropic.

Original example from guide (lines 220-320):
- Step 1: Define the State (lines 220-228)
- Step 2: Set Up Tools and Model (lines 232-249)
- Step 3: Define Node Functions (lines 254-277)
- Step 4: Build the Graph (lines 281-308)
- Step 5: Use the Graph (lines 313-320)
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

from typing import Annotated, Literal, TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langchain_tavily import TavilySearch

from config import get_azure_model, validate_environment


# Step 1: Define the State
class AgentState(TypedDict):
    """State schema for the ReAct agent."""
    # Messages with automatic merging
    messages: Annotated[list, add_messages]


def test_custom_react_graph():
    """Test custom ReAct agent graph."""
    print("=" * 60)
    print("Test 04: Custom ReAct Graph (Manual Build)")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # Step 2: Set Up Tools and Model
    # Create web search tool
    search_tool = TavilySearch(
        max_results=5,
        topic="general"
    )
    print("[OK] TavilySearch tool created")

    tools = [search_tool]

    # Create tool node for graph
    tool_node = ToolNode(tools)
    print("[OK] ToolNode created")

    # Initialize model with tools bound (Azure OpenAI instead of Anthropic)
    model = get_azure_model().bind_tools(tools)
    print("[OK] Azure OpenAI model initialized and tools bound")

    # Step 3: Define Node Functions
    def call_model(state: AgentState):
        """Agent node that calls the LLM."""
        system_prompt = SystemMessage(
            content="You are a helpful research assistant. Use the search tool to find current information and provide accurate answers with sources."
        )
        messages = [system_prompt] + state["messages"]
        response = model.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        """Determine whether to continue to tools or end."""
        messages = state["messages"]
        last_message = messages[-1]

        # If the LLM made tool calls, route to tools node
        if last_message.tool_calls:
            return "tools"

        # Otherwise, end the conversation
        return "__end__"

    print("[OK] Node functions defined")

    # Step 4: Build the Graph
    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    # Set entry point
    workflow.add_edge(START, "agent")

    # Add conditional edges from agent
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "__end__": END
        }
    )

    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")

    # Compile the graph
    graph = workflow.compile()
    print("[OK] Graph built and compiled")

    # Step 5: Use the Graph
    print("\n[QUERY] What is the current stock price of Apple?")
    print("-" * 40)

    result = graph.invoke({
        "messages": [{"role": "user", "content": "What is the current stock price of Apple?"}]
    })

    # Print the response
    final_response = result["messages"][-1].content
    print(f"\n[RESPONSE]\n{final_response}")

    print("\n" + "=" * 60)
    print("Test 04: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_custom_react_graph()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
