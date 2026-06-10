# TC-EXPERT-LAYER-REVIEW-001
**Title:** Review supervisor/evidence/host-runner layers and score against design contract
**Category:** INVESTIGATION
**Owner Lane:** AUTONOMY_SYSTEM_LANE
**Status:** TODO
**Severity:** N/A

## Allowed Files
- reports/expert-manual-system-review/layer-review-matrix.json

## Forbidden Files
- tools/supervisor/**
- reports/supervisor/**

## Entry Gate
- TC-EXPERT-SRC-INVENTORY-001 CLOSED_VERIFIED

## Exit Gate
- layer-review-matrix.json written with all layers scored

## Evidence Required
- layer-review-matrix.json

## Closeout Criteria
- All supervisor layers covered with HEALTHY/DEGRADED/BROKEN status

## Rollback Plan
- Delete reports — no source changes

## Dependencies
- TC-EXPERT-SRC-INVENTORY-001
