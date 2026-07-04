# Taskcard State Machine Validation Rules
Generated: 2026-07-04

## Invalid Transitions (Hard Block)

| From | To | Block Reason |
|------|----|-------------|
| TODO | CLOSED | Must traverse IMPLEMENTED → VERIFIED → SCORED first |
| READY | CLOSED | Must traverse IMPLEMENTED → VERIFIED → SCORED first |
| IMPLEMENTED | CLOSED | Must be VERIFIED and SCORED first |
| SCORED | IN_PROGRESS | Must go through REROUTED first |
| any | CLOSED (while micro-steps PENDING/FAILED) | All mandatory micro-steps must complete |
| parent | CLOSED (while children not CLOSED) | All mandatory children must close first |
| REROUTED | CLOSED | Without rework evidence = hard block |
| BLOCKED_EXTERNAL | CLOSED | Without unblock evidence record = hard block |
| PENDING | SKIPPED_NOT_APPLICABLE | Without explicit reason recorded = hard block |

## Quality Scoring Gate

Every child must score ≥ 4/5 on ALL 8 dimensions before CLOSED:
1. requirement_correctness
2. implementation_correctness
3. scope_discipline
4. validation_strength
5. evidence_completeness
6. regression_safety
7. maintainability
8. production_readiness

Any dimension < 4/5 → REROUTED (not CLOSED).

## Scope Discipline Hard Rules

- NEVER close a child while any mandatory micro-step is PENDING or FAILED
- NEVER close a parent while any mandatory child is not CLOSED
- SKIPPED_NOT_APPLICABLE requires explicit reason documented before applying
- REROUTED requires smallest possible repair micro-step before re-execution
