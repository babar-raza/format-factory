# Format Factory — Claude Code Session Instructions

## Session Start (MANDATORY — do this before anything else)

### Step 0 — Plan Lock (runs BEFORE reading session-resume.md, BEFORE any sprint work)

Check whether a per-chat plan file is loaded. Look for a system message containing
`A plan file exists from plan mode at:` in the conversation context.

**If a plan file is loaded:**
1. **Migrate external plan to in-repo FIRST** — if the plan file path is outside the repository
   (contains `/.claude/plans/` or `\.claude\plans\`), copy it into the repo before locking:
   ```
   # Copy to in-repo location
   cp <external-plan-path> plans/.claude/<filename>
   # Redirect the lock to the in-repo path
   python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/<filename>
   ```
   Example: plan at `C:/Users/.../.claude/plans/glistening-leaping-chipmunk.md` →
   copy to `plans/.claude/glistening-leaping-chipmunk.md`, then lock that path.
   The external file is the **seed only** — all subsequent reads, writes, taskcard
   updates, and hardening go to `plans/.claude/<filename>` in the repo.
2. Write the plan lock IMMEDIATELY — before any sprint, before any continuation check:
   ```
   python tools/supervisor/write_plan_lock.py --plan-path <plan-file-path>
   ```
   Example: `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/glistening-leaping-chipmunk.md`
3. The lock blocks `check_continuation.py` from returning CONTINUE for sprint loops.
4. Execute the loaded plan exclusively. Do NOT resume prior sprints. Do NOT run product
   deepening rotations. The conversation summary saying "sprint N was in progress" is
   IRRELEVANT — the loaded plan is the SOLE work authority.
5. When all plan taskcards are complete, run:
   ```
   python tools/supervisor/write_plan_lock.py --plan-path <plan-file-path> --terminal
   ```
   Use `--terminal` (NOT `--complete`) for in-session plan closures. `--terminal` writes
   `status: "TERMINAL_CLOSED"` which causes `check_continuation.py` to return a
   `POST_PLAN_TERMINAL` stop — blocking ledger work in the same session. `--complete`
   is reserved for marking a plan done from an external/background context where the
   ledger should become available in future sessions; it does NOT block the current session.
   The two flags are NOT interchangeable for in-session plan completion.

   **For MACHINERY or LIFECYCLE_HARDENING plans (plan type: machinery_hardening):**
   Before writing `--terminal`, run the post-completion audit:
   ```
   python tools/supervisor/lifecycle_audit.py \
     --mission-id <mission-id-from-plan-header> \
     --sprint-id <last-taskcard-id>
   ```
   Then close with:
   ```
   python tools/supervisor/write_plan_lock.py \
     --plan-path <plan-file-path> --terminal --audit-gate
   ```
   If the lock is written as `ITERATION_REQUIRED` (audit found unresolved work):
   - Do NOT stop. `check_continuation.py` will return CONTINUE for this session.
   - Read `.local/supervisor/lifecycle-audit-results.json` for next action.
   - Use the Edit tool to add any new taskcards identified by the audit to this plan.
   - Execute the next pending taskcard immediately.

   If the lock is written as `TERMINAL_CLOSED` (audit passed):
   - The POST_PLAN_TERMINAL rules below apply. STOP and report to user.

   Then **IMMEDIATELY STOP**. Report plan completion to the user:
   "Plan [name] complete. All [N] taskcards closed. Awaiting your next instruction."

   **POST-PLAN TERMINAL RULE (NON-NEGOTIABLE):**
   - Do NOT call `check_continuation.py` after plan completion
   - Do NOT read `next-sprint.md` or `next-work-items.json`
   - Do NOT start any product deepening, rotation, or ledger work
   - Do NOT interpret "sprint loop becomes available" as authorization to start it now
   - Plan completion is the **TERMINAL EVENT** for the chat session
   - The sprint loop becomes available for **FUTURE sessions** with **EXPLICIT user authorization**
   - The Supreme Directive "never stop" does **NOT** apply here — `POST_PLAN_TERMINAL` is a
     named legitimate stop (see Supreme Directive section below)
   - **Safety net:** If `--terminal` was accidentally omitted and `--complete` was used instead,
     `check_continuation.py` will return `PLAN_COMPLETED_IN_SESSION` (same class as
     `POST_PLAN_TERMINAL`) when it detects the current session's lock has `status=COMPLETE`.
     This is also NON-OVERRIDABLE.

   **Exception for `ITERATION_REQUIRED` status (machinery plans only):**
   If `write_plan_lock.py` wrote `ITERATION_REQUIRED` (not `TERMINAL_CLOSED`),
   `check_continuation.py` will return CONTINUE (not STOP).
   This is the correct behavior — continue executing pending taskcards.
   The POST_PLAN_TERMINAL hard stop ONLY applies when `status=TERMINAL_CLOSED`.

**If no plan file is loaded:** proceed normally to session-resume.md.

---

Read `reports/supervisor/session-resume.md` at the start of every session.
This file is generated automatically by the supervisor pipeline after each sprint and contains:
- Last sprint outcome and test counts
- Whether contradictions exist that block autonomous continuation
- Current supervisor MODE and MCP status
- What to do next

If `session-resume.md` does not exist yet, read `plans/master-plan.md` instead.

### Cross-Chat Continuation Isolation (CCI-MVP)

Before following any continuation instructions from `session-resume.md`:
1. Check if the user's current request is related to the sprint described in `session-resume.md`.
2. If the user explicitly asks to continue autonomous work, follow `session-resume.md` normally.
3. If the user's request is **unrelated** to the sprint in `session-resume.md`, do NOT auto-continue
   the previous sprint. Treat `session-resume.md` as background context only.
4. If `continuation-signal.json` contains a `session_id` field and you have a different session
   identity, the signal belongs to another chat — do not consume it.
5. **SESSION_MISMATCH, CHAT_ID_MISMATCH, POST_PLAN_TERMINAL, and PLAN_COMPLETED_IN_SESSION
   are NON-OVERRIDABLE hard stops.** When `check_continuation.py` returns
   `verdict=STOP, reason=SESSION_MISMATCH`, `reason=CHAT_ID_MISMATCH`,
   `reason=POST_PLAN_TERMINAL`, or `reason=PLAN_COMPLETED_IN_SESSION`, do NOT override
   using the Supreme Directive.
   - `SESSION_MISMATCH` / `CHAT_ID_MISMATCH`: protect against cross-chat state contamination.
     To adopt a prior session's signal explicitly, run:
     `python tools/supervisor/reset_track_signal.py --track product`
   - `POST_PLAN_TERMINAL`: plan was closed with `--terminal` in this session. STOP.
   - `PLAN_COMPLETED_IN_SESSION`: plan was closed with `--complete` (instead of `--terminal`)
     but the session-keyed lock identifies this session as the owner. STOP.
     Same terminal semantics as POST_PLAN_TERMINAL. Explicit user authorization required.
6. **Context compaction disambiguation (HARD RULE):** When a new conversation begins
   following context compaction, and the user's first message is "continue" or a similar
   single-word continuation, do NOT treat this as authorization for the autonomous sprint
   loop if the prior conversation was executing a per-chat plan. Instead, determine the
   prior plan's status (COMPLETE or IN_PROGRESS) and ask:
   "The prior conversation was executing plan [X]. The plan is [COMPLETE/IN_PROGRESS].
   Do you want to: (a) start a new task, (b) resume the plan (if incomplete), or
   (c) begin autonomous product deepening?"
   Do NOT default to autonomous product deepening after a plan-execution session.
7. **"continue" is only an autonomous loop signal when ALL of:**
   - The prior session was running autonomous product deepening (NOT a per-chat plan), AND
   - The continuation signal shows `autonomous_continue: true` with NO post-plan state, AND
   - No per-chat plan file is loaded in the current conversation.

### Mandatory Plan Files (read every session)

Read ALL files in the `plans/` root directory at the start of every session:
- `plans/master-plan.md` — the master project plan
- `plans/strategic/spec-to-feature-radical-correction-plan.md` — the spec-to-feature correction plan (master authority)
- The current chat's plan mode file, if one is loaded — detected from the system message `A plan file exists from plan mode at: <path>` (see Step 0 above)

These files define the project's strategic direction and must be read before any work begins.
If new files appear in `plans/`, read those too.

### VR-003: Cross-Check MEMORY.md Taskcard Claims Against HEAD

When MEMORY.md cites a commit for a fix to a taskcard listed as `not_attempted`
in master-plan §26, verify the fix exists at HEAD before continuing. If verified:
update §26 status. Do not trust MEMORY.md claim without HEAD verification.

## After Reading session-resume.md

Check `reports/supervisor/approval-gates.md`:
- `AUTONOMOUS_CONTINUE: YES` → proceed with `next-sprint.md` tasks
- `AUTONOMOUS_CONTINUE: NO` → address contradictions listed in `reports/supervisor/contradictions.md` first

## Spec-to-Feature Correction Plan (READ before product/architecture work)

Before any product architecture, source generation, spec-parity, or capability work, read:
- **Quick reference:** `docs/spec-to-feature-correction-plan-summary.md`
- **Full plan:** `plans/strategic/spec-to-feature-radical-correction-plan.md` (27 sections, ~3200 lines)

Key rules from this plan:
1. **System healing first:** Lanes 1-6, 14, 15 MUST complete before product regeneration (Lanes 7-13)
2. **Canonical naming:** Spec QName → canonical class (e.g., `Table.TableCell`) → facade in `Compat/` only (e.g., `FodsCell`). NEVER use format-prefixed names as primary implementation targets.
3. **Gate 11:** NOT approved. Babar Raza is the only approver. Criteria: C1-C20 (.NET), P1-P11 (Python).
4. **No fake progress:** Skeleton-only files are `architecture_only`, not product progress. No model class without `spec_qname` mapping. No product-progress claim without spec parity evidence.
5. **Supervision gaps exist:** Lane ownership and DAG ordering are NOT enforced by code (prompt-only). Overclaim detector is never called. These are known gaps being addressed in Lane 14.
6. **Zero durable learning:** All decision rules are static. No failure-memory.json exists. Corrections do not auto-propagate. Being addressed in Lane 15.

## Supreme Directive: Autonomous Execution Never Stops

The autonomous supervision loop is the highest-priority operational rule. **Nothing may block
forward progress on the master plan except TRUE_EXTERNAL_GATEs** (git push credentials,
Gate 11 execution approval by Babar Raza, package publication credentials).

**Named legitimate stop conditions (NOT TRUE_EXTERNAL_GATEs but still valid stops):**
- `POST_PLAN_TERMINAL`: Per-chat plan completed all taskcards in the current session →
  STOP and report to user. This is NOT a TRUE_EXTERNAL_GATE but IS a valid session boundary.
  The next ledger sprint requires explicit user authorization in the same or a new session.
  The Supreme Directive "never stop" does NOT override POST_PLAN_TERMINAL.

- Sprint closeout (evidence declaration, autonomous-cycle, review package) is best-effort
  infrastructure. If any closeout step fails, errors, times out, or gets stuck: **skip it
  and continue executing the next sprint immediately.**
- Closeout must NEVER block the next sprint. If autonomous-cycle exits non-zero, log the
  error and proceed. If the review package builder fails, log it and proceed. If the
  declaration YAML is invalid, log it and proceed.

### GOV_BLOCK Exception (BINDING — overrides Supreme Directive for structural failures)

`GOV_BLOCK:monolith_detection_validator`, `GOV_BLOCK:validate_source_architecture`,
`GOV_BLOCK:validate_multi_responsibility_file`, and `GOV_BLOCK:validate_analytics_naming_enforced`
are **structural failures**, not transient closeout failures. The Supreme Directive "log exit 3 and
proceed" does NOT apply to these validators.

When `rework_items` in the continuation signal contains any item matching one of these validators:

1. Do NOT proceed to the next product deepening sprint
2. The NEXT sprint must be the analytics separation refactor for the blocking format
   (apply §8.1 Analytics Separation Protocol from `docs/code-quality/production-library-standard-v2.md`)
3. Only after the GOV_BLOCK rework item is resolved (gone from `rework_items`) may
   product deepening resume
4. `check_continuation.py` will return STOP with `reason: structural_govblock_must_be_resolved_first`
   as the machine-enforceable gate

This is NOT a TRUE_EXTERNAL_GATE — the agent CAN resolve it by running the analytics
separation sprint. This scope is intentionally narrow (four named validators) to avoid
blocking on unrelated governance failures.

**Production Library Standard v2:** All governance validators enforce the standard at
`docs/code-quality/production-library-standard-v2.md`. This supersedes the v1 standard.
Healing protocol for V66/V77 blocks: §8.1 of the v2 standard (Monolith Healing Protocol).
- The only closeout that matters is the master plan. Every sprint must make progress on
  `reports/supervisor/next-sprint.md` tasks or gap-ledger closures.
- Do NOT pause, summarize, or ask the user between sprints. Do NOT say "let me know" or
  present options. Execute continuously until a TRUE_EXTERNAL_GATE or context exhaustion.
- **Per-chat plan precedence (HARD LOCK — not advisory):** If a plan file is loaded for the
  current conversation (e.g., via plan mode or system reminder), that plan is the **SOLE**
  work-selection authority until ALL taskcards in it are CLOSED.
  - Do NOT switch to product deepening sprints, rotation sprints (XCF/ZST/FODG etc.), or any
    `next-sprint.md` tasks while a per-chat plan is active.
  - `APPROVAL_GATE_NO`, exit 3, exit 1, `check_continuation STOP`, and `MAX_ITERATIONS` are
    NOT plan-switches. After any such signal, continue the per-chat plan's next taskcard — do
    NOT fall back to the general ledger.
  - **"Resume from where you left off"** means resume the PLAN, not the prior product sprint.
    A conversation summary saying "sprint 275 was in progress" does NOT override the loaded plan.
    The loaded plan is ALWAYS the first priority regardless of what prior context was doing.
  - After completing one taskcard group (e.g., TC-C3-001), the next action MUST be the next
    taskcard in the same plan (e.g., TC-DIAG-001), never a different plan's task.
  - The general ledger (`next-sprint.md`) governs ONLY when no per-chat plan is active.
  - MEMORY.md rules about this are structural confirmations, not the source — this CLAUDE.md
    entry is the enforceable version.
  - **PLAN LOCK FILE (mandatory mechanical enforcement):** When a per-chat plan is loaded:
    1. IMMEDIATELY write `.local/supervisor/active-plan-lock.json`:
       ```json
       {"plan_path": "<path to plan file>", "status": "IN_PROGRESS", "last_taskcard": "<first taskcard id>"}
       ```
    2. Update `last_taskcard` as each taskcard completes.
    3. When ALL taskcards are CLOSED, write `"status": "COMPLETE"` to the lock file.
    4. `check_continuation.py` blocks CONTINUE verdicts while the lock file has `status != "COMPLETE"`.
       This provides machine-level enforcement — no agent can reach product deepening while the plan is active.

## Sprint Closeout (best-effort — must not block continuation)

After completing sprint work, attempt these steps. If any step fails, log the failure
and proceed to the next sprint immediately.

0. **Detect NEW architecture violations** (best-effort — NEVER updates existing known_violations entries):
   If any `src/python/` source files were modified, run the NEW-violations detector before declaration.
   This script SKIPS all files already in `known_violations` (they have frozen `baseline_loc_cap` ceilings).
   It only adds NEW files that exceed limits and are not yet tracked.
   ```python
   python -c "
   import json, ast, sys
   from pathlib import Path
   bp = Path('registry/source-structure-baseline.json')
   b = json.loads(bp.read_text())
   k = b['known_violations']
   changed = False
   for rel in sorted(Path('src/python').rglob('*.py')):
       parts = rel.parts
       # Skip build artifacts and nested duplicate packages
       if 'build' in parts or '__pycache__' in parts:
           continue
       # Skip nested duplicate packages (e.g. fods/fods/)
       rel_to_src = rel.relative_to('src/python')
       if len(rel_to_src.parts) >= 2 and rel_to_src.parts[0] == rel_to_src.parts[1]:
           continue
       rel_str = rel.as_posix()
       if rel_str in k:
           continue
       try:
           loc = sum(1 for _ in rel.open(encoding='utf-8', errors='replace'))
           tree = ast.parse(rel.read_text(encoding='utf-8', errors='replace'))
           fn = sum(1 for n in ast.iter_child_nodes(tree) if isinstance(n, ast.FunctionDef))
       except Exception:
           continue
       if loc > 800 or fn > 60:
           k[rel_str] = {'loc': loc, 'baseline_loc_cap': loc, 'functions': fn, 'baseline_functions_cap': fn, 'category': 'new_violation_detected'}
           changed = True
           print(f'NEW VIOLATION: {rel_str} ({loc} LOC, {fn} functions)', file=sys.stderr)
   if changed:
       bp.write_text(json.dumps(b, indent=2) + chr(10))
   "
   ```
   **IMPORTANT:** This script NEVER modifies `loc`, `functions`, `baseline_loc_cap`, or `baseline_functions_cap`
   for files already in `known_violations`. Existing violations are governed by their frozen caps.

1. **Write an evidence declaration** at `.local/evidences/<run_id>/evidence-declaration.yaml`
   - Declare all work items with status, evidence paths, and test references
   - Include test results, changed files, and worker self-verdict
   - See `docs/automation/supervisor-worker-contract.md` for the full field list
   > **WARNING:** Do NOT write sprint-closeout evidence or plan amendments to
   > `plans/strategic/snoopy-juggling-seal.md`. That file is the SAL forensics plan.
   > Sprint closeout writes ONLY to `.local/evidences/<run_id>/` and to the
   > active per-chat plan file (if amending plan content).

1b. **Validate the declaration before submitting** (best-effort — log and proceed if tool unavailable):
   ```
   python tools/supervisor/sprint_executor_validate.py \
     .local/evidences/<run_id>/evidence-declaration.yaml --repair
   ```
   The `--repair` flag auto-corrects markdown fences, type mismatches, and banned fields.
   Fix any `FAIL` errors before proceeding to step 2. If the validator itself fails, log it
   and proceed to step 2 regardless.

2. **Run the supervisor pipeline:**
   ```
   python tools/supervisor/supervisor_loop.py autonomous-cycle \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
   ```
   This validates your declaration, grades each work item, generates the next sprint prompt,
   and regenerates `session-resume.md` + `approval-gates.md` + `next-sprint.md`.

3. **Check the exit code:**
   - Exit 0 → all items accepted, continue immediately
   - Exit 3 → log rework items, attempt quick fix, continue regardless
   - Exit 1 → log declaration error, continue regardless
   - Exit 9 → log error, continue regardless

4. **Build the review package:**
   ```
   python tools/supervisor/build_declaration_review_package.py \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
   ```
   Print the **absolute path** (starting with `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\`)
   and **SHA-256** in your output. If the builder fails, log it and continue.

Do NOT use the legacy `run-on-latest --bundle` command. It is deprecated.

## Autonomous Continuation

After Sprint Closeout (or after skipping failed closeout steps), run the continuation checker:

```
python tools/supervisor/check_continuation.py
```

- **Exit code 0** + `"verdict": "CONTINUE"` → proceed **IMMEDIATELY**:
  1. Read the `next_work_items_path` from the JSON output (structured work items)
  2. Read `reports/supervisor/next-sprint.md` for prose context
  2b. **Per-chat plan precedence (HARD LOCK):** If a plan file is loaded for the current
      conversation, that plan's taskcards are the ONLY valid next action — do NOT read
      `next-sprint.md` for work selection while a per-chat plan is active. `next-sprint.md`
      is authority ONLY when no per-chat plan is active. `exit 3`, `APPROVAL_GATE_NO`, and
      `check_continuation STOP` do not override this — they are non-blocking; continue the
      plan's next taskcard immediately.
  3. If `rework_items` exist in the output, address them FIRST before new work
  4. Increment `iteration` in `.local/supervisor/continuation-signal.json`
  5. Execute the sprint — use `next-sprint.md` as your sprint prompt
  6. At the end, attempt closeout (steps 1-4 above), then repeat from here

- **Exit code 1** + `"verdict": "STOP"` → check if the stop reason is a TRUE_EXTERNAL_GATE.
  If yes, report to the user and stop. If the stop reason is anything else (advisory,
  iteration limit, stale signal), override it: read `next-sprint.md` directly and continue.

- **If check_continuation.py itself fails** → read `next-sprint.md` directly and continue.

Do NOT manually check continuation-signal.json, approval-gates.md, or iteration counts
unless check_continuation.py is unavailable.

Note: `advisory_prompt_executable` is ALWAYS `false` by design — it does NOT indicate
that continuation is blocked. Ignore this field everywhere.

### One-Mechanism Lock

For each run, select exactly one autonomous authority — either the interactive
`/autonomous-loop` command (VSCode supervised) OR `sprint_executor.py run-loop`
(headless). Never run both simultaneously. If using the interactive path in VSCode,
the headless run-loop subprocess is inactive. If using headless run-loop, the VSCode
session is not issuing separate sprint executions. See AGENTS.md §AH1 for full rule.

### Sprint Audit (mandatory between sprints)

After each sprint's closeout produces `evidence-review.json`, produce a structured
sprint audit before starting the next sprint. The audit must categorize every work
item into exactly one of these 6 classifications:

- `completed_verified` — implemented AND verified with real tests and direct evidence
- `completed_but_weakly_verified` — implementation exists; proof is synthetic, narrow, or limited
- `partially_done` — code exists but is unwired, unregistered, or unvalidated against real source
- `not_attempted` — required work not started
- `claimed_unproven` — report or state claims completion without adequate direct proof
- `risk_not_reduced` — code changed but production/pipeline risk unchanged (stale artifacts, unwired gates)

Do not present implementation as verified behavior. Do not present synthetic tests
as real-world proof. The audit is a factual inventory, not a celebration.

`AUDIT COMPLETE` is NOT a valid stopping point — proceed immediately to Plan Hardening.

### Plan Hardening (mandatory before next sprint)

Immediately after the sprint audit, before executing the next sprint:

1. Convert every `partially_done`, `not_attempted`, `claimed_unproven`, and
   `risk_not_reduced` audit finding into an owned taskcard or lane amendment.
2. Do not carry forward unresolved findings as prose recommendations — they must
   become governed tasks with status tracking.
3. Do not modify product source during this step — only update plan/taskcard state.
4. Read `reports/supervisor/next-sprint.md` AFTER hardening, not before. The
   hardened amendments take priority over stale next-sprint.md content.

`PLAN HARDENED` is NOT a valid stopping point — proceed immediately to sprint execution.
The audit and plan-hardening steps form the transition gate between sprints. Together
they must complete within the same autonomous session as the sprint they follow.

**Plan file identity rule (HARD):** When hardening, write ONLY to the active
per-chat plan file loaded in the current conversation (detected from the
`A plan file exists from plan mode at:` system message, OR from
`.local/supervisor/plan-locks/<session_id>.json`).
Do NOT write plan amendments to `plans/strategic/snoopy-juggling-seal.md` unless that
file is explicitly the active per-chat plan. `snoopy-juggling-seal.md` is the
SAL forensics plan — it is NOT a global fallback for plan amendments.
Do NOT write plan amendments to `plans/master-plan-memory.md` (ledger-only).

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
- **MAX_ITERATIONS from check_continuation.py:** This is NOT a TRUE_EXTERNAL_GATE. When
  check_continuation.py returns `"reason": "MAX_ITERATIONS"`, apply governed rollover:
  run `python tools/supervisor/sprint_executor.py run-loop` (which resets iteration to 0),
  OR manually reset `iteration` to 0 in `.local/supervisor/continuation-signal.json` and
  continue. Never treat MAX_ITERATIONS as a stop condition. See also "Max Iterations" below.

### Max Iterations
Max iterations is NOT a stop signal. When iteration >= max_iterations, reset iteration to 0
and continue. The only things that stop execution are TRUE_EXTERNAL_GATEs or context exhaustion.
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

<!-- BEGIN:CAPABILITY-INDEX generated=2026-07-03T09:37:34+00:00 source=.governance/capabilities/registry.yaml -->

## Generated Capability Index

This section is auto-generated by `tools/capability_sync/run_sync.py`.
**Do not edit manually.** Run `/sync-capabilities` to update.

Total active capabilities: 117 | Canonical registry: `.governance/capabilities/registry.yaml`

| capability_id | status | product_track | parity_status | claude_code | codex |
|---|---|---|---|---|---|
| `backfill-gate4-prototype-evidence` | active | acquisition | PARTIAL | Y | Y |
| `check-gate` | active | acquisition | FULL_PARITY | Y | Y |
| `check-release-boundary` | active | acquisition | FULL_PARITY | Y | Y |
| `create-acquisition-pack` | active | acquisition | FULL_PARITY | Y | Y |
| `score-format` | active | acquisition | FULL_PARITY | Y | Y |
| `build-obligation-register` | active | all_format_deepening | PARTIAL | Y | Y |
| `portfolio-reconcile` | active | all_format_deepening | PARTIAL | Y | Y |
| `update-obligation-entry` | active | all_format_deepening | PARTIAL | Y | Y |
| `verify-obligation-entry` | active | all_format_deepening | PARTIAL | Y | Y |
| `add-dotnet-api` | active | commercial_dotnet | FULL_PARITY | Y | Y |
| `add-dotnet-object-model-feature` | active | commercial_dotnet | FULL_PARITY | Y | Y |
| `add-same-format-writer-feature` | active | cross_product | FULL_PARITY | Y | Y |
| `add-dogfood-export` | active | cross_product_export | FULL_PARITY | Y | Y |
| `verify-dogfood-path` | active | cross_product_export | FULL_PARITY | Y | Y |
| `add-installed-package-example` | active | developer_experience | FULL_PARITY | Y | Y |
| `add-python-api` | active | foss_python | FULL_PARITY | Y | Y |
| `add-python-object-model-feature` | active | foss_python | FULL_PARITY | Y | Y |
| `format-feature-expansion` | active | foss_python | PARTIAL | Y | Y |
| `new-format-kickstart` | active | foss_python | PARTIAL | Y | Y |
| `product-source-task` | active | foss_python | PARTIAL | Y | Y |
| `python-reduced-spec-parity-model` | active | foss_python | FULL_PARITY | Y | Y |
| `create-consumer-roundtrip` | active | foss_python_consumer | PARTIAL | Y | Y |
| `backfill-task-skill-ownership` | active | governance | FULL_PARITY | Y | Y |
| `build-capability-routes` | active | governance | FULL_PARITY | Y | Y |
| `certification-assertion-scorer` | active | governance | PARTIAL | Y | Y |
| `certification-dashboard` | active | governance | FULL_PARITY | Y | Y |
| `certification-dotnet-assertion-scorer` | active | governance | PARTIAL | Y | Y |
| `certification-exception-checker` | active | governance | PARTIAL | Y | Y |
| `certification-fix-weak-assertions` | active | governance | PARTIAL | Y | Y |
| `certification-generate-exception-tests` | active | governance | PARTIAL | Y | Y |
| `certification-generate-security-tests` | active | governance | PARTIAL | Y | Y |
| `certification-inventory-extractor` | active | governance | PARTIAL | Y | Y |
| `certification-stub-detector` | active | governance | PARTIAL | Y | Y |
| `check-dom-contract` | active | governance | FULL_PARITY | Y | Y |
| `check-skill-coverage` | active | governance | FULL_PARITY | Y | Y |
| `collect-skill-execution-receipts` | active | governance | FULL_PARITY | Y | Y |
| `detect-ad-hoc-execution` | active | governance | FULL_PARITY | Y | Y |
| `detect-duplicate-skills` | active | governance | FULL_PARITY | Y | Y |
| `enforce-skill-first-execution` | active | governance | FULL_PARITY | Y | Y |
| `inventory-commands` | active | governance | FULL_PARITY | Y | Y |
| `inventory-format-dom` | active | governance | FULL_PARITY | Y | Y |
| `inventory-skills` | active | governance | FULL_PARITY | Y | Y |
| `normalize-skill-registry` | active | governance | FULL_PARITY | Y | Y |
| `post-sprint-audit` | active | governance | FULL_PARITY | Y | Y |
| `post-sprint-loop` | active | governance | FULL_PARITY | Y | Y |
| `preflight-skill-entry` | active | governance | FULL_PARITY | Y | Y |
| `qname-backfill` | active | governance | FULL_PARITY | Y | Y |
| `run-skill-idempotency` | active | governance | FULL_PARITY | Y | Y |
| `scan-residual-bypasses` | active | governance | FULL_PARITY | Y | Y |
| `select-deepening-lane` | active | governance | FULL_PARITY | Y | Y |
| `sync-skill-command-registry` | active | governance | FULL_PARITY | Y | Y |
| `validate-mutation-guard` | active | governance | FULL_PARITY | Y | Y |
| `validate-skill-contracts` | active | governance | FULL_PARITY | Y | Y |
| `autonomous-loop` | active | infrastructure | FULL_PARITY | Y | Y |
| `query-control-index` | active | infrastructure | PARTIAL | Y | Y |
| `append-layer-verification-log` | active | layer_governance | PARTIAL | Y | Y |
| `append-layer-work-log` | active | layer_governance | PARTIAL | Y | Y |
| `capability-status` | active | layer_governance | FULL_PARITY | Y | Y |
| `close-layer-task` | active | layer_governance | PARTIAL | Y | Y |
| `create-cross-layer-handoff` | active | layer_governance | PARTIAL | Y | Y |
| `create-permanent-layer-plan` | active | layer_governance | PARTIAL | Y | Y |
| `detect-stale-layer-state` | active | layer_governance | PARTIAL | Y | Y |
| `detect-unlogged-work` | active | layer_governance | PARTIAL | Y | Y |
| `documentation-structure-migration` | active | layer_governance | PARTIAL | Y | Y |
| `generate-root-status` | active | layer_governance | FULL_PARITY | Y | Y |
| `identify-primary-layer` | active | layer_governance | PARTIAL | Y | Y |
| `inventory-permanent-layer-plans` | active | layer_governance | PARTIAL | Y | Y |
| `migrate-temporary-agent-plan` | active | layer_governance | PARTIAL | Y | Y |
| `reconcile-layer-index` | active | layer_governance | PARTIAL | Y | Y |
| `reconcile-layer-task-register` | active | layer_governance | PARTIAL | Y | Y |
| `register-layer-gap` | active | layer_governance | PARTIAL | Y | Y |
| `register-layer-task` | active | layer_governance | PARTIAL | Y | Y |
| `select-next-layer-task` | active | layer_governance | PARTIAL | Y | Y |
| `sync-capabilities` | active | layer_governance | FULL_PARITY | Y | Y |
| `sync-readmes` | active | layer_governance | FULL_PARITY | Y | Y |
| `update-layer-current-state` | active | layer_governance | PARTIAL | Y | Y |
| `update-layer-master-index` | active | layer_governance | PARTIAL | Y | Y |
| `update-layer-session-handoff` | active | layer_governance | PARTIAL | Y | Y |
| `validate-capability-parity` | active | layer_governance | FULL_PARITY | Y | Y |
| `validate-permanent-layer-plans` | active | layer_governance | PARTIAL | Y | Y |
| `audit-root-tools` | active | machinery_governance | PARTIAL | Y | Y |
| `rollback-and-recovery` | active | machinery_repair | FULL_PARITY | Y | Y |
| `sync-memory` | active | maintenance | FULL_PARITY | Y | Y |
| `run-oracle` | active | oracle_execution | PARTIAL | Y | Y |
| `package-install-proof` | active | packaging | FULL_PARITY | Y | Y |
| `build-context-pack` | active | planning | FULL_PARITY | Y | Y |
| `build-evidence-bundle` | active | planning | FULL_PARITY | Y | Y |
| `create-taskcard` | active | planning | FULL_PARITY | Y | Y |
| `evidence-review-next-prompt` | active | planning | FULL_PARITY | Y | Y |
| `execution-handoff` | active | planning | FULL_PARITY | Y | Y |
| `export-plan-context` | active | planning | FULL_PARITY | Y | Y |
| `generate-execution-handoff` | active | planning | FULL_PARITY | Y | Y |
| `materialize-declaration-review` | active | planning | FULL_PARITY | Y | Y |
| `memory-sprint` | active | planning | FULL_PARITY | Y | Y |
| `plan-hardening` | active | planning | FULL_PARITY | Y | Y |
| `promote-gap-to-taskcard` | active | planning | FULL_PARITY | Y | Y |
| `record-lane-execution` | active | planning | FULL_PARITY | Y | Y |
| `reproduce-master-plan` | active | planning | FULL_PARITY | Y | Y |
| `select-poc-gap` | active | planning | FULL_PARITY | Y | Y |
| `validate-product-code-ledger` | active | planning | FULL_PARITY | Y | Y |
| `validate-skill-transcript` | active | planning | FULL_PARITY | Y | Y |
| `diff-playbook-outputs` | active | playbook_governance | PARTIAL | Y | Y |
| `export-review-queue` | active | playbook_governance | PARTIAL | Y | Y |
| `replay-acquisition-playbook` | active | playbook_governance | PARTIAL | Y | Y |
| `validate-playbook` | active | playbook_governance | PARTIAL | Y | Y |
| `sal-pipeline-heal` | active | sal_infrastructure | FULL_PARITY | Y | Y |
| `ingest-spec-sal` | active | sal_ingestion | PARTIAL | Y | Y |
| `update-capability-matrix` | active | shared_reference_snapshot | FULL_PARITY | Y | Y |
| `check-source-loc` | active | source_structure | PARTIAL | Y | Y |
| `implement-spec-stub` | active | spec_literal_healing | FULL_PARITY | Y | Y |
| `python-qname-code-reviewer` | active | spec_literal_healing | FULL_PARITY | Y | Y |
| `spec-literal-qname-to-code-mapping` | active | spec_parity | FULL_PARITY | Y | Y |
| `spec-parity-source-regeneration-and-migration` | active | spec_parity | FULL_PARITY | Y | Y |
| `spec-parity-verification` | active | spec_parity | FULL_PARITY | Y | Y |
| `spec-shaped-product-architecture-blueprint` | active | spec_parity | FULL_PARITY | Y | Y |
| `extract-analytics-from-monolith` | active | src_healing | FULL_PARITY | Y | Y |
| `add-roundtrip-test` | active | testing | FULL_PARITY | Y | Y |

<!-- END:CAPABILITY-INDEX -->
