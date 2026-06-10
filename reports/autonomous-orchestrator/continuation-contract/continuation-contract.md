# Machine-State Continuation Contract
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001

## State Files

| File | Purpose |
|------|---------|
| .local/supervisor/active-continuation.json | Authoritative next-action routing |
| .local/supervisor/next-action.json | Current next-action to execute |
| .local/supervisor/orchestrator-state.json | Orchestrator run state (resumable) |
| .local/supervisor/orchestrator-heartbeat.json | Liveness marker |
| .local/supervisor/stop-reason.json | Why orchestrator stopped (resumable?) |

## Priority Rules

1. active-continuation.json is authoritative for routing (not next-sprint.md)
2. reports/supervisor/next-sprint.md is ADVISORY ONLY — never executable
3. review/next-work-items.json is advisory unless converted to validated next-action.json
4. autonomous_continue=true is invalid unless next_action_path exists and validates
5. Product prompts cannot override autonomy stream

## Replacement

This machine-state contract replaces advisory Markdown continuation.
The old flow: autonomous-cycle → continuation-signal.json → next-sprint.md → human paste
The new flow: autonomous-cycle → active-continuation.json → next-action.json → orchestrator runs
