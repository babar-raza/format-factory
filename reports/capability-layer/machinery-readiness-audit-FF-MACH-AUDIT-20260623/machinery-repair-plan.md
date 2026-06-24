# Machinery Repair Plan
**Plan:** sorted-purring-stardust | **Taskcard:** TC-SOL-001-01 | **Requirement:** REQ-SOL-001

## Repair Sequence (Dependency Order)

### Phase 6a — Critical Path (Sequential)
1. **TC-MACH-CAP-001** — Add write_selected_gaps() to capability_compiler.py
   - Unblocks: TC-MACH-CAP-002
   - Success: selected-product-gaps.json has selected_gap_count >= 1
   - Dependencies: None (first repair)

2. **TC-MACH-CAP-002** — Wire gap selection into autonomous_task_generator.py
   - Unblocks: All remaining repairs (parallel-safe)
   - Success: >=3 gap-referenced items in next-work-items.json
   - Dependencies: TC-MACH-CAP-001

### Phase 6b — Parallel Repairs (After TC-MACH-CAP-002)
These can execute in any order or in parallel:

3. **TC-MACH-VAL-001** — V50 spec_fact_refs density validator
   - Unblocks: TC-MACH-SRC-001
   - Can run parallel with TC-MACH-CAP-002

4. **TC-MACH-LANE-001** — Preventive lane guard
5. **TC-MACH-SAL-001** — SAL staleness escalation
6. **TC-MACH-BACK-001** — Backfill facility skeleton
7. **TC-MACH-SRC-001** — V51 public API surface governance
8. **TC-MACH-FM-001** — Failure memory escalation
9. **TC-MACH-CAP-003** — Architecture_only stub tracking

### Phase 6c — Close
10. **TC-MACH-CLOSE** — Final evidence bundle and plan terminal close

## Dependency Diagram
```
TC-MACH-CAP-001
  └─► TC-MACH-CAP-002 ─┬─► TC-MACH-LANE-001 ──┐
     │                  ├─► TC-MACH-SAL-001 ───┤
     │                  ├─► TC-MACH-BACK-001 ──┤
     │                  ├─► TC-MACH-FM-001 ────┤
     │                  └─► TC-MACH-CAP-003 ───┤
     │                                         ├─► TC-MACH-CLOSE
     └─► TC-MACH-VAL-001 ─► TC-MACH-SRC-001 ──┘
```

## Success Criteria Per Step
| Taskcard | Pass Condition |
|----------|---------------|
| TC-MACH-CAP-001 | selected_gap_count >= 1 after compiler run |
| TC-MACH-CAP-002 | >= 80% gap-referenced items in work queue |
| TC-MACH-VAL-001 | V50 3 tests pass, 0 regressions in governance suite |
| TC-MACH-LANE-001 | Mixed-lane declaration exits 3 at Step 1b |
| TC-MACH-SAL-001 | Stale SAL blocks product sprint, allows sal_repair |
| TC-MACH-BACK-001 | inventory.py produces valid FODS mapping |
| TC-MACH-SRC-001 | V51 2 tests pass |
| TC-MACH-FM-001 | 3 escalation threshold tests pass |
| TC-MACH-CAP-003 | gap-ledger total >= 967 (938 + 29) |
| TC-MACH-CLOSE | Final ZIP exists, plan lock TERMINAL_CLOSED |
