# R99 Parallel Execution Map

## Execution Order

```
Phase 1 (parallel): G1 (A,B) | G3 (E,F) — no code dependencies
Phase 2 (parallel): G2 (C,D) | G4 (G,H) — no code dependencies
Phase 3 (parallel): G5 (I,J) | G6 (K) — continuation depends on grading model
Phase 4 (sequential): L (Final IV) — must run after all others
Phase 5 (sequential): Evidence + autonomous-cycle — must be last
```

## Dependencies
- Train B (declaration-first model) changes autonomous_cycle.py → Trains C,D,E,F must be compatible
- Train J (continuation state machine) changes autonomous_cycle.py → Train I must be compatible
- Train K (stream-aware prompts) extends generate_next_worker_prompt.py → after Train F
- Train L (final IV) runs after all code changes
