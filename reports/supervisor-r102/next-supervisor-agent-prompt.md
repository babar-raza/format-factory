# Next Supervisor Agent Prompt

## Context
R102 fixed legacy review overwrite, stream prompt quality, and continuation policy.
The declaration-review model is now the primary evidence model; legacy R90 contract
is bypassed for declaration-review packages.

## Remaining Gaps
1. Bridge output protection (timestamp/source check) — documented in Fix 4 of root cause
2. Stream-aware contradiction detection — compare_goal_to_evidence.py still uses flat contradictions
3. Replay packages with intentionally mixed grades — current real packages are all-accepted

## Next Sprint Directive
Focus: Evidence model hardening + bridge protection + mixed-grade replay
Stream: supervisor
Priority: Fix 4 (bridge overwrite protection) > stream-aware contradictions > replay depth
