# Machinery Repair Plan
# Sprint ID: ff-machinery-readiness-audit-20260621-23d1333

## Overview

This plan sequences the machinery repairs in dependency order. All repairs are
MACHINERY LANE work — they do NOT touch product feature code in src/python/{format}/
or src/net/{format}/ (except canonical class creation in src/net/FormatFactory/).

## Priority Order

### P0 — Immediate (must complete before any autonomous sprint)

1. **TC-SUPERVISOR-LOCK-001** — Resolve stale plan lock
   - Read polished-hopping-glacier.md TC-HARD-011 status
   - If complete: `python tools/supervisor/write_plan_lock.py --plan-path ... --complete`
   - If not: execute remaining taskcards then close lock
   - Time: 30 minutes

2. **TC-FODS-TEST-FIX-001** — Fix 31 FODS Python ImportErrors
   - Decision per test file: implement missing function OR delete test
   - Priority: tests for REAL functionality → implement; tests for planned-but-abandoned analytics → delete
   - Time: 2-4 hours

### P1 — Machinery Core (must complete before product deepening with spec backing)

3. **TC-SAL-FIX-001** — Wire real FODS spec facts into SAL
   - Modify sal_master_runner.py to load verified-facts-review.yaml
   - Ensure FACT-FODS-NNN IDs are emitted
   - Run SAL tests to verify
   - Time: 4-6 hours

4. **TC-QNAME-GEN-001** — Implement qname_ontology_generator.py
   - Build the tool that generates qname-to-code maps from spec cache
   - Test with FODS format first
   - Time: 6-8 hours

### P2 — QName Foundation (required before backfill)

5. **TC-QNAME-CANONICAL-001** — Create canonical class library
   - Create src/net/FormatFactory/ with Office/, Table/, Text/ namespaces
   - Add spec_qname attributes
   - Run canonical class unit tests
   - Time: 8-12 hours

6. **TC-BACKFILL-TOOLING-001** — Build backfill tooling
   - Create tools/backfill/inventory_current_source.py
   - Create tools/backfill/analyze_qname_gaps.py
   - Run on FODS as pilot
   - Time: 4-6 hours

### P3 — Lane Separation (enables safe autonomous operation)

7. **TC-SUPERVISOR-LANES-001** — Add separate machinery continuation track
   - Add --track machinery to check_continuation.py
   - Create machinery signal file
   - Time: 4-6 hours

### P4 — Gate 11 (product work, after P0 at minimum)

8. **TC-PRODUCT-GATE11-FODS-001** — FODS Gate 11 G11-G submission
   - Can run IN PARALLEL with P1-P3 machinery repairs
   - Only TRUE_EXTERNAL_GATE blocks this: Babar Raza approval
   - Prepare final packet and submit

## What Can Run in Parallel

```
P0.1: Resolve plan lock     ───→ enables autonomous continuation
P0.2: Fix FODS test suite   ───→ runs in parallel with P0.1

P1.1: SAL fix               ───→ after P0 complete
P4: Gate 11 prep            ───→ can run during P1 (no dependency)

P2: QName canonical         ───→ after P1 complete
P3: Lane separation         ───→ can run during P2 (no dependency on qname)
```

## Estimated Total Repair Time

| Phase | Hours |
|-------|-------|
| P0 | 3-5 |
| P1 | 10-14 |
| P2 | 12-18 |
| P3 | 4-6 |
| Total | 29-43 hours |

At 2 hours per autonomous sprint, that's approximately 15-22 focused sprints.

## Product Deepening that CAN Proceed NOW (without waiting for P1-P3)

1. **FODS Gate 11 G11-G submission preparation** — agent-owned, no machinery blocker
2. **FODT Gate 11 evidence bundle preparation** — agent-owned
3. **FODS Python test suite repair** (TC-FODS-TEST-FIX-001) — product improvement, no machinery dep
4. **Adding FODT .NET C1-C20 evidence** — using existing features, no new product code

## Product Deepening that MUST WAIT

1. ANY new analytics functions for ZST/XCF/FODG — suspended per GOV_BLOCK
2. Any product claiming spec_fact_refs — requires SAL fix first (P1.1)
3. Any format migration or backfill — requires P2 canonical classes
4. Any new format beyond FODS/FODT — requires SAL multiformat facts (TC-SAL-MULTIFORMAT-001)
