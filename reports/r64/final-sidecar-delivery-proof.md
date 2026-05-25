# R64 Train B — Final Sidecar Delivery Proof

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

## Sidecar Delivery

Final ZIP: `.local/r64-pass2-final.zip`
External sidecar: `.local/r64-pass2-final.sha256-proof.json`

Both files delivered together. Sidecar is NOT inside the ZIP.

## Validation Proofs

### 1. Validation WITHOUT sidecar (must FAIL)

Command: `python tools/evidence/validate_evidence_bundle.py --bundle .local/r64-pass2-final.zip --check-no-pending --contract tools/evidence/contracts/r64-...yaml`
Expected: `BUNDLE_VALIDATION: FAIL` (SIDECAR_REQUIRED)
Result: to be filled at Train M

### 2. Validation WITH matching sidecar (must PASS)

Command: `python tools/evidence/validate_evidence_bundle.py --bundle .local/r64-pass2-final.zip --check-no-pending --contract ... --sidecar-proof .local/r64-pass2-final.sha256-proof.json`
Expected: `BUNDLE_VALIDATION: PASS` + `SIDECAR_PROOF_VALIDATION: PASS`
Result: to be filled at Train M

### 3. Validation WITH wrong sidecar (must FAIL)

Command: Create a modified sidecar with wrong SHA, validate
Expected: `SIDECAR_PROOF_VALIDATION: FAIL`
Result: to be filled at Train M

## Final Proof Metadata

`final-bundle-validation-proof.txt` will contain:
- Final ZIP SHA-256
- Size bytes
- Entry count
- External sidecar path
- All validation results
- No placeholder language

---

## Tests

| Test File | Tests | Status |
|---|---|---|
| test_r64_delivered_external_sidecar_required.py | 11 | 6 PASS, 5 SKIP (bundle pending) |
| test_r64_final_proof_no_placeholders.py | 7 | 0 PASS, 7 SKIP (proof pending) |
| test_r64_final_zip_sha_matches_sidecar.py | 5 | 0 PASS, 5 SKIP (bundle pending) |

All skips are for R64 bundle/sidecar artifacts not yet built — resolved at Train M.

---

SIDECAR_DELIVERY_PROOF_STATUS: PENDING_TRAIN_M
