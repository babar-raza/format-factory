# Cross-Stream Contamination Repair

## Fixes Applied in R103

### Fix 1: Inspector reads test_references alias
`inspect_declared_evidence.py` now reads both `tests_supporting` (schema) and
`test_references` (common alias). This fixes empty `tests_supporting` in grades.

### Fix 2: Evidence manifest includes declared artifacts
`evidence_manifest.py` now also iterates `evidence_artifacts` from the declaration
to include files that live outside `evidence_root`. Previously only scanned the
evidence_root directory, missing reports/ files.

### Fix 3: Package includes sprint reports
`build_declaration_review_package.py` now packages:
- All `evidence_artifacts` from the declaration under `sprint-reports/`
- All files from the review directory under `review/`

### Fix 4: Two new continuation states
- NO_WRONG_STREAM_CONTEXT — stops when context pack references wrong stream
- NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS — stops when ACCEPTED_VERIFIED has no logs

## Remaining: Per-Stream State Isolation
Full isolation (per-stream `reports/supervisor-{stream}/`) is deferred to R104.
R103 addresses the symptoms (packaging wrong state) with the review-directory approach.

## Test Evidence
32 tests in test_r103_cross_stream_and_grading.py, all passing.
