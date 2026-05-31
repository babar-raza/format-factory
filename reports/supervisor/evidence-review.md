# Evidence Review — Supervisor
Sprint ID: FORMAT-FACTORY-R83-BROAD-PRODUCT-FINISH-REVIEW-PACKAGE-ARTIFACTS-FODS-FODT-NEXTFORMATS-AUTHORITY-MEGA-TRAIN-001
Timestamp: 2026-05-31T14:43:05.211236
Verdict: ACCEPTED
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r83-pass2.zip

## Facts
- Tests: 161 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 3400
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
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r83-broad-product-finish-review-package-artifacts.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r83-pass2.zip
Bundle size: 6,021,969 bytes
Total entries: 3400
Top-level folders: ['bundle-metadata', 'repo']
Repo files: 3342
Metadata files: 58
Required repo files: 44 (missing: 0)
Required metadata files: 0 (missing: 0)
Min metadata required: 34
RUN_CONTRACT_METADATA_FLOOR (PASS): 58/30
Forbidden hits: 0
Git clean (PASS): git-status-final.txt shows clean working tree
Metadata identity check (PASS)

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.

BUNDLE_VALIDATION: FAIL

```
