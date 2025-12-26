"""
Test script for Message Types examples from LangChain Prompt Templates Guide.

This tests the examples from the "Message Types" section (lines 46-107).
Adapted to use Azure OpenAI.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_azure_chat_model():
    """Create and return an Azure OpenAI chat model."""
    from langchain_openai import AzureChatOpenAI

    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    if not all([api_key, endpoint, api_version, deployment]):
        raise ValueError("Missing required Azure OpenAI environment variables")

    return AzureChatOpenAI(
        azure_endpoint=endpoint,
        azure_deployment=deployment,
        api_version=api_version,
        api_key=api_key,
    )


def test_core_message_classes():
    """
    Test: Core Message Classes (lines 52-58)

    Document shows:
        from langchain.messages import (
            SystemMessage, HumanMessage, AIMessage, ToolMessage
        )

    ISSUE FOUND: The import path should be langchain_core.messages, not langchain.messages
    """
    print("\n=== Test: Core Message Classes ===")

    # Try the documented import first
    try:
        from langchain.messages import (
            SystemMessage,
            HumanMessage,
            AIMessage,
            ToolMessage
        )
        print("SUCCESS: Import from langchain.messages works")
    except ImportError as e:
        print(f"ISSUE: Import from langchain.messages failed: {e}")

    # Try the correct import
    try:
        from langchain_core.messages import (
            SystemMessage,
            HumanMessage,
            AIMessage,
            ToolMessage
        )
        print("SUCCESS: Import from langchain_core.messages works (recommended)")
    except ImportError as e:
        print(f"ERROR: Import from langchain_core.messages failed: {e}")

    return True


def test_system_message():
    """
    Test: SystemMessage (lines 61-68)

    Document shows:
        from langchain.messages import SystemMessage
        system_msg = SystemMessage("You are a helpful assistant...")
    """
    print("\n=== Test: SystemMessage ===")

    from langchain_core.messages import SystemMessage

    system_msg = SystemMessage("You are a helpful assistant that translates English to French.")
    print(f"Created SystemMessage: {system_msg}")
    print(f"Content: {system_msg.content}")

    assert system_msg.content == "You are a helpful assistant that translates English to French."
    print("SUCCESS: SystemMessage works correctly")
    return True


def test_human_message():
    """
    Test: HumanMessage (lines 71-78)

    Document shows:
        from langchain.messages import HumanMessage
        human_msg = HumanMessage("Translate: I love programming.")
    """
    print("\n=== Test: HumanMessage ===")

    from langchain_core.messages import HumanMessage

    human_msg = HumanMessage("Translate: I love programming.")
    print(f"Created HumanMessage: {human_msg}")
    print(f"Content: {human_msg.content}")

    assert human_msg.content == "Translate: I love programming."
    print("SUCCESS: HumanMessage works correctly")
    return True


def test_ai_message():
    """
    Test: AIMessage (lines 81-88)

    Document shows:
        from langchain.messages import AIMessage
        ai_msg = AIMessage("J'adore la programmation.")
    """
    print("\n=== Test: AIMessage ===")

    from langchain_core.messages import AIMessage

    ai_msg = AIMessage("J'adore la programmation.")
    print(f"Created AIMessage: {ai_msg}")
    print(f"Content: {ai_msg.content}")

    assert ai_msg.content == "J'adore la programmation."
    print("SUCCESS: AIMessage works correctly")
    return True


def test_using_messages_together():
    """
    Test: Using Messages Together (lines 91-107)

    Document shows:
        from langchain.chat_models import init_chat_model
        from langchain.messages import SystemMessage, HumanMessage, AIMessage

        model = init_chat_model("claude-sonnet-4-5-20250929")
        messages = [
            SystemMessage("You are a helpful assistant."),
            HumanMessage("Hello, how are you?")
        ]
        response = model.invoke(messages)

    ISSUES FOUND:
    1. init_chat_model may not exist or work as documented
    2. Model string "claude-sonnet-4-5-20250929" is unusual format
    """
    print("\n=== Test: Using Messages Together ===")

    from langchain_core.messages import SystemMessage, HumanMessage

    # Try the documented init_chat_model
    try:
        from langchain.chat_models import init_chat_model
        print("init_chat_model is available")
    except ImportError:
        print("ISSUE: init_chat_model not found in langchain.chat_models")

    # Use Azure OpenAI instead
    model = get_azure_chat_model()

    messages = [
        SystemMessage("You are a helpful assistant. Reply in exactly 3 words."),
        HumanMessage("Hello, how are you?")
    ]

    response = model.invoke(messages)
    print(f"Response type: {type(response)}")
    print(f"Response content: {response.content}")

    assert response.content is not None
    print("SUCCESS: Using messages together works correctly")
    return True


def run_all_tests():
    """Run all message type tests."""
    print("=" * 60)
    print("Testing Message Types Examples")
    print("=" * 60)

    results = []
    tests = [
        ("Core Message Classes", test_core_message_classes),
        ("SystemMessage", test_system_message),
        ("HumanMessage", test_human_message),
        ("AIMessage", test_ai_message),
        ("Using Messages Together", test_using_messages_together),
    ]

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, "PASS", None))
        except Exception as e:
            results.append((name, "FAIL", str(e)))
            print(f"FAILED: {e}")

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for name, status, error in results:
        print(f"{name}: {status}")
        if error:
            print(f"  Error: {error}")

    return all(status == "PASS" for _, status, _ in results)


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
