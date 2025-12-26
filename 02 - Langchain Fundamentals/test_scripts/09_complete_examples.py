"""
Test Script 09: Complete Examples
Tests the complete examples from the LangChain Fundamentals Guide.
"""

import os
from typing import List, Optional
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


def test_translation_chain():
    """
    Test Example: Translation Chain (Document Section: Complete Examples)
    From lines 1061-1096
    """
    print("\n=== Test: Translation Chain ===")

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    model = get_model()

    # Create translation chain
    translation_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional translator. Translate the following text from {source_lang} to {target_lang}. Only output the translation, nothing else."),
        ("human", "{text}")
    ])

    translation_chain = translation_prompt | model | StrOutputParser()

    # Use the chain
    result = translation_chain.invoke({
        "source_lang": "English",
        "target_lang": "Spanish",
        "text": "Hello, how are you today?"
    })
    print(f"Single translation result: {result}")

    # Batch translation
    translations = translation_chain.batch([
        {"source_lang": "English", "target_lang": "French", "text": "Good morning"},
        {"source_lang": "English", "target_lang": "German", "text": "Good night"},
    ])
    print(f"Batch translations: {translations}")

    return True


def test_streaming_chat_with_memory_simulation():
    """
    Test Example: Streaming Chat with Memory (Document Section: Complete Examples)
    From lines 1100-1145 (Simulated - non-interactive)
    """
    print("\n=== Test: Streaming Chat with Memory (Simulated) ===")

    model = get_model()

    messages = [
        SystemMessage("You are a helpful, friendly assistant.")
    ]

    # Simulated conversation
    test_inputs = [
        "Hello! My name is Bob.",
        "What's my name?",
        "Tell me a very short joke."
    ]

    for user_input in test_inputs:
        print(f"User: {user_input}")

        messages.append(HumanMessage(user_input))

        # Stream the response
        print("Assistant: ", end="", flush=True)

        full_response = None
        for chunk in model.stream(messages):
            print(chunk.content, end="", flush=True)
            full_response = chunk if full_response is None else full_response + chunk

        print("\n")

        # Add complete response to history
        messages.append(full_response)

    return True


def test_data_extraction_with_structured_output():
    """
    Test Example: Data Extraction with Structured Output (Document Section: Complete Examples)
    From lines 1149-1190
    """
    print("\n=== Test: Data Extraction with Structured Output ===")

    from pydantic import BaseModel, Field

    # Define the structure
    class ContactInfo(BaseModel):
        """Extracted contact information."""
        name: str = Field(description="Full name of the person")
        email: Optional[str] = Field(description="Email address if found")
        phone: Optional[str] = Field(description="Phone number if found")
        company: Optional[str] = Field(description="Company name if found")

    class ExtractedContacts(BaseModel):
        """List of extracted contacts."""
        contacts: List[ContactInfo] = Field(description="All contacts found in the text")

    model = get_model()
    extractor = model.with_structured_output(ExtractedContacts)

    # Extract from unstructured text
    text = """
    Meeting notes from yesterday:
    - John Smith (john.smith@acme.com, 555-1234) from Acme Corp will handle the backend.
    - Contact Sarah Johnson at TechStart for the frontend. Her email is sarah@techstart.io
    - Bob Williams mentioned his new number is 555-5678
    """

    result = extractor.invoke(f"Extract all contact information from this text:\n\n{text}")

    print("Extracted contacts:")
    for contact in result.contacts:
        print(f"  Name: {contact.name}")
        print(f"    Email: {contact.email}")
        print(f"    Phone: {contact.phone}")
        print(f"    Company: {contact.company}")
        print()

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Fundamentals - Complete Examples Tests")
    print("=" * 60)

    tests = [
        ("Translation Chain", test_translation_chain),
        ("Streaming Chat with Memory (Simulated)", test_streaming_chat_with_memory_simulation),
        ("Data Extraction with Structured Output", test_data_extraction_with_structured_output),
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
