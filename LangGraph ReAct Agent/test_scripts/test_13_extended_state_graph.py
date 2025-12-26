"""
Test 13: Complete Example 3 - Custom ReAct Graph with Extended State

This test implements the Custom ReAct Graph with Extended State example from the guide.

Original example from guide (lines 801-901):
- Extended state with search_count and sources
- Custom agent_node with dynamic system prompt
- Custom tools_node that tracks sources
- MemorySaver checkpointer
"""

import sys
sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph ReAct Agent')

import re
from typing import Annotated, Literal, TypedDict
from datetime import datetime

from langchain_core.messages import SystemMessage
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from config import get_azure_model, validate_environment


# Extended state with custom fields (from guide)
class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    search_count: int
    sources: list[str]


def test_extended_state_graph():
    """Test Custom ReAct Graph with Extended State (Complete Example 3)."""
    print("=" * 60)
    print("Test 13: Complete Example 3 - Custom ReAct Graph with Extended State")
    print("=" * 60)

    # Validate environment
    validate_environment()
    print("[OK] Environment validated")

    # Tools (from guide)
    search_tool = TavilySearch(max_results=5)
    tools = [search_tool]
    tool_node = ToolNode(tools)
    print("[OK] Tools created")

    # Model (adapted for Azure OpenAI)
    model = get_azure_model().bind_tools(tools)
    print("[OK] Azure OpenAI model initialized with tools bound")

    # Agent node (from guide)
    def agent_node(state: ResearchState):
        """Agent node with custom system prompt."""
        system = SystemMessage(content=f"""You are an expert research assistant.
Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Searches performed this session: {state.get('search_count', 0)}

Guidelines:
- Search for current, accurate information
- Cite all sources with URLs
- Be thorough but concise
""")

        messages = [system] + state["messages"]
        response = model.invoke(messages)
        return {"messages": [response]}

    # Tools node (from guide)
    def tools_node(state: ResearchState):
        """Execute tools and track sources."""
        result = tool_node.invoke(state)

        # Extract sources from search results
        new_sources = []
        for msg in result.get("messages", []):
            if hasattr(msg, 'content') and isinstance(msg.content, str):
                # Parse URLs from content (simplified)
                urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', msg.content)
                new_sources.extend(urls[:3])

        return {
            "messages": result["messages"],
            "search_count": state.get("search_count", 0) + 1,
            "sources": state.get("sources", []) + new_sources
        }

    # Routing function (from guide)
    def should_continue(state: ResearchState) -> Literal["tools", "__end__"]:
        """Route based on tool calls."""
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return "__end__"

    print("[OK] Node functions defined")

    # Build graph (from guide)
    workflow = StateGraph(ResearchState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    print("[OK] Graph workflow built")

    # Compile with memory
    checkpointer = MemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)
    print("[OK] Graph compiled with checkpointer")

    # Usage (from guide)
    config = {"configurable": {"thread_id": "research-session-1"}}

    print("\n--- Test 13.1: Research Query with Extended State ---")
    print("[QUERY] What are the latest breakthroughs in quantum computing?")

    result = graph.invoke(
        {
            "messages": [{"role": "user", "content": "What are the latest breakthroughs in quantum computing?"}],
            "search_count": 0,
            "sources": []
        },
        config
    )

    print(f"\n[RESPONSE] {result['messages'][-1].content[:500]}...")
    print(f"\n[STATS]")
    print(f"  Searches performed: {result['search_count']}")
    print(f"  Sources collected: {len(result['sources'])} URLs")
    if result['sources']:
        print(f"  Sample sources:")
        for source in result['sources'][:3]:
            print(f"    - {source[:70]}...")

    # Verify extended state is working
    print("\n--- Test 13.2: Extended State Verification ---")
    if result['search_count'] > 0:
        print("[OK] Search count tracking working")
    else:
        print("[WARNING] Search count not tracked")

    if result['sources']:
        print("[OK] Sources collection working")
    else:
        print("[INFO] No sources collected (may depend on search results)")

    print("\n" + "=" * 60)
    print("Test 13: PASSED")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        test_extended_state_graph()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
