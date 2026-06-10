# TC-EXPERT-PACKAGING-REVIEW-001
**Title:** Audit .csproj and Python package metadata against distribution requirements
**Category:** PACKAGING
**Owner Lane:** PACKAGING_LANE
**Status:** TODO
**Severity:** N/A

## Allowed Files
- reports/expert-manual-system-review/packaging-distribution-matrix.json

## Forbidden Files
- src/**

## Entry Gate
- TC-EXPERT-SRC-INVENTORY-001 CLOSED_VERIFIED

## Exit Gate
- packaging-distribution-matrix.json written

## Evidence Required
- packaging-distribution-matrix.json

## Closeout Criteria
- All 3 .NET packages and Python packages covered with gap list

## Rollback Plan
- Delete reports — no source changes

## Dependencies
- TC-EXPERT-SRC-INVENTORY-001
