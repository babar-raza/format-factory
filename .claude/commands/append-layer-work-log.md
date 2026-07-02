---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /append-layer-work-log

Append a new work log entry to §34 (Work Log) of a permanent layer plan file.
Called after completing work associated with a layer task.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `layer_id` | Layer ID (e.g., L01) |
| `permanent_plan_path` | Path to the layer plan file |
| `task_id` | Task ID the work belongs to |
| `sprint_id` | Sprint or session ID |
| `work_summary` | 1-3 sentence description of work done |
| `evidence_paths` | List of files changed or created |

## Execution

1. Read the layer plan file
2. Locate `## 34. Work Log` section
3. Append new work log entry with timestamp, task_id, and summary
4. Append change entry to `plans/layers/change-ledger.jsonl`

## Mandatory Validations

- `section_exists`: §34 must exist in the layer plan file
- `entry_appended`: new entry must appear in §34 after update

## Required Inputs

- `layer_id` — layer identifier from the permanent layer plan
- `permanent_plan_path` — path to the permanent layer plan file
- `task_id` — task identifier from the layer task register
- `sprint_id` — sprint identifier for this execution (e.g. `r120`)
- `work_summary` — value for `work_summary`
- `evidence_paths` — list of evidence file paths supporting this action

## Allowed Paths

- `plans/layers/`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no product source mutation
- `src/python/**` — no product source mutation
- `plans/strategic/**` — strategic plans are read-only
- `.supervisor/skill-registry.yaml` — skill registry is read-only here

## Stop Conditions

- Stop if the target section does not exist in the permanent plan
- Stop if the log entry cannot be appended to the plan

## Output Format

- Layer task register updated with the result of this operation
- Work log entry appended to the permanent layer plan
- Structured verdict: PASS / FAIL with supporting evidence
