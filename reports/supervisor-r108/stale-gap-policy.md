# Stale Gap Policy

## Problem
`.local/supervisor/selected-product-gaps.json` references R98 sprint. Supervisor stream does not use product gaps.

## Policy
1. Stale product gaps are a global reference artifact, not supervisor-active state
2. Supervisor stream MUST NOT treat R98 product gaps as current work items
3. Anti-skip `stale_gaps` detector compares gap sprint_id to current sprint_id
4. Stale gaps in supervisor context are classified as informational (severity: critical for mainstream, not applicable for supervisor)
5. Supervisor sprints that pass no gap data to anti-skip are correctly clean

## Verification
- `detect_stale_gaps({}, expected_sprint)` returns `is_violation: false` (no data = no violation)
- `detect_stale_gaps({"sprint_id": "R98"}, expected_sprint="R108")` returns `is_violation: true`
