"""
Test Script 01: LLM Connection Examples
Tests Azure OpenAI connection using different methods from the LangChain Fundamentals Guide.
"""

import os

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


def test_unified_model_initialization():
    """
    Test Example: Unified Model Initialization (Document Section: Connecting to LLMs)
    Adapted from lines 177-184 for Azure OpenAI
    """
    print("\n=== Test: Unified Model Initialization ===")

    from langchain.chat_models import init_chat_model

    # Azure OpenAI using init_chat_model
    model = init_chat_model(
        f"azure_openai:{os.environ['AZURE_OPENAI_DEPLOYMENT']}",
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    )

    response = model.invoke("Say hello in one word.")
    print(f"Response: {response.content}")
    return True


def test_provider_specific_class():
    """
    Test Example: Provider-Specific Classes (Document Section: Connecting to LLMs)
    Adapted from lines 215-220 for Azure OpenAI
    """
    print("\n=== Test: Provider-Specific Class (AzureChatOpenAI) ===")

    from langchain_openai import AzureChatOpenAI

    model = AzureChatOpenAI(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"]
    )

    response = model.invoke("What is 2 + 2?")
    print(f"Response: {response.content}")
    return True


def test_configuration_parameters():
    """
    Test Example: Configuration Parameters (Document Section: Configuration Parameters)
    Adapted from lines 266-272
    """
    print("\n=== Test: Configuration Parameters ===")

    from langchain_openai import AzureChatOpenAI

    model = AzureChatOpenAI(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        temperature=0.7,      # Controls randomness (0.0-1.0)
        timeout=30,           # Maximum seconds to wait
        max_tokens=100,       # Maximum tokens in response
        max_retries=3         # Retry attempts on failure
    )

    response = model.invoke("Write a short haiku about coding.")
    print(f"Response: {response.content}")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Fundamentals - LLM Connection Tests")
    print("=" * 60)

    tests = [
        ("Unified Model Initialization", test_unified_model_initialization),
        ("Provider-Specific Class", test_provider_specific_class),
        ("Configuration Parameters", test_configuration_parameters),
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
