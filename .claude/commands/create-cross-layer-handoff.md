---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /create-cross-layer-handoff

Register a new cross-layer handoff in `plans/layers/handoff-register.yaml` and
reference it in both the producer and consumer layer plan files.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `handoff_id` | Unique handoff ID (e.g., HO-008) |
| `producer_layer_id` | Layer that produces the artifact |
| `consumer_layer_id` | Layer that consumes the artifact |
| `artifact` | Path or description of the artifact |
| `task_id` | Task ID associated with this handoff |
| `acceptance_criteria` | List of criteria for handoff acceptance |

## Execution

1. Read `plans/layers/handoff-register.yaml` — confirm handoff_id is unique
2. Append new handoff block to handoff-register.yaml
3. Add handoff reference to producer layer plan §18 (Cross-Layer Dependencies)
4. Add handoff reference to consumer layer plan §18
5. Append change entries to `plans/layers/change-ledger.jsonl`

## Mandatory Validations

- `handoff_id_unique`: handoff_id must not exist in handoff-register.yaml
- `both_layers_exist`: producer and consumer layer plan files must exist on disk
- `register_updated`: handoff-register.yaml must contain new entry after execution

## Required Inputs

- `handoff_id` — value for `handoff_id`
- `producer_layer_id` — value for `producer_layer_id`
- `consumer_layer_id` — value for `consumer_layer_id`
- `artifact` — value for `artifact`
- `task_id` — task identifier from the layer task register
- `acceptance_criteria` — value for `acceptance_criteria`

## Allowed Paths

- `plans/layers/handoff-register.yaml`
- `plans/layers/`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no product source mutation
- `src/python/**` — no product source mutation
- `plans/strategic/**` — strategic plans are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here

## Stop Conditions

- Stop if the task register cannot be updated
- Stop if any required input field is missing or invalid

## Output Format

- Generated artifact written to the configured output path
- Confirmation message: file path and size
- Validation result confirming the output is well-formed
