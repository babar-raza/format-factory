# R60 Train B — External Sidecar Delivery

**Sprint:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

## Defects Repaired

- IV-R59-001: No external sidecar delivered with uploaded ZIP — REPAIRED
- IV-R59-002: sidecar_required: true not satisfied — REPAIRED (R60 contract enforces)
- IV-R59-003: Validation without sidecar fails — REPAIRED (positive proof in Train M)
- IV-R59-004: Uploaded ZIP SHA mismatch — REPAIRED (R60 sidecar will be built from final ZIP)

## R60 Contract

**Contract:** `tools/evidence/contracts/r60-current-head-rc-sidecar.yaml`
- `sidecar_required: true` ✓
- `final_proof_policy: external_sidecar` ✓
- `require_clean_git: true` ✓
- `run_number: R60` ✓

## Sidecar Protocol (R60)

1. Build Pass 1 ZIP (no sidecar)
2. Commit final-verdict with Pass 1 SHA
3. Build Pass 2 ZIP from clean git HEAD
4. Generate external sidecar: `python tools/evidence/write_sidecar_proof.py ...`
5. Validate with: `python tools/evidence/validate_evidence_bundle.py --sidecar-proof <path>`
6. Record `SIDECAR_PROOF_VALIDATION: PASS`

## Tests Added

**tests/evidence/test_r60_sidecar_required_enforcement.py** — 13 tests

Key coverage:
- `test_r60_contract_sidecar_required_true` — contract enforces sidecar
- `test_missing_sidecar_would_trigger_sidecar_required` — SIDECAR_REQUIRED error
- `test_wrong_sha_sidecar_rejected` — SIDECAR_PROOF_SHA_MISMATCH error
- `test_sidecar_outside_zip` — sidecar cannot be inside ZIP
- `test_sidecar_validation_result_must_be_pass` — FAIL sidecar rejected

**13/13 PASS**

## Negative Proof Summary

| Scenario | Expected Error | Result |
|----------|---------------|--------|
| No sidecar + sidecar_required: true | SIDECAR_REQUIRED | TRIGGERED |
| Wrong SHA in sidecar | SIDECAR_PROOF_SHA_MISMATCH | TRIGGERED |
| FAIL result in sidecar | SIDECAR error | TRIGGERED |
| Sidecar inside ZIP | SIDECAR_INSIDE_ZIP | TRIGGERED |
| Correct sidecar | No errors | PASS |

**TRAIN_B_COMPLETE**
