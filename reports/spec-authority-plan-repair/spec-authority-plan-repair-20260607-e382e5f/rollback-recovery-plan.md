# Rollback and Recovery Plan
# Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# Date: 2026-06-07

---

## Failure Modes and Recovery Actions

| FM | Description | Stop/Continue | State Transition | Rollback Action | Verdict |
|----|-------------|---------------|-----------------|-----------------|---------|
| FM-001 | JSON validation fail | continue | VALIDATING -> VALIDATION_FAILED | Fix JSON; revalidate | PLAN_NEEDS_REPAIR |
| FM-002 | Taskcard validator fails | continue | VALIDATING -> VALIDATION_FAILED | Fix check; rerun validator | PLAN_NEEDS_REPAIR |
| FM-003 | State machine count != 32 | continue | VALIDATING -> VALIDATION_FAILED | Recount; fix declaration | PLAN_NEEDS_REPAIR |
| FM-004 | Missing evidence input | STOP | BLOCKED_BY_MISSING_EVIDENCE | Record missing path | PLAN_REPAIR_BLOCKED |
| FM-005 | Stale evidence | continue_caveat | TRIAGED -> ROOT_CAUSE_CONFIRMED (caveat) | Mark STALE_EVIDENCE | continue |
| FM-006 | Dirty working tree (unexpected) | STOP and record | N/A | git status; do not clean | record_and_investigate |
| FM-007 | Lane ownership conflict | continue | L-COORD arbitrates | Assign exclusive ownership | continue |
| FM-008 | Tests unavailable | continue | N/A | Note in verification-gates | continue |
| FM-009 | CI unavailable locally | continue | N/A | Mark ci_available=false | continue |
| FM-010 | Plan contradiction found late | continue | ROOT_CAUSE_CONFIRMED -> fix | Apply minimal repair | continue |
| FM-011 | Unsafe prompt generated | do not include | N/A | Revise; re-review | PLAN_NEEDS_REPAIR |
| FM-012 | Evidence bundle incomplete | continue | N/A | Create missing files; rebuild | PLAN_NEEDS_REPAIR |

---

## Taskcard Rollback Rules

Every taskcard has a rollback_plan field. For plan-repair sprint:
- All changes are in `reports/spec-authority-plan-repair/${RUN_ID}/` only
- No src/ changes, no .local/spec-cache/ changes, no tools/ changes
- Rollback = delete the offending file in run_dir and recreate it
- No git stash needed (no git changes from this sprint)

---

## Hard Stops

The following conditions STOP the sprint and produce PLAN_REPAIR_BLOCKED verdict:
1. Investigation evidence bundle not found and cannot be located
2. Prior plan file not readable
3. All JSON files fail to parse (environment issue)
