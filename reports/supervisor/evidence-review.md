# Evidence Review — Supervisor
Sprint ID: unknown
Timestamp: 2026-06-01T20:51:05.801957
Verdict: BLOCKED_MISSING_FINAL_VERDICT
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r88-supervisor-review-package.zip

## Facts
- Tests: 0 passed, 0 failed, 0 skipped
- Git HEAD: unknown
- Bundle entries: 18
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
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r88-declaration-driven-autonomous-closeout-poc-product-deepening.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r88-supervisor-review-package.zip
Bundle size: 11,141,318 bytes
Total entries: 18
Top-level folders: ['dogfood-export', 'examples-docs-readiness', 'gate-readiness', 'product-capability-matrix', 'publication-readiness', 'r88-delivery-final-artifact-authority.json', 'r88-delivery-manifest.json', 'r88-delivery-supervisor-inspection-readme.md', 'r88-delivery.sha256.txt', 'r88-delivery.zip', 'r88-pass2.sha256-proof.json', 'r88-pass2.zip', 'r88-review-package-manifest.json', 'raw-dotnet-logs', 'raw-negative-proof-logs', 'raw-package-install-logs', 'raw-test-logs']
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
  - Extra top-level folders (not in required list): ['dogfood-export', 'examples-docs-readiness', 'gate-readiness', 'product-capability-matrix', 'publication-readiness', 'r88-delivery-final-artifact-authority.json', 'r88-delivery-manifest.json', 'r88-delivery-supervisor-inspection-readme.md', 'r88-delivery.sha256.txt', 'r88-delivery.zip', 'r88-pass2.sha256-proof.json', 'r88-pass2.zip', 'r88-review-package-manifest.json', 'raw-dotnet-logs', 'raw-negative-proof-logs', 'raw-package-install-logs', 'raw-test-logs']

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but 
```
