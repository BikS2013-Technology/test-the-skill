"""
Test 02: Basic Agent Creation with Azure OpenAI

This script tests basic agent creation using Azure OpenAI instead of
direct OpenAI/Anthropic as shown in the document.

ISSUE #1: The document uses init_chat_model() which doesn't directly support Azure OpenAI.
We need to use AzureChatOpenAI from langchain_openai.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify Azure OpenAI environment variables
required_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT"
]

for var in required_vars:
    value = os.environ.get(var)
    if not value:
        raise ValueError(f"{var} environment variable is not set")
    print(f"{var} is set (length: {len(value)})")

print("\n" + "="*60)
print("Testing Document Approach: init_chat_model()")
print("="*60)

# Test the document's approach first (this may fail for Azure)
try:
    from langchain.chat_models import init_chat_model

    # Document uses this syntax:
    # model = init_chat_model("claude-sonnet-4-5-20250929")

    # For Azure, try using azure deployment name
    azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    model = init_chat_model(
        azure_deployment,
        model_provider="azure_openai"
    )
    print(f"init_chat_model succeeded: {type(model)}")
except Exception as e:
    print(f"init_chat_model failed: {e}")

print("\n" + "="*60)
print("Testing Correct Azure Approach: AzureChatOpenAI()")
print("="*60)

# The correct way to use Azure OpenAI
from langchain_openai import AzureChatOpenAI

model = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

print(f"AzureChatOpenAI created: {type(model)}")

# Test simple invoke
print("\nTesting simple invoke...")
response = model.invoke("Say hello in one word")
print(f"Response: {response.content}")

print("\n" + "="*60)
print("Testing Agent Creation with create_agent()")
print("="*60)

# Test agent creation as shown in document
try:
    from langchain.agents import create_agent
    from langchain_tavily import TavilySearch

    search_tool = TavilySearch(max_results=3)

    agent = create_agent(
        model=model,
        tools=[search_tool]
    )
    print(f"create_agent succeeded: {type(agent)}")

    # Test basic invocation
    print("\nTesting agent invocation...")
    result = agent.invoke({
        "messages": [{"role": "user", "content": "What is 2 + 2?"}]
    })
    print(f"Result: {result['messages'][-1].content}")

except ImportError as e:
    print(f"ISSUE #2: create_agent import failed: {e}")
    print("The document references 'from langchain.agents import create_agent' which may not exist.")
except Exception as e:
    print(f"Agent creation/invocation failed: {e}")
