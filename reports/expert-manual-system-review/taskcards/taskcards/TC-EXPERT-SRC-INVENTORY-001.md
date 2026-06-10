# TC-EXPERT-SRC-INVENTORY-001
**Title:** Read all .NET and Python source files and populate src-inventory.md
**Category:** INVESTIGATION
**Owner Lane:** (none)
**Status:** TODO
**Severity:** N/A

## Allowed Files
- reports/expert-manual-system-review/src-inventory.md
- reports/expert-manual-system-review/src-format-matrix.json

## Forbidden Files
- src/**

## Entry Gate
- TC-EXPERT-CLAIM-AUDIT-001 CLOSED_VERIFIED

## Exit Gate
- src-inventory.md has entry per source file with SHA-256
- src-format-matrix.json written

## Evidence Required
- src-inventory.md
- src-format-matrix.json

## Closeout Criteria
- All .NET+Python source files inventoried
- Each entry has SHA-256 and function citations

## Rollback Plan
- Delete reports — no source changes

## Dependencies
- TC-EXPERT-CLAIM-AUDIT-001
