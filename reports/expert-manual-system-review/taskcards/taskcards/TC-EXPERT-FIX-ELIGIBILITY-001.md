# TC-EXPERT-FIX-ELIGIBILITY-001
**Title:** Classify every VERIFIED CRITICAL/HIGH problem for fix eligibility
**Category:** INVESTIGATION
**Owner Lane:** (none)
**Status:** TODO
**Severity:** N/A

## Allowed Files
- reports/expert-manual-system-review/fix-eligibility-matrix.json
- reports/expert-manual-system-review/fix-queue.json
- reports/expert-manual-system-review/human-action-adjudication.md
- reports/expert-manual-system-review/human-action-adjudication.json

## Forbidden Files
- src/**

## Entry Gate
- TC-EXPERT-PROBLEM-CONFIRMATION-001 CLOSED_VERIFIED

## Exit Gate
- fix-eligibility-matrix.json written
- fix-queue.json written with FIX_NOW_SAFE only

## Evidence Required
- fix-eligibility-matrix.json
- fix-queue.json
- human-action-adjudication.json

## Closeout Criteria
- Every CRITICAL/HIGH problem has classification
- fix-queue contains only FIX_NOW_SAFE

## Rollback Plan
- Delete reports — no source changes

## Dependencies
- TC-EXPERT-PROBLEM-CONFIRMATION-001
