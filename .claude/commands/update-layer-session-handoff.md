---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /update-layer-session-handoff

Write or update §36 (Current Session Handoff) of a permanent layer plan file.
Called at session end to ensure the next assistant can resume without prior context.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `layer_id` | Layer ID (e.g., L01) |
| `permanent_plan_path` | Path to the layer plan file |
| `session_id` | Current session identifier |
| `current_status` | Layer status at session end |
| `exact_next_task` | Next task_id to execute |
| `important_decisions` | List of key decisions made in this session |
| `resume_instructions` | Step-by-step instructions for next assistant |

## Execution

1. Read the layer plan file
2. Locate or create `## 36. Current Session Handoff` section
3. Replace the YAML block with updated handoff content
4. Update `last_updated_at` in the layer metadata header
5. Append change entry to `plans/layers/change-ledger.jsonl`

## Mandatory Validations

- `section_written`: §36 must contain a `layer_session_handoff` YAML block
- `exact_next_task_valid`: exact_next_task must be a registered task_id or null
- `change_logged`: change-ledger.jsonl must have new entry
