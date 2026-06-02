---
sprint: R91
generated_by: r91-worker
---

# Continuation Signal Stop Logic Repair

## Summary

The continuation signal has been updated with a new mode and repaired stop conditions. The key addition is `autonomous_continue: true_with_rework` — a mode where rework items exist but safe product lanes can still proceed without a full stop.

## New Continuation Signal Modes

| Value | Meaning |
|---|---|
| `true` | All items accepted, continue with pure new-work sprint |
| `true_with_rework` | Rework exists but safe lanes continue; rework lanes included in next sprint |
| `false` | Hard stop — one or more non-parallelizable blockers |

## Stop Conditions

The following conditions force `autonomous_continue: false`:

| Condition | Trigger |
|---|---|
| `external_gate` | Item requires Gate 8, Gate 11, or other human-approval gate |
| `credentials` | Item requires new credentials or MCP activation |
| `git_push_or_publication` | Any work item requires git push, PyPI publish, NuGet publish |
| `destructive_action` | Work requires destructive git operation or irreversible system change |
| `test_baseline_failure_blocking_product_truth` | Core test runner broken, cannot verify product correctness |
| `no_progress_threshold_exceeded` | Same items failing for N consecutive sprints without reduction |
| `max_iterations` | iteration >= max_iterations in signal file |

## Inherited Failure Handling

Inherited evidence failures (failures carried forward from prior sprints that are already classified) do NOT stop continuation if:
1. The failing tests do not touch any file changed in the current sprint, AND
2. The failure is classified in `reports/supervisor/known-failures.yaml` with a `root_cause` and `repair_sprint` assignment, AND
3. The changed product lanes have non-overlapping test coverage

This prevents the system from halting progress on unrelated lanes due to pre-existing failures that are tracked and assigned.

## Policy File Update

`.supervisor/policies.yaml` updated with:

```yaml
autonomous_continuation:
  max_iterations: 5
  rework_continues_safe_lanes: true
  inherited_failure_isolation: true
  stop_conditions:
    - external_gate
    - credentials
    - git_push_or_publication
    - destructive_action
    - test_baseline_failure_blocking_product_truth
    - no_progress_threshold_exceeded
    - max_iterations
```

## Signal File Fields

`.local/supervisor/continuation-signal.json` updated fields:

```json
{
  "autonomous_continue": "true_with_rework",
  "iteration": 1,
  "max_iterations": 5,
  "stop_reason": null,
  "rework_items": ["item_id_1", "item_id_2"],
  "safe_lanes_available": true,
  "inherited_failures_classified": true,
  "generated_at": "ISO-8601"
}
```

## Effect on autonomous_cycle.py

After grading, `autonomous_cycle.py` Step 5 writes the continuation signal. If global_status is `PARTIAL_REWORK_SAFE_LANES_CONTINUE`, it writes `autonomous_continue: true_with_rework` and includes rework lanes in next-sprint.md. The CLAUDE.md loop condition accepts `true_with_rework` as a continuation-eligible value.
