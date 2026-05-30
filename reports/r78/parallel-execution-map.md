# R78 Parallel Execution Map

**sprint_id:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**date:** 2026-05-30

## Execution Wave Model

### Wave 0 — Coordinator (blocking: none)
- Lane 0: Preflight, lane-ownership, parallel-execution-map, risk-register, scoreboard

### Wave 1 — IV + State Base (blocking: Wave 0)
- Train A: R77 independent verification + defect ledger + true-product-state-assessment
- Train B: State/master-plan repair + 4 new validator tests

### Wave 2 — Product Deep Work (blocking: Wave 1)
Parallel group 2A — FODS track:
- Train C: FODS reproducibility proof
- Train D: FODS product completion matrix
- Train E: FODS end-to-end workflow + tests + examples
- Train F: FODS package finalization report

Parallel group 2B — FODT track:
- Train G: FODT product completion matrix
- Train H: FODT workflow hardening + tests + examples

Parallel group 2C — ZST + probes + decisions:
- Train I: ZST local FOSS RC proof
- Train J: Probe overclaim correction (FODP/FODG/Gnumeric/ABW)
- Train K: Netpbm product family decision
- Train L: SYLK/DIF product decision

### Wave 3 — Commercial + Docs (blocking: Wave 2)
Parallel group 3A — commercial:
- Train M: .NET test discovery + commercial readiness
- Train N: Gate 11 approval packet

Parallel group 3B — docs/pub/AI:
- Train O: Examples/docs minimum baseline
- Train P: Publication readiness no-publish
- Train Q: AI-assisted product gap extraction

### Wave 4 — Final Closeout (blocking: Waves 1-3)
- Train R: Final closeout + supervisor review package build
- Train S: State/registry/memory/master-plan sync (runs after Train R)

## Critical Path

Wave 0 → Wave 1 → Wave 2 (all groups parallel) → Wave 3 (all groups parallel) → Train R → Train S

## Test Run Schedule

| Run | Scope | When |
|---|---|---|
| Full test suite (baseline confirm) | All tests | After Train B commits |
| FODS end-to-end test (new) | tests/python/fods/test_r78_fods_end_to_end_workflow.py | After Train E |
| FODT end-to-end test (new) | tests/python/fodt/test_r78_fodt_end_to_end_workflow.py | After Train H |
| Full test suite (final) | All tests | After all trains complete (before bundle build) |
