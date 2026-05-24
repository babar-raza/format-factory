# Bundle / Sidecar / Proof Protocol Repair — R57 Train B

**Sprint:** FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
**Train:** B — Bundle/Sidecar/Proof Protocol Repair
**Date:** 2026-05-23
**Closes:** IV-R56-001, IV-R56-002, IV-R56-003/004, IV-R56-008 (partial — full proof in Train L)

---

## 1. Validator PENDING Pattern Repair (IV-R56-003/004)

Added `BUNDLE_VALIDATION_PASS_2_SHA: PENDING` and `BUNDLE_VALIDATION_PASS_1_SHA: PENDING` to:

### 1.1 PENDING_MARKER_PATTERNS
`tools/evidence/validate_evidence_bundle.py` — scanned by `check_no_pending_reports()`.
Catches these patterns in ANY metadata file including `final-verdict.md`.

### 1.2 STATUS_LINE_PATTERNS (inside check_repo_reports_pending)
Same function in `check_repo_reports_pending()` — scans `repo/reports/*/final-verdict.md`
inside the bundle ZIP.

Both patterns now trigger FAIL when present as standalone status lines in verdict files.
Markdown list references (`- BUNDLE_VALIDATION_PASS_2_SHA: PENDING`) are still excluded
per the existing status-line detection logic.

---

## 2. Validator Wheel SHA Length Enforcement (IV-R56-007)

Added truncated-SHA detection in `check_artifact_inventory()`:
- Scans manifest for `sha256:`, `SHA-256:`, or `wheel_sha256:` lines
- If a hex value is found with length != 64, emits `ARTIFACT_SHA_TRUNCATED` error
- Error includes length, value, and fix suggestion
- Runs before artifact count validation — catches manifest written with MD5 values

This catches the R56 defect where `wheel_sha256: 9c10377a...` (32 chars) was silently skipped.

---

## 3. R57 Contract with Sidecar Policy (IV-R56-002)

`tools/evidence/contracts/r57-self-verifying-rc-replay.yaml` created with:
- `sidecar_required: true`
- `final_proof_policy: external_sidecar`
- `require_clean_git: true`
- `min_metadata_count: 30`
- `installed_artifact_policy: self_contained`
- 26 required repo files + 24 required metadata files

---

## 4. Test Evidence

### New test files (30 tests total):

| File | Tests | Description |
|------|-------|-------------|
| test_r57_pending_marker_strictness.py | 8 | PENDING_MARKER_PATTERNS + check_repo_reports_pending SHA-keyed variants |
| test_r57_sidecar_required_top_level.py | 11 | sidecar_required and final_proof_policy contract field enforcement |
| test_r57_final_proof_completeness.py | 11 | Final proof completeness schema (fields required in R57 proof) |

**All 30/30 tests PASS.**

---

## 5. Proof Completeness Standard (IV-R56-008)

The R57 final proof (built in Train L) must include:
1. Bundle filename (`r57-*.zip`)
2. SHA-256 Pass 1 (64 hex chars)
3. SHA-256 Pass 2 (64 hex chars)
4. Size in bytes
5. Entry count
6. Sidecar proof path
7. `BUNDLE_VALIDATION: PASS` confirmation
8. Sprint ID

Tests in `test_r57_final_proof_completeness.py` define and verify the schema.
Actual proof file is built in Train L after the final bundle run.

---

**STATUS: TRAIN_B_COMPLETE — 30 new tests; validator hardened; R57 contract created**
