"""
Test Script 05: Prompt Templates Examples
Tests prompt template functionality from the LangChain Fundamentals Guide.
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


def test_basic_templates():
    """
    Test Example: Basic Templates (Document Section: Prompt Templates)
    From lines 676-691
    """
    print("\n=== Test: Basic Templates ===")

    from langchain_core.prompts import PromptTemplate

    model = get_model()

    # Simple template
    template = PromptTemplate.from_template(
        "Translate the following text to {language}: {text}"
    )

    # Format the template
    prompt = template.format(language="French", text="Hello, how are you?")
    print(f"Formatted prompt: {prompt}")

    # Use with a model
    response = model.invoke(prompt)
    print(f"Response: {response.content}")
    return True


def test_chat_prompt_templates():
    """
    Test Example: Chat Prompt Templates (Document Section: Prompt Templates)
    From lines 697-714
    """
    print("\n=== Test: Chat Prompt Templates ===")

    from langchain_core.prompts import ChatPromptTemplate

    model = get_model()

    # Create a chat template
    chat_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that translates {input_language} to {output_language}."),
        ("human", "{text}")
    ])

    # Format and use
    messages = chat_template.format_messages(
        input_language="English",
        output_language="French",
        text="I love programming."
    )

    print(f"Formatted messages: {messages}")

    response = model.invoke(messages)
    print(f"Response: {response.content}")
    return True


def test_dynamic_prompts():
    """
    Test Example: Dynamic Prompts (Document Section: Prompt Templates)
    From lines 720-742
    """
    print("\n=== Test: Dynamic Prompts ===")

    model = get_model()

    def build_system_prompt(user_role: str, context: dict) -> str:
        """Generate system prompt based on user role and context."""
        base_prompt = "You are a helpful assistant."

        if user_role == "expert":
            base_prompt += " Provide detailed technical responses."
        elif user_role == "beginner":
            base_prompt += " Explain concepts simply and avoid jargon."

        if context.get("is_production"):
            base_prompt += " Be extra careful with any data modifications."

        return base_prompt

    # Use dynamically
    system_prompt = build_system_prompt("expert", {"is_production": True})
    print(f"Generated system prompt: {system_prompt}")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Explain machine learning briefly"}
    ]
    response = model.invoke(messages)
    print(f"Response (expert mode): {response.content[:200]}...")

    # Test beginner mode
    system_prompt_beginner = build_system_prompt("beginner", {"is_production": False})
    print(f"\nGenerated system prompt (beginner): {system_prompt_beginner}")

    messages_beginner = [
        {"role": "system", "content": system_prompt_beginner},
        {"role": "user", "content": "Explain machine learning briefly"}
    ]
    response_beginner = model.invoke(messages_beginner)
    print(f"Response (beginner mode): {response_beginner.content[:200]}...")

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Fundamentals - Prompt Templates Tests")
    print("=" * 60)

    tests = [
        ("Basic Templates", test_basic_templates),
        ("Chat Prompt Templates", test_chat_prompt_templates),
        ("Dynamic Prompts", test_dynamic_prompts),
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
