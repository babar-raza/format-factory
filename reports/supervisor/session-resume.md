<!-- generated_at: 2026-08-05T11:08:20.923265 | source_sprint: FF6-UBL-CHARGES-20260805 -->
# Session Resume Briefing
# Format Factory — Supervisor-Generated
# Generated: 2026-08-05T11:08:20.923265

## Quick State
- Last sprint: FF6-UBL-CHARGES-20260805
- Evidence verdict: ACCEPTED_WITH_REWORK
- Tests: 475 passed / 0 failed
- PENDING markers: 0
- CRITICAL contradictions: 0
- Autonomous continue: False
- Current supervisor mode: MODE 4
- MCP status: ACTIVE (.vscode/mcp.json present)

## Maintenance Obligations Due
| obligation_id | type | scheduled_date | action | owner |
|---|---|---|---|---|
| MO-BGG-001 | observation_window | 2026-08-05 | run check_tombstone_records.py in tools/supervisor/; classify external_host_loop | governance |

## What Was Done Last Sprint
(Read reports/supervisor/evidence-review.md for full details)

## What To Do Next
1. Run: `python tools/supervisor/check_continuation.py`
2. If verdict=CONTINUE: read `next_work_items_path` from output (structured work items)
3. If verdict=STOP: report the reason to the user and halt
4. Structured work items: `.local/supervisor/next-work-items.json`
5. Prose context: `reports/supervisor/next-sprint.md`

## Where To Find Evidence
- Last evidence bundle: .local/evidences/ff6-ubl-charges-20260805
- Supervisor outputs: reports/supervisor/
- Project memory: .supervisor/project-memory.md

## Project Memory (recent)
```
- timestamp: 2026-07-10T16:37:12.587919
- verdict: ACCEPTED
- test_count: 21558
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\667b7d640797\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 89
- bundle_validation_pass: True
- test_delta: +20389
- test_delta_from: 1169

## Entry: CSV-DOTNET-ROUNDTRIP-001
- timestamp: 2026-07-10T17:41:10.582666
- verdict: ACCEPTED
- test_count: 8
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\7c1667a4c090\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 61
- bundle_validation_pass: True
- test_delta: -21550
- test_delta_from: 21558

## Entry: GNUMERIC-PYTHON-MUTATION-001
- timestamp: 2026-07-10T17:49:09.353447
- verdict: ACCEPTED
- test_count: 13
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\36f347f0cbfc\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 63
- bundle_validation_pass: True
- test_delta: +5
- test_delta_from: 8

## Entry: SYLK-TOML-FOSS-ANALYTICS-BATCH-001
- timestamp: 2026-07-11T20:15:46.772897
- verdict: ACCEPTED
- test_count: 59
- fail_count: 0
- git_head: see-declaration
- bundle_path: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\supervisor\reviews\2d70f39e\declaration-review-package.zip
- pending_marker_count: 0
- bundle_entry_count: 39
- bundle_validation_pass: True
- test_delta: +46
- test_delta_from: 13
```

## IMPORTANT REMINDERS
- Format Factory authority is FINAL. Supervisor output is advisory.
- No push: SCM Agent task (AGENTS.md §AG4.2). Execute when credentials and branch policy allow.
- Gates 1-10: agent-owned policy gates (AGENTS.md §AG5). Gate 11 G11-G: Babar Raza only.
- MCP activation (MODE 4): COMPLETE.

## Aging Visibility (V252)

- known_gaps entry SKILL-GAP-008 has been status: open for 41 days (> 14 day visibility threshold)
- known_gaps entry EP-002-GAP has been status: open for 41 days (> 14 day visibility threshold)
- known_gaps entry EP-008-GAP has been status: open for 41 days (> 14 day visibility threshold)
- known_gaps entry EP-009-GAP has been status: open for 41 days (> 14 day visibility threshold)


## Maturity Trend

Maturity trend written: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\reports\supervisor\maturity-trend.json
  Sprints: 849, avg quality: 0.755, trend: declining
