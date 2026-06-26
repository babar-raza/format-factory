---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /detect-unlogged-work

Find git changes (since a given commit or HEAD~N) that are NOT referenced in any
permanent layer plan's §34 (Work Log). Identifies work done outside the governed
layer control plane.

## Handoff Fields (optional)

| Field | Description |
|---|---|
| `since_commit` | Commit SHA to diff from (default: HEAD~10) |
| `layer_ids` | Optional filter to specific layers |

## Execution

1. Run `git diff --name-only <since_commit>..HEAD` to get changed files
2. For each changed file, determine its primary layer via path prefix
3. Read the corresponding layer plan's §34 Work Log
4. Report files whose changes are NOT referenced in any work log entry

## Output

```yaml
unlogged_work:
  - file: tools/supervisor/autonomous_cycle.py
    primary_layer: L11
    layer_plan: plans/layers/supervisor-sprint-layer.md
    last_git_change: "2026-06-26 (commit a7744cf6)"
    work_log_mentions: 0
    action: APPEND_WORK_LOG
```

## Mandatory Validations

- This skill is read-only — no writes occur
- Output is advisory only; unlogged work emits WARN, not FAIL
