# Evidence Review — Supervisor
Sprint ID: unknown
Timestamp: 2026-06-01T15:25:05.719274
Verdict: BLOCKED_MISSING_FINAL_VERDICT
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r86-supervisor-review-package.zip

## Facts
- Tests: 0 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 8
- PENDING markers: 0

## Gate States
(none extracted)

## Limitation Notes
- No final-verdict.md found in bundle
- No test log found in bundle — test counts unavailable

## Existing Validator Output
```
============================================================
EVIDENCE BUNDLE VALIDATION REPORT
============================================================
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r86-supervisor-truth-poc-product-factory-deepening.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r86-supervisor-review-package.zip
Bundle size: 11,005,037 bytes
Total entries: 8
Top-level folders: ['r86-delivery-final-artifact-authority.json', 'r86-delivery-manifest.json', 'r86-delivery-supervisor-inspection-readme.md', 'r86-delivery.sha256.txt', 'r86-delivery.zip', 'r86-pass2.sha256-proof.json', 'r86-pass2.zip', 'r86-review-package-manifest.json']
Repo files: 0
Metadata files: 0
Required repo files: 19 (missing: 19)
Required metadata files: 0 (missing: 0)
Min metadata required: 30
RUN_CONTRACT_METADATA_FLOOR (FAIL): 0/30
Forbidden hits: 0
Git clean (MISSING): No git status file found in bundle metadata (checked: git-status-final.txt or git-status.txt)
Metadata identity check (PASS)

WARNINGS:
  - Extra top-level folders (not in required list): ['r86-delivery-final-artifact-authority.json', 'r86-delivery-manifest.json', 'r86-delivery-supervisor-inspection-readme.md', 'r86-delivery.sha256.txt', 'r86-delivery.zip', 'r86-pass2.sha256-proof.json', 'r86-pass2.zip', 'r86-review-package-manifest.json']

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.
  - Missing required top-level folders: ['bundle-metadata', 'repo']
  - Missing required repo files (19): ['reports/r86/r85-independent-verification.md', 'tests/supervisor/test_r86_supervisor_truth_repair.py', 'tests/net/netpbm/NetpbmBinaryWriteTests.cs', 'tests/net/fods/FodsR86ExporterHardeningTests.cs', 'tests/net/fodt/Fo
```
