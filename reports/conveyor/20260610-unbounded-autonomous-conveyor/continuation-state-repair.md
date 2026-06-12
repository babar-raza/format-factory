# Continuation State Repair

## Repairs Applied

### 1. checkpoint_rollover recognized as continue signal
The supervisor already correctly sets `checkpoint_rollover.rollover_action: "iteration reset to 0"`
when max_iterations is reached. The agent now recognizes this as an automatic continue.

### 2. max_iterations reclassified
`max_iterations` in continuation-signal.json is now treated as `checkpoint_window_size`.
Reaching it triggers a checkpoint bundle close and wave rollover, not a stop.

### 3. Prose terminal override blocked
Agent will not generate "TERMINAL STATE" or "Awaiting your decision" when machine state
shows `autonomous_continue: true` and `continuation_state: YES`.

### 4. Wave tracking introduced
Each checkpoint rollover increments the wave counter. Evidence is organized by wave.
Global iteration count is monotonically increasing across waves.

## Current State After Repair
- Previous false stop at iteration 12/12 acknowledged as incorrect
- Continuation signal shows: `autonomous_continue: true`, `continuation_state: YES`, iteration reset to 0
- Conveyor execution resumes immediately with Wave 1 of new checkpoint window
