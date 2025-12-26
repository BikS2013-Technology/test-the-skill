"""
Test Script 08: Tool Integration Examples
Tests tool integration functionality from the LangChain Fundamentals Guide.
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


def test_defining_tools_with_decorator():
    """
    Test Example: Defining Tools (Document Section: Tool Integration)
    From lines 971-994
    """
    print("\n=== Test: Defining Tools with @tool Decorator ===")

    from langchain.tools import tool

    @tool
    def get_weather(location: str) -> str:
        """Get the weather at a location.

        Args:
            location: The city and state, e.g. "San Francisco, CA"
        """
        # In a real app, call a weather API
        return f"It's sunny and 72F in {location}."

    @tool
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers.

        Args:
            a: First integer
            b: Second integer
        """
        return a * b

    # Test the tools directly
    weather_result = get_weather.invoke({"location": "Boston, MA"})
    print(f"Weather result: {weather_result}")

    multiply_result = multiply.invoke({"a": 5, "b": 7})
    print(f"Multiply result: {multiply_result}")

    return True


def test_tools_with_pydantic_models():
    """
    Test Example: Tools with Pydantic Models (Document Section: Tool Integration)
    From lines 998-1010
    """
    print("\n=== Test: Tools with Pydantic Models ===")

    from pydantic import BaseModel, Field

    class GetWeather(BaseModel):
        """Get the current weather in a given location"""
        location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

    class GetPopulation(BaseModel):
        """Get the current population in a given location"""
        location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

    model = get_model()
    model_with_tools = model.bind_tools([GetWeather, GetPopulation])

    # Test with a weather query
    response = model_with_tools.invoke("What's the weather in Boston?")
    print(f"Response tool_calls: {response.tool_calls}")

    return True


def test_binding_function_tools_to_models():
    """
    Test Example: Binding Tools to Models (Document Section: Tool Integration)
    From lines 1014-1029
    """
    print("\n=== Test: Binding Function Tools to Models ===")

    from langchain.tools import tool

    @tool
    def get_weather(location: str) -> str:
        """Get the weather at a location.

        Args:
            location: The city and state, e.g. "San Francisco, CA"
        """
        return f"It's sunny and 72F in {location}."

    @tool
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers.

        Args:
            a: First integer
            b: Second integer
        """
        return a * b

    model = get_model()
    model_with_tools = model.bind_tools([get_weather, multiply])

    # Invoke and check for tool calls
    response = model_with_tools.invoke("What's the weather in Boston?")

    print(f"Number of tool calls: {len(response.tool_calls)}")
    for tool_call in response.tool_calls:
        print(f"  Tool: {tool_call['name']}")
        print(f"  Args: {tool_call['args']}")

    return True


def test_streaming_tool_calls():
    """
    Test Example: Streaming Tool Calls (Document Section: Tool Integration)
    From lines 1035-1053
    """
    print("\n=== Test: Streaming Tool Calls ===")

    from langchain.tools import tool

    @tool
    def get_weather(location: str) -> str:
        """Get the weather at a location.

        Args:
            location: The city and state, e.g. "San Francisco, CA"
        """
        return f"It's sunny and 72F in {location}."

    model = get_model()
    model_with_tools = model.bind_tools([get_weather])

    print("Streaming tool call chunks:")
    for chunk in model_with_tools.stream("What's the weather in Boston?"):
        for tool_chunk in chunk.tool_call_chunks:
            if name := tool_chunk.get("name"):
                print(f"  Tool name: {name}")
            if args := tool_chunk.get("args"):
                print(f"  Args chunk: {args}")

    return True


def test_accumulating_tool_call_chunks():
    """
    Test Example: Accumulating Tool Call Chunks (Document Section: Tool Integration)
    From lines 1047-1053
    """
    print("\n=== Test: Accumulating Tool Call Chunks ===")

    from langchain.tools import tool

    @tool
    def get_weather(location: str) -> str:
        """Get the weather at a location.

        Args:
            location: The city and state, e.g. "San Francisco, CA"
        """
        return f"It's sunny and 72F in {location}."

    model = get_model()
    model_with_tools = model.bind_tools([get_weather])

    gathered = None
    for chunk in model_with_tools.stream("What's the weather in Boston?"):
        gathered = chunk if gathered is None else gathered + chunk

    print(f"Accumulated tool calls: {gathered.tool_calls}")

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Fundamentals - Tool Integration Tests")
    print("=" * 60)

    tests = [
        ("Defining Tools with @tool Decorator", test_defining_tools_with_decorator),
        ("Tools with Pydantic Models", test_tools_with_pydantic_models),
        ("Binding Function Tools to Models", test_binding_function_tools_to_models),
        ("Streaming Tool Calls", test_streaming_tool_calls),
        ("Accumulating Tool Call Chunks", test_accumulating_tool_call_chunks),
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
