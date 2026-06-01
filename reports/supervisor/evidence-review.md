# Evidence Review — Supervisor
Sprint ID: unknown
Timestamp: 2026-06-01T17:19:04.281124
Verdict: BLOCKED_MISSING_FINAL_VERDICT
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r87-supervisor-review-package.zip

## Facts
- Tests: 0 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 47
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
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r87-clean-supervisor-closeout-review-package-poc-product-factory-deepening.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r87-supervisor-review-package.zip
Bundle size: 11,340,832 bytes
Total entries: 47
Top-level folders: ['package-artifacts', 'r87-delivery-final-artifact-authority.json', 'r87-delivery-manifest.json', 'r87-delivery-supervisor-inspection-readme.md', 'r87-delivery.sha256.txt', 'r87-delivery.zip', 'r87-pass2.sha256-proof.json', 'r87-pass2.zip', 'r87-review-package-manifest.json', 'raw-supervisor-loop-logs', 'raw-test-logs', 'reports-supervisor']
Repo files: 0
Metadata files: 0
Required repo files: 19 (missing: 19)
Required metadata files: 0 (missing: 0)
Min metadata required: 35
RUN_CONTRACT_METADATA_FLOOR (FAIL): 0/30
Forbidden hits: 0
Git clean (MISSING): No git status file found in bundle metadata (checked: git-status-final.txt or git-status.txt)
Metadata identity check (PASS)

WARNINGS:
  - Extra top-level folders (not in required list): ['package-artifacts', 'r87-delivery-final-artifact-authority.json', 'r87-delivery-manifest.json', 'r87-delivery-supervisor-inspection-readme.md', 'r87-delivery.sha256.txt', 'r87-delivery.zip', 'r87-pass2.sha256-proof.json', 'r87-pass2.zip', 'r87-review-package-manifest.json', 'raw-supervisor-loop-logs', 'raw-test-logs', 'reports-supervisor']

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.
  - Missing required top-level folders: ['bundle-metadata', 'repo']
  - Missing required repo files (19): ['reports/r87/r86-
```
