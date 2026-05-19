# R29 Lane B: Evidence Validator Semantic Hardening
# Date: 2026-05-19

## Purpose
Prevent the R28 defect class: sprint-state.yaml left with non-terminal status after sprint completion.

## New Tests (6)

### TestSprintStateTerminality (2 tests)
1. `test_completed_sprint_states_are_terminal` — Any sprint-state.yaml with a matching COMPLETE verdict must have terminal status. Uses sprint_id matching to avoid false positives when multiple sprints share a directory.
2. `test_completed_lanes_are_terminal` — No lane in a terminal sprint should be pending/in_progress.

### TestSprintStateVerdictConsistency (1 test)
3. `test_no_in_progress_sprint_state_with_complete_verdict` — Direct regression test for R28 defect. Matches by sprint_id.

### TestPendingInRepairContext (2 tests)
4. `test_repair_reports_allow_quoted_pending` — Documents that repair reports mentioning historical PENDING (with arrow notation) are not false positives.
5. `test_active_pending_in_sprint_overview_detected` — Catches BUNDLE_VALIDATION: PENDING in sprint overviews (not in repair context).

### TestStaleCommitSHA (1 test)
6. `test_no_pending_commit_sha_in_recent_verdicts` — Catches COMMIT_SHA: PENDING left in final artifacts.

## All 6/6 PASS

## Key Design Decision
When multiple sprints share a directory (e.g., reports/r29/), the tests match by sprint_id to avoid flagging a new in_progress sprint-state alongside an older completed sprint's verdict.
