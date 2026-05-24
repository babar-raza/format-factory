# R59 Train C — Final Proof/Sidecar Authority Normalization

**Sprint:** FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Status:** COMPLETE
**Date:** 2026-05-24

---

## Problem (IV-R58-007)

`bundle-metadata/final-bundle-validation-proof.txt` contained SHA `676451...` (from a prior
build) while the actual final bundle SHA was `d040a288...` (from sidecar). The internal proof
file claimed a SHA that did not match the uploaded bundle.

---

## Final Proof Authority Policy

1. **External sidecar is authoritative** for final ZIP SHA/size/entry_count.
2. **Internal proof file** (`final-bundle-validation-proof.txt`) must:
   - Reference the external sidecar path and its SHA explicitly
   - State: "Authoritative final SHA is in external sidecar"
   - May optionally include Pass-1/pre-final internal hash clearly labeled as non-authoritative
   - Must NOT claim a "final SHA" that differs from the sidecar without clear labeling
3. `BUNDLE_VALIDATION: PENDING` is now a PROOF_FILE_PLACEHOLDER error (added to pattern list)

---

## Validator Changes

### `check_proof_file_finality` (tools/evidence/validate_evidence_bundle.py)
Added to `PROOF_FILE_PLACEHOLDER_PATTERNS`:
- `"BUNDLE_VALIDATION: PENDING"` — catches proof files written before validation completes
- `"validation: pending"` — case-insensitive variant

---

## R59 Proof File Format

The R59 final-bundle-validation-proof.txt will use this format:
```
Bundle: r59-pass2-final.zip
Sprint: FORMAT-FACTORY-R59-...
Internal SHA (pre-final, non-authoritative): <pass1-sha>
External sidecar: reports/r59/r59-pass2-final.zip.sha256-proof.json
Authoritative final SHA: <see external sidecar>
BUNDLE_VALIDATION: PASS
SIDECAR_PROOF_VALIDATION: PASS
Date: 2026-05-24
```

---

## Tests Added

- `tests/evidence/test_r59_final_proof_authority.py` — 8 tests

**All 8 tests: PASS**

Key tests:
- `test_stale_internal_sha_produces_warning` — stale SHA → PROOF_SHA_SIDECAR_RECOMMENDED warning
- `test_no_sha_in_proof_no_warning` — proof without SHA claim (sidecar-only) → no warning
- `test_pending_sha_fails` — BUNDLE_VALIDATION: PENDING → PROOF_FILE_PLACEHOLDER error
- `test_sidecar_sha_size_entries_match` — correct sidecar → no errors
- `test_wrong_sidecar_sha_fails` — wrong SHA in sidecar → SIDECAR_PROOF_SHA_MISMATCH error
- `test_sidecar_result_not_pass_fails` — sidecar FAIL result → error

---

## Verdict

**TRAIN_C_COMPLETE** — Final proof/sidecar authority policy defined. BUNDLE_VALIDATION: PENDING
now a placeholder error. 8 tests all PASS.
