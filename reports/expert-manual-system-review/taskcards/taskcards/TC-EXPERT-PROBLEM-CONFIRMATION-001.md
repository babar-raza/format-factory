# TC-EXPERT-PROBLEM-CONFIRMATION-001
**Title:** Confirm all suspected problems with source citations and severity
**Category:** INVESTIGATION
**Owner Lane:** (none)
**Status:** TODO
**Severity:** N/A

## Allowed Files
- reports/expert-manual-system-review/problem-register.json

## Forbidden Files
- src/**

## Entry Gate
- all REVIEW taskcards CLOSED_VERIFIED

## Exit Gate
- problem-register.json written with all CRITICAL/HIGH problems confirmed

## Evidence Required
- problem-register.json

## Closeout Criteria
- All CRITICAL/HIGH have VERIFIED confidence
- No VERIFIED problem lacks source_line_ref

## Rollback Plan
- Delete reports — no source changes

## Dependencies
- TC-EXPERT-DOTNET-REVIEW-001
- TC-EXPERT-PYTHON-REVIEW-001
- TC-EXPERT-PACKAGING-REVIEW-001
- TC-EXPERT-SECURITY-REVIEW-001
- TC-EXPERT-HOST-AUTONOMY-REVIEW-001
- TC-EXPERT-LAYER-REVIEW-001
