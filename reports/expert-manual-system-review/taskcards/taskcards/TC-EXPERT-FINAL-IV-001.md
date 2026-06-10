# TC-EXPERT-FINAL-IV-001
**Title:** Final independent verification and mechanical terminal gate
**Category:** IV
**Owner Lane:** INDEPENDENT_VERIFICATION_LANE
**Status:** TODO
**Severity:** N/A

## Allowed Files
- reports/expert-manual-system-review/final-healing-verdict.md
- reports/expert-manual-system-review/final-healing-verdict.json
- reports/expert-manual-system-review/terminal-gate-checklist.json
- reports/expert-manual-system-review/final-iv-json-validation.json
- reports/expert-manual-system-review/final-git-status.txt
- reports/expert-manual-system-review/execution-state.json

## Forbidden Files
- src/**
- tests/**

## Entry Gate
- TC-EXPERT-EVIDENCE-BUNDLE-001 CLOSED_VERIFIED

## Exit Gate
- terminal-gate-checklist.json all 8 conditions evaluated
- final-healing-verdict.json uses valid verdict

## Evidence Required
- terminal-gate-checklist.json
- final-healing-verdict.json
- final-git-status.txt
- execution-state.json (terminal=true if all pass)

## Closeout Criteria
- All 8 terminal conditions evaluated
- Valid verdict used
- No forbidden action occurred

## Rollback Plan
- Delete terminal checklist — no source changes

## Dependencies
- TC-EXPERT-EVIDENCE-BUNDLE-001
