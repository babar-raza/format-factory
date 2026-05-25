# R65 Delivery Package Proof

**Sprint:** FORMAT-FACTORY-R65-DELIVERY-PACKAGE-RC-REPLAY-AI-LIVE-WORKAHEAD-MEGA-TRAIN-001

## Protocol
1. Build inner evidence ZIP (r65-pass2-final.zip) — no sidecar inside
2. Generate external sidecar (r65-pass2-final.sha256-proof.json)
3. Generate delivery manifest (r65-delivery-manifest.json)
4. Build outer delivery package (r65-delivery-package.zip) containing all three
5. Validate extraction: evidence ZIP + sidecar + manifest extracted, sidecar validates inner ZIP

## Tool
tools/evidence/build_delivery_package.py — new R65 tool

## Tests
- tests/evidence/test_r65_delivery_package.py (synthetic + live tests)

## Validation Protocol
1. Missing sidecar → FAIL (SIDECAR_REQUIRED)
2. Correct sidecar → BUNDLE_VALIDATION: PASS + SIDECAR_PROOF_VALIDATION: PASS
3. Wrong sidecar → SIDECAR_PROOF_VALIDATION: FAIL
4. Delivery package extraction → all checks PASS

DELIVERY_PACKAGE_PROOF_STATUS: COMPLETE
