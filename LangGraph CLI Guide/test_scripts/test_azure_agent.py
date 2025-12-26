"""
Test script for the Azure OpenAI agent example from LangGraph CLI Guide.

This requires Azure OpenAI credentials to be set in environment variables:
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_API_VERSION
- AZURE_OPENAI_DEPLOYMENT
"""
import sys
import os

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv('/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph CLI Guide/.env')

sys.path.insert(0, '/Users/giorgosmarinos/aiwork/TrainingMaterial/LangGraph CLI Guide')

from langchain_core.messages import HumanMessage


def check_env_vars():
    """Check if required environment variables are set."""
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT"
    ]

    missing = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value or value.startswith('$'):
            missing.append(var)

    if missing:
        print(f"Missing or invalid environment variables: {', '.join(missing)}")
        print("\nPlease set the following environment variables in your .env file:")
        for var in missing:
            print(f"  {var}=your_value_here")
        return False
    return True


def test_azure_agent():
    """Test the Azure OpenAI agent graph execution."""
    if not check_env_vars():
        print("\nSkipping test due to missing environment variables.")
        return False

    from my_agent.azure_agent import azure_graph

    # Initial state with a human message
    initial_state = {
        "messages": [HumanMessage(content="Hello! Please respond with just 'Hi there!'")]
    }

    print("Testing Azure OpenAI agent...")
    print("Input:", initial_state["messages"][0].content)

    try:
        # Invoke the graph
        result = azure_graph.invoke(initial_state)

        print("Output:", result["messages"][-1].content)
        print("Test passed!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    success = test_azure_agent()
    sys.exit(0 if success else 1)
