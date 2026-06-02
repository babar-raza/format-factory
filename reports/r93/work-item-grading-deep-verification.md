---
sprint: R93
generated_by: r93-worker
train: D
---

# Work-Item Grading Deep Verification (Train D)

Sprint: FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

## Problem (D92-03)

Prior grading only checked path existence. An item with empty test files or
placeholder evidence files could be graded ACCEPTED incorrectly.

## Changes Made

### `tools/supervisor/inspect_declared_evidence.py` — Deep Content Inspection

Added `check_test_file_content(test_path)` function that:
- For `.cs` files: checks for `[Fact]`, `[Theory]`, test method patterns
- For `.py` files: counts `def test_*` methods
- Returns `{has_content: bool, method_count: int, reason: str}`

Enhanced `inspect_item()` to populate:
- `tests_with_content: list[str]` — test files with actual test methods found
- `tests_empty_or_stub: list[str]` — test files with no test methods
- `acceptance_criteria_verified: bool` — whether key pattern from acceptance_criteria appears in evidence
- `acceptance_criteria_pattern: str` — extracted pattern checked

### `tools/supervisor/grade_declared_work.py` — Deep Grade Rules

Enhanced the "completed with evidence, no missing paths" path to:
1. Check `tests_empty_or_stub` → if any, emit ACCEPTED_WITH_WARNINGS with failed criterion
2. Check `acceptance_criteria_verified` → if pattern not found, emit ACCEPTED_WITH_WARNINGS
3. Only emit plain ACCEPTED if all deep checks pass

## Grade Level Mapping (After Fix)

| Condition | Grade |
|-----------|-------|
| All paths found + tests have content + criteria verified | ACCEPTED |
| All paths found + tests have content + criteria not checkable | ACCEPTED |
| All paths found + test files exist but empty/stub | ACCEPTED_WITH_WARNINGS |
| All paths found + criteria pattern not found in evidence | ACCEPTED_WITH_WARNINGS |
| Missing paths | REWORK_REQUIRED |
| No evidence at all (declared complete) | OVERCLAIMED |
| Tests failed | REWORK_REQUIRED |
| External gate | BLOCKED_EXTERNAL_GATE |

## Backward Compatibility

The new fields (`tests_with_content`, `tests_empty_or_stub`, etc.) are additive.
Existing callers of `grade_all()` will still work — the new fields are only used
for the enhanced grade determination. Old grading logic preserved as fallback
when new fields are absent.

## Status: DEEP GRADING IMPLEMENTED
