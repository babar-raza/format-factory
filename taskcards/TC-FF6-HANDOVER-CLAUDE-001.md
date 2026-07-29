---
artifact_id: TC-FF6-HANDOVER-CLAUDE-001
artifact_type: taskcard
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
goal_id: FF6-PRODUCTION-LIBRARIES-001
status: IN_PROGRESS
skill_ids:
  - execution-handoff
  - create-taskcard
  - plan-control
---

# Publish a Provider-Neutral Claude/Codex Shift Handover

## Objective

Create a single-entry, evidence-backed, machine-readable handover that lets
Claude and Codex resume the FF6 mission from GitLab main without conversation
memory, provider-local state, lost work, duplicate execution, or false product
promotion.

## Allowed paths

- `plans/codex/handover/**`
- `plans/strategic/ff6/controller-state.yaml`
- `plans/strategic/ff6/events.jsonl`
- `taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md`
- this taskcard
- `taskcards/index.yaml`
- local task transcript and evidence metadata

## Acceptance

- One start file links every handover artifact and canonical authority.
- Exact commit, tree, controller event, next task, and evidence limits are
  recorded.
- Symptoms, root causes, structural weaknesses, preservation requirements,
  redesign direction, risks, and uncertainty are separated.
- Start, execution, checkpoint, takeover, validation, integration, and release
  procedures are provider-neutral and executable.
- The absent next taskcard is materialized as `READY`.
- Known global plan-control and line-ending digest contradictions are explicit.
- All internal links, YAML, normalized hashes, event chain, task index, and
  focused regression checks pass.
- Files are committed and pushed to GitLab main with remote verification.
- No product implementation or promotion occurs.
