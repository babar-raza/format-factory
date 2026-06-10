# Grader Test Evidence Bugfix

## Bug: D98-GRADE-01
`inspect_declared_evidence.py` treated all `tests_supporting` entries as file paths.
Summary strings like "8 new tests, all passed" were checked via `check_test_file_content()`,
which returned `has_content: False`. The grader then classified real work as ACCEPTED_WITH_LIMITATIONS.

## Fix
1. Added path detection: entries with `/`, `\`, `.py`, `.cs`, or starting with `tests/` are file paths.
2. Other entries are classified as `test_summaries` (not errors).
3. When only summaries exist (no file paths in tests_supporting), the inspector falls back to
   checking `evidence_paths` for test files and verifies their content.
4. New return field: `test_summaries` lists summary-only entries.

## Verified
```python
# Before fix: tests_empty_or_stub: ['8 new tests, FODS total 247 passed']
# After fix: test_summaries: ['8 new tests, FODS total 247 passed']
#            tests_with_content: ['tests/net/fods/FodsR97GetCellCountTests.cs']
```
