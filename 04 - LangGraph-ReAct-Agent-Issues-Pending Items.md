# Issues and Pending Items - LangGraph ReAct Agent Guide

## Pending Items

*All issues have been resolved. See Completed Items below.*

---

## Notes

### Tested and Working Features
All major features in the guide were tested and work correctly with Azure OpenAI:
- Basic ReAct agent creation
- System prompts (static and dynamic)
- Memory with MemorySaver checkpointer
- Custom graph building
- TavilySearch integration
- Custom tools (@tool decorator)
- Streaming (values, updates, progress)
- Async streaming
- Graph visualization (Mermaid, PNG)
- Extended state tracking

### Test Environment
- Date: December 26, 2025
- LangGraph version: 1.0.5
- langchain-tavily version: 0.2.15
- langchain-openai version: 1.1.6
- Python version: 3.13
- LLM Provider: Azure OpenAI

---

## Completed Items

### ISSUE-001: Deprecated Import Path for create_react_agent
- **Severity**: High
- **Location**: Guide lines 123, 151, 175, 419, 486, 517, 540, 597, 624, 698, 733, 1022
- **Problem**: The guide used `from langgraph.prebuilt import create_react_agent` but this is deprecated
- **Warning Message**: `create_react_agent has been moved to langchain.agents. Please update your import to from langchain.agents import create_agent. Deprecated in LangGraph V1.0 to be removed in V2.0.`
- **Fix Applied**: Updated all 12 occurrences to use `from langchain.agents import create_react_agent`
- **Status**: **COMPLETED** (December 26, 2025)

### ISSUE-003: Incorrect TavilySearch Results Structure
- **Severity**: Medium
- **Location**: Guide lines 354-378
- **Problem**: The guide showed an incorrect/outdated TavilySearch results structure
- **Fix Applied**: Updated the results structure to include all actual fields (`follow_up_questions`, `answer`, `images`, `raw_content`, `published_date`) with explanatory comments
- **Status**: **COMPLETED** (December 26, 2025)

### ISSUE-004: Undocumented TavilySearch Parameters
- **Severity**: Medium
- **Location**: Guide lines 328-344 and 932-950
- **Problem**: The guide showed TavilySearch parameters that may not be available in langchain-tavily
- **Fix Applied**:
  - Updated TavilySearch Configuration section to show only verified parameters (`max_results`, `topic`)
  - Added note about checking langchain-tavily documentation for advanced features
  - Updated Best Practices section to remove unverified parameters
- **Status**: **COMPLETED** (December 26, 2025)

### ISSUE-005: init_chat_model Import Path
- **Severity**: Medium
- **Location**: Guide lines 952-974
- **Problem**: The guide showed `from langchain.chat_models import init_chat_model` which may not exist
- **Fix Applied**: Replaced with direct model initialization examples showing ChatAnthropic, ChatOpenAI, and AzureChatOpenAI imports and usage
- **Status**: **COMPLETED** (December 26, 2025)

### ISSUE-002: Missing Dependency for ASCII Graph Visualization
- **Severity**: Low
- **Location**: Guide lines 79-80 (Installation) and 696-703 (ASCII Output)
- **Problem**: The guide showed `agent.get_graph().draw_ascii()` but didn't mention that `grandalf` package is required
- **Fix Applied**:
  - Added `uv add grandalf` to the Installation section as an optional dependency
  - Added note in the ASCII Output section explaining the dependency requirement
- **Status**: **COMPLETED** (December 26, 2025)

### ISSUE-006: Guide Uses Anthropic-Specific Examples
- **Severity**: Low
- **Location**: New section added at lines 117-169
- **Problem**: All examples used `ChatAnthropic` which required users to adapt for other providers
- **Fix Applied**:
  - Added new "Using Different LLM Providers" section with complete examples for:
    - Anthropic Claude
    - OpenAI (GPT-4o)
    - Azure OpenAI (with environment variables)
    - Google Gemini
  - Added note explaining how to substitute models throughout the guide
- **Status**: **COMPLETED** (December 26, 2025)
