# Preflight — Acceleration R111

## Sprint Identity
- Sprint ID: FORMAT-FACTORY-ACCELERATION-R111-STREAM-OUTPUT-AUTHORITY-GLOBAL-NEXT-SPRINT-CLEANUP-AND-EVIDENCE-QUALITY-CAMPAIGN-001
- Prior: FORMAT-FACTORY-ACCELERATION-R110-PROMPT-QUALITY-ADVANCEMENT-LANE-CLOSURE-AND-STREAM-STATE-CLEANUP-CAMPAIGN-001
- Prior verdict: ACCEPTED
- Prior tests: 401 passed, 0 failed

## R110 Reconciliation
- 401 tests pass, 0 fail
- Prompt quality: PASS (6/6)
- Anti-skip: all_pass=true (15/15 checks, 0 violations)
- Evidence quality score: 0.57 (4/7 verified)
- Lane ledger: 4 found
- Raw logs: 2 found
- Sample outputs: 1 found
- Next-work items: 3 acceleration-forward (correct)
- Global next-sprint.md: Stream=mainstream (WRONG for acceleration package)
- Classification: ACCEPTED_WITH_GLOBAL_NEXT_SPRINT_CONTAMINATION

## Root Cause
`generate_supervisor_packet.py` main() (CLI entry point) never detects stream from sprint_id.
It calls `synthesize_sprint_tasks(review, contradictions, repo_root)` without stream parameter,
defaulting to mainstream. The programmatic `generate_packet()` function correctly detects stream,
but `cmd_next()` in supervisor_loop.py invokes main() as a subprocess, not generate_packet().
