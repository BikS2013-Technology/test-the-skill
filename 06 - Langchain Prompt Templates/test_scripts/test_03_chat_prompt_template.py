"""
Test script for ChatPromptTemplate examples from LangChain Prompt Templates Guide.

This tests the examples from the "ChatPromptTemplate" section (lines 159-244).
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


def test_basic_chat_prompt_template():
    """
    Test: Basic ChatPromptTemplate (lines 163-180)

    Document shows:
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful chatbot."),
            ("user", "{question}")
        ])

        formatted = prompt.invoke({"question": "What is Python?"})
        model = init_chat_model("gpt-4.1")
        response = model.invoke(formatted)

    ISSUE FOUND: Model name "gpt-4.1" is not valid
    """
    print("\n=== Test: Basic ChatPromptTemplate ===")

    from langchain_core.prompts import ChatPromptTemplate

    # Create template with variables
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful chatbot. Answer in one sentence."),
        ("user", "{question}")
    ])

    # Format with variables
    formatted = prompt.invoke({"question": "What is Python?"})
    print(f"Formatted messages: {formatted}")

    # Use with model
    model = get_azure_chat_model()
    response = model.invoke(formatted)
    print(f"Response: {response.content}")

    assert response.content is not None
    print("SUCCESS: Basic ChatPromptTemplate works correctly")
    return True


def test_template_with_multiple_variables():
    """
    Test: Template with Multiple Variables (lines 186-198)

    Document shows:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a {role} that speaks {language}."),
            ("user", "Tell me about {topic}")
        ])

        formatted = prompt.invoke({
            "role": "teacher",
            "language": "formally",
            "topic": "quantum physics"
        })
    """
    print("\n=== Test: Template with Multiple Variables ===")

    from langchain_core.prompts import ChatPromptTemplate

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a {role} that speaks {language}. Be very brief."),
        ("user", "Tell me about {topic}")
    ])

    # Invoke with all variables
    formatted = prompt.invoke({
        "role": "teacher",
        "language": "formally",
        "topic": "quantum physics"
    })
    print(f"Formatted messages: {formatted}")

    model = get_azure_chat_model()
    response = model.invoke(formatted)
    print(f"Response: {response.content[:200]}...")

    assert response.content is not None
    print("SUCCESS: Multiple variables work correctly")
    return True


def test_chaining_with_models():
    """
    Test: Chaining with Models (lines 200-221)

    Document shows:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain.chat_models import init_chat_model

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful chatbot"),
            ("human", "Tell me a joke about {topic}")
        ])

        model = init_chat_model("gpt-4.1")
        chain = prompt | model
        response = chain.invoke({"topic": "bears"})
    """
    print("\n=== Test: Chaining with Models ===")

    from langchain_core.prompts import ChatPromptTemplate

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful chatbot. Keep jokes short."),
        ("human", "Tell me a joke about {topic}")
    ])

    model = get_azure_chat_model()

    # Create a chain using pipe operator
    chain = prompt | model

    # Invoke the chain
    response = chain.invoke({"topic": "bears"})
    print(f"Response: {response.content}")

    assert response.content is not None
    print("SUCCESS: Chaining with models works correctly")
    return True


def test_partial_templates():
    """
    Test: Partial Templates (lines 223-244)

    Document shows:
        from langchain_core.prompts import ChatPromptTemplate

        base_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a {dialect} SQL expert. Limit results to {top_k}."),
            ("user", "{query}")
        ])

        sql_prompt = base_prompt.partial(
            dialect="PostgreSQL",
            top_k="10"
        )

        formatted = sql_prompt.invoke({"query": "Show all users"})
    """
    print("\n=== Test: Partial Templates ===")

    from langchain_core.prompts import ChatPromptTemplate

    # Base template with multiple variables
    base_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a {dialect} SQL expert. Limit results to {top_k}. Only output SQL."),
        ("user", "{query}")
    ])

    # Partial application - fill dialect and top_k
    sql_prompt = base_prompt.partial(
        dialect="PostgreSQL",
        top_k="10"
    )

    # Check input variables
    print(f"Base template variables: {base_prompt.input_variables}")
    print(f"Partial template variables: {sql_prompt.input_variables}")

    # Now only needs 'query'
    formatted = sql_prompt.invoke({"query": "Show all users"})
    print(f"Formatted: {formatted}")

    model = get_azure_chat_model()
    response = model.invoke(formatted)
    print(f"Response: {response.content}")

    assert "query" in sql_prompt.input_variables
    assert "dialect" not in sql_prompt.input_variables
    print("SUCCESS: Partial templates work correctly")
    return True


def run_all_tests():
    """Run all ChatPromptTemplate tests."""
    print("=" * 60)
    print("Testing ChatPromptTemplate Examples")
    print("=" * 60)

    results = []
    tests = [
        ("Basic ChatPromptTemplate", test_basic_chat_prompt_template),
        ("Multiple Variables", test_template_with_multiple_variables),
        ("Chaining with Models", test_chaining_with_models),
        ("Partial Templates", test_partial_templates),
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
