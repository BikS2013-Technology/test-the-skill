"""
Test 03: Example 1 - Simple Q&A Agent

This is the document's Example 1 adapted for Azure OpenAI.

Original document code (lines 442-474):
```python
import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_tavily import TavilySearch

# Setup
os.environ["ANTHROPIC_API_KEY"] = "your-key"
os.environ["TAVILY_API_KEY"] = "your-key"

# Initialize
model = init_chat_model("claude-sonnet-4-5-20250929")
search_tool = TavilySearch(max_results=3)

# Create agent
agent = create_agent(
    model=model,
    tools=[search_tool],
    system_prompt="You are a helpful assistant that searches the web to answer questions accurately."
)

# Ask questions
def ask(question: str) -> str:
    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })
    return result["messages"][-1].content

# Usage
print(ask("What is the current population of Japan?"))
print(ask("Who is the CEO of OpenAI?"))
print(ask("What are the latest developments in fusion energy?"))
```

Adapted for Azure OpenAI below:
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify environment variables
required_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT",
    "TAVILY_API_KEY"
]

for var in required_vars:
    if not os.environ.get(var):
        raise ValueError(f"{var} environment variable is not set")

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_tavily import TavilySearch

# Initialize model using Azure OpenAI
# NOTE: The document uses init_chat_model("claude-sonnet-4-5-20250929")
# For Azure, we use init_chat_model with model_provider="azure_openai"
model = init_chat_model(
    os.environ["AZURE_OPENAI_DEPLOYMENT"],
    model_provider="azure_openai"
)

search_tool = TavilySearch(max_results=3)

# Create agent
agent = create_agent(
    model=model,
    tools=[search_tool],
    system_prompt="You are a helpful assistant that searches the web to answer questions accurately."
)

# Ask questions
def ask(question: str) -> str:
    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })
    return result["messages"][-1].content

# Usage - Test with a few questions
print("="*60)
print("Example 1: Simple Q&A Agent")
print("="*60)

questions = [
    "What is the current population of Japan?",
    "Who is the CEO of OpenAI?",
]

for q in questions:
    print(f"\nQuestion: {q}")
    print("-"*40)
    answer = ask(q)
    print(f"Answer: {answer}")
    print("="*60)
