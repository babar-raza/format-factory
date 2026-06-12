# Checkpoint Rollover Policy

## Terminology
- **wave_id**: Monotonically increasing autonomous wave number
- **checkpoint_window_size**: Number of sprints per checkpoint (default 12)
- **checkpoint_index**: Current sprint within the window
- **global_iteration**: Never reset; monotonically increasing across all waves
- **stop_reason**: Only true stops (null = continue)

## Rollover Rules

### Rule 1: Checkpoint windows are not terminal stops
When `checkpoint_index >= checkpoint_window_size`:
- Close current checkpoint evidence bundle
- Create next wave
- Reset checkpoint_index to 0
- Carry forward all unfinished taskcards
- Continue automatically

### Rule 2: Machine state wins over prose
If continuation-signal.json says `autonomous_continue: true` and `continuation_state: YES`,
no agent prose may override this to stop. "Terminal state" prose is invalid when machine
state says continue.

### Rule 3: Safe lanes override human gates
If true human gates exist (commit, push, Gate 11 approval, publication) but other safe
lanes remain, park the human gates and continue safe lanes.

### Rule 4: True stop conditions (exhaustive list)
- STOP_ALL_LANES_COMPLETE: No safe taskcards or next-work-items remain
- STOP_ONLY_TRUE_EXTERNAL_GATES_REMAIN: Only human approval items left
- STOP_UNSAFE_WORKSPACE: Repository corruption or irreversible risk
- STOP_CREDENTIAL_REQUIRED_AND_NO_SAFE_LANES

Any other stop reason is invalid.
