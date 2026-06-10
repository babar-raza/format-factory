# Root Cause: Why Supervisor Generates Generic Prompts

## Problem Statement
After every sprint (regardless of stream), the supervisor generates the same generic
next-sprint.md with "Continue normal mega-train lanes" and product-oriented tasks.
A supervisor stream sprint gets a product prompt. An acceleration sprint gets a product prompt.

## Root Cause Chain

### RC-1: `generate_supervisor_packet.py::synthesize_sprint_tasks()` is stream-blind
- Lines 246-497: Always generates product gaps, gate tasks, dogfood, package lanes
- No `stream` parameter accepted
- No awareness of which stream produced the current evidence

### RC-2: `autonomous_cycle.py` Step 7b calls `generate_packet()` without stream context
- Line 277: `generate_packet(repo_root)` — no stream argument
- The evidence-review.json bridge (Step 7) loses the sprint_id stream prefix
- `generate_supervisor_packet.py::generate_packet()` has no stream parameter

### RC-3: `generate_next_worker_prompt.py` has STREAM_GROUPS but it's unused in the legacy path
- Lines 436-441: STREAM_GROUPS defines 4 streams with group filtering
- Line 160: `generate_prompt(review, repo_root=repo_root)` — Step 4 in autonomous_cycle
- But Step 7b's legacy markdown path (`generate_supervisor_packet.py`) is what writes
  the actual `reports/supervisor/next-sprint.md` that workers consume
- Step 4's output goes to `.local/supervisor/reviews/<run_id>/combined-next-worker-prompt.md`
  which nobody reads

### RC-4: `generate_next_sprint_md()` has hardcoded product focus
- Line ~500: `"ADVANCE: Continue normal mega-train lanes"` is the default focus
- No conditional logic for stream-specific focus strings
- Sprint tasks always come from `synthesize_sprint_tasks()` which is product-only

### RC-5: No stream detection from declaration or sprint_id
- The sprint_id contains the stream name (e.g., "SUPERVISOR-R100", "ACCELERATION-R101")
- But no code extracts the stream prefix from sprint_id
- The evidence-declaration.yaml has no explicit `stream` field

## Fix Plan

### Fix 1: Add stream detection from sprint_id
Extract stream from sprint_id pattern: `FORMAT-FACTORY-{STREAM}-R{N}-...`

### Fix 2: Add stream parameter to `generate_packet()` and `synthesize_sprint_tasks()`
When stream != "product"/"mainstream", skip product gap/gate/dogfood/package tasks.
Generate stream-appropriate tasks instead.

### Fix 3: Add stream-specific focus strings
- mainstream: "ADVANCE: Product deepening — .NET commercial + Python FOSS"
- acceleration: "ADVANCE: Acceleration tooling — gap selector, skill engine, handoff generator"
- skills: "ADVANCE: Governed execution — skill commands, validation, transcript ledger"
- supervisor: "ADVANCE: Supervisor infrastructure — grading, continuation, prompts, evidence"

### Fix 4: Add stream-specific task synthesizers
Each stream needs its own task list, not just filtered product tasks.

### Fix 5: Wire stream through autonomous_cycle.py Step 7b
Pass detected stream to `generate_packet(repo_root, stream=...)`.
