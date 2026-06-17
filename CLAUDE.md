# Format Factory — Claude Code Session Instructions

## Session Start (MANDATORY — do this before anything else)

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

### Mandatory Plan Files (read every session)

Read ALL files in the `plans/` root directory at the start of every session:
- `plans/master-plan.md` — the master project plan
- `plans/spec-to-feature-radical-correction-plan.md` — the spec-to-feature correction plan (master authority)
- `plans/snoopy-juggling-seal.md` — active plan context

These files define the project's strategic direction and must be read before any work begins.
If new files appear in `plans/`, read those too.

## After Reading session-resume.md

Check `reports/supervisor/approval-gates.md`:
- `AUTONOMOUS_CONTINUE: YES` → proceed with `next-sprint.md` tasks
- `AUTONOMOUS_CONTINUE: NO` → address contradictions listed in `reports/supervisor/contradictions.md` first

## Spec-to-Feature Correction Plan (READ before product/architecture work)

Before any product architecture, source generation, spec-parity, or capability work, read:
- **Quick reference:** `docs/spec-to-feature-correction-plan-summary.md`
- **Full plan:** `plans/spec-to-feature-radical-correction-plan.md` (27 sections, ~3200 lines)

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

- Sprint closeout (evidence declaration, autonomous-cycle, review package) is best-effort
  infrastructure. If any closeout step fails, errors, times out, or gets stuck: **skip it
  and continue executing the next sprint immediately.**
- Closeout must NEVER block the next sprint. If autonomous-cycle exits non-zero, log the
  error and proceed. If the review package builder fails, log it and proceed. If the
  declaration YAML is invalid, log it and proceed.
- The only closeout that matters is the master plan. Every sprint must make progress on
  `reports/supervisor/next-sprint.md` tasks or gap-ledger closures.
- Do NOT pause, summarize, or ask the user between sprints. Do NOT say "let me know" or
  present options. Execute continuously until a TRUE_EXTERNAL_GATE or context exhaustion.

## Sprint Closeout (best-effort — must not block continuation)

After completing sprint work, attempt these steps. If any step fails, log the failure
and proceed to the next sprint immediately.

0. **Sync the source structure baseline** (best-effort — prevents false regression alerts):
   If any `src/python/` source files were modified, run the baseline sync before declaration:
   ```python
   python -c "import json,ast;from pathlib import Path;bp=Path('registry/source-structure-baseline.json');b=json.loads(bp.read_text());k=b['known_violations'];[exec('entry[\"loc\"]=sum(1 for _ in Path(rel).open());tree=ast.parse(Path(rel).read_text());entry[\"functions\"]=sum(1 for n in ast.iter_child_nodes(tree) if isinstance(n,ast.FunctionDef))') for rel,entry in k.items() if Path(rel).is_file() and rel.endswith('.py')];bp.write_text(json.dumps(b,indent=2)+chr(10))"
   ```

1. **Write an evidence declaration** at `.local/evidences/<run_id>/evidence-declaration.yaml`
   - Declare all work items with status, evidence paths, and test references
   - Include test results, changed files, and worker self-verdict
   - See `docs/automation/supervisor-worker-contract.md` for the full field list

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
