"""
Test Script 06: Chains and Runnables (LCEL) Examples
Tests LCEL functionality from the LangChain Fundamentals Guide.
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


def test_pipe_operator_chain():
    """
    Test Example: Creating Chains with Pipe Operator (Document Section: Chains and Runnables)
    From lines 761-777
    """
    print("\n=== Test: Pipe Operator Chain ===")

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    model = get_model()

    # Create components
    prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
    output_parser = StrOutputParser()

    # Chain them together
    chain = prompt | model | output_parser

    # Use the chain
    result = chain.invoke({"topic": "programming"})
    print(f"Joke result: {result}")
    return True


def test_multi_step_chain():
    """
    Test Example: Multi-Step Chains (Document Section: Chains and Runnables)
    From lines 781-809
    """
    print("\n=== Test: Multi-Step Chain ===")

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    model = get_model()

    # Step 1: Generate a topic
    topic_prompt = ChatPromptTemplate.from_template(
        "Generate a random topic for a short story in one word:"
    )

    # Step 2: Write a story about that topic
    story_prompt = ChatPromptTemplate.from_template(
        "Write a very short story (2-3 sentences) about: {topic}"
    )

    # Chain: generate topic -> write story
    topic_chain = topic_prompt | model | StrOutputParser()

    # Full chain with lambda to pass topic forward
    full_chain = (
        topic_chain
        | (lambda topic: {"topic": topic})
        | story_prompt
        | model
        | StrOutputParser()
    )

    result = full_chain.invoke({})
    print(f"Generated story: {result}")
    return True


def test_chain_decorator():
    """
    Test Example: The @chain Decorator (Document Section: Chains and Runnables)
    From lines 815-833 (Adapted - no vector store)
    """
    print("\n=== Test: @chain Decorator ===")

    from langchain_core.runnables import chain

    model = get_model()

    @chain
    def simple_chain(query: str) -> str:
        """Custom runnable that processes a query."""
        # Simulated retrieval/processing
        return f"Processed query: {query}"

    # Use as a runnable
    result = simple_chain.invoke("What is machine learning?")
    print(f"Simple chain result: {result}")

    # Supports batch operations automatically
    results = simple_chain.batch([
        "How many distribution centers does Nike have?",
        "When was Nike incorporated?",
    ])
    print(f"Batch results: {results}")

    return True


def test_runnable_configuration():
    """
    Test Example: Runnable Configuration (Document Section: Chains and Runnables)
    From lines 839-849
    """
    print("\n=== Test: Runnable Configuration ===")

    model = get_model()

    # Note: In actual usage, callbacks would be real callback handlers
    response = model.invoke(
        "Tell me a joke",
        config={
            "run_name": "joke_generation",
            "tags": ["humor", "demo"],
            "metadata": {"user_id": "123"},
            # "callbacks": [my_callback_handler],  # Would add real callbacks here
        }
    )

    print(f"Response with config: {response.content}")
    return True


def test_runnable_passthrough_lambda():
    """
    Test Example: RunnablePassthrough and RunnableLambda (Document Section: Chains and Runnables)
    From lines 853-868
    """
    print("\n=== Test: RunnablePassthrough and RunnableLambda ===")

    from langchain_core.runnables import RunnablePassthrough, RunnableLambda
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    model = get_model()

    # Pass input through unchanged
    passthrough = RunnablePassthrough()

    # Transform input with a function
    def add_context(input_dict):
        input_dict["context"] = "You are helping with a Python project"
        return input_dict

    transform = RunnableLambda(add_context)

    # Create a prompt that uses both input and context
    prompt = ChatPromptTemplate.from_template(
        "Context: {context}\n\nQuestion: {question}\n\nProvide a brief answer."
    )

    # Use in a chain
    chain = transform | prompt | model | StrOutputParser()

    result = chain.invoke({"question": "What is a decorator?"})
    print(f"Chain result: {result}")

    # Test passthrough
    passthrough_result = passthrough.invoke({"test": "value"})
    print(f"Passthrough result: {passthrough_result}")

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Fundamentals - Chains and Runnables (LCEL) Tests")
    print("=" * 60)

    tests = [
        ("Pipe Operator Chain", test_pipe_operator_chain),
        ("Multi-Step Chain", test_multi_step_chain),
        ("@chain Decorator", test_chain_decorator),
        ("Runnable Configuration", test_runnable_configuration),
        ("RunnablePassthrough and RunnableLambda", test_runnable_passthrough_lambda),
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
