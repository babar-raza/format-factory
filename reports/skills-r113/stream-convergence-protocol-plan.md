# Stream-Convergence Protocol Plan

## Problem
Multiple streams (skills, mainstream, acceleration, supervisor) write to shared state:
- `reports/supervisor/` — last-writer-wins, any stream overwrites
- `.local/supervisor/continuation-signal.json` — global, overwritten each cycle
- `.supervisor/context-pack.yaml` — single file, rebuilt each cycle

Stream-local outputs at `reports/supervisor-streams/{stream}/` are authoritative per-stream but not yet converged.

## Protocol
1. **Authority model**: Each stream's canonical state is in `reports/supervisor-streams/{stream}/`
2. **Global state**: `reports/supervisor/` is an advisory snapshot — the most recent stream's output
3. **Convergence map**: Machine-readable JSON defining which stream owns which file
4. **Conflict resolution**: When two streams disagree, the stream-local copy wins for that stream's decisions
5. **Merge policy**: Global state is informational only — no stream should read global as authoritative

## Deliverable
- `reports/skills-r113/stream-convergence-map.json` — machine-readable convergence protocol
