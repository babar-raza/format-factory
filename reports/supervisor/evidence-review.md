# Evidence Review — Supervisor
Sprint ID: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Timestamp: 2026-05-31T23:27:53.355345
Verdict: ACCEPTED
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r85-pass2-final.zip

## Facts
- Tests: 349 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 3482
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
Bundle: .local\r85-pass2-final.zip
Bundle size: 5,927,822 bytes
Total entries: 3482
Top-level folders: ['bundle-metadata', 'repo']
Repo files: 3448
Metadata files: 34
Required repo files: 42 (missing: 0)
Required metadata files: 0 (missing: 0)
Min metadata required: 30
RUN_CONTRACT_METADATA_FLOOR (PASS): 34/30
Forbidden hits: 0
Git clean (PASS): git-status-final.txt shows clean working tree
Metadata identity check (PASS)

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.

BUNDLE_VALIDATION: FAIL

```
