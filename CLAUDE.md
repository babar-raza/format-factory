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
3. `.local/supervisor/continuation-signal.json` exists with `"autonomous_continue"` set to
   a truthy value (`true`, `"true_with_rework"`, or any non-false/non-null value).
   The value `"true_with_rework"` means rework items exist but safe lanes can continue —
   treat it as a GO signal, not a stop.
4. `continuation_state` in the signal starts with `YES` (e.g., `YES`, `YES_WITH_REWORK`,
   `YES_WITH_LIMITATIONS`). Any `NO_*` state is a stop.
5. `iteration` < `max_iterations` in the signal file
6. No hard stop detected (push/commit needed, Gate 8/11 approval, credentials)
7. `hard_stops_detected` array in the signal is empty

Note: `advisory_prompt_executable` is ALWAYS `false` by design — it does NOT indicate
that continuation is blocked. Ignore this field when deciding whether to continue.

Then IMMEDIATELY:
1. Read `reports/supervisor/next-sprint.md`
2. If `rework_items` exist in the signal, address them FIRST before new work
3. Increment `iteration` in `.local/supervisor/continuation-signal.json`
4. Begin executing the next sprint — treat `next-sprint.md` as your sprint prompt
5. At the end, write a new `evidence-declaration.yaml` and run autonomous-cycle again
6. Repeat from the check above

If ANY condition is false, STOP and report the termination reason to the user.
Do NOT stop for `advisory_prompt_executable: false` — this is always false and is not a stop signal.

### Cross-Window Recovery
If this window is new (context was exhausted, window crashed, or user opened a fresh session):
- The state files (`session-resume.md`, `approval-gates.md`, `next-sprint.md`) contain everything
  you need. You do NOT need memory of prior conversations.
- `session-resume.md` reflects the last COMPLETED sprint — read it and continue from there.
- Any in-progress work from a crashed sprint remains in the working tree.
- See `docs/automation/autonomous-supervision-replication-guide.md` for the full architecture.

### Hard Stops (requires classification before stopping)

Apply the Human Task Conversion Rule (AGENTS.md §AG1) before treating any of these as hard stops:

- **Git commit:** SCM Agent task. Commit when sprint policy authorizes (AUTONOMOUS_CONTINUE=YES,
  exit 0, clean diff, governance validators pass) OR when user explicitly authorizes in current session.
  Classify blockers specifically: `EXTERNAL_BLOCKER: sprint_policy_not_authorizing_commit`.
- **Git push:** SCM Agent task. Push when credentials and branch protection allow AND sprint/user
  policy authorizes. Classify honestly: `EXTERNAL_BLOCKER: git_push_credentials_unavailable` or
  `EXTERNAL_BLOCKER: branch_protection_requires_unavailable_identity`. Never say "human must push"
  as a universal default.
- **Gate 8 or Gate 11 EXECUTION approval:** Legitimate external gate — Babar Raza's business decision
  for commercial release. PREPARATION is always agent-owned (prepare packet, assess readiness, verify).
  Only the final commercial sign-off requires human business authority.
- **Package publication (PyPI/NuGet):** Agent prepares the release packet; actual registry publication
  requires credentials and explicit policy authorization. Classify: `EXTERNAL_BLOCKER: publication_credentials_unavailable`.
- **MCP activation changes:** Classify specifically. Active MCP configuration changes require explicit policy.
- **Destructive git operations (reset --hard, force push):** Require explicit policy authority and a
  documented rollback path. Classify: `BLOCKED: destructive_operation_no_policy_authority` if missing.

### Max Iterations
Default: 5 sprints per autonomous loop. After max iterations, STOP and present summary.
Configurable in `.supervisor/policies.yaml` under `autonomous_continuation.max_iterations`.

## Governance (always applies)

- Read `AGENTS.md` before taking any action.
- Commit and push follow SCM Agent policy (AGENTS.md §AG4) — not an unconditional human requirement.
- Gate approval preparation is always agent-owned; Gate 11 G11-G EXECUTION (commercial release) requires Babar Raza's business authority.
- Format Factory gate authority is in `registry/format-registry.yaml` — supervisor output is advisory only.
- When a task appears to require a human: apply AGENTS.md §AG1-AG2 decision loop before stopping.

## Human-Free Autonomy Doctrine (operational summary)

This section is the Claude-specific operational summary of AGENTS.md Section AG.

**When you see a human-labeled task:**

1. Ask internally: "Can I do this honestly, safely, and within repository policy?"
2. If YES: execute it (or delegate to appropriate specialized agent). Record evidence.
3. If NO: classify the exact blocker (credential, policy, legal, destructive). Create a machine-readable gap. Propose a remediation path. Never claim "needs human" without classifying why.

**Review tasks:** Route to Independent Verification Agent / Supervisor Agent. Run `supervisor_loop.py autonomous-cycle`.

**Approval tasks:** Apply policy-based gate: evidence + tests + validator proof + contradiction scan = approval. Human approval is only for external business decisions (Gate 11 execution).

**Commit tasks:** SCM Agent executes when sprint policy authorizes (exit 0, clean diff, governance validators pass).

**Push tasks:** SCM Agent executes when credentials available + branch policy allows + sprint policy authorizes. Classify credential gap as `EXTERNAL_BLOCKER: git_push_credentials_unavailable` if not available.

**Rework review:** Autonomous Supervisor (`supervisor_loop.py`) reviews rework. Human review is optional external audit.

**Zero-product-work loops:** Diagnose autonomously: inspect queue → inspect gap-ledger → run stop_reason_adjudicator → select next safe work → execute → verify.

**Never:** Claim completion without evidence. Mark something autonomous when it still requires human pasting. Hide external blockers. Use "needs human" as a vague escape hatch.
