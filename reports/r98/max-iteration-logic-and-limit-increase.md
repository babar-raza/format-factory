# Max-Iteration Logic Repair and Limit Increase

## Bug Fixed
`autonomous_cycle.py` now checks `existing_iteration >= max_iterations` before allowing continuation.
If at max, `hard_stops.append("max_iterations_reached")` and `auto_continue_value = False`.

## Continuation States Added
- `YES` — all items accepted, pure new-work sprint
- `YES_WITH_REWORK` — rework items but safe lanes continue
- `NO_MAX_ITERATIONS` — iteration limit reached
- `NO_EXTERNAL_GATE` — external gate blocks
- `NO_BROKEN_BASELINE` — hard stop from other causes
- `NO_UNSAFE_SOURCE_STATE` — overclaimed/rejected items

## Limit Change
- Old: `max_iterations: 5`
- New: `max_iterations: 12`
- File: `.supervisor/policies.yaml`

## Checkpoint Settings Added
```yaml
checkpoint_every: 3
max_dirty_files_before_checkpoint: 75
max_src_files_changed_before_checkpoint: 12
max_consecutive_accept_with_limitations: 2
max_consecutive_no_product_gap_closure: 2
```

## Checkpoint Behavior
When a checkpoint triggers, the generated next-sprint must include a checkpoint/review lane.
Safe product lanes can continue. Checkpoint does NOT stop the entire loop.
