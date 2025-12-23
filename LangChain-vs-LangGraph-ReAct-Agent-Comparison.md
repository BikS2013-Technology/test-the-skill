# LangChain vs LangGraph: ReAct Agent Implementation Comparison

**Date:** December 23, 2025

This document provides a detailed comparison between implementing a ReAct agent using pure LangChain (via `create_agent`) versus implementing it using the LangGraph framework. Understanding these differences helps you choose the right approach for your use case.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Comparison](#architecture-comparison)
3. [Code Comparison](#code-comparison)
4. [Feature Comparison](#feature-comparison)
5. [State Management](#state-management)
6. [Persistence and Memory](#persistence-and-memory)
7. [Human-in-the-Loop](#human-in-the-loop)
8. [Streaming and Observability](#streaming-and-observability)
9. [When to Use Which Approach](#when-to-use-which-approach)
10. [Migration Path](#migration-path)

---

## Executive Summary

| Aspect | LangChain `create_agent` | LangGraph |
|--------|--------------------------|-----------|
| **Abstraction Level** | High-level, simple API | Low-level, explicit control |
| **Learning Curve** | Easy | Moderate |
| **Customization** | Limited | Extensive |
| **State Management** | Implicit (message-based) | Explicit (typed state) |
| **Persistence** | Not built-in | Built-in checkpointers |
| **Human-in-the-Loop** | Not supported | Native support |
| **Graph Visualization** | Not available | Built-in |
| **Deployment** | Standard Python | LangGraph Platform |
| **Best For** | Simple agents, prototypes | Production, complex workflows |

### Quick Recommendation

- **Use LangChain `create_agent`** when you need a simple ReAct agent for prototyping, learning, or straightforward Q&A tasks.
- **Use LangGraph** when you need production-grade agents with persistence, human oversight, complex state, or custom control flow.

---

## Architecture Comparison

### LangChain ReAct Agent Architecture

The LangChain `create_agent` function provides a **black-box abstraction** that handles the ReAct loop internally:

```
┌─────────────────────────────────────────┐
│           create_agent()                │
│  ┌─────────────────────────────────┐    │
│  │     Internal ReAct Loop         │    │
│  │  ┌─────────┐    ┌──────────┐    │    │
│  │  │   LLM   │◄──►│  Tools   │    │    │
│  │  └─────────┘    └──────────┘    │    │
│  │         ▲            ▲          │    │
│  │         └────────────┘          │    │
│  │       (Hidden from user)        │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Input: messages ──► Output: messages   │
└─────────────────────────────────────────┘
```

**Key Characteristics:**
- Single function creates the entire agent
- ReAct loop logic is hidden
- Message-based state only
- Limited customization points

### LangGraph ReAct Agent Architecture

LangGraph provides **explicit graph-based control** where you define nodes, edges, and transitions:

```
┌─────────────────────────────────────────────────────────┐
│                    StateGraph                            │
│                                                          │
│   ┌─────────┐         ┌─────────────┐                   │
│   │  START  │────────►│   Agent     │                   │
│   └─────────┘         │   (LLM)     │                   │
│                       └──────┬──────┘                   │
│                              │                          │
│                     ┌────────┴────────┐                 │
│                     │ should_continue │                 │
│                     └────────┬────────┘                 │
│                              │                          │
│              ┌───────────────┼───────────────┐          │
│              ▼               │               ▼          │
│        ┌──────────┐          │         ┌─────────┐      │
│        │  Tools   │──────────┘         │   END   │      │
│        │  Node    │                    └─────────┘      │
│        └──────────┘                                     │
│                                                          │
│   State: { messages, custom_fields, ... }               │
│   Checkpointer: Memory/PostgreSQL/MongoDB               │
└─────────────────────────────────────────────────────────┘
```

**Key Characteristics:**
- Explicit node and edge definitions
- Custom state schema with typed fields
- Conditional routing logic visible and modifiable
- Built-in persistence and interrupts

---

## Code Comparison

### Minimal ReAct Agent

#### LangChain Approach

```python
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_tavily import TavilySearch

# Initialize components
model = init_chat_model("claude-sonnet-4-5-20250929")
search_tool = TavilySearch(max_results=3)

# Create agent (one line!)
agent = create_agent(
    model=model,
    tools=[search_tool],
    system_prompt="You are a helpful research assistant."
)

# Use the agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "What is quantum computing?"}]
})
print(result["messages"][-1].content)
```

**Lines of code:** ~15

#### LangGraph Approach (Manual)

```python
from typing import Annotated, Literal, TypedDict
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langchain.tools import ToolNode

# Define state schema
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Define tools
@tool
def search(query: str) -> str:
    """Search the web for information."""
    # Implementation here
    return "Search results..."

tools = [search]
tool_node = ToolNode(tools)

# Initialize model with tools
model = init_chat_model("claude-sonnet-4-5-20250929").bind_tools(tools)

# Define routing logic
def should_continue(state: State) -> Literal["tools", END]:
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Define agent node
def call_model(state: State):
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

# Build the graph
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

# Compile
app = workflow.compile()

# Use the agent
result = app.invoke({
    "messages": [{"role": "user", "content": "What is quantum computing?"}]
})
print(result["messages"][-1].content)
```

**Lines of code:** ~45

#### LangGraph Approach (Prebuilt)

```python
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model

# Define tools
def search(query: str) -> str:
    """Search the web for information."""
    return "Search results..."

# Create agent using prebuilt function
model = init_chat_model("claude-sonnet-4-5-20250929")
agent = create_react_agent(
    model=model,
    tools=[search],
    prompt="You are a helpful research assistant."
)

# Use the agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "What is quantum computing?"}]
})
print(result["messages"][-1].content)
```

**Lines of code:** ~18

### Key Differences in Code

| Aspect | LangChain | LangGraph (Manual) | LangGraph (Prebuilt) |
|--------|-----------|-------------------|---------------------|
| State definition | Implicit | Explicit TypedDict | Implicit |
| Routing logic | Hidden | Visible function | Hidden |
| Tool binding | Automatic | Manual `.bind_tools()` | Automatic |
| Graph construction | N/A | Manual node/edge setup | Automatic |
| Compilation | N/A | Required | Automatic |

---

## Feature Comparison

### Feature Matrix

| Feature | LangChain `create_agent` | LangGraph Manual | LangGraph Prebuilt |
|---------|-------------------------|------------------|-------------------|
| Basic ReAct loop | Yes | Yes | Yes |
| Custom tools | Yes | Yes | Yes |
| System prompts | Yes | Yes | Yes |
| Streaming | Yes | Yes | Yes |
| Structured output | Yes | Yes | Yes |
| Custom state fields | No | Yes | Limited |
| State persistence | No | Yes | Yes |
| Checkpointing | No | Yes | Yes |
| Human-in-the-loop | No | Yes | Yes |
| Breakpoints/Interrupts | No | Yes | Yes |
| Time travel (replay) | No | Yes | Yes |
| Graph visualization | No | Yes | Yes |
| Custom routing logic | No | Yes | No |
| Pre/Post model hooks | No | Yes | Yes |
| Multi-agent support | Limited | Yes | Yes |
| Subgraphs | No | Yes | No |
| Parallel execution | No | Yes | No |

---

## State Management

### LangChain: Message-Only State

LangChain agents operate on a simple message-based state:

```python
# Input state
{
    "messages": [
        {"role": "user", "content": "What is the weather?"}
    ]
}

# Output state
{
    "messages": [
        {"role": "user", "content": "What is the weather?"},
        {"role": "assistant", "content": "...", "tool_calls": [...]},
        {"role": "tool", "content": "..."},
        {"role": "assistant", "content": "The weather is sunny..."}
    ]
}
```

**Limitations:**
- Cannot add custom fields (e.g., `user_id`, `session_data`)
- Cannot track metadata across invocations
- No typed state validation

### LangGraph: Rich Custom State

LangGraph allows defining custom state schemas:

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Core messages with automatic merging
    messages: Annotated[list, add_messages]

    # Custom fields
    user_id: str
    session_metadata: dict
    tool_call_count: int
    search_results_cache: list
    current_step: str

# Use in graph
workflow = StateGraph(AgentState)
```

**Advantages:**
- Type safety with TypedDict
- Custom reducers for field updates
- Track any metadata needed for your application
- State accessible in all nodes

### State Reducers in LangGraph

LangGraph provides powerful state reduction capabilities:

```python
from typing import Annotated
import operator

class State(TypedDict):
    # Messages are appended (not replaced)
    messages: Annotated[list, add_messages]

    # Counter is incremented
    call_count: Annotated[int, operator.add]

    # List items are concatenated
    results: Annotated[list, operator.add]
```

---

## Persistence and Memory

### LangChain: No Built-in Persistence

LangChain agents are stateless by default:

```python
# Each invocation is independent
result1 = agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Bob"}]})
result2 = agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]})
# Agent doesn't remember Bob!
```

To add memory, you must manage it externally:

```python
# Manual memory management
conversation_history = []

def chat(user_message: str) -> str:
    conversation_history.append({"role": "user", "content": user_message})
    result = agent.invoke({"messages": conversation_history})
    assistant_message = result["messages"][-1]
    conversation_history.append(assistant_message)
    return assistant_message.content
```

### LangGraph: Built-in Checkpointers

LangGraph provides multiple persistence options:

#### In-Memory (Development)

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

# Use thread_id to maintain conversation
config = {"configurable": {"thread_id": "user-123"}}

# First message
graph.invoke(
    {"messages": [{"role": "user", "content": "Hi, I'm Bob"}]},
    config
)

# Second message - remembers context!
graph.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    config
)
# Agent knows the name is Bob!
```

#### PostgreSQL (Production)

```python
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://user:pass@localhost:5432/db"
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    graph = workflow.compile(checkpointer=checkpointer)

    # Conversations persist across restarts
    config = {"configurable": {"thread_id": "user-123"}}
    graph.invoke({"messages": [...]}, config)
```

#### MongoDB

```python
from langgraph.checkpoint.mongodb import MongoDBSaver

with MongoDBSaver.from_conn_string("localhost:27017") as checkpointer:
    graph = workflow.compile(checkpointer=checkpointer)
```

### Time Travel and State Inspection

LangGraph allows inspecting and replaying from any checkpoint:

```python
# Get current state
state = graph.get_state({"configurable": {"thread_id": "user-123"}})
print(state.values)  # Current state values
print(state.next)    # Next node(s) to execute

# Get state at specific checkpoint
state = graph.get_state({
    "configurable": {
        "thread_id": "user-123",
        "checkpoint_id": "abc123"
    }
})

# List all checkpoints for a thread
for checkpoint in graph.get_state_history(config):
    print(checkpoint.checkpoint_id, checkpoint.created_at)
```

---

## Human-in-the-Loop

### LangChain: Not Supported

LangChain's `create_agent` has no built-in mechanism for pausing execution, getting human approval, or resuming from an interrupted state.

### LangGraph: Native Support

LangGraph provides multiple patterns for human-in-the-loop workflows:

#### Static Breakpoints

Pause execution at specific nodes:

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

# Compile with breakpoints
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["sensitive_action"],  # Pause BEFORE this node
    interrupt_after=["generate_plan"]       # Pause AFTER this node
)

config = {"configurable": {"thread_id": "1"}}

# Run until breakpoint
for event in graph.stream(initial_input, config):
    print(event)

# Graph is now paused - get human approval...
human_approved = get_human_approval()

if human_approved:
    # Resume execution
    for event in graph.stream(None, config):
        print(event)
```

#### Dynamic Interrupts

Pause based on runtime conditions:

```python
from langgraph.types import interrupt

def sensitive_action(state):
    # Check if action requires approval
    if state["action_risk"] == "high":
        # Pause and get human input
        human_decision = interrupt({
            "action": state["proposed_action"],
            "reason": "High-risk action requires approval",
            "options": ["approve", "reject", "modify"]
        })

        if human_decision == "reject":
            return {"status": "cancelled"}

    # Continue with action
    return execute_action(state)
```

#### Resuming with Human Input

```python
from langgraph.types import Command

# Initial run - will pause at interrupt
for event in graph.stream("Process this request", config):
    print(event)

# Human reviews and provides input
human_feedback = "approved with modifications: ..."

# Resume with human input
for event in graph.stream(
    Command(resume=human_feedback),
    config
):
    print(event)
```

### Use Cases for Human-in-the-Loop

| Use Case | LangChain | LangGraph |
|----------|-----------|-----------|
| Approve high-value transactions | Not possible | Use `interrupt_before` |
| Review generated content | Not possible | Use `interrupt` function |
| Correct agent mistakes | Not possible | Use `update_state` |
| Multi-step approval workflows | Not possible | Chain multiple interrupts |
| Audit trail for decisions | Manual logging | Automatic via checkpoints |

---

## Streaming and Observability

### Streaming Comparison

Both frameworks support streaming, but with different capabilities:

#### LangChain Streaming

```python
# Stream intermediate steps
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Research AI trends"}]},
    stream_mode="values"
):
    print(chunk["messages"][-1])

# Stream tokens
for token, metadata in agent.stream(
    {"messages": [...]},
    stream_mode="messages"
):
    print(token.content, end="")
```

#### LangGraph Streaming

```python
# Stream state updates
for event in graph.stream(input, config, stream_mode="updates"):
    print(f"Node: {list(event.keys())[0]}")
    print(f"Update: {event}")

# Stream with full values
for event in graph.stream(input, config, stream_mode="values"):
    print(event)

# Stream debug information
for event in graph.stream(input, config, stream_mode="debug"):
    print(f"Step: {event['step']}")
    print(f"Type: {event['type']}")
```

### Graph Visualization (LangGraph Only)

```python
# Generate visual representation
from IPython.display import Image, display

# Display in Jupyter
display(Image(graph.get_graph().draw_mermaid_png()))

# Save to file
png_data = graph.get_graph().draw_mermaid_png()
with open("agent_graph.png", "wb") as f:
    f.write(png_data)

# ASCII output for terminals
print(graph.get_graph().draw_ascii())
```

---

## When to Use Which Approach

### Use LangChain `create_agent` When:

1. **Prototyping and Learning**
   - Quick proof-of-concept
   - Learning ReAct patterns
   - Simple demos

2. **Simple Q&A Applications**
   - Stateless question answering
   - Single-turn interactions
   - No persistence requirements

3. **Minimal Customization Needed**
   - Standard ReAct behavior is sufficient
   - No special routing logic
   - No custom state fields

4. **Team Familiarity**
   - Team is new to agent development
   - Prefer simpler abstractions

### Use LangGraph When:

1. **Production Applications**
   - Need reliability and durability
   - Require state persistence
   - Must handle failures gracefully

2. **Complex Workflows**
   - Multi-step processes
   - Conditional branching
   - Parallel execution
   - Subgraphs and composition

3. **Human Oversight Required**
   - Approval workflows
   - Content review
   - High-stakes decisions
   - Audit requirements

4. **Custom State Management**
   - Track metadata across turns
   - Maintain session context
   - Complex state transformations

5. **Debugging and Monitoring**
   - Need graph visualization
   - Time travel debugging
   - Step-by-step inspection

6. **Deployment Requirements**
   - Deploy via LangGraph Platform
   - Need built-in scaling
   - Require API endpoints

### Decision Flowchart

```
Start
  │
  ▼
Need persistence/memory?
  │
  ├── Yes ──► LangGraph
  │
  No
  │
  ▼
Need human-in-the-loop?
  │
  ├── Yes ──► LangGraph
  │
  No
  │
  ▼
Need custom state fields?
  │
  ├── Yes ──► LangGraph
  │
  No
  │
  ▼
Complex routing/branching?
  │
  ├── Yes ──► LangGraph
  │
  No
  │
  ▼
Production deployment?
  │
  ├── Yes ──► LangGraph (recommended)
  │
  No
  │
  ▼
LangChain `create_agent` is sufficient
```

---

## Migration Path

### From LangChain to LangGraph

If you start with LangChain and need to migrate to LangGraph:

#### Step 1: Use LangGraph Prebuilt (Minimal Change)

```python
# Before (LangChain)
from langchain.agents import create_agent

agent = create_agent(model, tools=tools, system_prompt=prompt)

# After (LangGraph Prebuilt)
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(model, tools=tools, prompt=prompt)
```

#### Step 2: Add Checkpointing

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
agent = create_react_agent(
    model,
    tools=tools,
    prompt=prompt,
    checkpointer=checkpointer
)
```

#### Step 3: Convert to Manual Graph (Full Control)

When you need maximum customization, convert to a manual StateGraph:

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
    # Add custom fields
    user_context: dict
    step_count: int

def agent_node(state: State):
    # Custom logic
    ...

def tools_node(state: State):
    # Custom tool handling
    ...

def router(state: State):
    # Custom routing
    ...

workflow = StateGraph(State)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tools_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", router)
workflow.add_edge("tools", "agent")

graph = workflow.compile(checkpointer=checkpointer)
```

---

## Summary

| Dimension | LangChain `create_agent` | LangGraph |
|-----------|-------------------------|-----------|
| **Philosophy** | Simple abstraction | Explicit control |
| **Code Complexity** | Low | Medium to High |
| **Flexibility** | Limited | Extensive |
| **State** | Messages only | Custom TypedDict |
| **Memory** | Manual | Built-in checkpointers |
| **Human-in-the-Loop** | Not supported | Native support |
| **Visualization** | None | Built-in |
| **Debugging** | Basic | Time travel, breakpoints |
| **Deployment** | Standard | LangGraph Platform |
| **Best For** | Prototypes, simple agents | Production, complex workflows |

### Final Recommendation

- **Start with LangChain `create_agent`** if you're new to ReAct agents or building a simple prototype
- **Move to LangGraph** when you need production features like persistence, human oversight, or complex control flow
- **Use LangGraph `create_react_agent`** as a middle ground - simpler API with LangGraph's infrastructure benefits
