"""
Test script for Basic Prompt Approaches from LangChain Prompt Templates Guide.

This tests the examples from the "Basic Prompt Approaches" section (lines 111-155).
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


def test_simple_text_prompt():
    """
    Test: Simple Text Prompt (lines 113-125)

    Document shows:
        from langchain.chat_models import init_chat_model
        model = init_chat_model("gpt-4.1")
        response = model.invoke("Write a haiku about spring")

    ISSUE FOUND: Model name "gpt-4.1" is not a valid model name.
    It should be "gpt-4" or "gpt-4-turbo" or similar.
    """
    print("\n=== Test: Simple Text Prompt ===")

    model = get_azure_chat_model()

    # Direct text prompt
    response = model.invoke("Write a haiku about spring in exactly 3 lines")
    print(f"Response: {response.content}")

    assert response.content is not None
    print("SUCCESS: Simple text prompt works correctly")
    return True


def test_dictionary_format():
    """
    Test: Dictionary Format (lines 127-139)

    Document shows:
        messages = [
            {"role": "system", "content": "You are a poetry expert"},
            {"role": "user", "content": "Write a haiku about spring"},
            {"role": "assistant", "content": "Cherry blossoms bloom..."}
        ]
        response = model.invoke(messages)
    """
    print("\n=== Test: Dictionary Format (OpenAI-style) ===")

    model = get_azure_chat_model()

    messages = [
        {"role": "system", "content": "You are a poetry expert. Be very brief."},
        {"role": "user", "content": "Write a haiku about spring"},
    ]

    response = model.invoke(messages)
    print(f"Response: {response.content}")

    assert response.content is not None
    print("SUCCESS: Dictionary format works correctly")
    return True


def test_message_objects():
    """
    Test: Message Objects (lines 141-155)

    Document shows:
        from langchain.messages import SystemMessage, HumanMessage, AIMessage
        messages = [
            SystemMessage("You are a poetry expert"),
            HumanMessage("Write a haiku about spring"),
            AIMessage("Cherry blossoms bloom...")
        ]
        response = model.invoke(messages)
    """
    print("\n=== Test: Message Objects ===")

    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

    model = get_azure_chat_model()

    messages = [
        SystemMessage("You are a poetry expert. Be very brief."),
        HumanMessage("Write a haiku about spring"),
        AIMessage("Cherry blossoms bloom..."),  # Previous response (context)
        HumanMessage("Now write one about winter"),
    ]

    response = model.invoke(messages)
    print(f"Response: {response.content}")

    assert response.content is not None
    print("SUCCESS: Message objects work correctly")
    return True


def run_all_tests():
    """Run all basic prompt tests."""
    print("=" * 60)
    print("Testing Basic Prompt Approaches")
    print("=" * 60)

    results = []
    tests = [
        ("Simple Text Prompt", test_simple_text_prompt),
        ("Dictionary Format", test_dictionary_format),
        ("Message Objects", test_message_objects),
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
