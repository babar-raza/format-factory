# R108 Parallel Execution Map

## Phase 1: Planning (sequential)
- Preflight, lane ownership, overlap check, R107 review

## Phase 2: Evidence + Ledger (parallel)
- Lane A: R107 regrading
- Lane B: Source ledger closure + git state classification

## Phase 3: Product Work (parallel — no overlap)
- Lane C: FODS .NET depth (1-2 APIs)
- Lane D: FODT .NET depth (1-2 APIs)
- Lane E: Netpbm .NET depth (1-2 APIs)
- Lane F: Python/FOSS advancement (3-4 test suites)

## Phase 4: Integration (sequential after Phase 3)
- Coordinator: ledger updates, POC matrix sync
- Lane G: Dogfood tests
- Lane H: Package proof
- Lane I: Fresh gaps + next prompt

## Phase 5: Validation + Closeout (sequential)
- Lane J: Full test suite + IV
- Evidence declaration + autonomous-cycle + review package
