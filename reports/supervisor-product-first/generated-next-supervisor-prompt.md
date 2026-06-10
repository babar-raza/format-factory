# Generated Next Supervisor Prompt (Advisory)

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

Advisory output — non_authoritative: true, advisory_mode: deterministic_advisory.

## Recommended Next Sprint Direction

Based on the traffic controller analysis, the next Supervisor sprint should:

1. **Validate product-velocity scoring in production** — run `product_velocity_scorer.py`
   against the next Mainstream sprint evidence package to verify CLEAN_PASS / PARTIAL_*
   classification works as expected.

2. **Consume AI advisory output in Mainstream** — Acceleration stream should produce
   AI advisory outputs that Mainstream explicitly consumes (governed consumption chain).

3. **Verify 3 new continuation states fire correctly** — run a sprint that exercises
   NO_PRODUCT_OUTPUT_FLOOR by submitting evidence with families_touched=0.

4. **POC deepening** — FODS/FODT/Netpbm .NET + ZST/PBM/PGM/PPM/SYLK/DIF Python
   remain the primary POC targets per `product-capability-matrix/poc-targets.yaml`.

## Advisory Notes

- This prompt is advisory only. See next-sprint.md for authoritative next sprint prompt.
- External tool governance posture: unchanged (no invocations approved).
- Gate 11 requires human approval from Babar Raza.
