# Grading Regression Tests — R118

**Sprint:** FORMAT-FACTORY-UNIFIED-POC-AUTHORITY-RECONCILIATION-R118-001

---

## Regression Test Scenarios

These scenarios should be covered to prevent regression of the grading machinery failures found in R118.

### Test 1: tests_supporting enables ACCEPTED_VERIFIED

**Given:** A declaration work item with `tests_supporting` listing a test file path
**When:** `inspect_item()` processes the item
**Then:** `tests_with_content` is populated, `has_concrete_proof=True`, item grades `ACCEPTED_VERIFIED`

### Test 2: missing tests_supporting → ACCEPTED_WITH_LIMITATIONS

**Given:** A declaration work item with no `tests_supporting` field
**When:** `inspect_item()` processes the item
**Then:** `tests_with_content=[]`, `has_concrete_proof=False`, item grades `ACCEPTED_WITH_LIMITATIONS`

### Test 3: raw_log artifact entries fix missing_raw_logs

**Given:** A declaration with `evidence_artifacts` containing `type: raw_log` entries pointing to existing log files
**When:** `detect_missing_raw_logs()` runs
**Then:** Logs found, `is_violation=False`

### Test 4: dirty_state_classification suppresses dirty_git_state violation

**Given:** A declaration with `git_status_final` indicating dirty state AND `dirty_state_classification` set
**When:** `detect_dirty_git_state()` runs
**Then:** `has_classification=True`, `is_violation=False`

### Test 5: changed_files NOT used for test detection

**Given:** A declaration with `changed_files` listing test file paths but no `tests_supporting`
**When:** `inspect_item()` processes the item
**Then:** `tests_with_content=[]` (changed_files is not the source for test detection)

---

## Test Location (if written)

`tests/supervisor/test_r118_grading_regression.py` — Not written in this sprint (documenting only).
These patterns are demonstrable via existing `test_r100_grade_engine.py` and
`tests/supervisor/test_r100_validators.py` test suites.
