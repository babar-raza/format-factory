# Cross-Stream Contamination Root Cause

## Problem
After a supervisor stream autonomous-cycle, state files in reports/supervisor/ may reference
a different stream's sprint because autonomous-cycle runs for ALL streams in sequence.
The last stream to run overwrites shared state.

## Root Cause Chain

### RC-1: Shared state directory
All streams write to the same `reports/supervisor/` directory. When acceleration-r103 runs
after supervisor-r102, it overwrites:
- evidence-review.md/json
- contradictions.md/json
- context-pack.yaml/md
- session-resume.md
- next-sprint.md
- latest-cycle-summary.md

### RC-2: Context pack latest_sprint
`build_context_pack.py` reads the last autonomous-cycle output to set `latest_sprint`.
If acceleration-r103 ran last, context-pack points to acceleration, not supervisor.

### RC-3: Package builder reads shared state
`build_declaration_review_package.py` packages `reports/supervisor/*.md` — these are the
latest stream's outputs, not necessarily the reviewed stream's outputs.

### RC-4: No stream-scoped state isolation
There's no per-stream state directory. All streams share `reports/supervisor/`.

## Fix Plan

### Fix 1: Per-stream state snapshots at cycle time
autonomous_cycle.py should save a per-stream snapshot of evidence-review, contradictions,
context-pack, and next-sprint in the review directory before any other stream overwrites them.

### Fix 2: Package builder uses per-stream snapshots
build_declaration_review_package.py should read from the review directory's snapshots
instead of the shared reports/supervisor/ directory.

### Fix 3: Context pack stream field
context-pack.yaml should record which stream it was built for. downstream tools should
validate that the context-pack stream matches the current operation.
