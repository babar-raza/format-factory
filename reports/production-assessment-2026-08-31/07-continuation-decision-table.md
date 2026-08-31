# 07 — Continuation Decision Table

**Baseline commit:** dd909cf3a

## Scenarios x Path Behavior

| Scenario | Path 1 (Generic) | Path 2 (Plan Lock) | Path 3 (Goal Driver) | Path 4 (Deepening) | Notes |
|----------|------------------|--------------------|--------------------|-------------------|-------|
| Clean checkout | STOP/NO_SIGNAL → overridden | N/A (no lock) | CONTINUE, 4/6 (false cert) | format_not_found (FF6) | Three different answers |
| Missing .local/ signal | STOP/NO_SIGNAL → overridden | Lock missing → no constraint | Unaffected (reads committed) | Unaffected | Goal driver is the only correct one |
| Stale signal | STOP/SESSION_MISMATCH (non-overridable) | N/A | Unaffected | Unaffected | CCI protection works for Path 1 |
| Session mismatch | STOP (non-overridable) | Session-scoped lock | N/A (no session concept) | N/A | Path 3 has no session identity |
| Iteration exhaustion | STOP/MAX_ITERATIONS → reset to 0 | N/A | N/A (no iteration concept) | N/A | Supreme Directive overrides |
| Active plan lock | Blocked by lock | Plan taskcards only | Unaffected (still reads state) | Can still be reached via override | Plan lock strongest for Path 1 |
| Completed plan | POST_PLAN_TERMINAL (non-overridable) | Lock shows COMPLETE | Unaffected | Available via new session | POST_PLAN_TERMINAL is correct |
| FF6 active (normal) | May route to FF6 or generic | Per plan content | CONTINUE + next task | Disconnected | Ambiguous routing |
| Empty task queue | STOP → overridden → reads next-sprint.md | Next taskcard | Still has uncertified formats | format_not_found | Path 3 always has work until 6/6 |
| Validator failure | Exit 3 → continue (Supreme) | Continue plan taskcard | N/A (doesn't check validators) | N/A | Governance is advisory |
| Evidence failure | Exit 1 → continue (Supreme) | Continue plan taskcard | N/A | N/A | Evidence is advisory |
| CI failure | N/A (CI is separate) | N/A | N/A | N/A | CI doesn't block local execution |
| External gate | STOP (TRUE_EXTERNAL_GATE) | Continue plan (APPROVAL_GATE_NO not a plan-switch) | BLOCKED | N/A | Inconsistent: plan ignores gates |
| Context exhaustion | Session ends | Session ends | State committed, resumable | N/A | Goal driver handles this correctly |
| Interrupted process | .local/ state may be partial | Lock persists | Committed state safe | May have mutated candidates | Path 3 is safest |
| Concurrent workers | session_id protection | Session-scoped | Safe (read-only) | No coordination with FF6 | Coordination hooks help but are skill-blind |

## Key Observations

1. **No two paths give the same answer** for "clean checkout" — the fundamental requirement for reproducibility
2. **Goal driver (Path 3) is the most robust** — reads committed state, no session identity, deterministic, safe for concurrent use
3. **Generic continuation (Path 1) is the most fragile** — depends on ephemeral local signal, 17/23 STOPs overridden
4. **Generic deepening (Path 4) is completely disconnected** — cannot select FF6 work
5. **Plan locking (Path 2) has the strongest enforcement** for the interactive case but only governs Path 1
