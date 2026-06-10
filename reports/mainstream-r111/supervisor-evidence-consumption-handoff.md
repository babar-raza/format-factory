# Supervisor Evidence-Consumption Handoff

## From: Mainstream Stream (R111)
## To: Supervisor/Acceleration Stream
## Date: 2026-06-03

## Problem Statement
The supervisor grading pipeline grades all R110 items as ACCEPTED_WITH_LIMITATIONS (evidence_quality_score=0.0)
despite all test files, raw logs, source diffs, and skill transcripts being present on disk. This blocks
autonomous continuation even though product work is verified.

## Defects Identified

### D110-SUP-01: Inspector fallback guard too strict
**File:** `tools/supervisor/inspect_declared_evidence.py`
**Line:** 223
**Current code:**
```python
if not tests_with_content and not tests_empty_or_stub and test_summaries:
```
**Problem:** When `tests_supporting` field is absent in the declaration, `tests=[]` and `test_summaries=[]`.
The `test_summaries` guard prevents the fallback from scanning `evidence_paths` for test files.
**Fix:**
```python
if not tests_with_content and not tests_empty_or_stub:
```
Remove the `test_summaries` guard so evidence_paths are always scanned when no test files found yet.

### D110-SUP-02: Criteria verification limited to first 3 evidence paths
**File:** `tools/supervisor/inspect_declared_evidence.py`
**Line:** 210
**Current code:**
```python
for fp in found_paths[:3]:
```
**Problem:** Raw test logs often appear at position 4+ in evidence_paths. The criteria pattern "PASS" or
test count strings are in the log, not in source/test files.
**Fix:** Check all found_paths, or at least increase limit to 10.

### D110-SUP-03: Transcript validation only handles JSON
**File:** `tools/supervisor/inspect_declared_evidence.py` (check_transcript_in_evidence function)
**Problem:** R110 skill transcripts are Markdown files with structured front-matter, not JSON.
The validator skips them because JSON parsing fails.
**Fix:** Add Markdown transcript parsing (check for `# Skill Transcript:` header pattern).

## Failing Examples from R110

### Example 1: R110-WAVE-4A-FODS-GETCELLDATATYPE
- evidence_paths includes `tests/net/fods/FodsR110GetCellDataTypeTests.cs` (position 0)
- File exists, contains 8 test methods with `[Fact]` attributes
- Inspector returned `tests_with_content: []` because no `tests_supporting` and fallback blocked
- Expected grade: ACCEPTED_VERIFIED
- Actual grade: ACCEPTED_WITH_LIMITATIONS

### Example 2: R110-WAVE-5A-ZST-WORKFLOW
- evidence_paths includes `tests/python/zst/test_r110_zst_multiframe_workflow.py` (position 0)
- File exists, contains 8 test functions with `test_` prefix
- Same fallback issue
- Expected grade: ACCEPTED_VERIFIED
- Actual grade: ACCEPTED_WITH_LIMITATIONS

## Expected Corrected Behavior
After fixing D110-SUP-01/02/03:
- 13/13 product items should be ACCEPTED_VERIFIED
- evidence_quality_score should be >= 0.72 (13/18, 5 process items may remain WITH_LIMITATIONS)
- continuation_state should be YES
- stop_reason should be null

## Tests Supervisor/Acceleration Should Add
1. Test that items with evidence_paths containing test files but no tests_supporting still get tests_with_content populated
2. Test that criteria verification scans beyond first 3 evidence paths
3. Test that Markdown skill transcripts are recognized as valid transcripts
4. Test that evidence_quality_score > 0 when test files exist in evidence_paths
