---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /register-layer-task

Register a new task in §29 (Active Taskcards) of a permanent layer plan file
AND add a corresponding entry to `plans/layers/task-register.yaml`.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `layer_id` | Primary layer ID (e.g., L01) |
| `permanent_plan_path` | Path to the layer plan file |
| `task_id` | Task identifier (e.g., TC-SAL-002) |
| `title` | Short task title |
| `task_type` | Task type (SYSTEM_HEALING / DATA_EXPANSION / MAINTENANCE / etc.) |
| `severity` | CRITICAL / HIGH / MEDIUM / LOW |
| `priority` | P0 / P1 / P2 / P3 |
| `next_action` | First concrete action to take |

## Execution

1. Read the layer plan file
2. Add task entry to §29 Active Taskcards table
3. Append YAML block to `plans/layers/task-register.yaml`
4. Append change entry to `plans/layers/change-ledger.jsonl`

## Mandatory Validations

- `task_id_unique`: task_id must not already exist in task-register.yaml
- `layer_plan_has_task`: §29 must contain the new task_id after update
- `change_logged`: change-ledger.jsonl must have new entry

## Required Inputs

- `layer_id` — layer identifier from the permanent layer plan
- `permanent_plan_path` — path to the permanent layer plan file
- `task_id` — task identifier from the layer task register
- `title` — value for `title`
- `task_type` — value for `task_type`
- `severity` — value for `severity`
- `priority` — value for `priority`
- `next_action` — value for `next_action`

## Allowed Paths

- `plans/layers/`
- `plans/layers/task-register.yaml`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no product source mutation
- `src/python/**` — no product source mutation
- `plans/strategic/**` — strategic plans are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here

## Stop Conditions

- Stop if the skill's mandatory validations cannot be completed
- Stop if any required input field is missing or invalid

## Output Format

- Layer task register updated with the result of this operation
- Work log entry appended to the permanent layer plan
- Structured verdict: PASS / FAIL with supporting evidence
