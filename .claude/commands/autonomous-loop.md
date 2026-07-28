---
version: "2.1"
last-updated: "2026-06-21"
phase-available: "all"
gate-required: null
created-by: autonomous-loop activation sprint
updated-by: CCI-production-hardening
---

# /autonomous-loop

Execute the format-factory autonomous sprint loop continuously: check continuation →
inject declaration skeleton → execute sprint from next-sprint.md → closeout via
autonomous_cycle.py → repeat until TRUE_EXTERNAL_GATE or context exhaustion.

This is the actuator that was missing. The signals (continuation-signal.json,
approval-gates.md, next-sprint.md) already existed; this command wires them together.

## Supreme Directive

NEVER stop between iterations unless a TRUE_EXTERNAL_GATE is reached:
- Git push credentials unavailable
- Gate 11 execution approval required (Babar Raza)
- PyPI/NuGet publication credentials

**Canonical policy:** `docs/governance/authorization-policy-v1.yaml` (FORMAT_FACTORY_GATE_AUTHORIZATION_V1)

Advisory STOP signals (MAX_ITERATIONS, APPROVAL_GATE, NO_UNSAFE_SOURCE_STATE, etc.)
are overridden: read next-sprint.md directly and continue. Max iterations resets to
0, never blocks.

**EXCEPTION:** SESSION_MISMATCH, CHAT_ID_MISMATCH, ACTIVE_PLAN_INCOMPLETE, and
ACTIVE_PLAN_LOCK_CORRUPT are NON-OVERRIDABLE hard stops. See Step 0 and Step 1 below.

---

## Loop Steps (repeat until hard stop)

### Step 0 — Plan Lock Pre-Check (runs BEFORE check_continuation.py)

Check whether a per-chat plan is active and incomplete:

```python
python -c "
import json, sys
from pathlib import Path

# TC-HARD-003 (2026-06-22): DONE_STATUSES extended to include DEFERRED and
# TERMINAL_CLOSED_AUTHORIZED_OVERRIDE so foreign-session deferred plans and
# authorized-override closures do not falsely block the sprint loop.
DONE_STATUSES = {'COMPLETE', 'TERMINAL_CLOSED', 'DEFERRED'}

def _is_done(d):
    s = d.get('status')
    if s in DONE_STATUSES:
        return True
    # TERMINAL_CLOSED_AUTHORIZED_OVERRIDE is done only if it has a valid authorization_id
    if s == 'TERMINAL_CLOSED_AUTHORIZED_OVERRIDE' and d.get('authorization_id'):
        return True
    return False

def _get_session_id():
    try:
        sys.path.insert(0, 'tools/supervisor')
        from continuation_identity import get_or_create_session_identity
        return get_or_create_session_identity().session_id
    except Exception:
        return None

lock_path = Path('.local/supervisor/active-plan-lock.json')
locks_dir = Path('.local/supervisor/plan-locks')
current_sid = _get_session_id()
found = None

if lock_path.exists():
    d = json.loads(lock_path.read_text(encoding='utf-8'))
    if not _is_done(d):
        found = d

if not found and locks_dir.is_dir():
    for f in sorted(locks_dir.glob('*.json')):
        d = json.loads(f.read_text(encoding='utf-8'))
        # Skip locks from other sessions (TC-HARD-003: session-scoped filtering)
        lock_sid = d.get('session_id')
        if lock_sid and current_sid and lock_sid != current_sid:
            continue
        if not _is_done(d):
            found = d
            break
print(json.dumps(found))
sys.exit(1 if found else 0)
"
```

- Exit 0 (found=null): No active plan. Proceed to Step 1.
- Exit 1 (found=plan data): **HARD STOP. An active plan is incomplete.**
  Read the plan file at `found["plan_path"]`. Find the next OPEN taskcard.
  Execute it. Do NOT proceed to Step 1. Do NOT read next-sprint.md.
  This stop CANNOT be overridden by the Supreme Directive.

### Step 0c — Coordination preflight (Mission AGENT-COORD-2026-07-15)

Claude Code sessions are coordinated ambiently by the hooks in
`.claude/settings.json` (SessionStart auto-registers; PreToolUse auto-claims
and attributes; PostToolUse journals). Before starting loop work, verify the
plane and claim the loop's broad scope explicitly:

```
python -m tools.supervisor.coordination status
python -m tools.supervisor.coordination claim --resource logical:mission:format-factory-main --mode EXCLUSIVE_WRITE
```

- `status` exit 1 means OPEN conflicts exist: resolve them first
  (`conflicts list` / `conflicts resolve --id ... --state ... --note ...`).
- A claim conflict (exit 2) means another controller/agent owns the mission
  scope — do NOT proceed with overlapping work; coordinate or take over a
  STALE lease via `takeover --reason` only.
- On loop exit: `release --all`, then `complete`.
- Never `git add -A`/`git add .`; never clean or revert unexplained changes
  (AGENTS.md Section CO).

### Step 1 — Check continuation signal

```
python tools/supervisor/check_continuation.py --repo-root . --track product
```

**NON-OVERRIDABLE STOPS (Supreme Directive does NOT apply):**

- verdict=STOP, reason=SESSION_MISMATCH → **HARD STOP.**
  A different chat's continuation signal was detected. Do NOT consume it.
  This chat has no authority over another chat's state.
  To adopt the prior session explicitly:
  `python tools/supervisor/reset_track_signal.py --track product`
  Then restart from Step 0. Do NOT read next-sprint.md.

- verdict=STOP, reason=ACTIVE_PLAN_INCOMPLETE → **HARD STOP.**
  A per-chat plan is loaded and not yet complete. Do NOT switch to product deepening.
  Read the active plan file. Execute the next open taskcard. When all taskcards are
  CLOSED, run `write_plan_lock.py --complete`. Only then resume the sprint loop.

- verdict=STOP, reason=CHAT_ID_MISMATCH → **HARD STOP (Track M only).**
  NOTE: This stop can only fire under `--track machinery` (Track M / autonomous_orchestrator.py).
  This loop uses `--track product`; CHAT_ID_MISMATCH cannot fire here.
  If running Track M directly: a different chat's machinery state was detected. Do NOT consume it.
  Re-initialize Track M state for this chat via autonomous_orchestrator.py.

- verdict=STOP, reason=ACTIVE_PLAN_LOCK_CORRUPT → **HARD STOP.**
  Plan lock file is malformed. Inspect and repair manually. Do NOT proceed.

- verdict=STOP, reason=PLAN_COMPLETED_IN_SESSION → **HARD STOP (non-overridable).**
  The current session's plan was completed (status=COMPLETE, session_id matches).
  Report plan completion to the user and STOP. Do NOT auto-continue to product deepening.
  Ledger work requires explicit user authorization in a new or the same session.
  This stop is a safety net for cases where --complete was used instead of --terminal.
  The Supreme Directive "never stop" does NOT override PLAN_COMPLETED_IN_SESSION.

- verdict=STOP, reason=EXTERNAL_GATE or GIT_PUSH or GATE_11 → Report to user, stop.

- verdict=STOP, reason=structural_govblock_must_be_resolved_first → **HARD STOP
  (non-overridable, but NOT a TRUE_EXTERNAL_GATE).**
  A structural GOV_BLOCK (`tools/supervisor/governance_block_registry.py`'s
  `STRUCTURAL_GOV_BLOCKS`) was detected in `rework_items` by check_continuation.py's
  Check 8 (see `/pre-sprint-governance-hook`). The Supreme Directive's generic
  "any OTHER reason → override, continue" catch-all below does NOT apply to this
  reason — do not fall through to it. The agent CAN resolve this autonomously: the
  NEXT sprint must be the analytics-separation refactor for the blocking format
  (CLAUDE.md's "GOV_BLOCK Exception" section; §8.1 Analytics Separation Protocol in
  `docs/code-quality/production-library-standard-v2.md`). Only after the structural
  GOV_BLOCK item is resolved (gone from `rework_items`, or `govblock_resolved_by` is
  set on the signal) may product deepening resume.

**OVERRIDABLE STOPS (Supreme Directive applies — read next-sprint.md and continue):**

- verdict=CONTINUE → proceed to Step 2 normally
- verdict=STOP, reason=MAX_ITERATIONS → Reset iteration to 0, continue
- verdict=STOP, reason=APPROVAL_GATE_NO or APPROVAL_GATE_MISSING → Override, continue
- verdict=STOP, reason contains NO_ (continuation_state check) → Override, continue
- verdict=STOP, reason=AUTONOMOUS_CONTINUE_FALSE → Override if no hard_stops_detected, continue
- verdict=STOP, reason=HARD_STOP → Override ONLY if rework items are addressable this sprint
- verdict=STOP, any OTHER reason not explicitly listed in the NON-OVERRIDABLE list
  above (this includes `structural_govblock_must_be_resolved_first`, which IS
  explicitly listed above and therefore excluded from this catch-all)
  → Override, read next-sprint.md, continue

### Step 2 — Inject declaration skeleton

Generate a run_id: `autonomous-loop-YYYYMMDD-HHMMSS-<short_sha>`

```
python tools/supervisor/sprint_executor.py inject-declaration <run_id>
```

Note the declaration path printed: `.local/evidences/<run_id>/evidence-declaration.yaml`

### Step 2a — Skill Coverage Pre-Check (MANDATORY for product work)

Before executing the sprint, scan the tasks in `next-sprint.md` for any that
involve modifying files under `src/python/` or `src/net/`.

For EACH such task:
1. Identify the `work_type` (python_api, dotnet_api, dogfood_export, etc.)
2. Run `/check-skill-coverage` with the work_type and format_id
3. If result is `PROCEED_WITH_SKILL`: record the `skill_id` and proceed with skill invocation
4. If result is `BLOCKED_SKILL_GAP`: execute skill-gap workflow first:
   a. The taskcard has been created by `/check-skill-coverage`
   b. Design and register the missing skill (or escalate to planning)
   c. Only after skill is registered: proceed with product work using the skill
   d. Do NOT skip this step — skill-first is non-negotiable

This check is NOT required for non-product tasks (governance, reporting, docs, tools).

**SKILL-FIRST NON-NEGOTIABLE RULE:**
No sprint may modify `src/python/` or `src/net/` without first:
- Identifying the covering skill from `.supervisor/skill-registry.yaml`
- Invoking that skill explicitly (not just mentioning it in prose)
- Recording the `skill_id` in the evidence declaration's evidence_artifacts

If a task in `next-sprint.md` says "edit src/..." without naming a skill,
treat this as a missing skill signal — run `/check-skill-coverage` before proceeding.

### Step 3 — Execute the sprint

Read `reports/supervisor/next-sprint.md` (the current sprint prompt).
Also read `.local/supervisor/next-work-items.json` for structured work items.
If rework_items were in the continuation signal output, address them FIRST.

For ALL product source work (src/ modifications):
- Use the skill identified in Step 2a
- Name the skill_id in every evidence_artifact entry for product work
- Emit a skill invocation transcript to `reports/skills-r<N>/skill-transcripts/`

Execute all tasks. Do not summarize. Do not ask the user. Work continuously.

After completing the sprint work:
- Run tests: `python -m pytest tests/ -x -q 2>&1 | tail -20`
- Record changed files, test counts, and evidence

### Step 4 — Fill in the declaration

Edit `.local/evidences/<run_id>/evidence-declaration.yaml` (the skeleton from Step 2).
Fill in:
- `end_time` (current ISO timestamp)
- `git_head_end` (current HEAD)
- `git_status_final` (output of `git status --short`)
- `planned_work_items` (list of objects with item_id, title, status, evidence_paths, tests_supporting)
- `completed_work_items` (list of item_id strings for completed items)
- `changed_files` (list of changed file paths)
- `tests_run` (integer — full suite count)
- `test_results.passed/failed/skipped/errors`
- `evidence_artifacts` (list of {path, type, description, related_work_items})
- `worker_self_verdict` (prose summary)
- `worker_self_grade` (PASS / PARTIAL / FAIL / BLOCKED)
- `next_recommended_work` (list of strings)

### Step 4b — Validate declaration before closeout

```
python tools/supervisor/sprint_executor_validate.py \
  .local/evidences/<run_id>/evidence-declaration.yaml --repair
```

Fix any FAIL errors before proceeding. The --repair flag auto-fixes common issues
(fence stripping, type coercion, banned field removal).

### Step 5 — Closeout via autonomous_cycle.py

```
python tools/supervisor/autonomous_cycle.py \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```

Check exit code:
- 0 → all items ACCEPTED, autonomous_continue=true
- 3 → rework required — note rework_items, will address in next iteration
- 1 or 9 → log error, continue anyway (Supreme Directive: closeout must not block)

### Step 6 — Build review package

```
python tools/supervisor/sprint_executor.py build-review-package \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```

Print the **absolute path** (starting with `C:\Users\prora\OneDrive\Documents\GitHub\format-factory\`)
and **SHA-256** of the ZIP.

### Step 7 — Loop back to Step 1

Read the updated continuation-signal.json and repeat from Step 1.

---

## Decision Table

| Condition | Action |
|-----------|--------|
| Step 0: active plan found, status not in {COMPLETE, TERMINAL_CLOSED, DEFERRED, TERMINAL_CLOSED_AUTHORIZED_OVERRIDE+auth_id} | **HARD STOP** — execute plan taskcard, not sprint |
| verdict=CONTINUE | Execute sprint normally |
| verdict=STOP, reason=SESSION_MISMATCH | **HARD STOP** — run reset_track_signal.py first |
| verdict=STOP, reason=ACTIVE_PLAN_INCOMPLETE | **HARD STOP** — execute plan taskcard |
| verdict=STOP, reason=CHAT_ID_MISMATCH | **HARD STOP (Track M only)** — cannot fire under --track product; only from autonomous_orchestrator.py |
| verdict=STOP, reason=ACTIVE_PLAN_LOCK_CORRUPT | **HARD STOP** — repair lock manually |
| verdict=STOP, reason=EXTERNAL_GATE/GIT_PUSH/GATE_11 | Stop, report to user |
| verdict=STOP, reason=MAX_ITERATIONS | Override: reset iteration to 0, continue |
| verdict=STOP, reason=APPROVAL_GATE_NO/MISSING | Override: read next-sprint.md, continue |
| verdict=STOP, any other advisory reason | Override: read next-sprint.md, continue |
| autonomous_cycle exit 0 | Continue immediately |
| autonomous_cycle exit 3 | Note rework items, continue (address in next sprint) |
| autonomous_cycle exit 1 or 9 | Log error, continue (Supreme Directive) |
| iteration >= max_iterations | Reset iteration to 0, continue |
| tests_run=0 | Still proceed — declare 0 tests run honestly |

---

## Allowed Paths

- `.local/evidences/` (write declarations and sprint output)
- `.local/supervisor/` (read continuation signal, work items)
- `reports/supervisor/` (read next-sprint.md, approval-gates.md)
- `.supervisor/` (read schemas, policies)
- `tools/supervisor/` (execute scripts)
- `src/` (modify product source)
- `tests/` (create and run tests)

## Forbidden Paths

- `registry/format-registry.yaml` (registry authority)
- `AGENTS.md`, `GOVERNANCE.md` (governance docs)
- `plans/master-plan.md` (read only)

---

## Usage

```
/autonomous-loop
```

## Promotion Ledger Awareness (TC-CQGA-033-04)

The autonomous loop interacts with `registry/promotion-ledger.yaml` at each sprint closeout.
`autonomous_cycle.py` checks for api_baseline_hash changes on `PROMOTED_STABLE` entries.

**States:** `DRAFT → IMPLEMENTATION_VERIFIED → PILOT_ACCEPTED → PROMOTED_STABLE → REOPENED`

**REOPENED trigger:** When `autonomous_cycle.py` detects a hash change on a `PROMOTED_STABLE`
entry (promoted_files changed without a re-proof bundle), the entry is set to `state=REOPENED`
and the sprint verdict includes `WARN(PROMOTION_INTEGRITY_BREACH)`. The format must be
re-verified before returning to `PROMOTED_STABLE`.

**V119 validator** (`validate_promoted_code_changed_without_reopening`) also blocks sprint
declarations that modify `PROMOTED_STABLE` files without declaring REOPENED status.

The loop does NOT stop on a REOPENED event — it logs it and continues. The next sprint for
that format must address the re-proof requirement.

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

## Output Format

- PASS / FAIL / PARTIAL verdict printed to stdout
- Per-item findings list with skill_id, issue, and severity
- Report file at `reports/` with structured YAML findings
