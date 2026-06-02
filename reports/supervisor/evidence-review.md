# Evidence Review — Supervisor
Sprint ID: unknown
Timestamp: 2026-06-02T15:35:05.727821
Verdict: BLOCKED_MISSING_FINAL_VERDICT
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\r91\declaration-review-package.zip

## Facts
- Tests: 0 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 16
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
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r90-mainstream-poc-product-acceleration-governed-skills-supervisor-repair.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\r91\declaration-review-package.zip
Bundle size: 22,188 bytes
Total entries: 16
Top-level folders: ['evidence', 'materialized', 'package-manifest.json', 'r91-review', 'state', 'supervisor']
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
  - Extra top-level folders (not in required list): ['evidence', 'materialized', 'package-manifest.json', 'r91-review', 'state', 'supervisor']

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.
  - Missing required top-level folders: ['bundle-metadata', 'repo']
  - Missing required repo files (19): ['reports/r90/00-preflight.md', 'reports/r90/r89-independent-verification.md', 'reports/r90/r89-product-source-audit.md', 'reports/r90/multi-mega-train-scoreboard.md', 'reports/r90/final-verdict.md', 'reports/r90/final-adversarial-independent-verification.md', 'reports/r90/product-factory-acceleration-gap-analysis.md', 'reports/r90/governed-dogfood-export.md', 'reports/r90/product-code-change-ledger.json', 'reports/r90/product-code-change-ledger.md']
  - Metadata count 0 < minimum 35
  - RUN_CONTRACT_MET
```
