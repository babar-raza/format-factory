# Evidence Review — Supervisor
Sprint ID: unknown
Timestamp: 2026-06-01T20:49:05.077240
Verdict: BLOCKED_MISSING_FINAL_VERDICT
Bundle: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r88-delivery.zip

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
Contract: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\evidence\contracts\r88-declaration-driven-autonomous-closeout-poc-product-deepening.yaml
Bundle: c:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\r88-delivery.zip
Bundle size: 5,567,314 bytes
Total entries: 4
Top-level folders: ['r88-delivery-manifest.json', 'r88-delivery-supervisor-inspection-readme.md', 'r88-pass2.sha256-proof.json', 'r88-pass2.zip']
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
  - Extra top-level folders (not in required list): ['r88-delivery-manifest.json', 'r88-delivery-supervisor-inspection-readme.md', 'r88-pass2.sha256-proof.json', 'r88-pass2.zip']

ERRORS:
  - SIDECAR_REQUIRED: contract or verdict requires an external sidecar proof (sidecar_required: true / final_proof_policy: external_sidecar / clean-baseline verdict) but --sidecar-proof was not supplied. Run write_sidecar_proof.py and re-validate with --sidecar-proof <path>.
  - Missing required top-level folders: ['bundle-metadata', 'repo']
  - Missing required repo files (19): ['reports/r88/r87-independent-verification.md', 'reports/r88/r87-defect-ledger.json', 'reports/r88/multi-mega-train-scoreboard.md', 'reports/r88/claude-closeout-instruction-repair.md', 'reports/r88/autonomous-cycle-end-to-end-proof.md', 'reports/r88/authoritative-test-result-cleanup.md', 'tests/net/fods/FodsR88MultiSheetCsvTests.cs', 'tests/net/fodt/FodtR88TextAnalysisTests.cs', 'tests/net/netpbm/NetpbmR88TransformTests.cs', 'CLAUDE.md']
  - Metadata count 0 < minimum 35
  - R
```
