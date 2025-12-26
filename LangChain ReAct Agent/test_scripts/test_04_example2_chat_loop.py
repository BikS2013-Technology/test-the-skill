"""
Test 04: Example 2 - Interactive Chat Loop

This is the document's Example 2 adapted for Azure OpenAI and non-interactive testing.

Original document code (lines 478-533):
```python
import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_tavily import TavilySearch

# Setup
os.environ["ANTHROPIC_API_KEY"] = "your-key"
os.environ["TAVILY_API_KEY"] = "your-key"

model = init_chat_model("claude-sonnet-4-5-20250929")
search_tool = TavilySearch(max_results=3)

agent = create_agent(
    model=model,
    tools=[search_tool],
    system_prompt=\"\"\"You are a helpful research assistant.
Search the web to provide accurate, current information.
Always cite your sources.\"\"\"
)

def chat():
    \"\"\"Interactive chat loop with the agent.\"\"\"
    print("Research Assistant Ready! (type 'quit' to exit)")
    print("-" * 50)

    while True:
        user_input = input("\\nYou: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if not user_input:
            continue

        print("\\nAssistant: ", end="")

        # Stream the response
        for step in agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            stream_mode="values"
        ):
            message = step["messages"][-1]
            if hasattr(message, 'tool_calls') and message.tool_calls:
                print(f"\\n[Searching...]", end="")

        # Get final response
        result = agent.invoke({
            "messages": [{"role": "user", "content": user_input}]
        })
        print(result["messages"][-1].content)

if __name__ == "__main__":
    chat()
```

ISSUE #3 DETECTED: The code streams the response AND THEN re-invokes the agent.
This causes the agent to process the question TWICE, which is:
1. Inefficient (double API calls)
2. Potentially inconsistent (different answers)
3. Wastes tokens/money

The correct approach is to capture the final result FROM the stream.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify environment variables
required_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT",
    "TAVILY_API_KEY"
]

for var in required_vars:
    if not os.environ.get(var):
        raise ValueError(f"{var} environment variable is not set")

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_tavily import TavilySearch

# Initialize model using Azure OpenAI
model = init_chat_model(
    os.environ["AZURE_OPENAI_DEPLOYMENT"],
    model_provider="azure_openai"
)

search_tool = TavilySearch(max_results=3)

agent = create_agent(
    model=model,
    tools=[search_tool],
    system_prompt="""You are a helpful research assistant.
Search the web to provide accurate, current information.
Always cite your sources."""
)

print("="*60)
print("Example 2: Chat Loop (Non-Interactive Test)")
print("="*60)

# Simulate a chat with a single question
test_question = "What is the tallest building in the world?"

print(f"\nQuestion: {test_question}")
print("-"*40)

# Test the DOCUMENT'S approach (streaming + separate invoke)
print("\n--- Document Approach (streams then invokes separately) ---")
print("Streaming steps:")
final_result = None
for step in agent.stream(
    {"messages": [{"role": "user", "content": test_question}]},
    stream_mode="values"
):
    message = step["messages"][-1]
    if hasattr(message, 'tool_calls') and message.tool_calls:
        for tc in message.tool_calls:
            print(f"  [Tool Call: {tc['name']}]")
    final_result = step  # Capture the last step

# The document then calls invoke() again - this is INEFFICIENT!
# result = agent.invoke({"messages": [{"role": "user", "content": test_question}]})

# Instead, we should use the final_result from the stream
print(f"\nAnswer (from stream): {final_result['messages'][-1].content}")

print("\n" + "="*60)
print("ISSUE #3: The document's Example 2 calls agent.stream() AND THEN")
print("agent.invoke() separately, causing the agent to process the question")
print("twice. The correct approach is to capture the result from the stream.")
print("="*60)

# Show the correct approach
print("\n--- Correct Approach (capture from stream) ---")
test_question2 = "What is the world's largest ocean?"
print(f"\nQuestion: {test_question2}")
print("-"*40)

final_result = None
for step in agent.stream(
    {"messages": [{"role": "user", "content": test_question2}]},
    stream_mode="values"
):
    message = step["messages"][-1]
    if hasattr(message, 'tool_calls') and message.tool_calls:
        for tc in message.tool_calls:
            print(f"  [Tool Call: {tc['name']}]")
    final_result = step

# Use the result from the stream - no need to invoke() again!
print(f"\nAnswer: {final_result['messages'][-1].content}")
