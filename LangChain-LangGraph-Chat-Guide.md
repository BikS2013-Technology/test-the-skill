# LangChain & LangGraph Guide for Chat Applications

**Date:** December 22, 2025

This guide provides comprehensive instructions on using LangChain and LangGraph to communicate with various LLMs in the context of implementing chat applications.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [LangChain: Connecting to LLMs](#langchain-connecting-to-llms)
   - [Unified Model Initialization](#unified-model-initialization)
   - [Provider-Specific Classes](#provider-specific-classes)
   - [Supported LLM Providers](#supported-llm-providers)
   - [Runtime Model Switching](#runtime-model-switching)
4. [LangGraph: Building Chat Applications](#langgraph-building-chat-applications)
   - [Core Concepts](#core-concepts)
   - [Basic Chatbot Implementation](#basic-chatbot-implementation)
   - [Adding Memory (Persistence)](#adding-memory-persistence)
   - [Message Management](#message-management)
5. [Advanced Features](#advanced-features)
   - [Streaming Responses](#streaming-responses)
   - [Tool Integration](#tool-integration)
   - [Agents with Tools](#agents-with-tools)
6. [Complete Examples](#complete-examples)
7. [Best Practices](#best-practices)

---

## Overview

**LangChain** is a framework for developing applications powered by large language models (LLMs). It provides:
- Unified interfaces for multiple LLM providers
- Tools for building complex LLM workflows
- Standardized component interfaces

**LangGraph** is a low-level orchestration framework for building stateful agents and workflows. It provides:
- Durable execution with state persistence
- Human-in-the-loop capabilities
- Comprehensive memory management
- Production-ready deployment features

Together, they form a powerful stack for building sophisticated chat applications.

---

## Installation

### Base Installation

```bash
# Install LangChain core
pip install langchain

# Install LangGraph
pip install langgraph
```

### Provider-Specific Dependencies

```bash
# OpenAI
pip install -U "langchain[openai]"

# Anthropic (Claude)
pip install -U "langchain[anthropic]"

# Google (Gemini)
pip install -U "langchain[google-genai]"

# AWS Bedrock
pip install -U "langchain[aws]"

# HuggingFace
pip install -U "langchain[huggingface]"

# Ollama (Local Models)
pip install -qU langchain-ollama
```

---

## LangChain: Connecting to LLMs

### Unified Model Initialization

LangChain provides `init_chat_model()` - a unified way to initialize chat models from any provider:

```python
import os
from langchain.chat_models import init_chat_model

# OpenAI
os.environ["OPENAI_API_KEY"] = "sk-..."
model = init_chat_model("gpt-4.1")

# Anthropic Claude
os.environ["ANTHROPIC_API_KEY"] = "sk-..."
model = init_chat_model("claude-sonnet-4-5-20250929")

# Google Gemini
os.environ["GOOGLE_API_KEY"] = "..."
model = init_chat_model("google_genai:gemini-2.5-flash-lite")

# Azure OpenAI
os.environ["AZURE_OPENAI_API_KEY"] = "..."
os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"
model = init_chat_model(
    "azure_openai:gpt-4.1",
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
)

# AWS Bedrock
model = init_chat_model(
    "anthropic.claude-3-5-sonnet-20240620-v1:0",
    model_provider="bedrock_converse",
)

# HuggingFace
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "hf_..."
model = init_chat_model(
    "microsoft/Phi-3-mini-4k-instruct",
    model_provider="huggingface",
    temperature=0.7,
    max_tokens=1024,
)
```

### Configuration Parameters

```python
model = init_chat_model(
    "claude-sonnet-4-5-20250929",
    temperature=0.7,      # Controls randomness (0.0-1.0)
    timeout=30,           # Maximum seconds to wait
    max_tokens=1000,      # Maximum tokens in response
    max_retries=3         # Retry attempts on failure
)
```

### Provider-Specific Classes

For more granular control, use provider-specific classes:

```python
# OpenAI
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4.1")

# Anthropic
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-sonnet-4-5-20250929")

# Azure OpenAI
from langchain_openai import AzureChatOpenAI
model = AzureChatOpenAI(
    model="gpt-4.1",
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
)

# Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

# AWS Bedrock
from langchain_aws import ChatBedrock
model = ChatBedrock(model="anthropic.claude-3-5-sonnet-20240620-v1:0")

# HuggingFace
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
llm = HuggingFaceEndpoint(
    repo_id="microsoft/Phi-3-mini-4k-instruct",
    temperature=0.7,
    max_length=1024
)
model = ChatHuggingFace(llm=llm)

# Ollama (Local)
from langchain_ollama import OllamaEmbeddings
embeddings = OllamaEmbeddings(model="llama3")
```

### Supported LLM Providers

| Provider | Model Examples | Package |
|----------|---------------|---------|
| OpenAI | gpt-4.1, gpt-5-nano | `langchain[openai]` |
| Anthropic | claude-sonnet-4-5, claude-haiku | `langchain[anthropic]` |
| Google | gemini-2.5-flash-lite | `langchain[google-genai]` |
| Azure OpenAI | gpt-4.1 (via Azure) | `langchain[openai]` |
| AWS Bedrock | claude-3-5-sonnet | `langchain[aws]` |
| HuggingFace | Phi-3-mini, Llama | `langchain[huggingface]` |
| Ollama | llama3, mistral (local) | `langchain-ollama` |
| Custom | Any OpenAI-compatible API | `langchain[openai]` |

### Custom OpenAI-Compatible APIs

```python
model = init_chat_model(
    model="MODEL_NAME",
    model_provider="openai",
    base_url="https://your-api-endpoint.com/v1",
    api_key="YOUR_API_KEY",
)
```

### Runtime Model Switching

Switch between models dynamically at runtime:

```python
from langchain.chat_models import init_chat_model

# Create a configurable model
configurable_model = init_chat_model(temperature=0)

# Run with different models using config
response_gpt = configurable_model.invoke(
    "What's the capital of France?",
    config={"configurable": {"model": "gpt-4.1"}}
)

response_claude = configurable_model.invoke(
    "What's the capital of France?",
    config={"configurable": {"model": "claude-sonnet-4-5-20250929"}}
)
```

---

## LangGraph: Building Chat Applications

### Core Concepts

LangGraph uses a **graph-based** approach to manage conversation flow:

- **State**: Holds the conversation data (messages, metadata)
- **Nodes**: Functions that process and transform state
- **Edges**: Define the flow between nodes
- **Checkpointer**: Enables persistence across conversation turns

### Basic Chatbot Implementation

#### Using the Graph API

```python
from typing import Annotated
from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Define state structure
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize model
model = init_chat_model("claude-sonnet-4-5-20250929")

# Define chatbot node
def chatbot(state: State):
    return {"messages": [model.invoke(state["messages"])]}

# Build the graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Compile
graph = graph_builder.compile()

# Use the chatbot
response = graph.invoke({"messages": [{"role": "user", "content": "Hello!"}]})
print(response["messages"][-1].content)
```

#### Using the Functional API

```python
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from langgraph.func import entrypoint, task
from langgraph.checkpoint.memory import InMemorySaver
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-sonnet-4-5-20250929")

@task
def call_model(messages: list[BaseMessage]):
    response = model.invoke(messages)
    return response

checkpointer = InMemorySaver()

@entrypoint(checkpointer=checkpointer)
def workflow(inputs: list[BaseMessage], *, previous: list[BaseMessage]):
    if previous:
        inputs = add_messages(previous, inputs)

    response = call_model(inputs).result()
    return entrypoint.final(value=response, save=add_messages(inputs, response))

# Use with conversation threading
config = {"configurable": {"thread_id": "1"}}

# First message
input_message = {"role": "user", "content": "Hi! I'm Bob"}
for chunk in workflow.stream([input_message], config, stream_mode="values"):
    chunk.pretty_print()

# Follow-up (remembers context)
input_message = {"role": "user", "content": "What's my name?"}
for chunk in workflow.stream([input_message], config, stream_mode="values"):
    chunk.pretty_print()
```

### Adding Memory (Persistence)

#### Short-Term Memory (Thread-Level)

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph

checkpointer = InMemorySaver()

builder = StateGraph(...)
graph = builder.compile(checkpointer=checkpointer)

# Use with thread_id to maintain conversation context
graph.invoke(
    {"messages": [{"role": "user", "content": "Hi! I am Bob"}]},
    {"configurable": {"thread_id": "1"}},
)

# Same thread_id = same conversation
graph.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    {"configurable": {"thread_id": "1"}},  # Remembers previous context
)

# Different thread_id = new conversation
graph.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    {"configurable": {"thread_id": "2"}},  # Fresh context
)
```

#### Long-Term Memory (Cross-Conversation)

```python
from langgraph.store.memory import InMemoryStore
from langgraph.graph import StateGraph

store = InMemoryStore()

builder = StateGraph(...)
graph = builder.compile(store=store)
```

#### Production Memory with Redis

```python
from langgraph.checkpoint.redis import RedisSaver
from langgraph.store.redis import RedisStore

DB_URI = "redis://localhost:6379"

async def run_async_example():
    async with (
        RedisStore.from_conn_string(DB_URI) as store,
        RedisSaver.from_conn_string(DB_URI) as checkpointer,
    ):
        await store.setup()
        await checkpointer.setup()

        # Build graph with production storage
        graph = builder.compile(
            checkpointer=checkpointer,
            store=store,
        )
```

### Message Management

#### Using MessagesState

```python
from langgraph.graph import MessagesState

class State(MessagesState):
    """A state that includes messages and extra fields."""
    extra_field: int
    summary: str
```

#### Trimming Messages (Token Management)

```python
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, MessagesState

model = init_chat_model("claude-sonnet-4-5-20250929")

def call_model(state: MessagesState):
    # Trim messages to fit token limit
    messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=128,
        start_on="human",
        end_on=("human", "tool"),
    )
    response = model.invoke(messages)
    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node(call_model)
builder.add_edge(START, "call_model")
```

#### Deleting Old Messages

```python
from langchain.messages import RemoveMessage

def delete_messages(state):
    messages = state["messages"]
    if len(messages) > 2:
        # Remove the earliest two messages
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
```

#### Conversation Summarization

```python
from langgraph.graph import MessagesState
from langchain.schema import HumanMessage, RemoveMessage

class State(MessagesState):
    summary: str

def summarize_conversation(state: State):
    summary = state.get("summary", "")

    if summary:
        summary_message = (
            f"This is a summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}
```

---

## Advanced Features

### Streaming Responses

#### Basic Streaming

```python
# Stream token by token
for chunk in model.stream("Why do parrots talk?"):
    print(chunk.content, end="", flush=True)
```

#### Streaming with Agents

```python
from langchain.agents import create_agent

agent = create_agent(model="gpt-4.1", tools=[...])

# Stream with updates mode
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode="updates",
):
    for step, data in chunk.items():
        print(f"step: {step}")
        print(f"content: {data['messages'][-1].content_blocks}")

# Stream with values mode (full state at each step)
for chunk in agent.stream(
    {"messages": [...]},
    stream_mode="values"
):
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        print(f"Agent: {latest_message.content}")

# Stream individual tokens
for token, metadata in agent.stream(
    {"messages": [...]},
    stream_mode="messages",
):
    print(f"node: {metadata['langgraph_node']}")
    print(f"content: {token.content_blocks}")
```

#### Aggregating Streamed Chunks

```python
full = None
for chunk in model.stream("What color is the sky?"):
    full = chunk if full is None else full + chunk
    print(full.text)

print(full.content_blocks)
```

### Tool Integration

#### Defining Tools

```python
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get the weather at a location."""
    return f"It's sunny in {location}."

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers.

    Args:
        a: First int
        b: Second int
    """
    return a * b
```

#### Binding Tools to Models

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("claude-sonnet-4-5-20250929")
model_with_tools = model.bind_tools([get_weather, multiply])

response = model_with_tools.invoke("What's the weather in Boston?")
for tool_call in response.tool_calls:
    print(f"Tool: {tool_call['name']}")
    print(f"Args: {tool_call['args']}")
```

#### Tools with Pydantic Models

```python
from pydantic import BaseModel, Field

class GetWeather(BaseModel):
    """Get the current weather in a given location"""
    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

class GetPopulation(BaseModel):
    """Get the current population in a given location"""
    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

model_with_tools = model.bind_tools([GetWeather, GetPopulation])
```

### Agents with Tools

#### Using Prebuilt Components

```python
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated
from typing_extensions import TypedDict

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize model with tools
llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
tool = TavilySearch(max_results=2)
tools = [tool]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

# Add conditional routing
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()
```

#### Custom Agent with Graph API

```python
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain.messages import SystemMessage, ToolMessage
from typing import Literal

def llm_call(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    return {
        "messages": [
            llm_with_tools.invoke(
                [SystemMessage(content="You are a helpful assistant.")]
                + state["messages"]
            )
        ]
    }

def tool_node(state: dict):
    """Performs the tool call"""
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call['name']]
        observation = tool.invoke(tool_call['args'])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call['id']))
    return {"messages": result}

def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue or stop"""
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tool_node"
    return END

# Build workflow
agent_builder = StateGraph(MessagesState)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
agent_builder.add_edge("tool_node", "llm_call")

agent = agent_builder.compile()
```

---

## Complete Examples

### Simple Chat Application

```python
import os
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver

# Configure your preferred provider
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

# Initialize model
model = init_chat_model("claude-sonnet-4-5-20250929")

# Define chatbot node
def chatbot(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# Build graph with memory
builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# Chat loop
def chat(user_input: str, thread_id: str = "default"):
    config = {"configurable": {"thread_id": thread_id}}
    response = graph.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config
    )
    return response["messages"][-1].content

# Example usage
print(chat("Hello! My name is Alice."))
print(chat("What's my name?"))  # Will remember "Alice"
```

### Multi-Provider Chat with Dynamic Switching

```python
from dataclasses import dataclass
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver

# Pre-initialize models
MODELS = {
    "openai": init_chat_model("gpt-4.1"),
    "anthropic": init_chat_model("claude-sonnet-4-5-20250929"),
    "google": init_chat_model("google_genai:gemini-2.5-flash-lite"),
}

class State(MessagesState):
    provider: str  # Track which provider to use

def chatbot(state: State):
    provider = state.get("provider", "anthropic")
    model = MODELS.get(provider, MODELS["anthropic"])
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# Build graph
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile(checkpointer=InMemorySaver())

# Use with different providers
config = {"configurable": {"thread_id": "1"}}

# Chat with Claude
response = graph.invoke(
    {"messages": [{"role": "user", "content": "Hello!"}], "provider": "anthropic"},
    config
)

# Switch to GPT
response = graph.invoke(
    {"messages": [{"role": "user", "content": "Now using GPT!"}], "provider": "openai"},
    config
)
```

### Streaming Chat with Tools

```python
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Search results for: {query}"

@tool
def get_current_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Setup
model = init_chat_model("claude-sonnet-4-5-20250929")
tools = [search_web, get_current_time]
model_with_tools = model.bind_tools(tools)

def chatbot(state: MessagesState):
    return {"messages": [model_with_tools.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools=tools))
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")
builder.add_edge(START, "chatbot")

graph = builder.compile(checkpointer=InMemorySaver())

# Stream responses
config = {"configurable": {"thread_id": "1"}}

for event in graph.stream(
    {"messages": [{"role": "user", "content": "What time is it?"}]},
    config,
    stream_mode="values"
):
    message = event["messages"][-1]
    if hasattr(message, 'content') and message.content:
        print(f"Response: {message.content}")
    elif hasattr(message, 'tool_calls') and message.tool_calls:
        print(f"Calling tools: {[tc['name'] for tc in message.tool_calls]}")
```

---

## Best Practices

### 1. Environment Configuration

```python
import os

# Never hardcode API keys
# Use environment variables or secure configuration management
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

# Raise exceptions for missing configuration (as per project guidelines)
if not os.environ.get("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")
```

### 2. Error Handling

```python
from langchain.chat_models import init_chat_model

try:
    model = init_chat_model(
        "claude-sonnet-4-5-20250929",
        max_retries=3,
        timeout=30
    )
    response = model.invoke("Hello!")
except Exception as e:
    # Handle specific exceptions as needed
    raise RuntimeError(f"Failed to communicate with LLM: {e}")
```

### 3. Memory Management for Long Conversations

```python
# Always implement message trimming or summarization for production apps
from langchain_core.messages.utils import trim_messages, count_tokens_approximately

def call_model(state: MessagesState):
    trimmed = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=4000,  # Adjust based on model context window
        start_on="human",
    )
    return {"messages": [model.invoke(trimmed)]}
```

### 4. Thread Management

```python
# Use meaningful thread IDs for production
import uuid

def create_conversation_thread(user_id: str, conversation_type: str) -> str:
    """Generate a unique thread ID for conversation tracking."""
    return f"{user_id}_{conversation_type}_{uuid.uuid4().hex[:8]}"

thread_id = create_conversation_thread("user123", "support")
config = {"configurable": {"thread_id": thread_id}}
```

### 5. Model Selection Strategy

```python
# Select models based on task complexity
def select_model_for_task(task_type: str, message_count: int):
    if task_type == "simple_qa" or message_count < 5:
        return init_chat_model("gpt-4o-mini")  # Fast and cheap
    elif task_type == "complex_reasoning":
        return init_chat_model("claude-sonnet-4-5-20250929")  # More capable
    elif message_count > 20:
        return init_chat_model("claude-sonnet-4-5-20250929")  # Larger context
    else:
        return init_chat_model("gpt-4o")  # Default
```

---

## Summary

This guide covered the essential aspects of building chat applications with LangChain and LangGraph:

| Component | Purpose |
|-----------|---------|
| `init_chat_model()` | Unified model initialization |
| `StateGraph` | Graph-based conversation flow |
| `MessagesState` | Built-in message state management |
| `InMemorySaver` | Short-term conversation persistence |
| `InMemoryStore` | Long-term memory storage |
| `ToolNode` | Prebuilt tool execution |
| `tools_condition` | Automatic tool routing |
| `trim_messages` | Token management |
| `stream()` | Real-time response streaming |

For production deployments, consider:
- Using Redis or PostgreSQL for persistence instead of in-memory stores
- Implementing proper error handling and retry logic
- Setting up monitoring and logging
- Using environment-based configuration management
