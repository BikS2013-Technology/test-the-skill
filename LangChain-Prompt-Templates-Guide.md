# LangChain Prompt Templates Guide

**Date:** December 22, 2025

This guide explains what prompt templates are in LangChain/LangGraph and how to use them effectively in chat applications.

---

## Table of Contents

1. [What Are Prompt Templates?](#what-are-prompt-templates)
2. [Message Types](#message-types)
3. [Basic Prompt Approaches](#basic-prompt-approaches)
4. [ChatPromptTemplate](#chatprompttemplate)
5. [Variables and Placeholders](#variables-and-placeholders)
6. [MessagesPlaceholder](#messagesplaceholder)
7. [Dynamic Prompts with Middleware](#dynamic-prompts-with-middleware)
8. [Integration with LangGraph Agents](#integration-with-langgraph-agents)
9. [Prompt Management with LangSmith](#prompt-management-with-langsmith)
10. [Complete Examples](#complete-examples)
11. [Best Practices](#best-practices)

---

## What Are Prompt Templates?

Prompt templates are **reusable structures** for formatting inputs to language models. They allow you to:

- **Parameterize prompts**: Insert dynamic values into fixed structures
- **Maintain consistency**: Ensure uniform prompt formatting across your application
- **Separate concerns**: Keep prompt logic separate from business logic
- **Enable reusability**: Share and version prompts across projects

### Key Benefits

| Benefit | Description |
|---------|-------------|
| **Reusability** | Define once, use with different inputs |
| **Maintainability** | Update prompts in one place |
| **Type Safety** | Structured message objects prevent formatting errors |
| **Versioning** | Track and manage prompt versions with LangSmith |
| **Dynamic Content** | Insert context, user data, or retrieved information |

---

## Message Types

LangChain provides structured message types for building conversations:

### Core Message Classes

```python
from langchain.messages import (
    SystemMessage,    # Instructions for the AI
    HumanMessage,     # User input
    AIMessage,        # AI responses
    ToolMessage       # Tool/function results
)
```

### SystemMessage

Sets the behavior, persona, or instructions for the AI:

```python
from langchain.messages import SystemMessage

system_msg = SystemMessage("You are a helpful assistant that translates English to French.")
```

### HumanMessage

Represents user input:

```python
from langchain.messages import HumanMessage

human_msg = HumanMessage("Translate: I love programming.")
```

### AIMessage

Represents AI responses (useful for conversation history):

```python
from langchain.messages import AIMessage

ai_msg = AIMessage("J'adore la programmation.")
```

### Using Messages Together

```python
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AIMessage

model = init_chat_model("claude-sonnet-4-5-20250929")

# Build conversation with message objects
messages = [
    SystemMessage("You are a helpful assistant."),
    HumanMessage("Hello, how are you?")
]

response = model.invoke(messages)  # Returns AIMessage
print(response.content)
```

---

## Basic Prompt Approaches

### 1. Simple Text Prompt

For straightforward, single-turn interactions:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# Direct text prompt
response = model.invoke("Write a haiku about spring")
print(response.content)
```

### 2. Dictionary Format (OpenAI-style)

Compatible with OpenAI's chat completions format:

```python
messages = [
    {"role": "system", "content": "You are a poetry expert"},
    {"role": "user", "content": "Write a haiku about spring"},
    {"role": "assistant", "content": "Cherry blossoms bloom..."}
]

response = model.invoke(messages)
```

### 3. Message Objects

More structured and type-safe:

```python
from langchain.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage("You are a poetry expert"),
    HumanMessage("Write a haiku about spring"),
    AIMessage("Cherry blossoms bloom...")  # Previous response
]

response = model.invoke(messages)
```

---

## ChatPromptTemplate

`ChatPromptTemplate` is the primary class for creating reusable prompt templates with variables.

### Basic Usage

```python
from langchain_core.prompts import ChatPromptTemplate

# Create template with variables
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful chatbot."),
    ("user", "{question}")
])

# Format with variables
formatted = prompt.invoke({"question": "What is Python?"})

# Use with model
model = init_chat_model("gpt-4.1")
response = model.invoke(formatted)
```

### Template Syntax

Variables are enclosed in curly braces `{variable_name}`:

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} that speaks {language}."),
    ("user", "Tell me about {topic}")
])

# Invoke with all variables
formatted = prompt.invoke({
    "role": "teacher",
    "language": "formally",
    "topic": "quantum physics"
})
```

### Chaining with Models

Use the pipe operator `|` to chain prompts with models:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful chatbot"),
    ("human", "Tell me a joke about {topic}")
])

model = init_chat_model("gpt-4.1")

# Create a chain
chain = prompt | model

# Invoke the chain
response = chain.invoke({"topic": "bears"})
print(response.content)
```

### Partial Templates

Pre-fill some variables while leaving others for later:

```python
from langchain_core.prompts import ChatPromptTemplate

# Base template with multiple variables
base_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {dialect} SQL expert. Limit results to {top_k}."),
    ("user", "{query}")
])

# Partial application - fill dialect and top_k
sql_prompt = base_prompt.partial(
    dialect="PostgreSQL",
    top_k="10"
)

# Now only needs 'query'
formatted = sql_prompt.invoke({"query": "Show all users"})
```

---

## Variables and Placeholders

### Simple Variables

Insert single values:

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You translate {source_lang} to {target_lang}."),
    ("user", "Translate: {text}")
])

result = prompt.invoke({
    "source_lang": "English",
    "target_lang": "French",
    "text": "Hello, world!"
})
```

### Multi-line System Prompts

For complex instructions:

```python
system_prompt = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer.

Rules:
- Always limit your query to at most {top_k} results
- Never query for all columns from a specific table
- Only ask for relevant columns given the question
- DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.)
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{question}")
])
```

---

## MessagesPlaceholder

`MessagesPlaceholder` allows inserting a dynamic list of messages at a specific position in the template.

### Basic MessagesPlaceholder

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.messages import HumanMessage

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    MessagesPlaceholder("conversation_history"),
    ("user", "{current_question}")
])

# Invoke with message history
formatted = prompt.invoke({
    "conversation_history": [
        HumanMessage("What is Python?"),
        AIMessage("Python is a programming language...")
    ],
    "current_question": "Can you give me an example?"
})
```

### Alternative Placeholder Syntax

Use tuple syntax for simpler cases:

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("placeholder", "{messages}"),  # Alternative syntax
])

formatted = prompt.invoke({
    "messages": [HumanMessage("Hello!")]
})
```

### Use Case: Chat with History

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.messages import HumanMessage, AIMessage
from langchain.chat_models import init_chat_model

# Template with history placeholder
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly assistant. Be concise."),
    MessagesPlaceholder("history"),
    ("user", "{input}")
])

model = init_chat_model("claude-sonnet-4-5-20250929")
chain = prompt | model

# Maintain conversation history
history = []

def chat(user_input: str) -> str:
    response = chain.invoke({
        "history": history,
        "input": user_input
    })

    # Update history
    history.append(HumanMessage(user_input))
    history.append(response)

    return response.content

# Usage
print(chat("My name is Alice"))
print(chat("What's my name?"))  # Will remember "Alice"
```

---

## Dynamic Prompts with Middleware

For advanced use cases where prompts need to change based on runtime context, state, or user preferences.

### The @dynamic_prompt Decorator

```python
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def user_role_prompt(request: ModelRequest) -> str:
    """Generate system prompt based on user role."""
    user_role = request.runtime.context.get("user_role", "user")
    base_prompt = "You are a helpful assistant."

    if user_role == "expert":
        return f"{base_prompt} Provide detailed technical responses."
    elif user_role == "beginner":
        return f"{base_prompt} Explain concepts simply and avoid jargon."

    return base_prompt

# Use as middleware
agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[user_role_prompt],
    context_schema=Context
)
```

### State-Aware Prompts

Adjust prompts based on conversation length:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def state_aware_prompt(request: ModelRequest) -> str:
    message_count = len(request.messages)

    base = "You are a helpful assistant."

    if message_count > 10:
        base += "\nThis is a long conversation - be extra concise."

    return base

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[state_aware_prompt]
)
```

### Context-Aware Prompts

Use runtime context for personalization:

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dataclass
class Context:
    user_role: str
    deployment_env: str

@dynamic_prompt
def context_aware_prompt(request: ModelRequest) -> str:
    user_role = request.runtime.context.user_role
    env = request.runtime.context.deployment_env

    base = "You are a helpful assistant."

    if user_role == "admin":
        base += "\nYou have admin access. You can perform all operations."
    elif user_role == "viewer":
        base += "\nYou have read-only access. Guide users to read operations only."

    if env == "production":
        base += "\nBe extra careful with any data modifications."

    return base

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[context_aware_prompt],
    context_schema=Context
)
```

### Store-Aware Prompts

Retrieve user preferences from storage:

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

@dynamic_prompt
def store_aware_prompt(request: ModelRequest) -> str:
    user_id = request.runtime.context.user_id

    # Read from Store
    store = request.runtime.store
    user_prefs = store.get(("preferences",), user_id)

    base = "You are a helpful assistant."

    if user_prefs:
        style = user_prefs.value.get("communication_style", "balanced")
        base += f"\nUser prefers {style} responses."

    return base

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[store_aware_prompt],
    context_schema=Context,
    store=InMemoryStore()
)
```

### RAG Context Injection

Inject retrieved documents into prompts:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def prompt_with_context(request: ModelRequest) -> str:
    """Inject retrieved context into system message."""
    last_query = request.state["messages"][-1].text

    # Retrieve relevant documents
    retrieved_docs = vector_store.similarity_search(last_query)
    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

    system_message = (
        "You are a helpful assistant. Use the following context in your response:"
        f"\n\n{docs_content}"
    )

    return system_message

agent = create_agent(model, tools=[], middleware=[prompt_with_context])
```

---

## Integration with LangGraph Agents

### Static Prompts with create_react_agent

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[get_weather],
    # Static prompt - never changes
    prompt="Never answer questions about the weather."
)

agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)
```

### System Prompts in Graph Nodes

```python
from langgraph.graph import MessagesState
from langchain.messages import SystemMessage

def llm_call(state: MessagesState):
    """LLM node with system prompt."""
    system_prompt = SystemMessage(
        "You are a helpful assistant tasked with performing arithmetic."
    )

    return {
        "messages": [
            llm_with_tools.invoke([system_prompt] + state["messages"])
        ]
    }
```

### Multi-Agent System Prompts

```python
def make_system_prompt(suffix: str) -> str:
    """Generate prompts for multi-agent collaboration."""
    return (
        "You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards answering the question."
        " If you are unable to fully answer, that's OK, another assistant with different tools "
        " will help where you left off. Execute what you can to make progress."
        " If you or any of the other assistants have the final answer or deliverable,"
        " prefix your response with FINAL ANSWER so the team knows to stop."
        f"\n{suffix}"
    )

# Create specialized agent prompts
research_prompt = make_system_prompt("You specialize in web research and data gathering.")
analysis_prompt = make_system_prompt("You specialize in data analysis and visualization.")
```

### ChatPromptTemplate in LangGraph

```python
from langchain_core.prompts import ChatPromptTemplate

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "Respond directly by calling the Respond function."),
    ("placeholder", "{messages}"),
])

# Use in a chain
chain = prompt | bound_llm

# Invoke with messages
results = chain.invoke({
    "messages": [
        ("user", "Extract the summary from the following conversation...")
    ]
})
```

---

## Prompt Management with LangSmith

### Push Prompts to LangSmith

```python
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate

client = Client()

# Create prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful chatbot."),
    ("user", "{question}")
])

# Push for versioning
client.push_prompt("my-prompt-name", object=prompt)
```

### Pull Prompts from LangSmith

```python
from langchain import hub
from langchain.chat_models import init_chat_model

# Pull versioned prompt
prompt = hub.pull("my-org/joke-generator")

# Use in chain
model = init_chat_model("gpt-4o-mini")
chain = prompt | model
response = chain.invoke({"topic": "cats"})
```

---

## Complete Examples

### Example 1: Translation Chatbot

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, AIMessage

# Define the prompt template
translation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a professional translator.
Translate all user messages from {source_lang} to {target_lang}.
Maintain the tone and style of the original text.
Only provide the translation, no explanations."""),
    MessagesPlaceholder("history"),
    ("user", "{text}")
])

# Create the chain
model = init_chat_model("claude-sonnet-4-5-20250929")
chain = translation_prompt | model

# Translation function with history
class TranslationChat:
    def __init__(self, source_lang: str, target_lang: str):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.history = []

    def translate(self, text: str) -> str:
        response = chain.invoke({
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "history": self.history,
            "text": text
        })

        # Update history
        self.history.append(HumanMessage(text))
        self.history.append(response)

        return response.content

# Usage
translator = TranslationChat("English", "French")
print(translator.translate("Hello, how are you?"))
print(translator.translate("I'm learning French."))
```

### Example 2: Customer Support Agent

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.tools import tool

@dataclass
class CustomerContext:
    customer_id: str
    subscription_tier: str
    account_age_days: int

@tool
def lookup_order(order_id: str) -> str:
    """Look up order status by order ID."""
    return f"Order {order_id}: Shipped, arriving in 2 days"

@tool
def check_account(customer_id: str) -> str:
    """Check customer account details."""
    return f"Customer {customer_id}: Active account, premium tier"

@dynamic_prompt
def support_prompt(request: ModelRequest) -> str:
    ctx = request.runtime.context

    base = """You are a friendly customer support agent for TechCo.
Your goal is to help customers with their inquiries efficiently and professionally."""

    # Adjust based on subscription tier
    if ctx.subscription_tier == "premium":
        base += "\nThis is a PREMIUM customer. Prioritize their satisfaction."
    elif ctx.subscription_tier == "enterprise":
        base += "\nThis is an ENTERPRISE customer. Offer dedicated support options."

    # Adjust based on account age
    if ctx.account_age_days < 30:
        base += "\nThis is a new customer. Be extra welcoming and helpful."
    elif ctx.account_age_days > 365:
        base += "\nThis is a loyal customer. Thank them for their continued business."

    base += "\n\nAlways be polite, concise, and solution-oriented."

    return base

# Create the support agent
support_agent = create_agent(
    model="gpt-4o",
    tools=[lookup_order, check_account],
    middleware=[support_prompt],
    context_schema=CustomerContext
)

# Usage
result = support_agent.invoke(
    {"messages": [{"role": "user", "content": "Where is my order #12345?"}]},
    context=CustomerContext(
        customer_id="C001",
        subscription_tier="premium",
        account_age_days=450
    )
)
```

### Example 3: SQL Query Assistant

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

# SQL-specific prompt template
sql_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer.

Rules:
- Always limit your query to at most {top_k} results
- Order results by a relevant column to return the most interesting examples
- Never query for all columns from a specific table
- Only ask for the relevant columns given the question
- DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.)

Database Schema:
{schema}"""),
    ("user", "{question}")
])

# Partial application for specific database
postgres_prompt = sql_prompt.partial(
    dialect="PostgreSQL",
    top_k="10",
    schema="""
    - users (id, name, email, created_at)
    - orders (id, user_id, total, status, created_at)
    - products (id, name, price, category)
    """
)

# Create chain
model = init_chat_model("gpt-4o")
sql_chain = postgres_prompt | model

# Query
response = sql_chain.invoke({
    "question": "Show me the top 5 customers by total order value"
})
print(response.content)
```

---

## Best Practices

### 1. Keep Prompts Focused

```python
# Good: Single, clear purpose
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a translator. Translate text from English to French."),
    ("user", "{text}")
])

# Avoid: Too many responsibilities
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a translator, editor, summarizer, and analyst.
Translate, then edit, then summarize, then analyze the following..."""),
    ("user", "{text}")
])
```

### 2. Use Type-Safe Message Objects

```python
# Preferred: Message objects
from langchain.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage("You are helpful."),
    HumanMessage("Hello!")
]

# Acceptable but less type-safe: Dictionary format
messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"}
]
```

### 3. Validate Required Variables

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "Translate {source} to {target}"),
    ("user", "{text}")
])

# Check required variables
print(prompt.input_variables)  # ['source', 'target', 'text']

# Validate before invoking
def safe_invoke(prompt, variables: dict):
    missing = set(prompt.input_variables) - set(variables.keys())
    if missing:
        raise ValueError(f"Missing required variables: {missing}")
    return prompt.invoke(variables)
```

### 4. Version Prompts for Production

```python
from langsmith import Client

client = Client()

# Version your prompts
client.push_prompt("translation-v1", object=prompt)

# Pull specific versions in production
prompt = hub.pull("my-org/translation-v1")
```

### 5. Use Dynamic Prompts for Personalization

```python
# Instead of hardcoding user preferences
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a formal assistant.")  # Hardcoded!
])

# Use dynamic prompts
@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    user_prefs = get_user_preferences(request.runtime.context.user_id)
    style = user_prefs.get("communication_style", "balanced")
    return f"You are a {style} assistant."
```

### 6. Keep Context Windows in Mind

```python
from langchain_core.messages.utils import trim_messages, count_tokens_approximately

# Trim messages before adding to prompt
def prepare_history(messages, max_tokens=2000):
    return trim_messages(
        messages,
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=max_tokens,
        start_on="human"
    )
```

---

## Summary

| Component | Purpose | When to Use |
|-----------|---------|-------------|
| `SystemMessage` | AI instructions | Always, to set behavior |
| `HumanMessage` | User input | Every user turn |
| `AIMessage` | AI responses | Conversation history |
| `ChatPromptTemplate` | Reusable templates | Parameterized prompts |
| `MessagesPlaceholder` | Dynamic message lists | Chat history insertion |
| `@dynamic_prompt` | Runtime customization | Personalization, context-aware |
| `prompt.partial()` | Pre-fill variables | Shared configurations |
| LangSmith Hub | Version management | Production deployments |

### Quick Reference

```python
# Basic template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are {role}."),
    ("user", "{input}")
])

# With history
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are helpful."),
    MessagesPlaceholder("history"),
    ("user", "{input}")
])

# Chain with model
chain = prompt | model
response = chain.invoke({"role": "assistant", "input": "Hello"})

# Dynamic prompt
@dynamic_prompt
def my_prompt(request: ModelRequest) -> str:
    return f"You are helping {request.runtime.context.user_name}"
```
