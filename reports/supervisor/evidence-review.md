# Evidence Review — Supervisor
Sprint ID: FORMAT-FACTORY-R80-REPAIR-PLUS-ADVANCEMENT-SUPERVISOR-EVIDENCE-PRODUCT-SYSTEM-HARDENING-20260530
Timestamp: 2026-05-30T21:28:44.853898
Verdict: ACCEPTED
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\evidence\r80-repair-plus-advancement-supervisor-evidence-product-system-hardening-20260530.zip

## Facts
- Tests: 65 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 3159
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
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r80-repair-plus-advancement-supervisor-evidence-product-system-hardening.yaml
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\evidence\r80-repair-plus-advancement-supervisor-evidence-product-system-hardening-20260530.zip
Bundle size: 5,531,062 bytes
Total entries: 3159
Top-level folders: ['bundle-metadata', 'repo']
Repo files: 3153
Metadata files: 6
Required repo files: 42 (missing: 0)
Required metadata files: 0 (missing: 0)
Min metadata required: 5
RUN_CONTRACT_METADATA_FLOOR (PASS): 6/30
Forbidden hits: 0
Metadata identity check (PASS)

WARNINGS:
  - Git dirty (allowed — emergency_blocker_bundle: true): git-status-final.txt shows uncommitted changes: 'Changes not staged for commit:'

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.

BUNDLE_VALIDATION: FAIL

```
