# R53: Self-Verifying Baseline Sprint

**Sprint ID:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22
**Verdict:** R53_STATE_VALIDATOR_CLEAN_PRODUCT_PARTIAL

## R52 Correction

R52's verdict `R52_STATE_CONSISTENT_INSTALLED_ARTIFACT_BASELINE_CLEAN` was overclaimed.
Corrected R52 status: `R52_STATE_VERDICT_REPAIR_ACCEPTED_BASELINE_CLAIM_PARTIAL`

R52's real progress is preserved and accepted:
- State/verdict parser Format C repair (## Verdict + backtick)
- Validator hardening (check_state_verdict_agreement, check_proof_sha_consistency, etc.)
- 35 new guard tests

R52's overclaim:
- No artifact files in ZIP (zero .whl/.tar.gz/.nupkg)
- PASS 2 PENDING inside bundle proof (self-referential impossibility)
- No external sidecar proof produced
- No requirements matrix or gap ledger

## New Policies Adopted in R53

### Sidecar Proof Protocol

Final bundle cannot contain its own SHA. Protocol:
- Internal proof records PASS 1 SHA + PASS 2 result (no SHA)
- External sidecar `.sha256-proof.json` holds final SHA/size/entries
- Tool: `tools/evidence/write_sidecar_proof.py`
- Validator: `--sidecar-proof <path>` flag added to `validate_evidence_bundle.py`
- 8 tests in `tests/evidence/test_r53_sidecar_proof.py` all pass

### Installed Artifact Baseline Policy

Three tiers:
- Option A: Self-contained (artifacts in ZIP) — required for `_CLEAN` verdict suffix
- Option B: External reference (unchanged from prior sprint) — requires `_EXTERNAL_REF` or `_PARTIAL` suffix
- Option C: No claim — validator/docs-only sprints

R52 used Option B structure but Option A verdict. R53 corrects this.

## FODS Formula Preservation (TC-0054) — CLOSED

- Parser already captured `formula` attr (IR-FODS-008)
- Writer now emits `table:formula` verbatim (5-line fix in `_write_cell()`)
- `tests/python/fods/test_r53_formula_preservation.py`: 7/7 pass

## Requirements Matrix + Gap Ledger

First-ever requirements matrix for this project:
- `reports/r53/requirements-vs-actual-matrix.md` + `.json` (22 requirements)
- `reports/r53/gap-ledger.md` + `.json` (10 gaps, 2 remediated in R53)

## Test Results

- AUTHORITATIVE_TEST_RESULT: 3584 passed (non-AI), 13 skipped, 3 pre-existing fail
- Evidence suite: 882 passed (874 + 8 new sidecar proof tests)
- Formula tests: 7 new tests
- Pre-existing failures: test_build_report_all_built (hardcoded count), DIF/PPM probe_nonexistent

## Phase Audit 4 Status (R53)

- TC-0054 FODS formula: CLOSED (R53)
- TC-0057 FODT heading: OPEN → R54
- TC-0058 FODT list: OPEN → R54+
- TC-0059 FODT table: OPEN → R54+

## R54 Opening Items (HIGH)

1. FODT heading preservation (TC-0057)
2. Installed-wheel smoke from extracted bundle
3. dotnet test invocation fix
4. Phase Audit 5 execution
5. AI acceleration round 3 (live endpoint)

## Bundle Info

- Path: `.local/evidence-bundles/r53-self-verifying-baseline.zip`
- Sidecar: `.local/evidence-bundles/r53-self-verifying-baseline.sha256-proof.json`
- Verdict: `R53_STATE_VALIDATOR_CLEAN_PRODUCT_PARTIAL`

## Key Files (R53)

- `tools/evidence/write_sidecar_proof.py` (new)
- `tools/evidence/validate_evidence_bundle.py` (sidecar support added)
- `src/python/fods/writer.py` (formula preservation)
- `tests/python/fods/test_r53_formula_preservation.py` (new)
- `tests/evidence/test_r53_sidecar_proof.py` (new)
- `reports/r53/` (22+ report files)
