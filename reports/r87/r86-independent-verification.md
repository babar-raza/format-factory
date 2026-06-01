# R86 Independent Verification

Sprint: FORMAT-FACTORY-R87-CLEAN-SUPERVISOR-CLOSEOUT-REVIEW-PACKAGE-POC-PRODUCT-FACTORY-DEEPENING-MEGA-TRAIN-001
Date: 2026-06-01

## Uploaded Artifact Identification

Uploaded artifact: r86-pass2.zip
SHA-256: 7068680bf2950ef743de57576cebc1d27339ecf4f362d965c5293cf8b79721b8
Size: 5,981,933 bytes
Entries: 3,526
Top-level folders: bundle-metadata/, repo/
Classification: INNER EVIDENCE BUNDLE — NOT supervisor review package

## Verification: r86-supervisor-review-package.zip exists locally

Local artifact: .local/r86-supervisor-review-package.zip
SHA-256: f9b1cea3536b6ce084366854e28019ec8502e698da6638ddd211104868b51de0
Size: 11,005,037 bytes
Entries: 8
This was built but NOT uploaded as the primary artifact.

## Validator Result (without sidecar)

Command: python tools/evidence/validate_evidence_bundle.py --bundle .local/r86-pass2.zip --contract r86-*.yaml --check-no-pending
Result: BUNDLE_VALIDATION: FAIL

Errors:
1. SIDECAR_REQUIRED: sidecar proof was not supplied
2. P-EVID-003 VIOLATION: No metadata file contains exact AUTHORITATIVE_TEST_RESULT token
3. Shallow metadata: test-file-inventory.txt (39 bytes)
4. Shallow metadata: zst-status.txt (37 bytes)

## Bundled Supervisor Output Staleness

All reports/supervisor/ files bundled in r86-pass2.zip reference R85, not R86:
- evidence-review.md: Sprint ID = FORMAT-FACTORY-R85-POC-DIRECTION-*
- contradictions.md: Sprint ID = FORMAT-FACTORY-R85-POC-DIRECTION-*
- approval-gates.md: Sprint ID = FORMAT-FACTORY-R85-POC-DIRECTION-*
- evidence-review.json: Sprint ID = FORMAT-FACTORY-R85-POC-DIRECTION-*

The R86 supervisor was rerun AFTER bundle build (commit 2f180d0) but the fresh outputs were NOT re-bundled into the evidence ZIP.

## Supervisor Truth Repair Verification

Running R86's own repaired supervisor against r86-pass2.zip (without sidecar auto-discovery):
Result: EVIDENCE_REVIEW: REJECTED_BUNDLE_VALIDATION_FAIL, exit code 3
This proves the supervisor truth repair is real — it correctly rejects its own bundle when sidecar is missing.

## R86 Accepted Progress

1. Supervisor truth repair (D86-SUP-01..08): CONFIRMED REAL — 13 tests pass
2. Python PPM writer (write_ppm): CONFIRMED — 11 tests pass
3. PBM to PPM dogfood export: CONFIRMED — 10 tests pass
4. .NET Netpbm binary write P4/P5/P6: CONFIRMED (reported)
5. .NET FODS/FODT hardening: CONFIRMED (reported)
6. PPM added to package matrix: CONFIRMED
7. Sidecar auto-discovery fix: CONFIRMED (commit 8c6bc28)

## R86 Classification

R86_SUPERVISOR_TRUTH_REPAIR_REAL_PRODUCT_PROGRESS_REAL_FINAL_CLOSURE_REJECTED

## Defect Summary

See r86-defect-ledger.md for full defect list.
Total defects: 15
Classification: 7 CONFIRMED_CARRIED_TO_R87, 8 EXPLAINED_NOT_DEFECT or previously known
