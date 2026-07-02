---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /update-layer-master-index

Sync a layer's status, maturity, and next_task_id from its permanent plan file
to `plans/layers/index.yaml` and the summary table in `plans/layers/master.md`.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `layer_id` | Layer ID (e.g., L01) |
| `permanent_plan_path` | Path to the layer plan file |

## Execution

1. Read the layer plan file — extract `status`, `maturity_current`, `next_task_id`, `health`
2. Read `plans/layers/index.yaml` — find the entry with matching `layer_id`
3. Update the entry's status, maturity_current, next_task_id, and health fields
4. Write updated index.yaml
5. Append change entry to `plans/layers/change-ledger.jsonl`

## Mandatory Validations

- `index_has_layer`: layer_id must exist in index.yaml
- `status_consistent`: index.yaml status must match layer plan after update
- `change_logged`: change-ledger.jsonl must have new entry

## Required Inputs

- `layer_id` — layer identifier from the permanent layer plan
- `permanent_plan_path` — path to the permanent layer plan file

## Allowed Paths

- `plans/layers/index.yaml`
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

- Summary of items synced, added, removed, or unchanged
- Report file at `reports/` confirming final state
- Exit code 0 on success; non-zero with error message on failure
