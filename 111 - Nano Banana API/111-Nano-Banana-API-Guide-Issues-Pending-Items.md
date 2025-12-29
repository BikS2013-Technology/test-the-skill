# Issues and Pending Items - Nano Banana API Guide

**Document:** /Users/giorgosmarinos/aiwork/TrainingMaterial/111 - Nano-Banana-API-Guide.md
**Last Updated:** 2025-12-29
**Validation Completed:** 2025-12-28

## Summary

| Priority | Issue | Status |
|----------|-------|--------|
| MEDIUM | Issue #1: Image Blending missing response_modalities config | FIXED |
| LOW | Issue #2: ERD example may not generate images | FIXED (Documentation Note Added) |
| LOW | Issue #3: Sequence Diagram example may not generate images | FIXED (Documentation Note Added) |

## Pending Items

*No pending items - all issues have been resolved.*

---

## Completed Items

### Issue #1: Image Blending Example Missing response_modalities Config (MEDIUM) - FIXED

**Location:** Lines 217-243
**Date Fixed:** 2025-12-28

**Problem:** The Image Blending (Logo on Clothing) example did not include `response_modalities=['TEXT', 'IMAGE']` in the config. Without this, the API may return only text without generating an image.

**Fix Applied:** Added `config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE'],)` to the generate_content call.

---

### Issue #2: ERD Example May Not Generate Images (LOW) - FIXED

**Location:** Lines 652-696
**Date Identified:** 2025-12-28
**Date Fixed:** 2025-12-29

**Problem:** The Database ERD (Entity-Relationship Diagram) example consistently returns text-based diagram descriptions instead of generating actual images. The API appears to have limitations generating formal database diagrams with specific notation (PK, FK, crow's foot notation).

**Observed Behavior:** The API returns text describing the ERD structure rather than generating a visual image. This is a Gemini API limitation rather than a code issue.

**Fix Applied:** Added a documentation note to the Database Schema Diagrams section explaining that the API may return text-based descriptions or Mermaid syntax for formal ERD diagrams, and recommending dedicated diagramming tools for production use cases.

---

### Issue #3: Sequence Diagram Example May Not Generate Images (LOW) - FIXED

**Location:** Lines 703-755 (updated line numbers after Issue #2 fix)
**Date Identified:** 2025-12-28
**Date Fixed:** 2025-12-29

**Problem:** The Sequence Diagram example returns Mermaid diagram syntax instead of generating actual images. The API recognizes the request for a UML-style sequence diagram and provides text-based diagram code rather than an image.

**Observed Behavior:** API response includes Mermaid syntax:
```
```mermaid
sequenceDiagram
    actor Client as Client (web browser)
    ...
```

**Fix Applied:** Added a documentation note to the Sequence Diagrams section explaining that the API may return Mermaid syntax for UML-style sequence diagrams, and recommending Mermaid renderers or dedicated UML tools for production use cases.

---

## Verification Notes

| Test | Status | Notes |
|------|--------|-------|
| Python: Basic Text-to-Image | PASS | Lines 96-116 |
| Python: High-Resolution Generation | PASS | Lines 120-146, 2752x1536 output |
| Python: Image Editing (Inpainting) | PASS | Lines 150-176 |
| Python: Multiple Reference Images | PASS | Lines 180-213, 5 reference images |
| Python: Image Blending | PASS (after fix) | Lines 217-243 - Fixed Issue #1 |
| Python: Infographic | PASS | Lines 478-506 |
| Python: Architecture Diagram | PASS | Lines 554-592 |
| Python: Flowchart | PASS | Lines 600-644 |
| Python: Database ERD | API LIMITATION | Lines 652-696 - Documentation Note Added (Issue #2) |
| Python: Sequence Diagram | API LIMITATION | Lines 703-755 - Documentation Note Added (Issue #3) |
| Python: Tutorial/Process | PASS | Lines 758-795 |
| Python: Timeline | PASS | Lines 803-848 |
| Python: Multi-Turn Editing | PASS | Lines 858-919 |
| Python: Error Handling | PASS | Lines 1074-1123 |
| TypeScript: Basic Text-to-Image | PASS | Lines 257-283 |
| TypeScript: High-Resolution | PASS | Lines 287-318 |
| TypeScript: Image Editing | PASS | Lines 322-366 |
| TypeScript: Multiple Reference | SKIPPED | Same pattern as Python |
| TypeScript: Infographic | SKIPPED | Same pattern as Python |
| TypeScript: Multi-Turn Editing | SKIPPED | Same pattern as Python |
| TypeScript: Error Handling | PASS | Lines 1127-1196 |

## Test Output Files

All generated test images are saved in: `nano-banana-validation/output/`

| File | Size | Description |
|------|------|-------------|
| test_01_fox_painting.png | 1.9 MB | Basic text-to-image |
| test_02_water_cycle_infographic.png | 2.7 MB | High-res infographic |
| test_03_living_room_edited.png | 815 KB | Image editing |
| test_04_office_photo.png | 2.2 MB | Multiple reference images |
| test_05_woman_with_logo_v2.png | 1.5 MB | Image blending (fixed) |
| test_06_photosynthesis_infographic.png | 3.4 MB | Infographic |
| test_07_architecture.png | 2.2 MB | Architecture diagram |
| test_08_flowchart.png | 2.2 MB | Flowchart |
| test_11_tutorial.png | 3.4 MB | Tutorial diagram |
| test_12_timeline.png | 2.7 MB | Timeline |
| test_13_multiturn_v1.png | 953 KB | Multi-turn initial |
| test_13_multiturn_spanish.png | - | Multi-turn refined |
| test_14_error_handling.png | 1.4 MB | Error handling test |
| ts_test_01_basic.png | 1.9 MB | TypeScript basic |
| ts_test_02_highres.png | 2.9 MB | TypeScript high-res |
| ts_test_03_editing.png | 842 KB | TypeScript editing |
| ts_test_07_error_handling.png | 1.5 MB | TypeScript error handling |
