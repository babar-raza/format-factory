# Lane Ledger Proof
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R3-CLOSURE-HARDENING-AND-ODF-DEPTH-001
Generated: 2026-06-05

## Lane Ledger Location

File: reports/spec-authority-real-pilot-r3/lane-execution-ledger.yaml

The anti-skip checker searches for files matching *ledger*.yaml in:
- evidence_root (.local/evidences/spec-authority-real-pilot-r3/)
- reports/<run_id>/ (reports/spec-authority-real-pilot-r3/)

This file is in the reports/<run_id>/ directory, which is searched by R109 logic.

## Lanes Recorded

| Lane | Owner | Status | Commands | Artifacts |
|------|-------|--------|----------|-----------|
| lane-0 | coordinator | CLOSED_VERIFIED | 1 | 9 |
| lane-a | review-agent | CLOSED_VERIFIED | 1 | 2 |
| lane-b | repair-agent | CLOSED_VERIFIED | 1 | 1 |
| lane-c | ledger-agent | CLOSED_VERIFIED | no_command | 2 |
| lane-d | grading-agent | CLOSED_VERIFIED | no_command | 1 |
| lane-e | odf-agent | CLOSED_VERIFIED | 1 | 3 |
| lane-f | snapshot-agent | CLOSED_VERIFIED | no_command | 2 |
| lane-g | test-agent | CLOSED_VERIFIED | 1 | 5 |
| lane-h | evidence-agent | CLOSED_VERIFIED | 2 | 5 |

## Anti-Skip Fix

R2 violation: missing_lane_ledger (medium severity)
R3 fix: lane-execution-ledger.yaml present in reports/spec-authority-real-pilot-r3/
Expected R3 anti-skip result: missing_lane_ledger = NOT_VIOLATED
