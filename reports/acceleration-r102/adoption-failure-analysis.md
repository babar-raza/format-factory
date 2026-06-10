# Adoption Failure Analysis

## Why tools are improved but not adopted

### Root Cause 1: No decision engine
Tools exist (gap selector, router, handoff generator) but no automated pipeline calls them
in sequence. Each tool must be manually invoked. There is no "next-best-action" that
examines current state and decides which tool to run.

### Root Cause 2: Generic next prompts
`generate_supervisor_packet.py` produces one `next-sprint.md` that mixes all streams.
Workers cannot distinguish mainstream product work from acceleration tooling from skill
registry expansion. Result: every sprint tries to do everything, nothing gets deep.

### Root Cause 3: No forecasting
Each sprint is planned in isolation. There is no 3-sprint lookahead per stream.
Without forecasting, sprints cannot specialize — they always restart from scratch.

### Root Cause 4: No enforcement
Anti-skip checks exist in concept (stale detection in R101) but nothing blocks a sprint
from proceeding with stale gaps, missing raw logs, or generic prompts.

## Fix Plan
1. **next_best_action.py** — examines matrix, ledger, lane history; returns ranked actions
2. **stream_forecaster.py** — produces 3-sprint plan per stream
3. **anti_skip_checker.py** — detects generic prompts, stale gaps, missing logs, path-only acceptance
4. **stream_prompt_generator.py** — produces per-stream next prompt with forecasts and anti-skip
