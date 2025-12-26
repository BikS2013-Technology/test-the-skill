"""
Test 06: Example 4 - Structured Output Agent

This is the document's Example 4 adapted for Azure OpenAI.

Original document code (lines 622-670):
Agent that returns structured output using Pydantic models.

POTENTIAL ISSUE #5: The document uses `response_format=ResearchResult` parameter
in create_agent(). This parameter may not exist or may work differently.
Let's test this.
"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

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

# Define output structure (as in document)
class ResearchResult(BaseModel):
    """Structured research result."""
    summary: str = Field(description="Brief summary of findings")
    key_points: List[str] = Field(description="Key points discovered")
    sources: List[str] = Field(description="URLs of sources used")
    confidence: str = Field(description="Confidence level: high, medium, or low")

# Initialize model using Azure OpenAI
model = init_chat_model(
    os.environ["AZURE_OPENAI_DEPLOYMENT"],
    model_provider="azure_openai"
)

search_tool = TavilySearch(max_results=3)

print("="*60)
print("Example 4: Structured Output Agent")
print("="*60)

# Test the document's approach with response_format parameter
print("\n--- Testing Document Approach: response_format parameter ---")

try:
    agent = create_agent(
        model=model,
        tools=[search_tool],
        system_prompt="You are a research assistant. Search for information and provide structured results.",
        response_format=ResearchResult
    )
    print(f"create_agent with response_format succeeded: {type(agent)}")

    # Test invocation
    result = agent.invoke({
        "messages": [{"role": "user", "content": "What is the current state of electric vehicle adoption worldwide?"}]
    })

    # Check if structured_response exists
    structured = result.get("structured_response")
    if structured:
        print(f"\nStructured Response found!")
        print(f"Summary: {structured.summary}")
        print(f"\nKey Points:")
        for point in structured.key_points:
            print(f"  * {point}")
        print(f"\nSources: {structured.sources}")
        print(f"Confidence: {structured.confidence}")
    else:
        print(f"\nNo structured_response in result.")
        print(f"Result keys: {result.keys()}")
        print(f"Last message content: {result['messages'][-1].content[:500]}...")

except TypeError as e:
    print(f"\nISSUE #5 CONFIRMED: response_format parameter is not supported")
    print(f"Error: {e}")
    print("\nThe document's syntax for structured output may be incorrect.")
    print("Alternative approaches may be needed for structured output.")

except Exception as e:
    print(f"\nError testing response_format: {type(e).__name__}: {e}")

# Test alternative approach - asking LLM to output JSON
print("\n" + "="*60)
print("Alternative: Request JSON output in system prompt")
print("="*60)

agent_alt = create_agent(
    model=model,
    tools=[search_tool],
    system_prompt="""You are a research assistant. Search for information and provide structured results.

IMPORTANT: Your final response MUST be valid JSON with this exact structure:
{
    "summary": "Brief summary of findings",
    "key_points": ["point 1", "point 2", ...],
    "sources": ["url1", "url2", ...],
    "confidence": "high|medium|low"
}

Only output the JSON, no other text."""
)

result_alt = agent_alt.invoke({
    "messages": [{"role": "user", "content": "What is the population of Tokyo?"}]
})

print(f"\nAlternative approach result:")
print(result_alt["messages"][-1].content)
