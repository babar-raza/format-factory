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

## Sprint Closeout (MANDATORY — do this at the end of every sprint)

After completing sprint work, you MUST:

1. **Write an evidence declaration** at `.local/evidences/<run_id>/evidence-declaration.yaml`
   - Declare all work items with status, evidence paths, and test references
   - Include test results, changed files, and worker self-verdict
   - See `docs/automation/supervisor-worker-contract.md` for the full field list

2. **Run the supervisor pipeline:**
   ```
   python tools/supervisor/supervisor_loop.py autonomous-cycle \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
   ```
   This validates your declaration, grades each work item, generates the next sprint prompt,
   and regenerates `session-resume.md` + `approval-gates.md` + `next-sprint.md`.

3. **Check the exit code:**
   - Exit 0 → all items accepted, autonomous continue possible
   - Exit 3 → critical rework (OVERCLAIMED or REJECTED items), fix before continuing
   - Exit 1 → declaration invalid, fix the YAML
   - Exit 9 → unexpected error

Do NOT use the legacy `run-on-latest --bundle` command. It is deprecated.

## Governance (always applies)

- Read `AGENTS.md` before taking any action.
- No push, no commit, no gate approval without explicit human authorization.
- Format Factory gate authority is in `registry/format-registry.yaml` — supervisor output is advisory only.
- Commercial readiness (Gate 11 G11-G) requires human approval from Babar Raza.
