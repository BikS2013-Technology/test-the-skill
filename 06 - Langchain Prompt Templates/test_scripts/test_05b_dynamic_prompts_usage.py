"""
Test script for actually using Dynamic Prompts examples from LangChain Prompt Templates Guide.

Since the imports exist, let's test if they work as documented.
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


def test_dynamic_prompt_decorator():
    """
    Test: @dynamic_prompt decorator usage (lines 377-400)

    Document shows:
        from langchain.agents import create_agent
        from langchain.agents.middleware import dynamic_prompt, ModelRequest

        @dynamic_prompt
        def user_role_prompt(request: ModelRequest) -> str:
            user_role = request.runtime.context.get("user_role", "user")
            ...
    """
    print("\n=== Test: @dynamic_prompt decorator usage ===")

    from langchain.agents import create_agent
    from langchain.agents.middleware import dynamic_prompt, ModelRequest

    # Check decorator signature
    print(f"dynamic_prompt type: {type(dynamic_prompt)}")
    print(f"ModelRequest type: {type(ModelRequest)}")

    # Try to use the decorator
    @dynamic_prompt
    def user_role_prompt(request: ModelRequest) -> str:
        """Generate system prompt based on user role."""
        # Try to access the structure as documented
        try:
            user_role = request.runtime.context.get("user_role", "user")
        except AttributeError:
            user_role = "user"

        base_prompt = "You are a helpful assistant."

        if user_role == "expert":
            return f"{base_prompt} Provide detailed technical responses."
        elif user_role == "beginner":
            return f"{base_prompt} Explain concepts simply and avoid jargon."

        return base_prompt

    print(f"Decorated function: {user_role_prompt}")
    print(f"Decorated function type: {type(user_role_prompt)}")

    return True


def test_create_agent_with_dynamic_prompt():
    """
    Test: create_agent with dynamic_prompt (lines 394-400)

    Document shows:
        agent = create_agent(
            model="gpt-4o",
            tools=[...],
            middleware=[user_role_prompt],
            context_schema=Context
        )
    """
    print("\n=== Test: create_agent with dynamic_prompt ===")

    from langchain.agents import create_agent
    from langchain.agents.middleware import dynamic_prompt, ModelRequest
    from dataclasses import dataclass

    @dataclass
    class Context:
        user_role: str

    @dynamic_prompt
    def simple_prompt(request: ModelRequest) -> str:
        return "You are a helpful assistant."

    # Try to create an agent
    try:
        model = get_azure_chat_model()

        agent = create_agent(
            model=model,
            tools=[],
            middleware=[simple_prompt],
            context_schema=Context
        )
        print(f"Agent created: {agent}")
        print(f"Agent type: {type(agent)}")
        return True
    except Exception as e:
        print(f"ISSUE: create_agent failed: {e}")
        print(f"Exception type: {type(e)}")
        return False


def test_create_react_agent_with_prompt():
    """
    Test: create_react_agent with static prompt (lines 538-553)

    Document shows:
        from langgraph.prebuilt import create_react_agent

        agent = create_react_agent(
            model="anthropic:claude-3-7-sonnet-latest",
            tools=[get_weather],
            prompt="Never answer questions about the weather."
        )
    """
    print("\n=== Test: create_react_agent with static prompt ===")

    from langgraph.prebuilt import create_react_agent
    from langchain_core.tools import tool

    @tool
    def get_weather(location: str) -> str:
        """Get weather for a location."""
        return f"Weather in {location}: Sunny, 72°F"

    model = get_azure_chat_model()

    try:
        agent = create_react_agent(
            model=model,
            tools=[get_weather],
            prompt="You are a weather assistant. Answer questions about weather."
        )
        print(f"Agent created: {type(agent)}")

        # Try to invoke
        result = agent.invoke({
            "messages": [{"role": "user", "content": "What is the weather in San Francisco?"}]
        })
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if hasattr(result, 'keys') else 'N/A'}")

        if "messages" in result:
            for msg in result["messages"][-2:]:
                print(f"Message: {msg}")

        return True
    except Exception as e:
        print(f"ISSUE: create_react_agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all dynamic prompt usage tests."""
    print("=" * 60)
    print("Testing Dynamic Prompts Usage")
    print("=" * 60)

    results = []
    tests = [
        ("@dynamic_prompt decorator", test_dynamic_prompt_decorator),
        ("create_agent with dynamic_prompt", test_create_agent_with_dynamic_prompt),
        ("create_react_agent with prompt", test_create_react_agent_with_prompt),
    ]

    for name, test_func in tests:
        try:
            result = test_func()
            status = "PASS" if result else "FAIL"
            results.append((name, status, None))
        except Exception as e:
            results.append((name, "ERROR", str(e)))
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for name, status, error in results:
        print(f"{name}: {status}")
        if error:
            print(f"  Error: {error}")

    return results


if __name__ == "__main__":
    run_all_tests()
