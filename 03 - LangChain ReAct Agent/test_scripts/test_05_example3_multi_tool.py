"""
Test 05: Example 3 - Multi-Tool Research Agent

This is the document's Example 3 adapted for Azure OpenAI.

Original document code (lines 535-620):
Multi-tool agent with search, URL fetching, and date tools.

ISSUE #4 DETECTED: Same issue as Example 2 - the research() function
streams AND THEN invokes separately, causing double processing.
"""
import os
import requests
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
from langchain.tools import tool
from langchain_tavily import TavilySearch

# Define custom tools (as in document)
@tool
def fetch_webpage(url: str) -> str:
    """Fetch and return the text content of a webpage.

    Args:
        url: The URL of the webpage to fetch
    """
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/1.0)'
        })
        response.raise_for_status()
        # Return first 5000 chars to avoid token limits
        return response.text[:5000]
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"

@tool
def get_current_date() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Initialize model using Azure OpenAI
model = init_chat_model(
    os.environ["AZURE_OPENAI_DEPLOYMENT"],
    model_provider="azure_openai"
)

search_tool = TavilySearch(max_results=5)

# Create multi-tool agent
agent = create_agent(
    model=model,
    tools=[search_tool, fetch_webpage, get_current_date],
    system_prompt="""You are an advanced research assistant with multiple capabilities:

1. **Web Search**: Search for current information on any topic
2. **Webpage Fetcher**: Fetch full content from specific URLs for detailed analysis
3. **Date/Time**: Get the current date and time

Research Process:
- Start with a web search to find relevant sources
- If you need more details, fetch specific webpages
- Cross-reference information from multiple sources
- Always cite your sources with URLs
- Provide comprehensive, well-structured answers
"""
)

# Modified research function - CORRECTED to not double-invoke
def research(topic: str) -> str:
    """Conduct research on a topic."""
    print(f"\n{'='*60}")
    print(f"Researching: {topic}")
    print('='*60)

    final_result = None
    for step in agent.stream(
        {"messages": [{"role": "user", "content": topic}]},
        stream_mode="values"
    ):
        message = step["messages"][-1]
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tc in message.tool_calls:
                print(f"  -> Using {tc['name']}...")
        final_result = step

    # CORRECTED: Use final_result from stream instead of calling invoke() again
    # Original document code would call:
    # result = agent.invoke({"messages": [{"role": "user", "content": topic}]})
    # This is ISSUE #4: Double invocation

    return final_result["messages"][-1].content

print("="*60)
print("Example 3: Multi-Tool Research Agent")
print("="*60)

# Test with a simpler query first
result = research("What is today's date and what major tech news happened today?")
print(f"\nResult:\n{result}")
