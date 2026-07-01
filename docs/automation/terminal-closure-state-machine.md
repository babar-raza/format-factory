# Terminal Closure State Machine

**Document:** TC-TCF-010 / TC-TCF-002 supplementary
**Created:** 2026-06-26

---

## Plan Lock Status Transitions

```
                  write_plan_lock --completion-candidate
                  ↓
IN_PROGRESS ──────────────────────────→ COMPLETION_CANDIDATE
    │                                          │
    │  write_plan_lock --terminal              │  lifecycle_audit passes (all TCs closed)
    │  + _should_require_audit() = False       │  + no GUARD_FAIL findings
    ↓                                          ↓
TERMINAL_CLOSED ←─────────────────────────────┘
    │
    │  reopen_plan_lock.py (any VALID_TRIGGER)
    ↓
SUPERSEDED (original lock) + new IN_PROGRESS lock
    │
    │  successor_path provided
    ↓
SUPERSEDED_BY_SUCCESSOR (original) + new IN_PROGRESS (successor plan)
```

---

## Scope Hierarchy

| Scope | Unit | Completion Criterion |
|-------|------|---------------------|
| Task | TC-* entry in plan file | Status = CLOSED |
| Sprint | One autonomous execution cycle | evidence-declaration.yaml accepted |
| Plan | Active work unit (plan lock) | All mandatory TC-* entries CLOSED + audit passes |
| Mission | Full project goal | All plans in scope reach TERMINAL_CLOSED |

---

## COMPLETION_CANDIDATE State (TC-TCF-002)

- Written by: `write_plan_lock.py --completion-candidate`
- Meaning: All current taskcards appear closed; awaiting lifecycle audit before TERMINAL_CLOSED
- `check_continuation.py` behavior: returns CONTINUE (non-blocking)
- Transitions to: TERMINAL_CLOSED (audit pass) or ITERATION_REQUIRED (audit fail)

---

## Mandatory Audit Gate (TC-TCF-003)

`write_plan_lock.py --terminal` triggers `lifecycle_audit.run_lifecycle_audit()` automatically
when `_should_require_audit(plan_path)` returns True (plan contains TC-* taskcard entries).

Override: `--skip-audit` flag (emergency bypass only; evidence validator V-TCF-002 will warn).

### Four Premature-Closure Guards

| Guard | ID | Blocks? |
|-------|----|---------|
| Queue exhaustion | G1 | CRITICAL → AUDIT_REQUIRES_ITERATION |
| Closeout task | G2 | CRITICAL → AUDIT_REQUIRES_ITERATION |
| Iteration limit | G3 | MEDIUM → GUARD_WARN only |
| Sprint audit gap | G4 | MEDIUM → GUARD_WARN only |

---

## Reopening Policy (TC-TCF-006)

Use `reopen_plan_lock.py` to reopen a TERMINAL_CLOSED plan.

### Same-Plan Reopen

```bash
python tools/supervisor/reopen_plan_lock.py \
  --plan-path <plan.md> \
  --reason "Missed TC-XXX found post-closure" \
  --trigger MISSED_REQUIREMENT
```

Use when: missed work belongs to the original mission scope (classify_work_scope → IN_SCOPE).

### Successor Plan

```bash
python tools/supervisor/reopen_plan_lock.py \
  --plan-path <old-plan.md> \
  --successor <new-plan.md> \
  --reason "New capability outside original scope" \
  --trigger OUT_OF_SCOPE_WORK
```

Use when: new work is genuinely outside original mission scope (classify_work_scope → OUT_OF_SCOPE).

### Scope Classification

`classify_work_scope(new_work_description, original_plan_path, trigger)` returns:

- **IN_SCOPE**: trigger in {MISSED_REQUIREMENT, REGRESSION, AUDIT_FINDING, ...} OR TC-ID from
  new_work_description appears in original plan file
- **OUT_OF_SCOPE**: trigger is OUT_OF_SCOPE_WORK, OR no TC-ID overlap and trigger is OTHER/WRONG_MISSION

---

## Closure Evidence Artifact (TC-TCF-004)

Written automatically when TERMINAL_CLOSED is set:

```
.local/evidences/plan-closures/{plan_hash}/terminal_closure_record.json
```

Fields: `plan_path`, `plan_hash`, `status`, `locked_at`, `locked_by_session`,
`audit_verdict`, `all_taskcards_closed`, `open_taskcards`, `guard_results`.

V-TCF-002 warns when terminal closure is claimed but no record exists.

---

## Autonomous Reopening (TC-TCF-005)

`autonomous_cycle.py` Step 0b-reopen-check detects TERMINAL_CLOSED plans with open taskcards
and automatically calls `reopen_plan()`. After reopening, `find_next_eligible_task_in_plan()`
identifies the first open TC to prevent fall-through to product deepening.

Functions in `autonomous_cycle_extensions/__init__.py`:
- `find_next_eligible_task_in_plan(plan_path)` → first open TC dict or None
- `scan_closed_plan_test_regression(repo_root)` → regressions in evidence-review.json
- `scan_closure_evidence_invalidation(repo_root)` → closures with missing plan files
