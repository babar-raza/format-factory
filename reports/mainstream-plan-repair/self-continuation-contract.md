# Self-Continuation Contract

## Continuation Decision Rules

1. ONLY stop when one of these is TRUE:
   - All required POC criteria pass → MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED
   - True external blocker → MAINSTREAM_POC_BLOCKED_EXTERNAL_GATE
   - Unsafe workspace → MAINSTREAM_POC_UNSAFE_WORKSPACE
   - Runtime/context limit → MAINSTREAM_POC_PROGRESS_CONTINUATION_REQUIRED_BY_RUNTIME_LIMIT

2. NEVER stop for:
   - Supervisor ACCEPTED
   - Iteration complete
   - max_iterations reached (checkpoint rollover instead)
   - Evidence package created
   - Evidence quality issues
   - Prompt quality issues
   - One lane blocked (reroute instead)

3. After each iteration:
   - Write train-state.json
   - Write iteration report
   - Update proof graph
   - Update gap queue
   - Continue immediately to next iteration without user interaction
