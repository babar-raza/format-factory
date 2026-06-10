# Phase 0 Preflight
# Sprint: FORMAT-FACTORY-FULL-AUTONOMOUS-SYSTEM-AUDIT-AND-REPAIR-001
# Date: 2026-06-05

## Git State

- HEAD: 3a86a05295cb4b82ed40a3408b0612a90f93643c
- Branch: main
- Dirty files: ~438 (all pre-existing sprint WIP from R93 + post-R93 accumulated work)
- Last commit: feat(r93): context-pack, D92 defect repair, governed acceleration

## Python

- Python 3.13.2

## Dirty State Classification

See `dirty-state-classification.json` for per-category classification.

Summary:
- PRE_EXISTING_AUTONOMY_WIP: tools/supervisor/autonomous_host_runner.py, tools/supervisor/proof_backed_poc_gate.py, tools/supervisor/autonomous_train_executor.py (Sprint 2 work)
- PRE_EXISTING_SUPERVISOR_WIP: reports/supervisor/**, .supervisor/**, tools/supervisor/** (accumulated from R94–R100)
- PRE_EXISTING_PRODUCT_WIP: src/net/fods/**, src/net/fodt/**, src/net/netpbm/**, src/python/sylk/** (R94–R100 product work)
- PRE_EXISTING_TEST_WIP: tests/net/**, tests/python/** (R94–R100 tests)
- ALLOWED_THIS_SPRINT_DIRTY_STATE: reports/autonomous-system-audit/** (this sprint)
- UNSAFE_DIRTY_STATE_REQUIRES_STOP: NONE

## Coordinator Plan

This sprint will:
1. Map all 16 autonomous system layers
2. Catalog root causes for R84–R100 stop failures
3. Define and enforce the autonomous execution contract
4. Fix adoption compliance (false pass with 0 transcripts)
5. Fix anti-skip false positives (declared logs not discovered)
6. Add proof graph projection from ledger (reconcile "ledger is canonical")
7. Prove host runner live invocation or classify exact blocker
8. Simulate end-to-end autonomous loop
9. Repair current generated outputs
10. Validate all new tests
11. Issue final autonomy readiness verdict
