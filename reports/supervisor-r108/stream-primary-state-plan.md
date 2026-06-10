# Stream-Primary State Isolation Plan

## Problem
`reports/supervisor/` files are last-run copies overwritten by any stream. When Mainstream R109/R110 ran after Supervisor R107, the global state became Mainstream-primary.

## Current Behavior
- `session-resume.md`: references MAINSTREAM-R110
- `evidence-review.md`: reviews Mainstream work
- `contradictions.md`: Mainstream contradictions
- `context-pack.yaml`: identifies Mainstream as current stream

## R108 Enforcement
1. Supervisor stream-primary state lives in `reports/supervisor-r108/`
2. `reports/supervisor/` is a last-run convenience copy, not authoritative
3. Package builder includes stream identity classification
4. Wrong-stream references in current state generate sample-wrong-stream-warning
5. Continuation signal includes `source_sprint_id` for stream identification

## Full Per-Stream Isolation (R109+)
- `reports/supervisor-{stream}/` as primary output per stream
- Autonomous-cycle writes to stream-scoped directory
- Package builder reads from stream directory (not shared)
- Shared `reports/supervisor/` becomes last-run copy only
