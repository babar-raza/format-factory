---
version: "1.0"
last-updated: "2026-05-08"
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

## Changelog

- 1.0 (2026-05-08): Initial version. Created in memory-planning-methodology-and-agent-handoff sprint.
