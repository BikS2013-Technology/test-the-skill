# Issues - Pending Items

## Date: 2025-12-26

## Pending Items

_No pending items. All identified issues have been resolved._

---

## Completed Items

### 9. Python Version Mismatch Between pyproject.toml and Dockerfile (MEDIUM) - FIXED

**Date Identified:** December 26, 2025
**Date Fixed:** December 26, 2025

**Problem:** The project had a Python version mismatch:
- `pyproject.toml`: `requires-python = ">=3.13"`
- `Dockerfile`: `FROM langchain/langgraph-api:3.11`

**Fix Applied:** Updated `pyproject.toml` to use `requires-python = ">=3.11"` to match the Docker base image.

---

### 10. pyproject.toml Uses UV-Specific Format Instead of PEP 621 (LOW) - FIXED

**Date Identified:** December 26, 2025
**Date Fixed:** December 26, 2025

**Problem:** The implementation used the UV-specific `[dependency-groups]` format instead of the standard PEP 621 `[project.optional-dependencies]` format shown in the guide.

**Fix Applied:** Changed `[dependency-groups]` to `[project.optional-dependencies]` to match the guide document.

---

### 2025-12-26

1. **FIXED - JavaScript Zod Import Path (Previously Line 499)**
   - **Issue**: The JavaScript test example used `from "zod/v4"` which is an unusual import path
   - **Fix**: Changed to `from "zod"` for standard Zod usage
   - **Location**: LangGraph-CLI-Guide.md, line 715

2. **FIXED - Missing Azure OpenAI Guidance**
   - **Issue**: The document showed `langchain_openai` dependency but only mentioned OpenAI, not Azure OpenAI
   - **Fix**: Added complete "Example Agent with Azure OpenAI" section including:
     - Environment variables configuration
     - Full agent implementation with `AzureChatOpenAI`
     - Updated langgraph.json example
   - **Location**: LangGraph-CLI-Guide.md, lines 429-516

3. **FIXED - Missing Dependencies List**
   - **Issue**: The document mentioned `requirements.txt` and `pyproject.toml` but didn't specify dependencies
   - **Fix**: Added two new sections:
     - "Python Dependencies" with UV commands and pyproject.toml/requirements.txt examples
     - "JavaScript Dependencies" with package.json example
   - **Location**: LangGraph-CLI-Guide.md, lines 353-420

4. **ADDRESSED - Basic Agent Example Has No LLM Usage**
   - **Issue**: The Python agent example was too simplistic without LLM integration
   - **Resolution**: The new Azure OpenAI example (Issue #2 fix) now provides a complete LLM integration example
   - **Note**: The basic example is still useful for understanding graph structure without LLM dependencies

5. **FIXED - langgraph-sdk vs langgraph Distinction Not Clear**
   - **Issue**: The SDK example used `from langgraph_sdk import get_sync_client` but the distinction between `langgraph` and `langgraph-sdk` packages wasn't explained
   - **Fix**: Added explanatory note before the "Testing Deployed API" section clarifying:
     - `langgraph` is for building and defining graphs locally
     - `langgraph-sdk` is a lightweight client library for deployed servers
   - **Location**: LangGraph-CLI-Guide.md, lines 741-747

6. **FIXED - Stream Response Format Not Documented**
   - **Issue**: The curl testing example showed `stream_mode: "updates"` but didn't document the response format
   - **Fix**: Added "Understanding Stream Response Format" section including:
     - SSE format explanation (event, data, id)
     - Example response output
     - Table of all stream modes (updates, values, messages, events)
     - Python code example for parsing SSE
   - **Location**: LangGraph-CLI-Guide.md, lines 799-843

7. **FIXED - Add Wolfi Image Recommendation**
   - **Issue**: The CLI recommends using Wolfi Linux for enhanced security, but document didn't mention it
   - **Fix**: Added `"image_distro": "wolfi"` to Python langgraph.json example and included a security recommendation note explaining:
     - Smaller image sizes (faster deployments)
     - Fewer vulnerabilities (minimal attack surface)
     - Regular security updates
   - **Location**: LangGraph-CLI-Guide.md, lines 111-125

8. **FIXED - Environment Variable Validation**
   - **Issue**: The document didn't emphasize the importance of proper .env file configuration
   - **Fix**: Added comprehensive "Environment Variables Configuration" section including:
     - Example .env file with OpenAI and Azure OpenAI options
     - LangSmith configuration
     - Best practices (gitignore, validation, environment-specific files, documentation)
     - Python validation pattern code example
   - **Location**: LangGraph-CLI-Guide.md, lines 422-479

---

## Verification Notes

All examples from the LangGraph CLI Guide were implemented and tested:

| Test | Status | Notes |
|------|--------|-------|
| Basic langgraph.json | PASS | Works as documented |
| Python agent example | PASS | Basic example works |
| Azure OpenAI agent | PASS | Works with Azure credentials |
| langgraph dev | PASS | Server starts correctly on port 2024 |
| API testing | PASS | Both assistants accessible via API |
| pytest unit tests | PASS | All 4 tests pass |
| langgraph build | PASS | Docker image builds successfully |
| langgraph dockerfile | PASS | Generates correct Dockerfile |

---

## Summary

**Current Status:** All 10 issues resolved.

| Priority | Issue | Status |
|----------|-------|--------|
| MEDIUM | Issue #9: Python version mismatch | ✅ Fixed - December 26, 2025 |
| LOW | Issue #10: pyproject.toml format differs from guide | ✅ Fixed - December 26, 2025 |

The LangGraph CLI Guide document is complete with:
- Correct code examples (Zod import fixed)
- Azure OpenAI integration guidance
- Complete dependency specifications for Python and JavaScript
- Clear distinction between langgraph and langgraph-sdk packages
- Comprehensive stream response format documentation
- Security recommendations (Wolfi image)
- Environment variable management best practices
