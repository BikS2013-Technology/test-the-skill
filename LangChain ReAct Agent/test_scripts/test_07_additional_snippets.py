"""
Test 07: Additional Code Snippets from the Document

Testing various smaller code examples from the document.
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
model = init_chat_model(
    os.environ["AZURE_OPENAI_DEPLOYMENT"],
    model_provider="azure_openai"
)

search_tool = TavilySearch(max_results=3)

print("="*60)
print("Testing Additional Document Snippets")
print("="*60)

# Test 1: Basic Invocation with Message Objects (lines 227-235)
print("\n--- Test 1: Message Objects ---")
try:
    from langchain.messages import HumanMessage

    agent = create_agent(model=model, tools=[search_tool])

    result = agent.invoke({
        "messages": [HumanMessage(content="What is 10 * 5?")]
    })

    print(f"Result: {result['messages'][-1].content}")
    print("SUCCESS: HumanMessage import from langchain.messages works")
except ImportError as e:
    print(f"ISSUE: langchain.messages import failed: {e}")
    print("Checking alternative import locations...")
    try:
        from langchain_core.messages import HumanMessage
        print("Alternative: from langchain_core.messages import HumanMessage")
    except ImportError:
        print("No alternative found")

# Test 2: Accessing Full Conversation (lines 239-252)
print("\n--- Test 2: Full Conversation Access ---")
agent = create_agent(model=model, tools=[search_tool])

result = agent.invoke({
    "messages": [{"role": "user", "content": "What is Python?"}]
})

# Print all messages in the conversation
print("Conversation messages:")
for i, message in enumerate(result["messages"]):
    msg_type = getattr(message, 'type', type(message).__name__)
    content_preview = str(message.content)[:100] if message.content else "(no content)"
    print(f"  {i+1}. {msg_type}: {content_preview}...")

    # Check for tool calls
    if hasattr(message, 'tool_calls') and message.tool_calls:
        for tc in message.tool_calls:
            print(f"     Tool: {tc['name']}, Args: {tc['args']}")

# Test 3: TavilySearchResults alternative (lines 156-161)
print("\n--- Test 3: TavilySearchResults Alternative ---")
try:
    from langchain_community.tools.tavily_search import TavilySearchResults

    # Returns a list of result dictionaries
    search_tool_alt = TavilySearchResults(max_results=3)
    result = search_tool_alt.invoke("What is AI?")
    print(f"TavilySearchResults result type: {type(result)}")
    print(f"TavilySearchResults works: {len(result) > 0}")
except ImportError as e:
    print(f"ISSUE #6: TavilySearchResults import failed: {e}")
    print("The document mentions 'from langchain_community.tools.tavily_search import TavilySearchResults'")
    print("This may require: uv add langchain-community")

# Test 4: Custom tool with args_schema (lines 359-373)
print("\n--- Test 4: Custom Tool with Pydantic Schema ---")
from pydantic import BaseModel, Field
from langchain.tools import tool

class SearchQuery(BaseModel):
    """Search query parameters."""
    query: str = Field(description="The search query")
    num_results: int = Field(default=3, description="Number of results to return")

@tool(args_schema=SearchQuery)
def advanced_search(query: str, num_results: int = 3) -> str:
    """Perform an advanced web search with configurable results."""
    search = TavilySearch(max_results=num_results)
    return str(search.invoke(query))

# Test the custom tool
print(f"Custom tool created: {advanced_search.name}")
print(f"Tool schema: {advanced_search.args_schema}")

# Create agent with custom tool
agent_custom = create_agent(model=model, tools=[advanced_search])
result = agent_custom.invoke({
    "messages": [{"role": "user", "content": "Search for 'machine learning' with 2 results"}]
})
print(f"Custom tool agent result: {result['messages'][-1].content[:200]}...")

# Test 5: Safe ask error handling (lines 678-688)
print("\n--- Test 5: Error Handling Pattern ---")

def safe_ask(agent, question: str) -> str:
    """Safely invoke agent with error handling."""
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": question}]
        })
        return result["messages"][-1].content
    except Exception as e:
        return f"Error occurred: {str(e)}"

# Test with a valid question
answer = safe_ask(agent, "What is 2+2?")
print(f"Safe ask result: {answer[:100]}...")

print("\n" + "="*60)
print("Additional Snippets Testing Complete")
print("="*60)
