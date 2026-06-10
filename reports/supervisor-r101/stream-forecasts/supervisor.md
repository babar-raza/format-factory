# Supervisor Stream — 3-Sprint Forecast

## Next Sprint (R102)
- Focus: Supervisor infrastructure — grading, continuation, stream prompts, evidence model
- Targets: Anti-regression tests for generic prompt detection; checkpoint policy tests
- Harden: Evidence manifest validation; materialization verification; review package builder
- Expected test growth: ~15-20 new supervisor infrastructure tests

## Next+1 (R103)
- Focus: Replay infrastructure and cross-stream validation
- Targets: Replay test fixtures from all 4 streams; cross-stream grade comparison
- Expected: Replaying any package produces identical grades to original run

## Next+2 (R104)
- Focus: Autonomous loop self-validation
- Targets: Supervisor cycle can validate its own outputs end-to-end
- Expected: Full autonomous loop (up to max_iterations) tested with synthetic data
