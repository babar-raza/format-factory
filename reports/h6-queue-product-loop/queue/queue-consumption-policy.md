# Queue Consumption Policy

## Change: Queue-First Orchestrator Mode

Added `--queue-first` flag to `tools/supervisor/autonomous_orchestrator.py`.

When `--queue-first` is set:
1. Before generating a synthetic next action, call `action_queue.dequeue_next()`
2. If a pending item is found (not external_gate, priority-sorted):
   - Convert queue item → next-action.json format via `_queue_item_to_next_action()`
   - Save to `.local/supervisor/next-action.json`
   - Execute via `next_action_runner.py`
   - After execution: mark done (if SUCCESS) or failed (if error)
3. If queue is empty or all items blocked → fall back to `next_action_generator.py`

## Queue Item Priority

Items are sorted by `(priority, queued_at)` — lower priority number = selected first.
The product-safe item was assigned priority=0 to ensure it runs first.

## Queue Status Transitions

```
pending → running  (dequeue_next() called)
running → done     (mark_done() called after SUCCESS)
running → failed   (mark_failed() called after non-SUCCESS)
```

## Safety Enforcement

- `product_action_guard.py` has `PRODUCT_GAP_CLASSIFICATION_READONLY` in `SAFE_PRODUCT_PILOT_ACTIONS`
- `local_deterministic_backend.py` implements the action type
- Write root merging ensures queue item's `allowed_write_roots` are respected
- No src/ writes enforced by `FORBIDDEN_WRITE_PATHS`
