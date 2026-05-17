# R20 Evidence Hygiene Hardening Report
Sprint: FORMAT-FACTORY-R20-PRODUCTIZATION-TRAIN-ZST-FODP-FODG-GNUMERIC-ABW-SOURCE-AND-GATE11-ARCHITECTURE-SWARM-001
Date: 2026-05-16

## Problem Statement (from R19)

R19 final bundle had r19-sprint-gate-status.md with Gate 19 as "IN PROGRESS" even though the
bundle validation passed. The existing PENDING_MARKER_PATTERNS did not catch "| IN PROGRESS |"
table-row patterns in sprint-gate-status metadata files.

Additionally, no automated check enforced AUTHORITATIVE_TEST_RESULT presence in final bundles.

## Changes Made

### tools/evidence/validate_evidence_bundle.py

**Added to PENDING_MARKER_PATTERNS:**
- `"| IN PROGRESS |"` — catches markdown table rows (e.g., sprint-gate-status.md)
- `"| IN_PROGRESS |"` — catches YAML-style underscored variant

These patterns are checked when `--check-no-pending` is passed. Any metadata file containing
them will cause BUNDLE_VALIDATION: FAIL.

**Added function: `check_authoritative_test_result_present()`**
- Scans all metadata files for `AUTHORITATIVE_TEST_RESULT`
- Returns error list if not found in any metadata file
- Called when `--check-no-pending` is active
- Enforces P-EVID-003: test counts are unambiguous

**Updated `validate_bundle()` to call the new check and print result.**

### tests/evidence/test_negative_bundle_validation.py

**Added 4 new test functions:**
1. `test_in_progress_gate_status_fails_with_flag` — P-EVID-002 enforcement
2. `test_in_progress_gate_status_passes_without_flag` — guard is off without flag
3. `test_missing_authoritative_test_result_fails` — P-EVID-003 enforcement
4. `test_present_authoritative_test_result_passes` — correct AUTHORITATIVE_TEST_RESULT accepted

**Fixed existing test:** `test_closure_contradiction_passes_when_consistent` — added
`AUTHORITATIVE_TEST_RESULT` line to its bundle since it uses `--check-no-pending`.

## Test Results

26 passed, 0 failed (was 25 passed, 1 failed before fix)

## Policy Coverage

| Policy | Guard | Test Coverage |
|--------|-------|---------------|
| P-EVID-001 | Post-commit bundle (process, not automated) | N/A |
| P-EVID-002 | IN_PROGRESS detection in PENDING_MARKER_PATTERNS | 2 new tests |
| P-EVID-003 | AUTHORITATIVE_TEST_RESULT check | 2 new tests |
| P-EVID-004 | Verdict stale HEAD (existing closure contradiction check) | existing tests |

## R20 Bundle Impact

The R20 final bundle will use `--check-no-pending`. Therefore:
- Final sprint gate status file must say COMPLETE (not IN PROGRESS) for all gates
- At least one metadata file must contain AUTHORITATIVE_TEST_RESULT

EVIDENCE_HYGIENE_HARDENING: COMPLETE
