# Issues - Pending Items

## Date: 2025-12-26

## Pending Items

_No pending items. All issues have been resolved._

---

## Completed Items

### Fixed on 2025-12-26

1. **Document Issue - Invalid Model Names Throughout Document** ✓
   - **Issue**: The document used invalid/unusual model name formats like "gpt-4.1" and "claude-sonnet-4-5-20250929"
   - **Resolution**: Updated all model names to use valid "gpt-4o" format
   - **Locations Fixed**: Lines 97, 120, 178, 213, 346, 544, 675

2. **Document Issue - Missing Azure OpenAI Guidance** ✓
   - **Issue**: The document only showed OpenAI examples, not Azure OpenAI
   - **Resolution**: Added "Using Azure OpenAI" section with full configuration example using `AzureChatOpenAI`
   - **Location**: Added after "Message Objects" section

3. **Document Issue - Deprecated Import Warning** ✓
   - **Issue**: `create_react_agent` from `langgraph.prebuilt` may show deprecation warning
   - **Resolution**: Added note in document warning about potential deprecation and directing users to check LangGraph documentation for latest recommended import path
   - **Location**: Added note before the `create_react_agent` example in "Integration with LangGraph Agents" section

4. **Document Issue - Import Path Inconsistency** ✓
   - **Issue**: The document used `from langchain.messages import ...` but the recommended path is `from langchain_core.messages import ...`
   - **Resolution**: Updated all import statements to use `langchain_core.messages` consistently
   - **Locations Fixed**: Lines 53-58, 66, 76, 86, 95, 146, 341, 603, 706

5. **Document Issue - Customer Support Agent Example** ✓
   - **Issue**: The Customer Support Agent example used a model string instead of instance and the context passing mechanism needed clarification
   - **Resolution**:
     - Added note about API version variability
     - Changed tool import to `langchain_core.tools`
     - Added model instance creation with `init_chat_model`
     - Updated context passing to use `config={"configurable": {"context": ...}}` pattern
   - **Location**: Lines 749-821

6. **Document Suggestion - Add Environment Variable Validation** ✓
   - **Issue**: The document didn't show how to validate required environment variables
   - **Resolution**: Added "### 7. Validate Environment Variables" section in Best Practices with:
     - `get_required_env()` helper function that raises ValueError for missing variables
     - Examples for both OpenAI and Azure OpenAI model initialization with validation
   - **Location**: Added to Best Practices section (lines 975-1015)

7. **Document Suggestion - Add Error Handling Examples** ✓
   - **Issue**: Examples didn't show error handling for API calls
   - **Resolution**: Added "### 8. Handle API Errors Gracefully" section in Best Practices with:
     - `invoke_with_retry()` function with exponential backoff
     - Handling for rate limiting, authentication errors, context length errors
     - Complete usage example with try/except patterns
   - **Location**: Added to Best Practices section (lines 1017-1082)

---

## Verification Notes

All examples from the LangChain Prompt Templates Guide were implemented and tested:

| Test | Status | Notes |
|------|--------|-------|
| Core Message Classes Import | PASS | Both langchain.messages and langchain_core.messages work |
| SystemMessage | PASS | Works as documented |
| HumanMessage | PASS | Works as documented |
| AIMessage | PASS | Works as documented |
| Using Messages Together | PASS | Works with Azure OpenAI |
| Simple Text Prompt | PASS | Works as documented |
| Dictionary Format | PASS | Works as documented |
| Message Objects | PASS | Works as documented |
| Basic ChatPromptTemplate | PASS | Works as documented |
| Multiple Variables | PASS | Works as documented |
| Chaining with Models | PASS | Pipe operator works correctly |
| Partial Templates | PASS | Works as documented |
| Basic MessagesPlaceholder | PASS | Works as documented |
| Alternative Placeholder Syntax | PASS | Works as documented |
| Chat with History | PASS | Model correctly remembers context |
| @dynamic_prompt decorator | PASS | Available and works |
| create_agent with middleware | PASS | Works but uses deprecated API |
| create_react_agent | PASS | Works but deprecated warning shown |
| InMemoryStore | PASS | Works as documented |
| Translation Chatbot | PASS | Full example works |
| SQL Query Assistant | PASS | Partial templates work correctly |
| Variable Validation | PASS | input_variables property works |
| trim_messages | PASS | Available with count_tokens_approximately |

---

## Test Files Created

1. `test_scripts/test_01_message_types.py` - Message type tests
2. `test_scripts/test_02_basic_prompts.py` - Basic prompt approach tests
3. `test_scripts/test_03_chat_prompt_template.py` - ChatPromptTemplate tests
4. `test_scripts/test_04_messages_placeholder.py` - MessagesPlaceholder tests
5. `test_scripts/test_05_dynamic_prompts.py` - Dynamic prompts import tests
6. `test_scripts/test_05b_dynamic_prompts_usage.py` - Dynamic prompts usage tests
7. `test_scripts/test_06_complete_examples.py` - Complete example tests

---

## Summary

The LangChain Prompt Templates Guide has been fully reviewed and all issues have been resolved. The document now includes:

- **Valid model names** using standard formats (gpt-4o)
- **Azure OpenAI configuration** examples for enterprise users
- **Consistent imports** using `langchain_core.messages`
- **Updated API patterns** with notes about version compatibility
- **Environment variable validation** best practices
- **Error handling patterns** for production use

All core functionality (ChatPromptTemplate, MessagesPlaceholder, partial templates, chaining, dynamic prompts) works as documented.
