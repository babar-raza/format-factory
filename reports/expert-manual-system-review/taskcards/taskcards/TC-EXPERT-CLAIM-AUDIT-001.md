# TC-EXPERT-CLAIM-AUDIT-001
**Title:** Re-validate CLAIM-001 through CLAIM-004 against current worktree files
**Category:** CLAIM_AUDIT
**Owner Lane:** CLAIM_REALITY_LANE
**Status:** TODO
**Severity:** HIGH

## Allowed Files
- reports/expert-manual-system-review/claim-vs-source-matrix.json

## Forbidden Files
- product-capability-matrix/poc-targets.yaml
- src/**

## Entry Gate
- TC-EXPERT-PREFLIGHT-001 CLOSED_VERIFIED

## Exit Gate
- claim-vs-source-matrix.json written with 4 entries, each with SHA-256 and verdict

## Evidence Required
- claim-vs-source-matrix.json (4 claims, each VERIFIED/REFUTED/PARTIALLY_VERIFIED)

## Closeout Criteria
- All 4 claims have verdict
- SHA-256 per file recorded

## Rollback Plan
- Delete claim-vs-source-matrix.json — no source changes

## Dependencies
- TC-EXPERT-PREFLIGHT-001
