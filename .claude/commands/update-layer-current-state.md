---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /update-layer-current-state

Update §9 (Current Implementation) of a permanent layer plan file with the latest
observed state from the codebase.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `layer_id` | Layer ID (e.g., L01) |
| `permanent_plan_path` | Path to the layer plan file |
| `current_state_summary` | Brief description of current implementation state |
| `key_metrics` | Dict of measurable current-state metrics |

## Execution

1. Read the layer plan file at `permanent_plan_path`
2. Locate `## 9. Current Implementation` section
3. Replace or append the current-state description with updated content
4. Append a change entry to `plans/layers/change-ledger.jsonl`

## Mandatory Validations

- `layer_plan_exists`: `permanent_plan_path` must exist
- `section_updated`: §9 must contain post-update content
- `change_logged`: change-ledger.jsonl must have new entry

## Required Inputs

- `layer_id` — layer identifier from the permanent layer plan
- `permanent_plan_path` — path to the permanent layer plan file
- `current_state_summary` — value for `current_state_summary`
- `key_metrics` — value for `key_metrics`

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

- Summary of items synced, added, removed, or unchanged
- Report file at `reports/` confirming final state
- Exit code 0 on success; non-zero with error message on failure
