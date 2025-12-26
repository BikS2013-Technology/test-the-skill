"""
Test Script 03: Simple Chat Application Examples
Tests basic chat functionality from the LangChain Fundamentals Guide.
"""

import os
from langchain_openai import AzureChatOpenAI
from langchain.messages import HumanMessage, AIMessage, SystemMessage

# Validate required environment variables
required_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT"
]

for var in required_vars:
    if not os.environ.get(var):
        raise ValueError(f"{var} environment variable is required")


def get_model():
    """Get configured Azure OpenAI model."""
    return AzureChatOpenAI(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"]
    )


def test_basic_invocation():
    """
    Test Example: Basic Invocation (Document Section: Building a Simple Chat Application)
    From lines 492-499
    """
    print("\n=== Test: Basic Invocation ===")

    model = get_model()

    # Single prompt
    response = model.invoke("Write a haiku about spring")
    print(f"Response: {response.content}")
    return True


def test_conversation_history():
    """
    Test Example: Conversation History (Document Section: Building a Simple Chat Application)
    From lines 506-533
    """
    print("\n=== Test: Conversation History ===")

    model = get_model()

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

    # Example conversation - test memory
    print("User: Hello! My name is Alice.")
    response1 = chat("Hello! My name is Alice.")
    print(f"Assistant: {response1}")

    print("\nUser: What's my name?")
    response2 = chat("What's my name?")  # Will remember "Alice"
    print(f"Assistant: {response2}")

    # Verify Alice was remembered
    if "alice" in response2.lower():
        print("\n[Memory test PASSED - Assistant remembered the name]")
        return True
    else:
        print("\n[Memory test FAILED - Assistant did not remember the name]")
        return False


def test_simple_chat_loop_simulation():
    """
    Test Example: Simple Chat Loop (Document Section: Building a Simple Chat Application)
    From lines 539-581 - Simulated (non-interactive) test
    """
    print("\n=== Test: Simple Chat Loop (Simulated) ===")

    model = get_model()

    messages = [
        SystemMessage("You are a helpful, friendly assistant. Be concise in your responses.")
    ]

    # Simulated user inputs
    test_inputs = [
        "What is the capital of France?",
        "And what about Italy?",
    ]

    for user_input in test_inputs:
        print(f"User: {user_input}")

        # Add user message
        messages.append(HumanMessage(user_input))

        # Get response
        response = model.invoke(messages)

        # Add to history
        messages.append(response)

        print(f"Assistant: {response.content}\n")

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Fundamentals - Simple Chat Application Tests")
    print("=" * 60)

    tests = [
        ("Basic Invocation", test_basic_invocation),
        ("Conversation History", test_conversation_history),
        ("Simple Chat Loop (Simulated)", test_simple_chat_loop_simulation),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, "PASSED" if success else "FAILED"))
        except Exception as e:
            results.append((name, f"ERROR: {e}"))

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    for name, result in results:
        print(f"{name}: {result}")
