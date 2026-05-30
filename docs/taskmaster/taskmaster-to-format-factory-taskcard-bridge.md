# Task Master to Format Factory Taskcard Bridge

## Purpose

Every Task Master task must be anchored to a Format Factory artifact.
The bridge fields prevent TM from drifting into self-referential state.

## Required Bridge Fields

Each task in `next-sprint-taskmaster.json` must have at least one of:

| Field | Points to | Example |
|-------|-----------|---------|
| `ff_taskcard_ref` | A taskcard in `taskcards/` | `"TC-0057"` |
| `ff_gate_ref` | A gate in the gate pipeline | `"G8-FODS"` |
| `ff_doc_ref` | A doc or spec in `docs/` | `"docs/ai/ai-platform-operating-model.md"` |

## Bridge Validation Rules

`tools/taskmaster/validate_taskmaster_bridge.py` enforces:

1. **Missing bridge ref** — task has none of ff_taskcard_ref, ff_gate_ref, ff_doc_ref → FAIL
2. **Missing acceptance_evidence** — empty or absent → FAIL
3. **Missing validation_command** — empty or absent → FAIL
4. **Blocked without blocker_type** — status=blocked or evidence_blocked without blocker_type → FAIL
5. **Done without non_authoritative** — status=done and non_authoritative=False → FAIL
6. **Invalid status** — status not in allowed set → FAIL

Allowed statuses: `pending`, `in_progress`, `done`, `blocked`, `evidence_blocked`, `deferred`

## No-Drift Contract

`tools/taskmaster/validate_dual_orchestration_bridge.py` enforces the dual-orchestration contract:

### RULE-1: TM done does NOT mean FF gate closed
A TM task with `status: done` must NOT contain gate closure keywords in any field:
- `gate_closed`, `gate_N_approved`, `commercial_product_ready`
- A task done + non_authoritative=False also violates RULE-1

### RULE-2: Ruflo complete does NOT mean evidence accepted
A Ruflo lane with `status: completed` must have `non_authoritative: true`

### RULE-3: All Ruflo lanes must have non_authoritative: true
Every lane in next-ruflo-lanes.json must have `non_authoritative: true` (not false, not absent)

### RULE-4: Ruflo state cannot claim gate closure
Ruflo lane fields (title, owner_role, etc.) must NOT contain gate closure keywords

### RULE-5: Supervisor verdict cannot claim gate approval
Supervisor verdict file must NOT contain `GATE_APPROVED`, `COMMERCIAL_READY`,
`PRODUCT_READY`, or `RELEASE_AUTHORIZED` in the verdict value

## TM State Machine vs FF Gate State

| TM Task Status | FF Gate Status | Relationship |
|---------------|----------------|-------------|
| pending | not_started | Aligned — work not begun |
| in_progress | in_progress | Aligned — work underway |
| done | pending/in_progress | **NOT aligned** — TM done ≠ gate closed |
| done | g*_approved | Aligned — human approved the gate (TM reflects post-fact) |
| evidence_blocked | blocked | Aligned — evidence gate failed |
| blocked | blocked | Aligned — external dependency |

TM task "done" means: Claude Code completed the work and evidence was generated.
FF gate "approved" means: Human reviewed and approved the gate artifact.
These are separate events. TM state updates first; FF gate approval is always human.

## Example: Correct Task with Bridge Ref

```json
{
  "task_id": "TASK-001",
  "title": "Implement FODS sheet management API",
  "status": "done",
  "ff_taskcard_ref": "TC-0060",
  "acceptance_evidence": "pytest tests/python/fods/test_r77_fods_sheet_mgmt.py -v: 21 passed",
  "validation_command": "pytest tests/python/fods/test_r77_fods_sheet_mgmt.py -v",
  "non_authoritative": true
}
```

## Example: Incorrect Task (violates RULE-1)

```json
{
  "task_id": "TASK-002",
  "title": "gate_closed — FODS Gate 10 approved",
  "status": "done",
  "ff_gate_ref": "G10-FODS",
  "non_authoritative": false
}
```

This fails: gate_closed keyword + non_authoritative=False both violate RULE-1.
