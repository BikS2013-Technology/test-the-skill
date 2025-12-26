"""
Test 01: Basic Tavily Search Tool Setup

This script tests the basic Tavily Search tool from the document.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify TAVILY_API_KEY is set
tavily_key = os.environ.get("TAVILY_API_KEY")
if not tavily_key:
    raise ValueError("TAVILY_API_KEY environment variable is not set")

print(f"TAVILY_API_KEY is set (length: {len(tavily_key)})")

# Test the Tavily Search tool
from langchain_tavily import TavilySearch

# Create search tool with max 3 results
search_tool = TavilySearch(max_results=3)

# Test the tool directly
print("\nTesting TavilySearch.invoke()...")
results = search_tool.invoke("What is the capital of France?")
print(f"Results type: {type(results)}")
print(f"Results: {results}")
