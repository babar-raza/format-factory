# Continuation Routing Proof

## Before Repair

`continuation-signal.json` had:
- `autonomous_continue: true`
- `next_sprint_path: "reports/supervisor/next-sprint.md"` (advisory Markdown only)
- No `machine_continuation_path`, `active_continuation_path`, `next_action_path`, or `action_queue_path`

**Gap:** `autonomous_continue=true` but future automation would read only Markdown — advisory, not executable.

## Repair Applied

Called `evidence_continuation.repair_global_continuation_signal()` with:
- `sprint_id: FORMAT-FACTORY-H6-AUTONOMOUS-PRODUCT-QUEUE-CONSUMPTION-001`

Added to signal:
- `machine_continuation_path: .local/supervisor/next-action.json`
- `active_continuation_path: .local/supervisor/active-continuation.json`
- `next_action_path: .local/supervisor/next-action.json`
- `action_queue_path: .local/supervisor/action-queue.jsonl`
- `advisory_prompt_executable: false`
- `global_repair_applied: true`

## After Repair

`next_sprint_path` still exists (advisory, not removed) but is marked non-executable.
All machine-readable paths now present.
Future automation CAN read `next_action_path` directly without Markdown parsing.
