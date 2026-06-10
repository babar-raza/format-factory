# Train I: Max Iterations and Checkpointing

## Current Policy (already in policies.yaml since R98)
```yaml
autonomous_continuation:
  max_iterations: 12
  checkpoint_every: 3
  max_dirty_files_before_checkpoint: 75
  max_src_files_changed_before_checkpoint: 12
  max_consecutive_accept_with_limitations: 2
  max_consecutive_no_product_gap_closure: 2
```

## Implementation Status
| Setting | Implemented? | Where |
|---------|-------------|-------|
| max_iterations: 12 | YES | autonomous_cycle.py (R98 fix) |
| checkpoint_every: 3 | DOCUMENTED | policies.yaml — requires human commit at checkpoint |
| max_dirty_files_before_checkpoint: 75 | DOCUMENTED | policies.yaml — not enforced in code |
| max_src_files_changed_before_checkpoint: 12 | DOCUMENTED | policies.yaml — not enforced in code |
| max_consecutive_accept_with_limitations: 2 | DOCUMENTED | policies.yaml — not enforced in code |
| max_consecutive_no_product_gap_closure: 2 | DOCUMENTED | policies.yaml — not enforced in code |

## R99 Contribution
- No code changes needed (R98 already fixed the max_iterations enforcement)
- Checkpoint enforcement (dirty files count, src files changed) requires git status inspection at the start of each iteration — deferred to autonomous_continuation module
- The continuation state machine (Train J) classifies the reason when iteration limit is hit

## Checkpoint Behavior
Checkpoint does NOT block all safe lanes:
- Git commit (human authorized) is the checkpoint action
- Autonomous work continues in the same iteration until the commit happens
- Hard stop only when max_iterations is reached without a checkpoint
