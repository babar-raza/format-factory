# Evidence Review — Supervisor
Sprint ID: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Timestamp: 2026-05-31T23:25:06.198338
Verdict: ACCEPTED
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r85-pass1.zip

## Facts
- Tests: 349 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 3481
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
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r85-poc-direction-local-supervisor-autonomous-product-factory.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r85-pass1.zip
Bundle size: 5,928,231 bytes
Total entries: 3481
Top-level folders: ['bundle-metadata', 'repo']
Repo files: 3448
Metadata files: 33
Required repo files: 42 (missing: 0)
Required metadata files: 0 (missing: 0)
Min metadata required: 30
RUN_CONTRACT_METADATA_FLOOR (PASS): 33/30
Forbidden hits: 0
Git clean (PASS): git-status-final.txt shows clean working tree
Metadata identity check (PASS)

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.

BUNDLE_VALIDATION: FAIL

```
