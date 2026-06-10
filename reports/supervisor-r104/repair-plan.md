# R104 Repair and Advancement Plan

## Fixes Applied

### Fix 1: Materializer diffs ALL changed files (not just src/*)
- File: tools/supervisor/materialize_declared_evidence.py
- Before: Only generated diffs for files matching `src/*`
- After: Diffs ALL declared changed_files (tools, tests, supervisor scripts)
- Bug found and fixed: `src_changes` variable removed but 2 references remained (lines 264, 307) → replaced with `diffs`

### Fix 2: Package builder includes changed files + stream identity
- File: tools/supervisor/build_declaration_review_package.py
- Added `changed-files/` section: all declared changed_files are packaged
- Added stream identity validation: detects wrong-stream references in state files
- Package manifest now includes `stream_identity_warnings` and `declared_changed_files_count`

### Fix 3: ACCEPTED_VERIFIED requires concrete proof
- File: tools/supervisor/grade_declared_work.py
- Before: Any completed item with evidence paths → ACCEPTED_VERIFIED
- After: ACCEPTED_VERIFIED requires `tests_with_content` or `acceptance_criteria_verified`
- Path-only evidence now gets ACCEPTED_WITH_LIMITATIONS with documented reason

### Fix 4: Test suite alignment
- tests/supervisor/test_r103_cross_stream_and_grading.py: Updated sprint-reports/ → sprint-evidence/ prefix
- tests/supervisor/test_r100_grade_engine.py: Updated path-only grade expectation + added concrete proof test
- tests/supervisor/test_r100_review_package.py: Updated to R105 global-state/ prefix layout

## Test Results
- R104 tests: 17 passed
- R103 tests: 32 passed
- R100 tests: 24 passed
- Full supervisor suite: 666 passed, 2 pre-existing failures (stale ledger)
