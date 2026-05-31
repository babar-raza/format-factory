# Evidence Review — Supervisor
Sprint ID: unknown
Timestamp: 2026-05-31T14:45:05.664690
Verdict: BLOCKED_MISSING_FINAL_VERDICT
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r83-delivery-package.zip

## Facts
- Tests: 0 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 4
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
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r83-broad-product-finish-review-package-artifacts.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r83-delivery-package.zip
Bundle size: 5,553,866 bytes
Total entries: 4
Top-level folders: ['r83-delivery-manifest.json', 'r83-pass2-sidecar.sha256-proof.json', 'r83-pass2.zip', 'r83-supervisor-inspection-readme.md']
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
  - Extra top-level folders (not in required list): ['r83-delivery-manifest.json', 'r83-pass2-sidecar.sha256-proof.json', 'r83-pass2.zip', 'r83-supervisor-inspection-readme.md']

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.
  - Missing required top-level folders: ['bundle-metadata', 'repo']
  - Missing required repo files (44): ['reports/r83/00-preflight.md', 'reports/r83/r82-independent-verification.md', 'reports/r83/r82-defect-ledger.md', 'reports/r83/r82-defect-ledger.json', 'reports/r83/multi-mega-train-scoreboard.md', 'reports/r83/lane-ownership.md', 'reports/r83/broad-sprint-scope-map.md', 'reports/r83/risk-register.md', 'reports/r83/parallel-execution-map.md', 'reports/r83/true-current-system-state.md']
  - Metadata count 0 < minimum 34
  - RUN_CONTRACT_METADATA_FLOOR: FAIL — metadata count 0 < absolut
```
