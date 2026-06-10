---
version: "1.1"
last-updated: "2026-06-03"
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

## Usage

```
/plan-hardening
```

## Allowed Paths

- `reports/supervisor/` (write hardening outputs)
- `memory/` (read for context)
- `plans/master-plan.md` (read only)
- `docs/` (read planning methodology, hardening checklist)

## Forbidden Paths

- `src/**` (no source edits)
- `registry/format-registry.yaml` (gate authority)
- `tests/**` (no test changes)

## Constraints

- Do not create any repo files outside allowed paths
- Do not commit or push
- Hardened plan must score >= 18/22 before handoff

## Rollback

1. Remove hardened plan output from `reports/supervisor/`
2. No source or test changes to revert

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, plan_path, hardening_score, gaps_found, verdict.

## Sample Invocation

```
/plan-hardening
# Inputs:
#   plan_path: reports/planning/r94-sprint-plan.md
```

## Changelog

- 1.0 (2026-05-08): Initial version. Created in memory-planning-methodology-and-agent-handoff sprint.
- 1.1 (2026-06-03): Added usage, allowed/forbidden paths, constraints, rollback, transcript, sample invocation (Skills R102).
