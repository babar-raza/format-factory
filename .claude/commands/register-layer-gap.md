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
