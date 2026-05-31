# Evidence Review — Supervisor
Sprint ID: ** FORMAT-FACTORY-R83-BROAD-PRODUCT-FINISH-REVIEW-PACKAGE-ARTIFACTS-FODS-FODT-NEXTFORMATS-AUTHORITY-MEGA-TRAIN-001
Timestamp: 2026-05-31T14:47:05.121708
Verdict: ACCEPTED
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r83-supervisor-review-package.zip

## Facts
- Tests: 0 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 9
- PENDING markers: 1

## Gate States
(none extracted)

## Limitation Notes
- No test log found in bundle — test counts unavailable

## Existing Validator Output
```
============================================================
EVIDENCE BUNDLE VALIDATION REPORT
============================================================
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r83-broad-product-finish-review-package-artifacts.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r83-supervisor-review-package.zip
Bundle size: 11,112,770 bytes
Total entries: 9
Top-level folders: ['final-verdict.md', 'r83-delivery-manifest.json', 'r83-delivery-package.sha256.txt', 'r83-delivery-package.zip', 'r83-final-artifact-authority.json', 'r83-pass2-sidecar.sha256-proof.json', 'r83-pass2.zip', 'r83-review-package-manifest.json', 'r83-supervisor-inspection-readme.md']
Repo files: 0
Metadata files: 0
Required repo files: 44 (missing: 44)
Required metadata files: 0 (missing: 0)
Min metadata required: 34
RUN_CONTRACT_METADATA_FLOOR (FAIL): 0/30
Forbidden hits: 0
Git clean (MISSING): No git status file found in bundle metadata (checked: git-status-final.txt or git-status.txt)
Metadata identity check (PASS)

WARNINGS:
  - Extra top-level folders (not in required list): ['final-verdict.md', 'r83-delivery-manifest.json', 'r83-delivery-package.sha256.txt', 'r83-delivery-package.zip', 'r83-final-artifact-authority.json', 'r83-pass2-sidecar.sha256-proof.json', 'r83-pass2.zip', 'r83-review-package-manifest.json', 'r83-supervisor-inspection-readme.md']

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.
  - Missing required top-level folders: ['bundle-metadata', 'repo']
  - Missing required repo files (44): ['reports/r83/00-preflight.md', 'reports/r83/r82-independent-verification.md', 'reports/r83/r82-defect-ledger.md', 'reports/r83/r82-defect-ledger.json', 'reports/r83/mu
```
