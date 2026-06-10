# TC-EXPERT-PREFLIGHT-001
**Title:** Governance preflight, coordinator setup, and initial taskcard registration
**Category:** INVESTIGATION
**Owner Lane:** (none)
**Status:** IN_PROGRESS
**Severity:** N/A

## Allowed Files
- reports/expert-manual-system-review/**

## Forbidden Files
- src/**
- tests/**
- examples/**
- product-capability-matrix/**
- registry/**
- .supervisor/policies.yaml

## Entry Gate
- None

## Exit Gate
- governance-preflight.md written
- all 13 taskcards created
- coordinator files created
- execution-state.json written

## Evidence Required
- governance-preflight.json
- taskcard-registry.json with 13 entries
- coordinator/coordinator-log.md

## Closeout Criteria
- All 13 taskcards created as .json+.md
- execution-state.json state=PREFLIGHT

## Rollback Plan
- Delete reports/expert-manual-system-review/ — no source files touched

## Dependencies
- None
