# TC-EXPERT-HOST-AUTONOMY-REVIEW-001
**Title:** Score the autonomous host runner and supervisor pipeline on H0-H5 scale
**Category:** AUTONOMY
**Owner Lane:** AUTONOMY_SYSTEM_LANE
**Status:** TODO
**Severity:** N/A

## Allowed Files
- reports/expert-manual-system-review/host-autonomy-review-matrix.json

## Forbidden Files
- tools/supervisor/**
- .local/supervisor/**

## Entry Gate
- TC-EXPERT-SRC-INVENTORY-001 CLOSED_VERIFIED

## Exit Gate
- host-autonomy-review-matrix.json written with H-score and CLAIM-003 verdict

## Evidence Required
- host-autonomy-review-matrix.json

## Closeout Criteria
- H-score assigned with source citation
- CLAIM-003 contradiction resolved

## Rollback Plan
- Delete reports — no source changes

## Dependencies
- TC-EXPERT-SRC-INVENTORY-001
