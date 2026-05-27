# R69 Work-Ahead W3 — Closeout Automation Hardening

Sprint: FORMAT-FACTORY-R69-FINAL-DELIVERY-SEAL-RC-CLOSURE-WORKAHEAD-MEGA-TRAIN-001
Date: 2026-05-27

## Objective

Prevent future "wrong artifact uploaded" mistakes by improving closeout pipeline tooling.

## run_closeout_pipeline.py

The `tools/evidence/run_closeout_pipeline.py` script was enhanced in R69.

Key improvements:
1. Always produces FOUR output paths in a clearly labeled final block:
   - Inner evidence ZIP
   - External sidecar
   - Delivery manifest
   - Outer delivery package
2. Fails with a clear error if delivery package was not produced
3. Prints a copy/paste block with all required paths and SHAs
4. Documents the distinction between the inner ZIP (for validation) and the delivery
   package (the artifact to provide to human reviewers)

## Final Output Block Format

```
============================================================
R69 DELIVERY CLOSEOUT — FINAL PATHS AND HASHES
============================================================
Inner Evidence ZIP:   .local/r69-pass2-final.zip
  SHA-256: <sha>
  Size:    <bytes>

External Sidecar:     .local/r69-pass2-final.sha256-proof.json
  SHA-256: <sha>

Delivery Manifest:    .local/r69-delivery-manifest.json

Outer Delivery Pkg:   .local/r69-delivery-package.zip  <-- PROVIDE THIS TO REVIEWER
  SHA-256: <sha>
  Size:    <bytes>

BUNDLE_VALIDATION: PASS
SIDECAR_PROOF_VALIDATION: PASS
DELIVERY_PACKAGE_VALIDATION: PASS (6/6)
============================================================
```

## Protocol Note

The INNER evidence ZIP is used for validation and contains the bundle.
The OUTER delivery package (ZIP containing ZIP + sidecar + manifest) is the
artifact that must be provided to human reviewers.

CLOSEOUT_AUTOMATION: HARDENED
