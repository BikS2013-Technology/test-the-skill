"""
Test script for MessagesPlaceholder examples from LangChain Prompt Templates Guide.

This tests the examples from the "MessagesPlaceholder" section (lines 291-367).
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


def test_basic_messages_placeholder():
    """
    Test: Basic MessagesPlaceholder (lines 295-315)

    Document shows:
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.messages import HumanMessage

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant"),
            MessagesPlaceholder("conversation_history"),
            ("user", "{current_question}")
        ])

        formatted = prompt.invoke({
            "conversation_history": [
                HumanMessage("What is Python?"),
                AIMessage("Python is a programming language...")
            ],
            "current_question": "Can you give me an example?"
        })
    """
    print("\n=== Test: Basic MessagesPlaceholder ===")

    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, AIMessage

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Be brief."),
        MessagesPlaceholder("conversation_history"),
        ("user", "{current_question}")
    ])

    # Invoke with message history
    formatted = prompt.invoke({
        "conversation_history": [
            HumanMessage("What is Python?"),
            AIMessage("Python is a programming language...")
        ],
        "current_question": "Can you give me an example?"
    })

    print(f"Formatted messages count: {len(formatted.messages)}")
    for msg in formatted.messages:
        print(f"  - {type(msg).__name__}: {msg.content[:50]}...")

    model = get_azure_chat_model()
    response = model.invoke(formatted)
    print(f"Response: {response.content[:200]}...")

    assert len(formatted.messages) == 4  # system + 2 history + user
    print("SUCCESS: Basic MessagesPlaceholder works correctly")
    return True


def test_alternative_placeholder_syntax():
    """
    Test: Alternative Placeholder Syntax (lines 317-330)

    Document shows:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant"),
            ("placeholder", "{messages}"),
        ])

        formatted = prompt.invoke({
            "messages": [HumanMessage("Hello!")]
        })
    """
    print("\n=== Test: Alternative Placeholder Syntax ===")

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Greet the user."),
        ("placeholder", "{messages}"),
    ])

    formatted = prompt.invoke({
        "messages": [HumanMessage("Hello!")]
    })

    print(f"Formatted messages count: {len(formatted.messages)}")
    for msg in formatted.messages:
        print(f"  - {type(msg).__name__}: {msg.content}")

    model = get_azure_chat_model()
    response = model.invoke(formatted)
    print(f"Response: {response.content}")

    assert len(formatted.messages) == 2  # system + placeholder content
    print("SUCCESS: Alternative placeholder syntax works correctly")
    return True


def test_chat_with_history():
    """
    Test: Chat with History (lines 332-367)

    Document shows:
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.messages import HumanMessage, AIMessage
        from langchain.chat_models import init_chat_model

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a friendly assistant. Be concise."),
            MessagesPlaceholder("history"),
            ("user", "{input}")
        ])

        model = init_chat_model("claude-sonnet-4-5-20250929")
        chain = prompt | model

        history = []

        def chat(user_input: str) -> str:
            response = chain.invoke({
                "history": history,
                "input": user_input
            })
            history.append(HumanMessage(user_input))
            history.append(response)
            return response.content

        print(chat("My name is Alice"))
        print(chat("What's my name?"))

    ISSUE FOUND: Model name "claude-sonnet-4-5-20250929" is unusual
    """
    print("\n=== Test: Chat with History ===")

    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage

    # Template with history placeholder
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a friendly assistant. Be very concise. Remember user details."),
        MessagesPlaceholder("history"),
        ("user", "{input}")
    ])

    model = get_azure_chat_model()
    chain = prompt | model

    # Maintain conversation history
    history = []

    def chat(user_input: str) -> str:
        response = chain.invoke({
            "history": history,
            "input": user_input
        })

        # Update history
        history.append(HumanMessage(user_input))
        history.append(response)

        return response.content

    # Test conversation memory
    response1 = chat("My name is Alice")
    print(f"Response 1: {response1}")

    response2 = chat("What's my name?")
    print(f"Response 2: {response2}")

    # Check that the model remembers the name
    assert "Alice" in response2 or "alice" in response2.lower()
    print("SUCCESS: Chat with history works correctly (model remembers context)")
    return True


def run_all_tests():
    """Run all MessagesPlaceholder tests."""
    print("=" * 60)
    print("Testing MessagesPlaceholder Examples")
    print("=" * 60)

    results = []
    tests = [
        ("Basic MessagesPlaceholder", test_basic_messages_placeholder),
        ("Alternative Placeholder Syntax", test_alternative_placeholder_syntax),
        ("Chat with History", test_chat_with_history),
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
