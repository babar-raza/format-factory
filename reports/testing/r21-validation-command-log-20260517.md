---
artifact_id: r21-validation-command-log
artifact_type: report
sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
date: "2026-05-17"
gate: "14"
visibility: internal
---

# R21 Gate 14 — Validation Command Log

## Commands Run

### 1. Current State Consistency
```
python tools/evidence/check_current_state_consistency.py
```
Result: CURRENT_STATE_CONSISTENCY: PASS

### 2. Evidence + Examples + Python Tests
```
python -c "...pytest..." tests/evidence tests/examples tests/python -q
```
Result: 398 passed, 4 skipped, 26 warnings

### 3. Full Suite (evidence + examples + python + skills)
```
python -c "...pytest..." tests/evidence tests/examples tests/python tests/skills -q
```
Result: 1634 passed, 12 skipped, 67 warnings in 273.81s (0:04:33)

## New Tests Added in R21

| Test File | Tests | Status |
|-----------|-------|--------|
| tests/evidence/test_python_package_matrix.py | 13 | PASS |
| tests/evidence/test_python_release_manifests.py | 50 (parametrized 5×10+matrix) | PASS |
| tests/examples/test_python_examples_smoke.py | 18 | PASS |
| Total new | ~81 | ALL PASS |

## R20 Baseline Preserved

All 1552 R20 tests continue to pass. No regressions introduced.

## AUTHORITATIVE_TEST_RESULT

AUTHORITATIVE_TEST_RESULT: 1634 passed, 12 skipped, 0 failed
