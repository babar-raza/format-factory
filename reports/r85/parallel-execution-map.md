# R85 Parallel Execution Map

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Execution Wave 1 — Foundation (no dependencies)

Run in parallel:
- Train A: Direction correction (memory, master-plan, docs)
- Train B: POC target matrix (product-capability-matrix/)
- Train C: Supervisor verification (run-on-latest smoke)

## Execution Wave 2 — Policy + Product Setup (depends on Wave 1)

Run in parallel after Wave 1:
- Train D: Supervisor product-factory policy
- Train E: Approval gate classifier update
- Train G: FODS reproducibility audit
- Train I: FODS .NET product slice audit

## Execution Wave 3 — Product Work (depends on Wave 2)

Run in parallel:
- Train H: Format family templates
- Train J: FODT .NET product slice audit
- Train K: Third commercial product (.NET Netpbm first slice)
- Train L: ZST FOSS status
- Train M: Netpbm Python FOSS — PBM→PGM dogfood export
- Train N: SYLK FOSS status

## Execution Wave 4 — Dogfooding + Examples (depends on Wave 3)

Run in parallel:
- Train F: TM/Ruflo alignment + tests
- Train O: Dogfood export map
- Train P: First dogfooded export implementation/tests
- Train R: Examples/docs baseline

## Execution Wave 5 — Integration (depends on Wave 4)

Sequential:
- Train Q: Package build + install proof
- Train S: AI gap extraction (fixture-only)
- Train T: Supervisor autonomous loop (run-on-latest)

## Execution Wave 6 — Closure (sequential)

- Train U: State/registry/memory sync
- Train V: Final adversarial IV
- Final: Evidence bundle + supervisor review package

## Critical Path

Wave 1 → Train K (.NET Netpbm implementation) → Train P (dogfood tests) → Train V (IV) → Bundle

## Parallelism Notes

Trains with no shared file writes can run concurrently.
Trains writing to state/ or plans/ must be sequentialized with coordinator gate.
