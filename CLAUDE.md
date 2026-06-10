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

## Autonomous Continuation (when authorized)

After Sprint Closeout step 3 (checking exit code), if ALL of these are true:
1. autonomous-cycle exit code was 0
2. `reports/supervisor/approval-gates.md` contains `AUTONOMOUS_CONTINUE: YES`
3. `.local/supervisor/continuation-signal.json` exists with `"autonomous_continue": true`
4. `iteration` < `max_iterations` in the signal file
5. No hard stop detected (push/commit needed, Gate 8/11 approval, credentials)

Then IMMEDIATELY:
1. Read `reports/supervisor/next-sprint.md`
2. Increment `iteration` in `.local/supervisor/continuation-signal.json`
3. Begin executing the next sprint — treat `next-sprint.md` as your sprint prompt
4. At the end, write a new `evidence-declaration.yaml` and run autonomous-cycle again
5. Repeat from the check above

If ANY condition is false, STOP and report the termination reason to the user.

### Cross-Window Recovery
If this window is new (context was exhausted, window crashed, or user opened a fresh session):
- The state files (`session-resume.md`, `approval-gates.md`, `next-sprint.md`) contain everything
  you need. You do NOT need memory of prior conversations.
- `session-resume.md` reflects the last COMPLETED sprint — read it and continue from there.
- Any in-progress work from a crashed sprint remains in the working tree.
- See `docs/automation/autonomous-supervision-replication-guide.md` for the full architecture.

### Hard Stops (never autonomous)
- Git push or commit (requires explicit user authorization)
- Gate 8 or Gate 11 approval
- Package publication
- MCP activation changes
- Destructive git operations

### Max Iterations
Default: 5 sprints per autonomous loop. After max iterations, STOP and present summary.
Configurable in `.supervisor/policies.yaml` under `autonomous_continuation.max_iterations`.

## Governance (always applies)

- Read `AGENTS.md` before taking any action.
- No push, no commit, no gate approval without explicit human authorization.
- Format Factory gate authority is in `registry/format-registry.yaml` — supervisor output is advisory only.
- Commercial readiness (Gate 11 G11-G) requires human approval from Babar Raza.
