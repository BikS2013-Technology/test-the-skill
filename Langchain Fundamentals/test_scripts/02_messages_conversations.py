"""
Test Script 02: Messages and Conversations Examples
Tests different message types and conversation patterns from the LangChain Fundamentals Guide.
"""

import os
from langchain_openai import AzureChatOpenAI

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


def test_dictionary_format():
    """
    Test Example: Dictionary Format (Document Section: Messages and Conversations)
    From lines 341-349
    """
    print("\n=== Test: Dictionary Format Messages ===")

    model = get_model()

    conversation = [
        {"role": "system", "content": "You are a helpful assistant that translates English to French."},
        {"role": "user", "content": "Translate: I love programming."},
        {"role": "assistant", "content": "J'adore la programmation."},
        {"role": "user", "content": "Translate: I love building applications."}
    ]

    response = model.invoke(conversation)
    print(f"Response: {response.content}")
    return True


def test_message_objects():
    """
    Test Example: Message Objects (Document Section: Messages and Conversations)
    From lines 356-368
    """
    print("\n=== Test: Message Objects ===")

    from langchain.messages import HumanMessage, AIMessage, SystemMessage

    model = get_model()

    conversation = [
        SystemMessage("You are a helpful assistant that translates English to French."),
        HumanMessage("Translate: I love programming."),
        AIMessage("J'adore la programmation."),
        HumanMessage("Translate: I love building applications.")
    ]

    response = model.invoke(conversation)
    print(f"Response: {response.content}")
    return True


def test_creating_messages_manually():
    """
    Test Example: Creating Messages Manually (Document Section: Messages and Conversations)
    From lines 372-387
    """
    print("\n=== Test: Creating Messages Manually ===")

    from langchain.messages import AIMessage, SystemMessage, HumanMessage

    model = get_model()

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
    print(f"Response: {response.content}")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Fundamentals - Messages and Conversations Tests")
    print("=" * 60)

    tests = [
        ("Dictionary Format Messages", test_dictionary_format),
        ("Message Objects", test_message_objects),
        ("Creating Messages Manually", test_creating_messages_manually),
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
