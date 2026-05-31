# Format Factory — Claude Code Session Instructions

## Session Start (MANDATORY — do this before anything else)

Read `reports/supervisor/session-resume.md` at the start of every session.
This file is generated automatically by the supervisor pipeline after each sprint and contains:
- Last sprint outcome and test counts
- Whether contradictions exist that block autonomous continuation
- Current supervisor MODE and MCP status
- What to do next

If `session-resume.md` does not exist yet, read `plans/master-plan.md` instead.

## After Reading session-resume.md

Check `reports/supervisor/approval-gates.md`:
- `AUTONOMOUS_CONTINUE: YES` → proceed with `next-sprint.md` tasks
- `AUTONOMOUS_CONTINUE: NO` → address contradictions listed in `reports/supervisor/contradictions.md` first

## Governance (always applies)

- Read `AGENTS.md` before taking any action.
- No push, no commit, no gate approval without explicit human authorization.
- Format Factory gate authority is in `registry/format-registry.yaml` — supervisor output is advisory only.
- Commercial readiness (Gate 11 G11-G) requires human approval from Babar Raza.
