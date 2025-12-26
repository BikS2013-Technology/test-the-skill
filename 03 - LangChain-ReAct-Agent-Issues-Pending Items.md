# LangChain ReAct Agent - Issues and Pending Items

**Document Last Updated:** December 26, 2025

This document tracks issues, inconsistencies, and pending items discovered during testing of the `LangChain-ReAct-Agent-WebSearch-Guide.md` document.

---

## Pending Issues

*No pending issues at this time. All identified issues have been resolved.*

---

## Completed/Resolved Items

### Issue #8: Double Invocation in Best Practices - Log Tool Usage Function (HIGH) - FIXED

**Location:** Lines 788-809 (`invoke_with_logging` function in Best Practices section)

**Problem:** The `invoke_with_logging()` function streamed the response AND THEN called `invoke()` separately, causing the agent to process the question twice. This was the same bug that was fixed in Examples 2 and 3 (Issues #3 and #4), but was missed in the Best Practices section.

**Resolution:** Fixed on December 26, 2025. The code now captures the final result from the stream instead of invoking separately.

**Fixed Code:**
```python
def invoke_with_logging(agent, question: str):
    """Invoke agent with tool usage logging."""
    print(f"Question: {question}\n")

    final_result = None
    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values"
    ):
        message = step["messages"][-1]
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tc in message.tool_calls:
                print(f"[Tool Call] {tc['name']}: {tc['args']}")
        final_result = step

    print(f"\nFinal Answer:\n{final_result['messages'][-1].content}")
    return final_result
```

---

### Issue #7: No Azure OpenAI Instructions - FIXED

**Location:** Lines 87-150 (Setting Up the Environment)

**Problem:** The document only covered OpenAI, Anthropic, and Google providers. It did not mention Azure OpenAI setup, which is a common enterprise requirement.

**Resolution:** Fixed on December 26, 2025. Added comprehensive Azure OpenAI instructions including:
- Environment variables in Python code block
- Environment variables in .env file example
- New "Using Azure OpenAI" subsection with two options:
  - Option 1: Using `init_chat_model` with `model_provider="azure_openai"`
  - Option 2: Using `AzureChatOpenAI` directly

**Added Content:**
```python
# Azure OpenAI (alternative to direct OpenAI)
os.environ["AZURE_OPENAI_API_KEY"] = "your-azure-key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://your-resource.openai.azure.com/"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-15-preview"
os.environ["AZURE_OPENAI_DEPLOYMENT"] = "your-deployment-name"
```

---

### Issue #6: Missing langchain-community in Installation Instructions - FIXED

**Location:** Lines 50-64 and 66-75 (Installation section)

**Problem:** The document mentioned `TavilySearchResults` from `langchain_community.tools.tavily_search`, but `langchain-community` was not included in the installation instructions.

**Resolution:** Fixed on December 26, 2025. Added `langchain-community` to both pip and UV installation sections.

**Fixed Code (pip):**
```bash
# Community tools (includes TavilySearchResults alternative)
pip install langchain-community
```

**Fixed Code (UV):**
```bash
uv add langchain langchain-tavily langchain-community
```

---

### Issue #3: Double Invocation in Example 2 (Chat Loop) - FIXED

**Location:** Lines 556-567 in the document (after Azure OpenAI additions)

**Problem:** The Interactive Chat Loop example streamed the response AND THEN called `invoke()` separately, causing the agent to process the question twice.

**Resolution:** Fixed on December 26, 2025. The code now captures the final result from the stream instead of invoking separately.

**Fixed Code:**
```python
# Stream the response and capture the final result
final_result = None
for step in agent.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    stream_mode="values"
):
    message = step["messages"][-1]
    if hasattr(message, 'tool_calls') and message.tool_calls:
        print(f"\n[Searching...]", end="")
    final_result = step

# Print the final response from the stream
print(final_result["messages"][-1].content)
```

---

### Issue #4: Double Invocation in Example 3 (Multi-Tool Research) - FIXED

**Location:** Lines 634-651 in the document (after Azure OpenAI additions)

**Problem:** Same issue as Issue #3 - the `research()` function streamed AND THEN invoked separately.

**Resolution:** Fixed on December 26, 2025. The code now captures the final result from the stream.

**Fixed Code:**
```python
def research(topic: str) -> str:
    """Conduct research on a topic."""
    print(f"\n{'='*60}")
    print(f"Researching: {topic}")
    print('='*60)

    final_result = None
    for step in agent.stream(
        {"messages": [{"role": "user", "content": topic}]},
        stream_mode="values"
    ):
        message = step["messages"][-1]
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tc in message.tool_calls:
                print(f"  → Using {tc['name']}...")
        final_result = step

    return final_result["messages"][-1].content
```

---

### Verified Working Features

The following features from the document have been tested and verified to work correctly:

1. **TavilySearch Basic Setup** - ✅ Works
2. **Basic Agent Creation with create_agent()** - ✅ Works
3. **System Prompt Configuration** - ✅ Works
4. **Basic Invocation** - ✅ Works
5. **Message Objects (HumanMessage)** - ✅ Works
6. **Accessing Full Conversation** - ✅ Works
7. **Custom Tools with @tool decorator** - ✅ Works
8. **Custom Tools with Pydantic Schema** - ✅ Works
9. **Structured Output with response_format** - ✅ Works
10. **Error Handling Pattern** - ✅ Works
11. **Azure OpenAI with init_chat_model** - ✅ Works
12. **Azure OpenAI with AzureChatOpenAI** - ✅ Works

---

## Test Scripts Created

The following test scripts were created to verify the document examples:

| Test Script | Description | Status |
|-------------|-------------|--------|
| `test_01_tavily_search.py` | Basic Tavily Search tool | ✅ Pass |
| `test_02_basic_agent_azure.py` | Agent with Azure OpenAI | ✅ Pass |
| `test_03_example1_simple_qa.py` | Example 1: Simple Q&A Agent | ✅ Pass |
| `test_04_example2_chat_loop.py` | Example 2: Interactive Chat Loop | ✅ Pass |
| `test_05_example3_multi_tool.py` | Example 3: Multi-Tool Research | ✅ Pass |
| `test_06_example4_structured_output.py` | Example 4: Structured Output | ✅ Pass |
| `test_07_additional_snippets.py` | Various smaller snippets | ✅ Pass |

---

## Summary

| Priority | Issue | Status |
|----------|-------|--------|
| HIGH | Issue #8: Double invocation in Best Practices | ✅ Fixed - December 26, 2025 |
| HIGH | Issue #3: Double invocation in Example 2 | ✅ Fixed - December 26, 2025 |
| HIGH | Issue #4: Double invocation in Example 3 | ✅ Fixed - December 26, 2025 |
| MEDIUM | Issue #6: Missing langchain-community package | ✅ Fixed - December 26, 2025 |
| LOW | Issue #7: No Azure OpenAI instructions | ✅ Fixed - December 26, 2025 |

---

**All issues have been resolved. The document is now complete and verified.**
