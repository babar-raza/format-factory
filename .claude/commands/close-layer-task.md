---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /close-layer-task

Close a layer task: move it from §29 (Active Taskcards) to §31 (Completed Tasks)
in the layer plan file, and update `status: CLOSED` in `task-register.yaml`.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `layer_id` | Layer ID (e.g., L01) |
| `permanent_plan_path` | Path to the layer plan file |
| `task_id` | Task ID to close |
| `closure_verdict` | COMPLETED / PARTIALLY_COMPLETED / SUPERSEDED |
| `evidence_paths` | List of evidence files supporting closure |

## Pre-conditions (Gate Check)

Before closing, verify §36 (Session Handoff) has been written for this session.
If §36 is missing or stale (no entry for this session), write it first.

## Execution

1. Read the layer plan file
2. Move task entry from §29 to §31 with closed_at timestamp and verdict
3. Update task entry in `plans/layers/task-register.yaml`: set `status: CLOSED`, `closed_at`
4. Append verification log entry to §35
5. Append change entry to `plans/layers/change-ledger.jsonl`

## Mandatory Validations

- `task_was_active`: task_id must be in §29 before closure
- `evidence_provided`: at least one evidence_path must be supplied
- `register_updated`: task-register.yaml must show status=CLOSED after update
