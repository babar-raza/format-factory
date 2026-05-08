---
version: "1.0"
last-updated: "2026-05-08"
phase-available: "all"
gate-required: null
created-by: memory-planning-methodology-and-agent-handoff sprint
---

# /plan-hardening

Review, challenge, and harden a draft plan against repo truth before execution.

## Steps

1. Read memory/00-index.md, plans/master-plan.md, AGENTS.md, GOVERNANCE.md.
2. Read docs/planning-methodology.md and docs/plan-hardening-checklist.md.
3. Read all files referenced in the plan being reviewed.
4. Run git log --oneline -5, git status --short, and python tools/evidence/check_current_state_consistency.py.
5. Apply all 22 items from docs/plan-hardening-checklist.md.
6. For each NO answer, identify the gap and the fix.
7. Produce a hardened version of the plan with confirmed facts, corrected claims, added validation steps, added stop conditions, and added forbidden paths.
8. Report the plan hardening score (X/22).
9. Do not create any repo files. Do not commit. Do not push.

## Output Format

1. Plan hardening score (X/22).
2. Confirmed facts (with citations).
3. Corrected claims (original vs. corrected).
4. Added validation steps.
5. Added stop conditions.
6. Hardened plan ready for execution handoff.
7. Final line: NEXT_PROMPT_READY: yes

## Validation

The hardened plan must score at least 18/22 before being converted to an execution prompt.

## Changelog

- 1.0 (2026-05-08): Initial version. Created in memory-planning-methodology-and-agent-handoff sprint.
