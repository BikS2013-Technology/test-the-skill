# LangChain Fundamentals Guide

**Date:** December 23, 2025

This guide provides comprehensive instructions on using LangChain to communicate with various LLMs, build simple chat applications, use chains, templates, and runnables.

---

## Table of Contents

- [LangChain Fundamentals Guide](#langchain-fundamentals-guide)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Installation](#installation)
    - [Setting Up Your Project with uv](#setting-up-your-project-with-uv)
    - [Base Installation](#base-installation)
    - [Provider-Specific Dependencies](#provider-specific-dependencies)
    - [Running Python Scripts](#running-python-scripts)
      - [Option 1: Activate the Virtual Environment](#option-1-activate-the-virtual-environment)
      - [Option 2: Use uv run (Recommended)](#option-2-use-uv-run-recommended)
    - [Verifying Your Installation](#verifying-your-installation)
  - [Connecting to LLMs](#connecting-to-llms)
    - [Unified Model Initialization](#unified-model-initialization)
    - [Provider-Specific Classes](#provider-specific-classes)
    - [Supported LLM Providers](#supported-llm-providers)
    - [Custom OpenAI-Compatible APIs](#custom-openai-compatible-apis)
    - [Configuration Parameters](#configuration-parameters)
    - [Runtime Model Switching](#runtime-model-switching)
      - [Configurable Fields with Prefixes](#configurable-fields-with-prefixes)
  - [Messages and Conversations](#messages-and-conversations)
    - [Message Types](#message-types)
    - [Dictionary Format](#dictionary-format)
    - [Message Objects](#message-objects)
      - [Creating Messages Manually](#creating-messages-manually)
    - [Multimodal Messages](#multimodal-messages)
      - [Images](#images)
      - [Audio and Video](#audio-and-video)
      - [PDF Documents](#pdf-documents)
  - [Building a Simple Chat Application](#building-a-simple-chat-application)
    - [Basic Invocation](#basic-invocation)
    - [Conversation History](#conversation-history)
    - [Simple Chat Loop](#simple-chat-loop)
  - [Streaming Responses](#streaming-responses)
    - [Basic Streaming](#basic-streaming)
    - [Async Streaming with Events](#async-streaming-with-events)
    - [Aggregating Streamed Chunks](#aggregating-streamed-chunks)
    - [Batch Processing](#batch-processing)
  - [Prompt Templates](#prompt-templates)
    - [Basic Templates](#basic-templates)
    - [Chat Prompt Templates](#chat-prompt-templates)
    - [Dynamic Prompts](#dynamic-prompts)
  - [Chains and Runnables (LCEL)](#chains-and-runnables-lcel)
    - [What is LCEL](#what-is-lcel)
    - [Creating Chains with Pipe Operator](#creating-chains-with-pipe-operator)
      - [Multi-Step Chains](#multi-step-chains)
    - [The @chain Decorator](#the-chain-decorator)
    - [Runnable Configuration](#runnable-configuration)
      - [RunnablePassthrough and RunnableLambda](#runnablepassthrough-and-runnablelambda)
  - [Structured Output](#structured-output)
    - [Using Pydantic Models](#using-pydantic-models)
    - [Using TypedDict](#using-typeddict)
    - [Using JSON Schema](#using-json-schema)
    - [Include Raw Response](#include-raw-response)
  - [Tool Integration](#tool-integration)
    - [Defining Tools](#defining-tools)
    - [Tools with Pydantic Models](#tools-with-pydantic-models)
    - [Binding Tools to Models](#binding-tools-to-models)
    - [Streaming Tool Calls](#streaming-tool-calls)
      - [Accumulating Tool Call Chunks](#accumulating-tool-call-chunks)
  - [Complete Examples](#complete-examples)
    - [Translation Chain](#translation-chain)
    - [Streaming Chat with Memory](#streaming-chat-with-memory)
    - [Data Extraction with Structured Output](#data-extraction-with-structured-output)
  - [Best Practices](#best-practices)
    - [1. Environment Configuration](#1-environment-configuration)
    - [2. Error Handling](#2-error-handling)
    - [3. Token Management](#3-token-management)
    - [4. Reusable Chain Patterns](#4-reusable-chain-patterns)
    - [5. Logging and Debugging](#5-logging-and-debugging)
  - [Summary](#summary)

---

## Overview

**LangChain** is a framework for developing applications powered by large language models (LLMs). It provides:

- **Unified interfaces** for multiple LLM providers (OpenAI, Anthropic, Google, AWS, HuggingFace, etc.)
- **Standardized component interfaces** for building complex LLM workflows
- **Tools and abstractions** for prompt management, chains, and output parsing
- **LCEL (LangChain Expression Language)** for composing runnables

This guide focuses on LangChain's core capabilities without diving into LangGraph's advanced agent orchestration features.

---

## Installation

This guide uses **uv** as the package and environment manager. uv is a fast Python package installer and resolver that provides virtual environment management.

### Setting Up Your Project with uv

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a new project directory
mkdir my-langchain-project
cd my-langchain-project

# Initialize a new Python project with uv
uv init

# This creates:
# - pyproject.toml (project configuration)
# - .python-version (Python version specification)
# - .venv/ (virtual environment)
```

### Base Installation

```bash
# Install LangChain core
uv add langchain
```

### Provider-Specific Dependencies

```bash
# OpenAI
uv add "langchain[openai]"

# Anthropic (Claude)
uv add "langchain[anthropic]"

# Google (Gemini)
uv add "langchain[google-genai]"

# AWS Bedrock
uv add "langchain[aws]"

# HuggingFace
uv add "langchain[huggingface]"

# Ollama (Local Models)
uv add langchain-ollama
```

### Running Python Scripts

When running Python scripts in a uv-managed project, you have two options:

#### Option 1: Activate the Virtual Environment

```bash
# Activate the virtual environment first
source .venv/bin/activate

# Then run your Python script
python my_script.py
```

#### Option 2: Use uv run (Recommended)

```bash
# Run directly with uv (automatically uses the virtual environment)
uv run python my_script.py

# Or run a module
uv run python -m my_module
```

### Verifying Your Installation

```bash
# Check installed packages
uv pip list

# Verify LangChain is installed
uv run python -c "import langchain; print(langchain.__version__)"
```

---

## Connecting to LLMs

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
os.environ["AZURE_OPENAI_API_VERSION"] = "2025-03-01-preview"
model = init_chat_model(
    f"azure_openai:{os.environ['AZURE_OPENAI_DEPLOYMENT']}",
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
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
    model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"]
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

### Custom OpenAI-Compatible APIs

```python
model = init_chat_model(
    model="MODEL_NAME",
    model_provider="openai",
    base_url="https://your-api-endpoint.com/v1",
    api_key="YOUR_API_KEY",
)
```

### Azure OpenAI Configuration

Azure OpenAI requires specific environment variables and configuration. Here's a comprehensive setup:

**Required Environment Variables:**
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL (e.g., `https://your-resource.openai.azure.com/`)
- `AZURE_OPENAI_API_VERSION`: API version (e.g., `2025-03-01-preview`)
- `AZURE_OPENAI_DEPLOYMENT`: Your deployment name

**Using init_chat_model (Unified Approach):**
```python
import os
from langchain.chat_models import init_chat_model

# The model string format is: azure_openai:<deployment_name>
model = init_chat_model(
    f"azure_openai:{os.environ['AZURE_OPENAI_DEPLOYMENT']}",
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
)
```

**Using AzureChatOpenAI (Provider-Specific):**
```python
from langchain_openai import AzureChatOpenAI

model = AzureChatOpenAI(
    model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    temperature=0.7,
    max_tokens=1000,
)
```

> **Note:** When using Azure OpenAI, the `model` and `azure_deployment` parameters typically have the same value - your Azure deployment name.

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

#### Configurable Fields with Prefixes

```python
first_model = init_chat_model(
    model="gpt-4.1-mini",
    temperature=0,
    configurable_fields=("model", "model_provider", "temperature", "max_tokens"),
    config_prefix="first",  # Useful when you have multiple models in a chain
)

# Use defaults
first_model.invoke("what's your name")

# Override at runtime
first_model.invoke(
    "what's your name",
    config={
        "configurable": {
            "first_model": "claude-sonnet-4-5-20250929",
            "first_temperature": 0.5,
            "first_max_tokens": 100,
        }
    },
)
```

#### Azure OpenAI Runtime Configuration

For Azure OpenAI, runtime model switching works differently because you're switching between Azure deployments rather than model names:

```python
import os
from langchain_openai import AzureChatOpenAI

# Create multiple Azure OpenAI models for different deployments
def get_azure_model(deployment_name: str = None):
    """Get Azure OpenAI model with optional deployment override."""
    deployment = deployment_name or os.environ["AZURE_OPENAI_DEPLOYMENT"]
    return AzureChatOpenAI(
        model=deployment,
        azure_deployment=deployment,
        temperature=0.7,
    )

# Use default deployment
model = get_azure_model()
response = model.invoke("Hello!")

# Use a different deployment
model_gpt4 = get_azure_model("gpt-4-deployment")
response = model_gpt4.invoke("Hello!")
```

> **Note:** Azure OpenAI requires pre-configured deployments in your Azure resource. You cannot dynamically switch to arbitrary model names like with direct OpenAI API access. Plan your deployments in advance based on your application's needs.

---

## Messages and Conversations

### Message Types

LangChain supports several message types for representing conversation turns:

- **SystemMessage**: Instructions for the model's behavior
- **HumanMessage**: User input
- **AIMessage**: Model responses
- **ToolMessage**: Results from tool calls

### Dictionary Format

The simplest way to represent messages is using dictionaries:

```python
conversation = [
    {"role": "system", "content": "You are a helpful assistant that translates English to French."},
    {"role": "user", "content": "Translate: I love programming."},
    {"role": "assistant", "content": "J'adore la programmation."},
    {"role": "user", "content": "Translate: I love building applications."}
]

response = model.invoke(conversation)
print(response)  # AIMessage("J'adore creer des applications.")
```

### Message Objects

For more type-safety and features, use LangChain message objects:

```python
from langchain.messages import HumanMessage, AIMessage, SystemMessage

conversation = [
    SystemMessage("You are a helpful assistant that translates English to French."),
    HumanMessage("Translate: I love programming."),
    AIMessage("J'adore la programmation."),
    HumanMessage("Translate: I love building applications.")
]

response = model.invoke(conversation)
print(response)  # AIMessage("J'adore creer des applications.")
```

#### Creating Messages Manually

```python
from langchain.messages import AIMessage, SystemMessage, HumanMessage

# Create an AI message manually (e.g., for conversation history)
ai_msg = AIMessage("I'd be happy to help you with that question!")

# Add to conversation history
messages = [
    SystemMessage("You are a helpful assistant"),
    HumanMessage("Can you help me?"),
    ai_msg,  # Insert as if it came from the model
    HumanMessage("Great! What's 2+2?")
]

response = model.invoke(messages)
```

### Multimodal Messages

LangChain supports images, audio, video, and documents in messages:

#### Images

```python
# From URL
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Describe the content of this image."},
        {"type": "image", "url": "https://example.com/path/to/image.jpg"},
    ]
}

# From base64 data
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Describe the content of this image."},
        {
            "type": "image",
            "base64": "AAAAIGZ0eXBtcDQy...",
            "mime_type": "image/jpeg",
        },
    ]
}

# From provider-managed File ID
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Describe the content of this image."},
        {"type": "image", "file_id": "file-abc123"},
    ]
}
```

#### Audio and Video

```python
# Audio from base64
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Describe the content of this audio."},
        {
            "type": "audio",
            "base64": "AAAAIGZ0eXBtcDQy...",
            "mime_type": "audio/wav",
        },
    ]
}

# Video from base64
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Describe the content of this video."},
        {
            "type": "video",
            "base64": "AAAAIGZ0eXBtcDQy...",
            "mime_type": "video/mp4",
        },
    ]
}
```

#### PDF Documents

```python
# From URL
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Describe the content of this document."},
        {"type": "file", "url": "https://example.com/path/to/document.pdf"},
    ]
}

# From base64 data
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Describe the content of this document."},
        {
            "type": "file",
            "base64": "AAAAIGZ0eXBtcDQy...",
            "mime_type": "application/pdf",
        },
    ]
}
```

---

## Building a Simple Chat Application

### Basic Invocation

The simplest way to interact with an LLM:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("claude-sonnet-4-5-20250929")

# Single prompt
response = model.invoke("Write a haiku about spring")
print(response.content)
```

### Conversation History

Maintain conversation context by passing message history:

```python
from langchain.messages import HumanMessage, AIMessage, SystemMessage

model = init_chat_model("claude-sonnet-4-5-20250929")

# Initialize conversation
messages = [
    SystemMessage("You are a helpful assistant. Be concise."),
]

def chat(user_input: str) -> str:
    """Send a message and get a response while maintaining history."""
    # Add user message
    messages.append(HumanMessage(user_input))

    # Get response
    response = model.invoke(messages)

    # Add response to history
    messages.append(response)

    return response.content

# Example conversation
print(chat("Hello! My name is Alice."))
print(chat("What's my name?"))  # Will remember "Alice"
print(chat("What did I tell you first?"))  # Will recall the greeting
```

### Simple Chat Loop

A complete interactive chat application:

```python
import os
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, AIMessage, SystemMessage

# Ensure API key is set
if not os.environ.get("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

model = init_chat_model("claude-sonnet-4-5-20250929")

def run_chat():
    """Run an interactive chat session."""
    messages = [
        SystemMessage("You are a helpful, friendly assistant. Be concise in your responses.")
    ]

    print("Chat started. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ('quit', 'exit', 'bye'):
            print("Goodbye!")
            break

        if not user_input:
            continue

        # Add user message
        messages.append(HumanMessage(user_input))

        # Get response
        response = model.invoke(messages)

        # Add to history
        messages.append(response)

        print(f"Assistant: {response.content}\n")

if __name__ == "__main__":
    run_chat()
```

---

## Streaming Responses

### Basic Streaming

Stream tokens as they are generated:

```python
# Stream token by token
for chunk in model.stream("Why do parrots talk?"):
    print(chunk.content, end="", flush=True)
```

### Async Streaming with Events

For more control over streaming events:

```python
async for event in model.astream_events("Hello", version="v2"):
    if event["event"] == "on_chat_model_start":
        print(f"Input: {event['data']['input']}")

    elif event["event"] == "on_chat_model_stream":
        print(f"Token: {event['data']['chunk'].content}")

    elif event["event"] == "on_chat_model_end":
        print(f"Full message: {event['data']['output'].content}")
```

Example output:
```
Input: Hello
Token: Hi
Token:  there
Token: !
Token:  How
Token:  can
Token:  I
...
Full message: Hi there! How can I help today?
```

### Aggregating Streamed Chunks

Build the complete message from chunks:

```python
full = None
for chunk in model.stream("What color is the sky?"):
    full = chunk if full is None else full + chunk
    print(full.content)

# Output:
# The
# The sky
# The sky is
# The sky is typically
# The sky is typically blue
# ...

print(full.content_blocks)
```

### Batch Processing

Process multiple inputs efficiently:

```python
# Standard batch (waits for all to complete)
responses = model.batch([
    "Why do parrots have colorful feathers?",
    "How do airplanes fly?",
    "What is quantum computing?"
])

# Batch as completed (returns results as they finish with their index)
for idx, response in model.batch_as_completed([
    "Why do parrots have colorful feathers?",
    "How do airplanes fly?",
    "What is quantum computing?"
]):
    print(f"Response {idx}: {response.content}")
```

---

## Prompt Templates

### Basic Templates

Create reusable prompt templates with variable substitution:

```python
from langchain_core.prompts import PromptTemplate

# Simple template
template = PromptTemplate.from_template(
    "Translate the following text to {language}: {text}"
)

# Format the template
prompt = template.format(language="French", text="Hello, how are you?")
print(prompt)
# Output: Translate the following text to French: Hello, how are you?

# Use with a model
response = model.invoke(prompt)
```

### Chat Prompt Templates

For multi-message prompts:

```python
from langchain_core.prompts import ChatPromptTemplate

# Create a chat template
chat_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that translates {input_language} to {output_language}."),
    ("human", "{text}")
])

# Format and use
messages = chat_template.format_messages(
    input_language="English",
    output_language="French",
    text="I love programming."
)

response = model.invoke(messages)
```

### Dynamic Prompts

Build prompts with conditional logic:

```python
def build_system_prompt(user_role: str, context: dict) -> str:
    """Generate system prompt based on user role and context."""
    base_prompt = "You are a helpful assistant."

    if user_role == "expert":
        base_prompt += " Provide detailed technical responses."
    elif user_role == "beginner":
        base_prompt += " Explain concepts simply and avoid jargon."

    if context.get("is_production"):
        base_prompt += " Be extra careful with any data modifications."

    return base_prompt

# Use dynamically
system_prompt = build_system_prompt("expert", {"is_production": True})
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Explain machine learning"}
]
response = model.invoke(messages)
```

---

## Chains and Runnables (LCEL)

### What is LCEL

**LangChain Expression Language (LCEL)** is a declarative way to compose chains of operations. Every component in LangChain implements the **Runnable** interface, which provides:

- `invoke()`: Call the chain on a single input
- `batch()`: Call the chain on a list of inputs
- `stream()`: Stream back chunks of the response
- `ainvoke()`, `abatch()`, `astream()`: Async versions

### Creating Chains with Pipe Operator

Chain components together using the `|` (pipe) operator:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model

# Create components
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
model = init_chat_model("claude-sonnet-4-5-20250929")
output_parser = StrOutputParser()

# Chain them together
chain = prompt | model | output_parser

# Use the chain
result = chain.invoke({"topic": "programming"})
print(result)
```

#### Multi-Step Chains

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Step 1: Generate a topic
topic_prompt = ChatPromptTemplate.from_template(
    "Generate a random topic for a short story in one word:"
)

# Step 2: Write a story about that topic
story_prompt = ChatPromptTemplate.from_template(
    "Write a very short story (2-3 sentences) about: {topic}"
)

# Chain: generate topic -> write story
topic_chain = topic_prompt | model | StrOutputParser()

# Full chain with lambda to pass topic forward
full_chain = (
    topic_chain
    | (lambda topic: {"topic": topic})
    | story_prompt
    | model
    | StrOutputParser()
)

result = full_chain.invoke({})
print(result)
```

### The @chain Decorator

Create custom runnables using the `@chain` decorator:

```python
from typing import List
from langchain_core.documents import Document
from langchain_core.runnables import chain

@chain
def retriever(query: str) -> List[Document]:
    """Custom retriever that wraps a vector store search."""
    return vector_store.similarity_search(query, k=3)

# Use as a runnable
docs = retriever.invoke("What is machine learning?")

# Supports batch operations automatically
results = retriever.batch([
    "How many distribution centers does Nike have?",
    "When was Nike incorporated?",
])
```

### Runnable Configuration

Pass configuration options to any runnable:

```python
response = model.invoke(
    "Tell me a joke",
    config={
        "run_name": "joke_generation",
        "tags": ["humor", "demo"],
        "metadata": {"user_id": "123"},
        "callbacks": [my_callback_handler],
    }
)
```

#### RunnablePassthrough and RunnableLambda

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Pass input through unchanged
passthrough = RunnablePassthrough()

# Transform input with a function
def add_context(input_dict):
    input_dict["context"] = "Additional context here"
    return input_dict

transform = RunnableLambda(add_context)

# Use in a chain
chain = transform | prompt | model
```

---

## Structured Output

Get responses in a specific structured format.

### Using Pydantic Models

```python
from pydantic import BaseModel, Field

class Movie(BaseModel):
    """A movie with details."""
    title: str = Field(..., description="The title of the movie")
    year: int = Field(..., description="The year the movie was released")
    director: str = Field(..., description="The director of the movie")
    rating: float = Field(..., description="The movie's rating out of 10")

model_with_structure = model.with_structured_output(Movie)
response = model_with_structure.invoke("Provide details about the movie Inception")
print(response)
# Movie(title="Inception", year=2010, director="Christopher Nolan", rating=8.8)
```

### Using TypedDict

```python
from typing_extensions import TypedDict, Annotated

class MovieDict(TypedDict):
    """A movie with details."""
    title: Annotated[str, ..., "The title of the movie"]
    year: Annotated[int, ..., "The year the movie was released"]
    director: Annotated[str, ..., "The director of the movie"]
    rating: Annotated[float, ..., "The movie's rating out of 10"]

model_with_structure = model.with_structured_output(MovieDict)
response = model_with_structure.invoke("Provide details about the movie Inception")
print(response)
# {'title': 'Inception', 'year': 2010, 'director': 'Christopher Nolan', 'rating': 8.8}
```

### Using JSON Schema

```python
json_schema = {
    "title": "Movie",
    "description": "A movie with details",
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "The title of the movie"
        },
        "year": {
            "type": "integer",
            "description": "The year the movie was released"
        },
        "director": {
            "type": "string",
            "description": "The director of the movie"
        },
        "rating": {
            "type": "number",
            "description": "The movie's rating out of 10"
        }
    },
    "required": ["title", "year", "director", "rating"]
}

model_with_structure = model.with_structured_output(
    json_schema,
    method="json_schema"
)
response = model_with_structure.invoke("Provide details about the movie Inception")
print(response)
# {'title': 'Inception', 'year': 2010, ...}
```

### Include Raw Response

Get both the parsed structure and the raw AI message:

```python
model_with_structure = model.with_structured_output(Movie, include_raw=True)
response = model_with_structure.invoke("Provide details about the movie Inception")
print(response)
# {
#     "raw": AIMessage(...),
#     "parsed": Movie(title=..., year=..., ...),
#     "parsing_error": None,
# }
```

---

## Tool Integration

### Defining Tools

Use the `@tool` decorator to create tools:

```python
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get the weather at a location.

    Args:
        location: The city and state, e.g. "San Francisco, CA"
    """
    # In a real app, call a weather API
    return f"It's sunny and 72F in {location}."

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers.

    Args:
        a: First integer
        b: Second integer
    """
    return a * b
```

### Tools with Pydantic Models

Define tools using Pydantic for more control:

```python
from pydantic import BaseModel, Field

class GetWeather(BaseModel):
    """Get the current weather in a given location"""
    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

class GetPopulation(BaseModel):
    """Get the current population in a given location"""
    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
```

### Binding Tools to Models

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("claude-sonnet-4-5-20250929")
model_with_tools = model.bind_tools([get_weather, multiply])

# Or with Pydantic models
model_with_tools = model.bind_tools([GetWeather, GetPopulation])

# Invoke and check for tool calls
response = model_with_tools.invoke("What's the weather in Boston?")

for tool_call in response.tool_calls:
    print(f"Tool: {tool_call['name']}")
    print(f"Args: {tool_call['args']}")
```

### Streaming Tool Calls

See tool calls as they're being generated:

```python
for chunk in model_with_tools.stream("What's the weather in Boston and Tokyo?"):
    for tool_chunk in chunk.tool_call_chunks:
        if name := tool_chunk.get("name"):
            print(f"Tool: {name}")
        if args := tool_chunk.get("args"):
            print(f"Args: {args}")
```

#### Accumulating Tool Call Chunks

```python
gathered = None
for chunk in model_with_tools.stream("What's the weather in Boston?"):
    gathered = chunk if gathered is None else gathered + chunk

print(gathered.tool_calls)
# [{'name': 'get_weather', 'args': {'location': 'Boston, MA'}, 'id': 'call_xxx'}]
```

---

## Complete Examples

### Translation Chain

```python
import os
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Ensure API key is set
if not os.environ.get("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

# Initialize model
model = init_chat_model("claude-sonnet-4-5-20250929")

# Create translation chain
translation_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a professional translator. Translate the following text from {source_lang} to {target_lang}. Only output the translation, nothing else."),
    ("human", "{text}")
])

translation_chain = translation_prompt | model | StrOutputParser()

# Use the chain
result = translation_chain.invoke({
    "source_lang": "English",
    "target_lang": "Spanish",
    "text": "Hello, how are you today?"
})
print(result)  # "Hola, como estas hoy?"

# Batch translation
translations = translation_chain.batch([
    {"source_lang": "English", "target_lang": "French", "text": "Good morning"},
    {"source_lang": "English", "target_lang": "German", "text": "Good night"},
])
print(translations)
```

### Streaming Chat with Memory

```python
import os
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, AIMessage, SystemMessage

if not os.environ.get("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

model = init_chat_model("claude-sonnet-4-5-20250929")

def run_streaming_chat():
    """Run an interactive chat with streaming responses."""
    messages = [
        SystemMessage("You are a helpful, friendly assistant.")
    ]

    print("Chat started (with streaming). Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ('quit', 'exit'):
            print("Goodbye!")
            break

        if not user_input:
            continue

        messages.append(HumanMessage(user_input))

        # Stream the response
        print("Assistant: ", end="", flush=True)

        full_response = None
        for chunk in model.stream(messages):
            print(chunk.content, end="", flush=True)
            full_response = chunk if full_response is None else full_response + chunk

        print("\n")

        # Add complete response to history
        messages.append(full_response)

if __name__ == "__main__":
    run_streaming_chat()
```

### Data Extraction with Structured Output

```python
import os
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain.chat_models import init_chat_model

if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Define the structure
class ContactInfo(BaseModel):
    """Extracted contact information."""
    name: str = Field(description="Full name of the person")
    email: Optional[str] = Field(description="Email address if found")
    phone: Optional[str] = Field(description="Phone number if found")
    company: Optional[str] = Field(description="Company name if found")

class ExtractedContacts(BaseModel):
    """List of extracted contacts."""
    contacts: List[ContactInfo] = Field(description="All contacts found in the text")

# Initialize model with structure
model = init_chat_model("gpt-4.1")
extractor = model.with_structured_output(ExtractedContacts)

# Extract from unstructured text
text = """
Meeting notes from yesterday:
- John Smith (john.smith@acme.com, 555-1234) from Acme Corp will handle the backend.
- Contact Sarah Johnson at TechStart for the frontend. Her email is sarah@techstart.io
- Bob Williams mentioned his new number is 555-5678
"""

result = extractor.invoke(f"Extract all contact information from this text:\n\n{text}")

for contact in result.contacts:
    print(f"Name: {contact.name}")
    print(f"  Email: {contact.email}")
    print(f"  Phone: {contact.phone}")
    print(f"  Company: {contact.company}")
    print()
```

---

## Best Practices

### 1. Environment Configuration

```python
import os

# Never hardcode API keys
# Use environment variables or secure configuration management

# Raise exceptions for missing configuration (never use fallbacks)
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")
```

### 2. Error Handling

```python
from langchain.chat_models import init_chat_model

def safe_invoke(prompt: str, max_retries: int = 3) -> str:
    """Invoke model with error handling."""
    model = init_chat_model(
        "claude-sonnet-4-5-20250929",
        max_retries=max_retries,
        timeout=30
    )

    try:
        response = model.invoke(prompt)
        return response.content
    except Exception as e:
        raise RuntimeError(f"Failed to communicate with LLM: {e}")
```

### 3. Token Management

For long conversations, implement message trimming:

```python
# Import path may vary by LangChain version
# Try the primary import first, fall back to alternative if needed
try:
    from langchain_core.messages.utils import trim_messages, count_tokens_approximately
except ImportError:
    from langchain_core.messages import trim_messages
    # Define a simple approximate counter if not available
    def count_tokens_approximately(messages):
        return sum(len(str(m.content).split()) for m in messages)

def get_trimmed_messages(messages: list, max_tokens: int = 4000) -> list:
    """Trim messages to fit within token limit."""
    return trim_messages(
        messages,
        strategy="last",  # Keep most recent messages
        token_counter=count_tokens_approximately,
        max_tokens=max_tokens,
        start_on="human",  # Always start with a human message
    )
```

> **Version Compatibility:** The import path for `trim_messages` may vary between LangChain versions. The example above includes a fallback pattern for compatibility.

### 4. Reusable Chain Patterns

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model

def create_summarization_chain(model_name: str = "claude-sonnet-4-5-20250929"):
    """Create a reusable summarization chain."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a skilled summarizer. Summarize the following text in {style} style."),
        ("human", "{text}")
    ])

    model = init_chat_model(model_name)

    return prompt | model | StrOutputParser()

# Use it
summarizer = create_summarization_chain()
summary = summarizer.invoke({
    "style": "bullet points",
    "text": "Long article text here..."
})
```

### 5. Logging and Debugging

For OpenAI models, you can track token usage and costs:

```python
from langchain.callbacks import get_openai_callback

# Track token usage (OpenAI direct API only)
with get_openai_callback() as cb:
    response = model.invoke("Tell me a joke")
    print(f"Tokens used: {cb.total_tokens}")
    print(f"Cost: ${cb.total_cost:.4f}")
```

> **Note for Azure OpenAI users:** The `get_openai_callback()` is designed for direct OpenAI API usage. For Azure OpenAI, token usage is available in the response metadata:
> ```python
> response = model.invoke("Tell me a joke")
> print(f"Token usage: {response.response_metadata.get('token_usage', {})}")
> ```

---

## Summary

This guide covered the essential LangChain capabilities:

| Feature | Description |
|---------|-------------|
| `init_chat_model()` | Unified model initialization for any provider |
| Message Types | `SystemMessage`, `HumanMessage`, `AIMessage` for conversations |
| `invoke()`, `stream()`, `batch()` | Core methods for model interaction |
| Prompt Templates | Reusable templates with variable substitution |
| LCEL (Pipe Operator) | Chain components with `\|` for complex workflows |
| `@chain` decorator | Create custom runnables |
| `with_structured_output()` | Get responses in Pydantic/TypedDict/JSON format |
| `@tool` decorator | Define tools for model function calling |
| `bind_tools()` | Attach tools to models |

For more advanced stateful agents and workflows, see the LangGraph documentation.
