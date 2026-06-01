# Evidence Review — Supervisor
Sprint ID: FORMAT-FACTORY-R87-CLEAN-SUPERVISOR-CLOSEOUT-REVIEW-PACKAGE-POC-PRODUCT-FACTORY-DEEPENING-MEGA-TRAIN-001
Timestamp: 2026-06-01T17:11:05.315131
Verdict: REJECTED_BUNDLE_VALIDATION_FAIL
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r87-pass1.zip

## Facts
- Tests: 65 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 3549
- PENDING markers: 0

## Gate States
(none extracted)

## Limitation Notes
None

## Existing Validator Output
```
============================================================
EVIDENCE BUNDLE VALIDATION REPORT
============================================================
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r87-clean-supervisor-closeout-review-package-poc-product-factory-deepening.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r87-pass1.zip
Bundle size: 6,015,027 bytes
Total entries: 3549
Top-level folders: ['bundle-metadata', 'repo']
Repo files: 3509
Metadata files: 40
Required repo files: 19 (missing: 0)
Required metadata files: 0 (missing: 0)
Min metadata required: 35
RUN_CONTRACT_METADATA_FLOOR (PASS): 40/30
Forbidden hits: 0
Git clean (PASS): git-status-final.txt shows clean working tree
Metadata identity check (PASS)

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.

BUNDLE_VALIDATION: FAIL

```
