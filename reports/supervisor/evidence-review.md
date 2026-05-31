# Evidence Review — Supervisor
Sprint ID: unknown
Timestamp: 2026-05-31T20:13:06.512906
Verdict: BLOCKED_MISSING_FINAL_VERDICT
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r84-supervisor-review-package.zip

## Facts
- Tests: 6634 passed, 19 failed, 34 skipped
- Git HEAD: unknown
- Bundle entries: 38
- PENDING markers: 0

## Gate States
(none extracted)

## Limitation Notes
- No final-verdict.md found in bundle

## Existing Validator Output
```
============================================================
EVIDENCE BUNDLE VALIDATION REPORT
============================================================
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r84-broad-closure-raw-logs-final-authority.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r84-supervisor-review-package.zip
Bundle size: 11,463,473 bytes
Total entries: 38
Top-level folders: ['package-artifacts', 'r84-delivery-final-artifact-authority.json', 'r84-delivery-manifest.json', 'r84-delivery-supervisor-inspection-readme.md', 'r84-delivery.sha256.txt', 'r84-delivery.zip', 'r84-pass3-final.sha256-proof.json', 'r84-pass3-final.zip', 'r84-review-package-manifest.json', 'raw-dotnet-logs', 'raw-install-logs', 'raw-negative-proof-logs', 'raw-test-logs']
Repo files: 0
Metadata files: 0
Required repo files: 46 (missing: 46)
Required metadata files: 0 (missing: 0)
Min metadata required: 36
RUN_CONTRACT_METADATA_FLOOR (FAIL): 0/30
Forbidden hits: 0
Git clean (MISSING): No git status file found in bundle metadata (checked: git-status-final.txt or git-status.txt)
Metadata identity check (PASS)

WARNINGS:
  - Extra top-level folders (not in required list): ['package-artifacts', 'r84-delivery-final-artifact-authority.json', 'r84-delivery-manifest.json', 'r84-delivery-supervisor-inspection-readme.md', 'r84-delivery.sha256.txt', 'r84-delivery.zip', 'r84-pass3-final.sha256-proof.json', 'r84-pass3-final.zip', 'r84-review-package-manifest.json', 'raw-dotnet-logs', 'raw-install-logs', 'raw-negative-proof-logs', 'raw-test-logs']

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.
  - Missing required top-level folders: ['bundle-metadata', 'repo']
  - Missing required repo files 
```
