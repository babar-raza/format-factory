# Evidence Review — Supervisor
Sprint ID: FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001
Timestamp: 2026-06-02T08:43:05.684140
Verdict: REJECTED_BUNDLE_VALIDATION_FAIL
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r89-pass2.zip

## Facts
- Tests: 65 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 3627
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
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r89-authoritative-test-baseline-declaration-closeout-poc-product-deepening.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r89-pass2.zip
Bundle size: 6,095,216 bytes
Total entries: 3627
Top-level folders: ['bundle-metadata', 'repo']
Repo files: 3591
Metadata files: 36
Required repo files: 19 (missing: 0)
Required metadata files: 0 (missing: 0)
Min metadata required: 35
RUN_CONTRACT_METADATA_FLOOR (PASS): 36/30
Forbidden hits: 0
Git clean (PASS): git-status-final.txt shows clean working tree
Metadata identity check (FAIL)

ERRORS:
  - METADATA_IDENTITY: mixed primary sprint/contract identities found: FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001, r89-authoritative-test-baseline-declaration-closeout-poc-product-deepening

BUNDLE_VALIDATION: FAIL
Sidecar proof check (PASS): SHA/size/entries match — e4c7bec764a094ad...
SIDECAR_PROOF_VALIDATION: PASS

```
