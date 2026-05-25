# R64 Train A — R63 Independent Verification

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25
**Prior sprint:** FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001

---

## Classification

R63 is reclassified as:
R63_BROAD_PRODUCT_AND_WORKAHEAD_PROGRESS_ACCEPTED_SELF_VERIFYING_RC_REJECTED

---

## Defect Ledger

### IV-R63-001: No external sidecar delivered with uploaded ZIP
- **Severity:** CRITICAL
- **Evidence:** Sidecar file `.local/r63-pass2-final.sha256-proof.json` exists locally but was not included in the delivery. Contract requires `sidecar_required: true` and `final_proof_policy: external_sidecar`.
- **Verification:** `ls -la .local/r63-pass2-final.sha256-proof.json` shows file exists locally; verifier received only the ZIP.
- **R64 repair:** Train B — generate and deliver both ZIP and sidecar.

### IV-R63-002: Validation without sidecar fails
- **Severity:** CRITICAL
- **Evidence:** `python tools/evidence/validate_evidence_bundle.py --bundle .local/r63-pass2-final.zip --check-no-pending --contract ... → BUNDLE_VALIDATION: FAIL (SIDECAR_REQUIRED)`
- **Verification:** Deterministic command above.
- **R64 repair:** Train B + M — validate with sidecar and prove pass.

### IV-R63-003: final-bundle-validation-proof.txt has placeholder language
- **Severity:** HIGH
- **Evidence:** `.local/r63-metadata/final-bundle-validation-proof.txt` lines 16-18: `SHA-256: to be computed`, `BUNDLE_BUILD: to be confirmed`, `BUNDLE_VALIDATION: to be confirmed`
- **Verification:** `grep "to be" .local/r63-metadata/final-bundle-validation-proof.txt`
- **R64 repair:** Train B — final proof must have no placeholder tokens.

### IV-R63-004: R63 report SHA history shows intermediate SHA
- **Severity:** MEDIUM
- **Evidence:** R63 final-verdict was committed with SHA `2572391bf...` (commit 7c3b32e) before final rebuild produced `355482ce...` (commit ebac1e5). The final committed verdict has the correct SHA but the intermediate commit created a SHA-mismatch window.
- **Verification:** `git log --oneline reports/r63/final-verdict.md` shows two SHA updates.
- **R64 repair:** Train M — single Pass 2 SHA update after final rebuild only.

### IV-R63-005: Sidecar tests skip actual delivered-sidecar file checks
- **Severity:** HIGH
- **Evidence:** R63 sidecar tests use `pytest.skip()` when sidecar/verdict files are absent, meaning they pass in any environment. 26 PASS, 11 SKIP — but the 11 skips include the actual sidecar-exists verification.
- **Verification:** `pytest tests/evidence/test_r63_final_response_sidecar_path_exists.py -v` — skipped tests are the file-existence checks.
- **R64 repair:** Train B — R64 tests must validate sidecar existence without skip when bundle is present.

### IV-R63-006: Artifact discovery not run-aware for extracted bundles
- **Severity:** HIGH
- **Evidence:** `find_artifact_dir()` checks `bundle-metadata/package-artifacts/` which is not run-specific. In an extracted bundle environment, requesting `r99999` would return the extracted bundle's artifacts. Currently returns None in source tree because `bundle-metadata/` doesn't exist.
- **Verification:** Code review of `tools/packaging/find_bundle_artifacts.py` lines 63-70 — candidates 2-4 are not run-gated.
- **R64 repair:** Train C — add run-awareness to non-local candidates.

### IV-R63-007: Legacy packaging tests depend on .local/package-builds
- **Severity:** MEDIUM
- **Evidence:** Legacy `tests/packaging/` tests reference `.local/package-builds` paths that don't exist in extracted bundles.
- **Verification:** `grep -r "package-builds" tests/packaging/`
- **R64 repair:** Train C — separate source-build and extracted-bundle test modes.

### IV-R63-008: R63 packaging test passes from source tree but needs extracted-bundle mode
- **Severity:** MEDIUM
- **Evidence:** `test_r63_package_rc.py` passes 21/21 from source tree using `.local/r63-metadata/package-artifacts/`. From extracted bundle without this path, tests would skip via `_skip_if_no_artifacts()`.
- **Verification:** All 21 tests pass locally; extracted-bundle mode would need `FORMAT_FACTORY_BUNDLE_METADATA_DIR` env var.
- **R64 repair:** Train C — explicit extracted-bundle RC test.

### IV-R63-009: AI reviewers all fixture-only (0 tokens, 0 calls)
- **Severity:** LOW
- **Evidence:** All 6 R63 AI reviewer JSON files show `token_usage: 0`, `api_calls_count: 0`, `mode: fixture`, `ai_not_live: true`.
- **Verification:** `python -c "import json,glob; ..."` confirms all files.
- **R64 repair:** Train G — AI_NOT_LIVE explicitly declared in verdict.

### IV-R63-010: Work-ahead is report-heavy, lacks concrete code/tests
- **Severity:** LOW
- **Evidence:** R63 work-ahead produced 6 report files but no concrete test scaffolds, fixture manifests, or validator gap implementations.
- **Verification:** `ls reports/r63/workahead-* reports/r63/r64-readiness-matrix.md reports/r63/validator-gap-analysis.md reports/r63/publication-readiness.md`
- **R64 repair:** W1-W7 — concrete deliverables per lane.

### IV-R63-011: R63 accepted real progress
- **Severity:** N/A (positive finding)
- **Evidence:** Clean bundle structure (no pycache/pyc), 10+10+2 artifacts with valid SHA-256, FODS 11 + FODT 11 APIs exported, installed wheel proof passes, 108 new tests PASS, 4726 total tests pass.
- **Status:** ACCEPTED

### IV-R63-012: Phase Audit 14 partial — sidecar delivery and packaging replay failed
- **Severity:** MEDIUM
- **Evidence:** `reports/r63/phase-audit-14.md` — Phase Audit 14 was declared PASS but sidecar was not delivered and packaging replay was not fully normalized.
- **R64 repair:** Train J — Phase Audit 14 repair.

### IV-R63-013: Scoreboard Train M shows intermediate status
- **Severity:** LOW
- **Evidence:** Scoreboard was updated to show final Pass 2 SHA but the proof metadata inside the bundle still has placeholders (IV-R63-003).
- **R64 repair:** Train M — scoreboard and proof must agree.

---

## Summary

| Category | Count |
|---|---|
| CRITICAL defects | 2 (IV-R63-001, IV-R63-002) |
| HIGH defects | 3 (IV-R63-003, IV-R63-005, IV-R63-006) |
| MEDIUM defects | 4 (IV-R63-004, IV-R63-007, IV-R63-008, IV-R63-012) |
| LOW defects | 3 (IV-R63-009, IV-R63-010, IV-R63-013) |
| Positive findings | 1 (IV-R63-011) |
| **Total defects** | **12** |

---

R63_IV_STATUS: COMPLETE
