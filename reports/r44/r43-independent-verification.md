# R43 Independent Verification

**Sprint:** FORMAT-FACTORY-R44-TWO-PRODUCT-LOCAL-RC-BASELINE-001
**Date:** 2026-05-21
**Reviewing:** FORMAT-FACTORY-R43-AUTHORITY-PROOF-COMPLETE-001
**R43 commit:** adc208c (post-R43 batch acceptance chain)

## R43 Classification

**AUTHORITY_PROOF_ACCEPTED_PRODUCT_PROOF_PARTIAL**

R43 successfully closed all 10 R42 authority/proof blockers. The state snapshot is now
authoritative. Package build logs are present. However, product delivery proof (semantic
smoke, .NET consumer project, G11-G packet) remains incomplete.

---

## R43 Claim-by-Claim Verification

### Blocker 1: State snapshot regex fails for title-case bold verdict
**R43 Claim:** Fixed `state_snapshot.py` verdict regex to `r"\*{0,2}VERDICT:\*{0,2}\s*\*{0,2}([A-Z0-9_]+)"` with `re.IGNORECASE`
**Status:** VERIFIED
**Evidence:** `tools/state/state_snapshot.py` contains the corrected regex; `tests/state/test_state_snapshot.py::TestVerdictRegexFormats` has 6 tests all PASS

### Blocker 2: `state/current-state.md` showed `no_final_verdict`
**R43 Claim:** Fixed — regex repair means state now shows correct verdict after regeneration
**Status:** VERIFIED
**Evidence:** `state/current-state.md` shows `R43 — R43_AUTHORITY_PROOF_COMPLETE`

### Blocker 3: Rerunning `state_snapshot.py` still produced `unknown`
**R43 Claim:** Root cause was regex bug (case-sensitive, no bold marker); same fix resolves this
**Status:** VERIFIED (subsumed by Blocker 1 fix)

### Blocker 4: Root cause — case-sensitive regex, no bold marker handling
**R43 Claim:** Explicitly documented and fixed with `\*{0,2}` + `re.IGNORECASE`
**Status:** VERIFIED

### Blocker 5: Bundle validates despite state/verdict mismatch
**R43 Claim:** Added `check_state_verdict_agreement()` to `validate_evidence_bundle.py`
**Status:** VERIFIED
**Evidence:** `tests/evidence/test_r43_validator_hardening.py::TestStateVerdictMismatch` — 6 tests PASS

### Blocker 6: No artifacts (whl/nupkg) or raw build logs in evidence bundle
**R43 Claim:** Raw build/install/smoke logs added to `reports/r43/package-proof/python/` + `dotnet/`
**Status:** VERIFIED
**Note:** Actual .whl/.nupkg files are NOT in the bundle (local-only); logs are present. This is accepted — artifacts are local, logs prove the build.

### Blocker 7: No install logs, smoke logs, pack logs
**R43 Claim:** All 3 log types present in `reports/r43/package-proof/`
**Status:** VERIFIED
**Evidence:** `reports/r43/package-proof/python/fods-build-log.txt`, `fods-install-log.txt`, `fods-smoke-log.txt` + FODT equivalents; `reports/r43/package-proof/dotnet/fods-test-log.txt`, `fods-pack-log.txt` + FODT

### Blocker 8: `python -m build` missing from system Python
**R43 Claim:** Resolved via `.local/build-venv` with `build==1.5.0`
**Status:** VERIFIED
**Note:** Build venv is in `.local/` (gitignored). Reproducibility requires re-creating venv from instructions in `reports/r43/package-proof/python/package-proof-summary.md`.

### Blocker 9: `test_auto_proof_bundle.py` timed out after 7 tests
**R43 Claim:** All 9 tests pass with `--timeout=30`; timeout was environmental, not a code defect
**Status:** PARTIAL — `pytest-timeout` is NOT installed in system Python
**Note:** R43 ran with the CLI flag which requires the plugin. The plugin was not verified as installed. R44 Lane 1C must fix timeout portability.

### Blocker 10: State shows "Production Blockers: None detected" while real blockers remain
**R43 Claim:** Fixed `get_production_blockers()` — now reports G11-G, Gate 8, PACKAGE_NOT_PUSHED
**Status:** VERIFIED
**Evidence:** `state/current-state.md` shows 3 production blockers

---

## Additional R43 Claims

### FODS/FODT Deepening (21+25 tests)
**Status:** VERIFIED — `tests/python/fods/test_r43_deepening.py` (21), `tests/python/fodt/test_r43_deepening.py` (25) all PASS

### PGM/PBM/SYLK Gate 9 Deepening (7+6+6 tests)
**Status:** VERIFIED — all 19 tests PASS

### Validator Hardening (16 tests)
**Status:** VERIFIED — all 16 tests PASS

### `replay_extracted_bundle.py`
**Status:** PARTIAL — Script exists and REPLAY_VALIDATION: PASS on R42 bundle, but:
- Known pycache defect: Python imports during replay create `__pycache__` which gets repacked and may trigger forbidden-file check against contracts that exclude `**/__pycache__/**`
- R44 Lane 1B must fix this

### AUTHORITATIVE_TEST_RESULT: 1967 passed
**Status:** CLAIMED — not independently re-run in this IV (this is the R43 sprint's own count)
**Note:** Pre-existing failures documented as `tests/python/dif/test_dif_parser.py::TestDifProbe::test_probe_nonexistent` and `tests/python/ppm/test_ppm_parser.py::TestPpmProbe::test_probe_nonexistent`

---

## FODT Semantic Smoke Gap

R43's FODT smoke logged `block_count: None` for all samples, reporting `blocks=0 OK`. This
is insufficient — the smoke did not verify that actual semantic content (paragraphs, headings,
lists, tables) was detected. R44 Lane 2C must enforce a meaningful FODT semantic check.

---

## Summary

| Category | Verdict |
|----------|---------|
| State snapshot authority repair | ACCEPTED |
| Validator STATE_VERDICT_MISMATCH | ACCEPTED |
| Validator PACKAGE_PROOF_MISSING | ACCEPTED |
| Python package build logs | ACCEPTED |
| .NET test+pack logs | ACCEPTED |
| Auto-proof timeout (Blocker 9) | PARTIAL — pytest-timeout gap (R44 Lane 1C) |
| replay_extracted_bundle.py | PARTIAL — pycache defect (R44 Lane 1B) |
| FODT semantic smoke | INSUFFICIENT — blocks=0 OK (R44 Lane 2C) |

**R43 overall classification:** AUTHORITY_PROOF_ACCEPTED_PRODUCT_PROOF_PARTIAL

R44 accepts R43 as baseline and supersedes it for product delivery proof.

IV_VERDICT: R43_ACCEPTED_WITH_NOTED_GAPS
