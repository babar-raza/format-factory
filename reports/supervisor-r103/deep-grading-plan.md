# Deep Grading v3 Plan

## Root Cause: tests_supporting always empty
Declaration schema field: `tests_supporting`
R102 declarations used: `test_references`
Inspector reads: `item.get("tests_supporting", [])` — never finds `test_references`

## Fix Applied
`inspect_declared_evidence.py` line 71 now reads:
```python
tests = item.get("tests_supporting", []) or item.get("test_references", [])
```

## Deep Grading Rules (grade_declared_work.py)
1. Path-only (no content) -> OVERCLAIMED
2. Stub test files -> ACCEPTED_WITH_LIMITATIONS
3. Missing paths -> REWORK_REQUIRED
4. Failed tests -> REWORK_REQUIRED
5. No tests_supporting for test-backed claims -> now populated correctly

## Test Coverage
- tests/supervisor/test_r103_cross_stream_and_grading.py: 5 grading tests + 4 inspector tests
