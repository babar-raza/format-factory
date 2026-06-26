---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /select-next-layer-task

Read `plans/layers/index.yaml` and `plans/layers/task-register.yaml` to return
the next ready, dependency-valid layer task for execution. Used by the autonomous
supervisor for work selection from the layer control plane.

## Handoff Fields (optional)

| Field | Description |
|---|---|
| `priority_filter` | Filter to P0/P1/P2/P3 (default: all) |
| `layer_id_filter` | Filter to specific layer (default: all) |

## Execution

1. Read `plans/layers/task-register.yaml`
2. Filter to tasks with `status: TODO` or `status: IN_PROGRESS`
3. Resolve dependencies: exclude tasks whose dependencies are not CLOSED
4. Sort by priority (P0 first), then severity
5. Return the first eligible task with: task_id, title, primary_layer_id, next_action

## Output

```yaml
next_layer_task:
  task_id: TC-SAL-001
  title: "Activate 17 dormant SAL tools; run spec extraction for all 20 formats"
  primary_layer_id: L01
  permanent_plan_path: plans/layers/specification-authority-layer.md
  priority: P0
  next_action: "Run /sal-pipeline-heal skill; verify all 20 formats get facts"
  dependency_valid: true
  blocked_by: []
```

## Mandatory Validations

- This skill is read-only — no writes occur
- If no eligible task found, return `next_layer_task: null` with explanation
