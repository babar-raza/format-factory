---
version: "1.1"
last-updated: "2026-06-03"
phase-available: "all"
gate-required: null
created-by: memory-planning-methodology-and-agent-handoff sprint
---

# /execution-handoff

Convert a hardened plan into a single-go autonomous execution prompt with internal gates.

## Steps

1. Confirm the plan has passed /plan-hardening (score >= 18/22).
2. Read docs/agent-execution-handoff-standard.md.
3. Read the primary evidence input (latest passing bundle).
4. Read all files the plan requires.
5. Convert each prose step into an executable form (see docs/agent-execution-handoff-standard.md Section 4).
6. Add forbidden paths for every file that must not be touched.
7. Add a self-challenge section (minimum 17 yes/no questions).
8. Add the final response format ending with EVIDENCE_BUNDLE: <absolute Windows path to zip>.
9. Produce the complete execution handoff prompt using docs/prompts/execution-handoff-prompt-template.md as the structure.
10. Do not execute the plan. Do not create repo files. Do not commit. Do not push.
11. Record the coordination state in the handoff (Mission AGENT-COORD-2026-07-15):
    run `python -m tools.supervisor.coordination --json status` and include the
    active agents, live leases relevant to the handed-off scope, and any OPEN
    conflicts. The receiving agent must `register` and `claim` its scope before
    writing (AGENTS.md Section CO).

## Output Format

A complete execution handoff prompt ready to paste, including:
- MODE: EXECUTION MODE.
- Sprint type.
- Sprint name.
- Read first (exact file paths).
- Allowed paths.
- Forbidden paths (including hard prohibitions).
- All execution sections with exact commands.
- Validation section.
- Evidence contract specification.
- Commit rules.
- Self-challenge (17+ questions).
- Final response format.
- Final line: EVIDENCE_BUNDLE: <absolute Windows path to zip>

## Validation

The execution prompt must contain all 20 components from docs/planning-methodology.md Section 6 (Prompt Anatomy).

## Usage

```
/execution-handoff
```

## Allowed Paths

- `reports/supervisor/` (write handoff outputs)
- `plans/master-plan.md` (read only)
- `docs/` (read handoff standard, planning methodology, prompt templates)
- `memory/` (read for context)

## Forbidden Paths

- `src/**` (no source edits)
- `registry/format-registry.yaml` (gate authority)
- `tests/**` (no test changes)

## Constraints

- Do not execute the plan — only produce the handoff prompt
- Do not create repo files outside allowed paths
- Do not commit or push

## Rollback

1. Remove the generated handoff prompt file if created
2. No source or test changes to revert

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, plan_path, handoff_score, verdict.

## Sample Invocation

```
/execution-handoff
# Inputs:
#   plan_path: reports/planning/r94-sprint-plan.md
#   hardening_score: 20/22
```

## Changelog

- 1.0 (2026-05-08): Initial version. Created in memory-planning-methodology-and-agent-handoff sprint.
- 1.1 (2026-06-03): Added allowed/forbidden paths, constraints, rollback, transcript, sample invocation (Skills R102).
