---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /register-layer-gap

Add a new gap entry to §14 (Gap Register) of a permanent layer plan file.
Gaps represent the delta between current state and target design.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `layer_id` | Layer ID (e.g., L01) |
| `permanent_plan_path` | Path to the layer plan file |
| `gap_id` | Gap identifier (e.g., SAL-GAP-002) |
| `severity` | CRITICAL / HIGH / MEDIUM / LOW |
| `current_state` | What exists today |
| `target_state` | What should exist |
| `task_id` | Task ID that will resolve the gap (or null) |

## Execution

1. Read the layer plan file
2. Locate `## 14. Gap Register` section
3. Append new row to the gap table
4. Append change entry to `plans/layers/change-ledger.jsonl`

## Mandatory Validations

- `gap_id_unique`: gap_id must not already exist in the gap table
- `change_logged`: change-ledger.jsonl must have new entry

## Required Inputs

- `layer_id` — layer identifier from the permanent layer plan
- `permanent_plan_path` — path to the permanent layer plan file
- `gap_id` — value for `gap_id`
- `severity` — value for `severity`
- `current_state` — JSON or YAML snapshot of the current layer state
- `target_state` — value for `target_state`
- `task_id` — task identifier from the layer task register

## Allowed Paths

- `plans/layers/`
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
