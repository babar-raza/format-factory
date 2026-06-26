---
version: "1.0"
last-updated: "2026-06-26"
phase-available: "all"
gate-required: null
created-by: TC-LP-023
spec_qname_required: "false"
product_track: "layer_governance"
---

# /reconcile-layer-task-register

Verify that `plans/layers/task-register.yaml` is consistent with the §29 (Active
Taskcards) sections in all permanent layer plan files. Reports discrepancies.

## Execution

1. Read `plans/layers/task-register.yaml` — load all task entries
2. For each task, read the task's `permanent_layer_plan` file
3. Check that the task_id appears in §29 (Active Taskcards) or §31 (Completed Tasks)
4. For each layer plan §29, check that all task_ids appear in task-register.yaml
5. Report: tasks in register but not in plan file; tasks in plan file but not in register

## Output

```yaml
reconcile_result:
  total_tasks: 10
  consistent: 9
  in_register_not_in_plan:
    - task_id: TC-OLD-001
      register_primary_layer: L01
      plan_file: plans/layers/specification-authority-layer.md
  in_plan_not_in_register:
    - task_id: TC-QN-002
      plan_file: plans/layers/qname-hierarchy-layer.md
  verdict: WARN
```

## Mandatory Validations

- This skill is read-only — no writes occur
- Discrepancies emit WARN; register must be updated via /register-layer-task
