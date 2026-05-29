# R74 Evidence Validator Hardening

**Sprint:** FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Train:** B

---

## Changes to validate_evidence_bundle.py

### 1. PENDING_MARKER_PATTERNS additions (IV-R74-002, 003)

Added to `PENDING_MARKER_PATTERNS`:
- `"PENDING_BUNDLE_BUILD"` — catches sidecar-proof-summary stale placeholder
- `"-> PENDING"` — catches `full suite -> PENDING` in validation-command-log.txt
- `"full suite -> PENDING"` — explicit variant
- `"suite -> PENDING"` — explicit variant

These patterns are checked in `check_no_pending_reports()` against all bundle-metadata/ files
(excluding git-log.txt, git-status files).

### 2. CLOSEOUT_HYGIENE_TOKENS additions (IV-R74-004)

Added to `CLOSEOUT_HYGIENE_TOKENS`:
- `"[to be filled after"` — catches `[to be filled after Pass N build]` variants
- `"to be generated after"` — catches deferred-generation placeholders
- `"pending_bundle_build"` — lowercase variant for closeout hygiene check

### 3. CLOSEOUT_HYGIENE_REPORT_FILES additions (IV-R74-004)

Added to `CLOSEOUT_HYGIENE_REPORT_FILES`:
- `"final-independent-verification.txt"` — the `.txt` variant used in R73
- `"external-sidecar-proof-summary.txt"` — explicitly scanned for placeholder patterns
- `"validation-command-log.txt"` — explicitly scanned for placeholder patterns

### 4. check_negative_proof_quality() (IV-R74-006, 007)

New function added at line ~769. Checks that negative proof files contain actual
command evidence (validate_evidence_bundle invocation, exit code, or FAIL marker).
Issues warnings (not errors) when files are stubs. Wired into the validation loop
after `check_negative_sidecar_proofs_present()`.

---

## New Test Files (35 tests total)

| File | Tests | Coverage |
|---|---|---|
| test_r74_rejects_pending_bundle_build_in_sidecar_summary.py | 4 | PENDING_BUNDLE_BUILD detection |
| test_r74_rejects_validation_command_log_pending.py | 4 | -> PENDING in command log |
| test_r74_rejects_to_be_filled_placeholders.py | 6 | [to be filled after] detection |
| test_r74_rejects_stale_final_verdict_sha.py | 6 | PENDING SHA in final-verdict |
| test_r74_requires_real_negative_proof_logs.py | 7 | Negative proof quality check |
| test_r74_current_run_placeholder_scope.py | 8 | Scope/false-positive tests |

---

## Proof: R73-Style Stale Bundle Would Now Fail

The following R73 metadata files would NOW fail `--check-no-pending`:
1. `external-sidecar-proof-summary.txt` with `PENDING_BUNDLE_BUILD` → FAIL (PENDING_MARKER_PATTERNS)
2. `validation-command-log.txt` with `-> PENDING` → FAIL (PENDING_MARKER_PATTERNS)
3. `final-independent-verification.txt` with `[to be filled after]` → FAIL (CLOSEOUT_HYGIENE_TOKENS)

Confirmed by test_r74_rejects_pending_bundle_build_in_sidecar_summary.py::test_r73_style_stale_bundle_would_fail,
test_r74_rejects_validation_command_log_pending.py::test_r73_stale_command_log_rejected,
test_r74_rejects_to_be_filled_placeholders.py::test_r73_stale_final_iv_rejected.

All 35 tests PASS.

VALIDATOR_HARDENING: PASS
