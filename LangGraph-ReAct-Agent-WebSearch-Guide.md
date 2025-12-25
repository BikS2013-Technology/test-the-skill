# LangGraph ReAct Agent with Web Search Guide

**Date:** December 23, 2025

This guide explains how to build a ReAct (Reasoning + Acting) agent using the **LangGraph framework** that can search the web to answer user questions. LangGraph provides explicit graph-based control, state management, persistence, and production-ready features.

---

## Table of Contents

1. [What is a LangGraph ReAct Agent?](#what-is-a-langgraph-react-agent)
2. [Installation](#installation)
3. [Setting Up the Environment](#setting-up-the-environment)
4. [Approach 1: Using the Prebuilt `create_react_agent`](#approach-1-using-the-prebuilt-create_react_agent)
5. [Approach 2: Building a Custom ReAct Graph](#approach-2-building-a-custom-react-graph)
6. [Web Search Tools](#web-search-tools)
7. [Streaming Responses](#streaming-responses)
8. [Adding Memory with Checkpointers](#adding-memory-with-checkpointers)
9. [Custom System Prompts](#custom-system-prompts)
10. [Graph Visualization](#graph-visualization)
11. [Complete Examples](#complete-examples)
12. [Best Practices](#best-practices)

---

## What is a LangGraph ReAct Agent?

A **LangGraph ReAct Agent** implements the ReAct (Reasoning + Acting) pattern using an explicit graph structure:

```
                    ┌─────────────────────────────────────┐
                    │           StateGraph                │
                    │                                     │
┌─────────┐         │  ┌─────────┐      ┌─────────────┐  │
│  User   │────────►│  │  Agent  │◄────►│    Tools    │  │
│  Input  │         │  │  (LLM)  │      │ (Web Search)│  │
└─────────┘         │  └────┬────┘      └─────────────┘  │
                    │       │                             │
                    │       ▼                             │
                    │  ┌─────────┐                        │
                    │  │  END    │                        │
                    │  └─────────┘                        │
                    │                                     │
                    │  State: { messages, ... }           │
                    │  Checkpointer: Memory/PostgreSQL    │
                    └─────────────────────────────────────┘
```

**Key LangGraph Advantages:**
- **Explicit Control Flow**: Visible nodes, edges, and routing logic
- **Custom State**: Define any fields beyond just messages
- **Persistence**: Built-in checkpointers for conversation memory
- **Human-in-the-Loop**: Native support for interrupts and approvals
- **Graph Visualization**: Visual debugging of agent structure
- **Production Ready**: Deploy via LangGraph Platform

---

## Installation

### Prerequisites

- Python 3.11+
- UV package manager (recommended)

### Install Required Packages

```bash
# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Core LangGraph packages
uv add langgraph

# Web search tool (Tavily)
uv add langchain-tavily

# LLM provider (choose one or more)
uv add langchain-anthropic   # Anthropic Claude
uv add langchain-openai      # OpenAI
uv add langchain-google-genai # Google Gemini

# Additional utilities
uv add langchain-core
```

---

## Setting Up the Environment

### API Keys

You need API keys for:
1. Your LLM provider (Anthropic, OpenAI, etc.)
2. Tavily Search API (get a free key at https://tavily.com)

```python
import os

# LLM Provider (choose one)
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
os.environ["OPENAI_API_KEY"] = "sk-..."

# Tavily Search API
os.environ["TAVILY_API_KEY"] = "tvly-..."
```

Or use a `.env` file:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
```

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Approach 1: Using the Prebuilt `create_react_agent`

LangGraph provides a prebuilt `create_react_agent` function for quick agent creation with all LangGraph benefits.

### Basic Usage

```python
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch

# Initialize the LLM
model = ChatAnthropic(model="claude-sonnet-4-20250514")

# Create the web search tool
search_tool = TavilySearch(max_results=3)

# Create the ReAct agent
agent = create_react_agent(
    model=model,
    tools=[search_tool]
)

# Invoke the agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "What are the latest AI news?"}]
})

# Print the response
print(result["messages"][-1].content)
```

### With System Prompt

```python
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch

model = ChatAnthropic(model="claude-sonnet-4-20250514")
search_tool = TavilySearch(max_results=5)

# Create agent with a system prompt
agent = create_react_agent(
    model=model,
    tools=[search_tool],
    prompt="You are a helpful research assistant. Always search the web for current information and cite your sources with URLs."
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Who won the latest Nobel Prize in Physics?"}]
})

print(result["messages"][-1].content)
```

### With Memory (Checkpointer)

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch

model = ChatAnthropic(model="claude-sonnet-4-20250514")
search_tool = TavilySearch(max_results=3)

# Create a checkpointer for conversation memory
checkpointer = MemorySaver()

# Create agent with memory
agent = create_react_agent(
    model=model,
    tools=[search_tool],
    prompt="You are a helpful assistant with web search capabilities.",
    checkpointer=checkpointer
)

# Use thread_id to maintain conversation state
config = {"configurable": {"thread_id": "user-123"}}

# First message
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Search for information about quantum computing"}]},
    config=config
)
print(result["messages"][-1].content)

# Follow-up message - agent remembers context!
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What are its practical applications?"}]},
    config=config
)
print(result["messages"][-1].content)
```

---

## Approach 2: Building a Custom ReAct Graph

For maximum control, you can build the ReAct agent graph manually.

### Step 1: Define the State

```python
from typing import Annotated, Literal, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """State schema for the ReAct agent."""
    # Messages with automatic merging
    messages: Annotated[list, add_messages]
```

### Step 2: Set Up Tools and Model

```python
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode

# Create web search tool
search_tool = TavilySearch(
    max_results=5,
    topic="general"
)

tools = [search_tool]

# Create tool node for graph
tool_node = ToolNode(tools)

# Initialize model with tools bound
model = ChatAnthropic(model="claude-sonnet-4-20250514").bind_tools(tools)
```

### Step 3: Define Node Functions

```python
from langchain_core.messages import SystemMessage

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
```

### Step 4: Build the Graph

```python
from langgraph.graph import StateGraph, START, END

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
```

### Step 5: Use the Graph

```python
# Invoke the graph
result = graph.invoke({
    "messages": [{"role": "user", "content": "What is the current stock price of Apple?"}]
})

print(result["messages"][-1].content)
```

---

## Web Search Tools

### TavilySearch Configuration

```python
from langchain_tavily import TavilySearch

search_tool = TavilySearch(
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
```

### Testing the Search Tool Directly

```python
# Test the tool independently
results = search_tool.invoke("Latest developments in AI")
print(results)
```

### TavilySearch Results Structure

```python
{
    'query': 'Latest developments in AI',
    'results': [
        {
            'title': 'Article Title',
            'url': 'https://example.com/article',
            'content': 'Article content snippet...',
            'score': 0.95
        },
        # ... more results
    ],
    'response_time': 1.2
}
```

### Adding Custom Tools

You can combine web search with custom tools:

```python
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

search_tool = TavilySearch(max_results=3)

@tool
def get_current_date() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression like '2 + 2' or '10 * 5'
    """
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

# Combine all tools
tools = [search_tool, get_current_date, calculate]

# Create agent with multiple tools
agent = create_react_agent(
    model=model,
    tools=tools,
    prompt="You are a helpful assistant with web search, date/time, and calculation capabilities."
)
```

---

## Streaming Responses

LangGraph provides multiple streaming modes for real-time output.

### Stream State Values

```python
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch

model = ChatAnthropic(model="claude-sonnet-4-20250514")
search_tool = TavilySearch(max_results=3)
agent = create_react_agent(model, tools=[search_tool])

# Stream complete state at each step
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is quantum computing?"}]},
    stream_mode="values"
):
    # Get the latest message
    message = chunk["messages"][-1]
    message.pretty_print()
```

### Stream State Updates

```python
# Stream only the changes at each step
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Search for AI news"}]},
    stream_mode="updates"
):
    for node_name, update in chunk.items():
        print(f"\n--- Update from: {node_name} ---")
        if "messages" in update:
            for msg in update["messages"]:
                msg.pretty_print()
```

### Stream with Progress Indicator

```python
def stream_with_progress(agent, question: str):
    """Stream agent response with progress updates."""
    print(f"Question: {question}\n")

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values"
    ):
        message = chunk["messages"][-1]

        # Check if it's a tool call
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tc in message.tool_calls:
                print(f"[Searching: {tc['args'].get('query', 'N/A')}]")

        # Check if it's a tool response
        elif message.type == "tool":
            print(f"[Received search results]")

        # Final response
        elif message.type == "ai" and message.content:
            print(f"\nAnswer:\n{message.content}")

# Usage
stream_with_progress(agent, "What are the latest breakthroughs in fusion energy?")
```

### Async Streaming

```python
import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch

async def async_stream_agent():
    model = ChatAnthropic(model="claude-sonnet-4-20250514")
    search_tool = TavilySearch(max_results=3)
    agent = create_react_agent(model, tools=[search_tool])

    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": "Latest tech news"}]},
        stream_mode="values"
    ):
        message = chunk["messages"][-1]
        if message.content:
            print(message.content)

# Run async
asyncio.run(async_stream_agent())
```

---

## Adding Memory with Checkpointers

LangGraph supports multiple persistence backends for conversation memory.

### In-Memory (Development)

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

checkpointer = MemorySaver()

agent = create_react_agent(
    model=model,
    tools=[search_tool],
    checkpointer=checkpointer
)

# Thread ID maintains conversation state
config = {"configurable": {"thread_id": "conversation-1"}}

# Multi-turn conversation
agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Alice"}]}, config)
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config)
# Agent remembers: "Your name is Alice"
```

### PostgreSQL (Production)

```python
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent

DB_URI = "postgresql://user:password@localhost:5432/langgraph"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    # Run setup once to create tables
    # checkpointer.setup()

    agent = create_react_agent(
        model=model,
        tools=[search_tool],
        checkpointer=checkpointer
    )

    config = {"configurable": {"thread_id": "user-123"}}

    # Conversation persists across application restarts
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "Search for Python tutorials"}]},
        config,
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()
```

### Retrieving State History

```python
# Get current state
state = agent.get_state(config)
print(f"Current messages: {len(state.values['messages'])}")
print(f"Next node: {state.next}")

# Get state history
for checkpoint in agent.get_state_history(config):
    print(f"Checkpoint: {checkpoint.config['configurable']['checkpoint_id']}")
    print(f"Created at: {checkpoint.created_at}")
```

---

## Custom System Prompts

### Static Prompt

```python
agent = create_react_agent(
    model=model,
    tools=[search_tool],
    prompt="You are a research assistant specializing in technology news. Always cite sources."
)
```

### Dynamic Prompt Function

```python
from langchain_core.messages import AnyMessage
from langgraph.prebuilt import create_react_agent

def dynamic_prompt(state) -> list[AnyMessage]:
    """Generate dynamic system prompt based on state."""
    user_context = state.get("user_context", "general user")

    system_content = f"""You are a helpful research assistant.
User context: {user_context}

Guidelines:
1. Always search for current, accurate information
2. Cite sources with URLs
3. Be concise but comprehensive
4. If uncertain, search again with different terms
"""
    return [{"role": "system", "content": system_content}] + state["messages"]

agent = create_react_agent(
    model=model,
    tools=[search_tool],
    prompt=dynamic_prompt
)
```

### Custom State with User Information

```python
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.messages import AnyMessage

class CustomState(AgentState):
    """Extended state with user information."""
    user_name: str
    user_preferences: dict

def personalized_prompt(state: CustomState) -> list[AnyMessage]:
    """Create personalized prompt based on user state."""
    name = state.get("user_name", "User")
    prefs = state.get("user_preferences", {})

    system_msg = f"""You are a personal research assistant for {name}.
User preferences: {prefs}
Search the web to provide accurate, personalized responses."""

    return [{"role": "system", "content": system_msg}] + state["messages"]

agent = create_react_agent(
    model=model,
    tools=[search_tool],
    state_schema=CustomState,
    prompt=personalized_prompt
)

# Invoke with custom state
result = agent.invoke({
    "messages": [{"role": "user", "content": "Find me some good restaurants"}],
    "user_name": "Alice",
    "user_preferences": {"cuisine": "Italian", "location": "NYC"}
})
```

---

## Graph Visualization

LangGraph can visualize your agent's structure:

### Display in Jupyter

```python
from IPython.display import Image, display

# Visualize the agent graph
display(Image(agent.get_graph().draw_mermaid_png()))
```

### Save to File

```python
# Save graph visualization to PNG
png_data = agent.get_graph().draw_mermaid_png()
with open("agent_graph.png", "wb") as f:
    f.write(png_data)
```

### ASCII Output (Terminal)

```python
# Print ASCII representation
print(agent.get_graph().draw_ascii())
```

---

## Complete Examples

### Example 1: Simple Research Agent

```python
import os
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch

# Setup
os.environ["ANTHROPIC_API_KEY"] = "your-key"
os.environ["TAVILY_API_KEY"] = "your-key"

# Initialize components
model = ChatAnthropic(model="claude-sonnet-4-20250514")
search_tool = TavilySearch(max_results=3)

# Create agent
agent = create_react_agent(
    model=model,
    tools=[search_tool],
    prompt="You are a research assistant. Search for accurate information and cite sources."
)

# Ask questions
def ask(question: str) -> str:
    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })
    return result["messages"][-1].content

# Usage
print(ask("What is the population of Japan in 2024?"))
print(ask("Who is the current CEO of Tesla?"))
```

### Example 2: Interactive Chat with Memory

```python
import os
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch

# Setup
os.environ["ANTHROPIC_API_KEY"] = "your-key"
os.environ["TAVILY_API_KEY"] = "your-key"

model = ChatAnthropic(model="claude-sonnet-4-20250514")
search_tool = TavilySearch(max_results=3)
checkpointer = MemorySaver()

agent = create_react_agent(
    model=model,
    tools=[search_tool],
    prompt="You are a helpful research assistant with web search capabilities.",
    checkpointer=checkpointer
)

def chat():
    """Interactive chat loop with memory."""
    print("Research Assistant Ready! (type 'quit' to exit, 'new' for new conversation)")
    print("-" * 60)

    thread_id = "default"
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if user_input.lower() == 'new':
            import uuid
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            print(f"Started new conversation: {thread_id[:8]}...")
            continue

        if not user_input:
            continue

        print("\nAssistant: ", end="", flush=True)

        # Stream the response
        final_response = ""
        for chunk in agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
            stream_mode="values"
        ):
            message = chunk["messages"][-1]
            if hasattr(message, 'tool_calls') and message.tool_calls:
                print("[Searching...]", end=" ", flush=True)
            elif message.content and message.type == "ai":
                final_response = message.content

        print(final_response)

if __name__ == "__main__":
    chat()
```

### Example 3: Custom ReAct Graph with Extended State

```python
import os
from typing import Annotated, Literal, TypedDict
from datetime import datetime

from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Setup
os.environ["ANTHROPIC_API_KEY"] = "your-key"
os.environ["TAVILY_API_KEY"] = "your-key"

# Extended state with custom fields
class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    search_count: int
    sources: list[str]

# Tools
search_tool = TavilySearch(max_results=5)
tools = [search_tool]
tool_node = ToolNode(tools)

# Model
model = ChatAnthropic(model="claude-sonnet-4-20250514").bind_tools(tools)

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

def tools_node(state: ResearchState):
    """Execute tools and track sources."""
    result = tool_node.invoke(state)

    # Extract sources from search results
    new_sources = []
    for msg in result.get("messages", []):
        if hasattr(msg, 'content') and isinstance(msg.content, str):
            # Parse URLs from content (simplified)
            import re
            urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', msg.content)
            new_sources.extend(urls[:3])

    return {
        "messages": result["messages"],
        "search_count": state.get("search_count", 0) + 1,
        "sources": state.get("sources", []) + new_sources
    }

def should_continue(state: ResearchState) -> Literal["tools", "__end__"]:
    """Route based on tool calls."""
    last_message = state["messages"][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return "__end__"

# Build graph
workflow = StateGraph(ResearchState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tools_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

# Compile with memory
checkpointer = MemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

# Usage
config = {"configurable": {"thread_id": "research-session-1"}}

result = graph.invoke(
    {
        "messages": [{"role": "user", "content": "What are the latest breakthroughs in quantum computing?"}],
        "search_count": 0,
        "sources": []
    },
    config
)

print("Response:", result["messages"][-1].content)
print(f"\nSearches performed: {result['search_count']}")
print(f"Sources collected: {result['sources']}")
```

---

## Best Practices

### 1. Handle Errors Gracefully

```python
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
```

### 2. Configure Search Tool Appropriately

```python
# For news queries
news_search = TavilySearch(
    max_results=5,
    topic="news",
    time_range="week"
)

# For general research
research_search = TavilySearch(
    max_results=10,
    search_depth="advanced",
    include_raw_content=True
)

# For specific domains
domain_search = TavilySearch(
    max_results=5,
    include_domains=["arxiv.org", "nature.com", "science.org"]
)
```

### 3. Use Appropriate Models

```python
from langchain.chat_models import init_chat_model

# For quick responses - faster, cheaper
fast_model = init_chat_model("anthropic:claude-3-5-haiku-latest")

# For complex research - more capable
capable_model = init_chat_model("anthropic:claude-sonnet-4-20250514")

# Create agents for different use cases
quick_agent = create_react_agent(fast_model, tools=[search_tool])
research_agent = create_react_agent(capable_model, tools=[search_tool])
```

### 4. Validate Environment at Startup

```python
import os

def validate_environment():
    """Ensure required API keys are set."""
    required_keys = ["ANTHROPIC_API_KEY", "TAVILY_API_KEY"]
    missing = [key for key in required_keys if not os.environ.get(key)]

    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")

validate_environment()
```

### 5. Log Tool Usage for Debugging

```python
def invoke_with_logging(agent, question: str, config: dict = None):
    """Invoke agent with detailed logging."""
    print(f"Question: {question}\n")

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
                        print(f"  Content: {msg.content[:200]}...")
    print()
```

---

## Summary

| Component | Purpose |
|-----------|---------|
| `create_react_agent()` | Create prebuilt ReAct agent with LangGraph features |
| `StateGraph` | Build custom graph with explicit control flow |
| `TavilySearch` | Web search tool optimized for LLMs |
| `MemorySaver` | In-memory checkpointer for development |
| `PostgresSaver` | PostgreSQL checkpointer for production |
| `ToolNode` | Prebuilt node for executing tools |
| `agent.stream()` | Stream responses in real-time |
| `agent.get_graph()` | Get graph for visualization |

### Quick Start Template

```python
import os
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch

# Environment
os.environ["ANTHROPIC_API_KEY"] = "your-key"
os.environ["TAVILY_API_KEY"] = "your-key"

# Setup
model = ChatAnthropic(model="claude-sonnet-4-20250514")
search_tool = TavilySearch(max_results=3)
checkpointer = MemorySaver()

# Create agent
agent = create_react_agent(
    model=model,
    tools=[search_tool],
    prompt="You are a helpful research assistant. Search the web for accurate information.",
    checkpointer=checkpointer
)

# Use with memory
config = {"configurable": {"thread_id": "session-1"}}

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Your question here"}]},
    config
)

print(result["messages"][-1].content)
```
