---
version: "1.0"
last-updated: "2026-06-16"
phase-available: "all"
gate-required: null
created-by: autonomous-loop activation sprint
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

All other STOP signals from check_continuation.py are overridden: read
next-sprint.md directly and continue. Max iterations resets to 0, never blocks.

---

## Loop Steps (repeat until hard stop)

### Step 1 — Check continuation signal

```
python tools/supervisor/check_continuation.py --repo-root .
```

- verdict=CONTINUE → proceed to Step 2
- verdict=STOP, reason is TRUE_EXTERNAL_GATE → report to user, stop
- verdict=STOP, any other reason → override, read reports/supervisor/next-sprint.md directly, proceed to Step 2

### Step 2 — Inject declaration skeleton

Generate a run_id: `autonomous-loop-YYYYMMDD-HHMMSS-<short_sha>`

```
python tools/supervisor/sprint_executor.py inject-declaration <run_id>
```

Note the declaration path printed: `.local/evidences/<run_id>/evidence-declaration.yaml`

### Step 3 — Execute the sprint

Read `reports/supervisor/next-sprint.md` (the current sprint prompt).
Also read `.local/supervisor/next-work-items.json` for structured work items.
If rework_items were in the continuation signal output, address them FIRST.

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
| verdict=CONTINUE | Execute sprint normally |
| verdict=STOP, reason=EXTERNAL_GATE/GIT_PUSH/GATE_11 | Stop, report to user |
| verdict=STOP, any other reason | Override, read next-sprint.md directly |
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
