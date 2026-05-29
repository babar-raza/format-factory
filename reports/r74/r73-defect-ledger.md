# R73 Defect Ledger

**Sprint:** FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Previous sprint:** R73

---

## Defects

### IV-R74-001 — Stale SHAs inside inner evidence ZIP

- **Severity:** RC-BLOCKING
- **Category:** Build-order / proof-integrity
- **Status:** REPAIRED in R74 Train C+K
- **Description:** `repo/reports/r73/final-verdict.md` inside the inner evidence ZIP (ffa23117...)
  records stale SHA values for BUNDLE_VALIDATION_PASS_2_SHA (e4784a0f instead of ffa23117),
  SIDECAR_SHA (fdff3bb9 instead of 12ecae49), and DELIVERY_PACKAGE_RECORDED_SHA (4f2b2917 instead of 0733856f).
- **Root cause:** Bundle was rebuilt from commit f2d0c6b state. After commits b7cc298 and 72c620f
  updated final-verdict.md with correct SHAs, a subsequent "rebuild" did not produce a new ZIP
  because the R73 session ended before verifying the bundled verdict content.
- **Fix:** In R74, implement the three-pass build protocol: (1) Pass 1 SHA committed; (2) final
  metadata committed; (3) Pass 2 built AFTER all SHA commits; (4) sidecar generated; (5) sidecar
  SHA committed; (6) bundle NOT rebuilt after sidecar commit (sidecar is authority). The bundled
  final-verdict will show Pass-1 SHA (real), Pass-2 SHA (real from pass-2 build), and SIDECAR_SHA
  delegated to external sidecar.

### IV-R74-002 — PENDING_BUNDLE_BUILD in external-sidecar-proof-summary.txt

- **Severity:** RC-BLOCKING
- **Category:** Stale metadata placeholder
- **Status:** REPAIRED in R74 (metadata file updated + validator hardened)
- **Description:** `external-sidecar-proof-summary.txt` contains `EXTERNAL_SIDECAR_PROOF_SUMMARY:
  PENDING_BUNDLE_BUILD`. This placeholder was written before the sidecar was generated and never
  updated with the actual sidecar values.
- **Root cause:** File was pre-written as a template; R73 bundle build never updated it.
- **Fix:** Update file with actual sidecar values before Pass 2 build. Add PENDING_BUNDLE_BUILD
  to PENDING_MARKER_PATTERNS in validator.

### IV-R74-003 — "full suite -> PENDING" in validation-command-log.txt

- **Severity:** RC-BLOCKING
- **Category:** Stale metadata placeholder
- **Status:** REPAIRED in R74 (metadata file updated + validator hardened)
- **Description:** `validation-command-log.txt` line 24 contains `-> PENDING`, indicating the full
  test suite result was never filled in.
- **Root cause:** Template written before authoritative test run completed.
- **Fix:** Update command log with real test suite results. Add `-> PENDING` pattern to validator.

### IV-R74-004 — [to be filled] placeholders in final-independent-verification.txt

- **Severity:** RC-BLOCKING
- **Category:** Stale metadata placeholder
- **Status:** REPAIRED in R74 (metadata file updated + validator hardened)
- **Description:** `final-independent-verification.txt` contains three `[to be filled after X]`
  placeholders for SHA fields.
- **Root cause:** File was pre-written; SHA fields never updated. Validator misses `.txt` extension
  (CLOSEOUT_HYGIENE_REPORT_FILES only checks `.md`).
- **Fix:** Update file with real SHA values. Add `.txt` extension and `[to be filled after`
  pattern to validator closeout hygiene check.

### IV-R74-005 — Validator passed stale placeholders

- **Severity:** RC-BLOCKING
- **Category:** Validator gap
- **Status:** REPAIRED in R74 Train B
- **Description:** Running `validate_evidence_bundle.py --check-no-pending` returns PASS despite
  IV-R74-002, 003, 004 being present in the metadata files.
- **Root cause:** Missing patterns in PENDING_MARKER_PATTERNS; CLOSEOUT_HYGIENE_REPORT_FILES
  uses wrong file extension for final-independent-verification.
- **Fix:** Add missing patterns; fix extension; add 6 new test files proving hardening.

### IV-R74-006 — Missing-sidecar negative proof is stub

- **Severity:** MODERATE
- **Category:** Negative proof gap
- **Status:** REPAIRED in R74 Train K
- **Description:** `missing-sidecar-negative-proof.txt` references test file names but contains no
  actual command invocation, stdout/stderr capture, or exit code proving that validation fails.
- **Fix:** Run actual failing validation command; capture output; write to proof file.

### IV-R74-007 — Wrong-sidecar negative proof is stub

- **Severity:** MODERATE
- **Category:** Negative proof gap
- **Status:** REPAIRED in R74 Train K
- **Description:** Same as IV-R74-006 for wrong-sidecar scenario.
- **Fix:** Run actual failing validation command with wrong sidecar; capture output.

### IV-R74-008 — ZST Unicode example failure

- **Severity:** RC-BLOCKING
- **Category:** Test failure
- **Status:** REPAIRED in R74 Train D
- **Description:** `test_zst_example_runs_without_crash` fails with UnicodeEncodeError because
  `compress_decompress_file.py` prints `→` (U+2192) which cp1252 cannot encode.
- **Fix:** Replace `→` with `->` in compress_decompress_file.py; add encoding-safety test.

### IV-R74-009 — INV-011 stale reference in state/current-state.md

- **Severity:** MODERATE
- **Category:** State drift
- **Status:** REPAIRED in R74 Train I
- **Description:** state/current-state.md Production Blockers still lists INV-011 referencing
  "shows R72" even though the file header now shows R73.
- **Fix:** Run state_snapshot.py to regenerate current-state.md for R74.

---

## Summary

Total defects: 9
RC-blocking: 5 (IV-R74-001..005, 008)
Moderate: 4 (IV-R74-006, 007, 009)
All defects: REPAIRED in R74
