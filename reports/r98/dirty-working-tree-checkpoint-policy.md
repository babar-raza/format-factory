# Dirty Working Tree Checkpoint Policy

## Classification States
- `CLEAN` — no uncommitted changes
- `DIRTY_EXPECTED_AUTONOMOUS_RUN` — changes accumulated during autonomous loop (normal)
- `DIRTY_NEEDS_CHECKPOINT` — exceeded dirty file threshold
- `DIRTY_UNSAFE` — destructive state (merge conflicts, detached HEAD, etc.)

## Policy
1. Autonomous runs accumulate uncommitted changes. This is expected.
2. Git commit remains approval-blocked unless user explicitly authorizes.
3. Supervisor may continue safe lanes with `DIRTY_EXPECTED_AUTONOMOUS_RUN`.
4. When `max_dirty_files_before_checkpoint` (75) or `max_src_files_changed_before_checkpoint` (12) is exceeded, checkpoint is required.
5. Checkpoint includes source diffs and ledger deltas packaged in review material.
6. Dirty-tree status is recorded in context-pack and continuation-signal.

## Current State
- R98 start: 59 changed files (30 modified + 28 untracked + 1 staged)
- Classification: DIRTY_EXPECTED_AUTONOMOUS_RUN
