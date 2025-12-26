# Issues - Pending Items

**Last Updated:** December 26, 2025

---

## Pending Items

### LangChain Fundamentals Guide Issues

#### 6. Model Names May Be Outdated (LOW)
**Location:** Various (lines 167, 171, 175, etc.)
**Issue:** Model names like `gpt-4.1`, `gpt-5-nano`, `claude-sonnet-4-5-20250929` are used, which may not match current API model names.
**Recommendation:** Add a note that model names should be verified against current provider documentation.

---

## Completed Items

### LangChain Fundamentals Guide - Fixed Issues (December 26, 2025)

#### 1. Incorrect Attribute Names in Streaming Examples (HIGH) - FIXED
**Location:** Lines 637, 640, 664 (original lines 602-611, 630-645)
**Issue:** The document used `.text` attribute for accessing content from AIMessage chunks, but the correct attribute is `.content`.
**Resolution:** Updated all occurrences to use `.content` instead of `.text`.

#### 2. Environment Variable Naming Inconsistency (MEDIUM) - FIXED
**Location:** Lines 210, 212-213, 248-249 (original lines 179, 183, 219)
**Issue:** The document used `AZURE_OPENAI_DEPLOYMENT_NAME` but common convention is `AZURE_OPENAI_DEPLOYMENT`.
**Resolution:**
- Standardized all Azure OpenAI environment variables to use `AZURE_OPENAI_DEPLOYMENT`
- Updated `OPENAI_API_VERSION` to `AZURE_OPENAI_API_VERSION` for consistency

#### 3. OpenAI Callback Not Applicable for Azure OpenAI (MEDIUM) - FIXED
**Location:** Lines 1304-1322 (original lines 1277-1284)
**Issue:** The `get_openai_callback()` example was shown without noting it doesn't work with Azure OpenAI.
**Resolution:** Added a note explaining that `get_openai_callback()` is for direct OpenAI API only, and provided Azure OpenAI alternative using `response.response_metadata.get('token_usage', {})`.

#### 4. Missing Azure OpenAI Examples in Unified Model Initialization (MEDIUM) - FIXED
**Location:** Lines 293-327 (new section added)
**Issue:** Azure OpenAI configuration was not clearly documented.
**Resolution:** Added comprehensive "Azure OpenAI Configuration" section with:
- Required environment variables list
- `init_chat_model` unified approach example
- `AzureChatOpenAI` provider-specific example
- Note explaining that `model` and `azure_deployment` typically have the same value

#### 5. Potential Import Path Changes (LOW) - FIXED
**Location:** Lines 1300-1322 (original lines 1235-1236)
**Issue:** The import path for `trim_messages` may vary between LangChain versions.
**Resolution:** Added try/except import pattern with fallback for version compatibility, plus a note about version compatibility.

#### 7. Runtime Model Switching Example Ambiguity (LOW) - FIXED
**Location:** Lines 389-416 (new section added)
**Issue:** Runtime model switching with `init_chat_model()` doesn't work intuitively with Azure OpenAI.
**Resolution:** Added "Azure OpenAI Runtime Configuration" section with:
- Explanation that Azure uses deployments, not model names
- Factory function pattern for switching between Azure deployments
- Note about pre-configuring deployments in Azure resource

---

## Notes

- All test scripts are located in `/Users/giorgosmarinos/aiwork/TrainingMaterial/Langchain Fundamentals/test_scripts/`
- Tests were run using Azure OpenAI with the deployment specified in the `AZURE_OPENAI_DEPLOYMENT` environment variable
- All 10 test scripts pass successfully after applying the fixes
- Test coverage includes: LLM Connection, Messages, Chat Applications, Streaming, Prompt Templates, LCEL Chains, Structured Output, Tool Integration, Complete Examples, and Best Practices
