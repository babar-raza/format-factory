# False Terminal Root Cause Analysis

## Incident
Sprint REWORK-MEGATRAIN-FINAL-001 (iteration 12/12) ended with agent producing prose:
"Autonomous Mega-Train Complete — TERMINAL STATE" and "Awaiting your decision on next steps"

## Machine State at Time of False Stop
- `autonomous_continue: true`
- `continuation_state: YES`
- `safe_lanes_available: true`
- `hard_stops_detected: []`
- `stop_reason: null`
- `checkpoint_rollover: CHECKPOINT_ROLLOVER_CONTINUE`
- `iteration: 0` (reset from 12)
- `rollover_rule: Rule 6`
- Next work items available and executable

## Root Causes

### RC-1: Agent treated `max_iterations` as terminal stop
CLAUDE.md said "Default: 5 sprints per autonomous loop. After max iterations, STOP and present summary."
The agent correctly followed this instruction — but the instruction was wrong.
`max_iterations` is a checkpoint window, not a terminal stop.

### RC-2: Agent prose overrode machine-readable continuation state
The continuation signal file said `autonomous_continue: true` and `continuation_state: YES`.
The agent ignored this and wrote "TERMINAL STATE" based on its own iteration counting.
Machine state must always win over agent prose.

### RC-3: No checkpoint rollover handling in CLAUDE.md
CLAUDE.md had no instruction for what to do when `checkpoint_rollover` is present.
The supervisor correctly reset iteration to 0 and wrote `CHECKPOINT_ROLLOVER_CONTINUE`.
The agent had no instruction to recognize this as a continue signal.

## Corrective Actions
1. `max_iterations` reclassified as `checkpoint_window_size`
2. Checkpoint rollover creates new wave automatically
3. Agent prose cannot override machine continuation state
4. Stop only for true external gates with no safe lanes remaining
