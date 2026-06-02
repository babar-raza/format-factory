---
sprint: R92
generated_by: r92-worker
---

# Work Item Grading Enforcement (Train E)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Current State

`tools/supervisor/grade_declared_work.py` — PRESENT (from R88+)
`reports/supervisor/work-item-grades.json` — PRESENT (from R91 autonomous-cycle)
`reports/supervisor/work-item-grades.md` — PRESENT (from R91 autonomous-cycle)

## Enforcement Rules

1. Supervisor MUST produce work-item-grades.json + .md after every autonomous-cycle run.
2. Each declared item gets exactly one of:
   - ACCEPTED
   - ACCEPTED_WITH_WARNINGS
   - REWORK_REQUIRED
   - REJECTED
   - BLOCKED_EXTERNAL_GATE
   - NOT_ATTEMPTED
   - OVERCLAIMED
   - INSUFFICIENT_EVIDENCE (added by materializer for missing paths)
3. Missing artifacts → INSUFFICIENT_EVIDENCE (not global crash)
4. Accepted items excluded from next sprint's rework section
5. Rework items included in next sprint rework section
6. New master-plan/POC work always added regardless of rework state

## R92 Verification

autonomous_cycle.py already calls grade_declared_work.py and copies output to reports/supervisor/.
The materializer (Train B) adds pre-cycle INSUFFICIENT_EVIDENCE grades for missing paths.
Together these ensure item-level grading without global failure.

## Status: ENFORCED
