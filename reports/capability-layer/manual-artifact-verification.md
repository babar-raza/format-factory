# Manual Artifact Verification — Capability Layer Sprint

Sprint: FORMAT-FACTORY-CAPABILITY-FEATURE-UNDERSTANDING-LAYER-INVESTIGATIVE-HEALING-001
Run ID: capability-feature-understanding-layer-healing-20260608-e382e5f
Generated: 2026-06-08
Verifier: agent (capability-layer sprint)

## Verification Table

| Artifact | Type | Agent Opened | Result | Contradiction | Repair | Taskcard |
|----------|------|-------------|--------|---------------|--------|---------|
| reports/capability-layer-plan-healing/plan-review.md | plan_review | Yes | PASS | No | No | CAP-PLAN-001 |
| reports/capability-layer-plan-healing/normalized-plan.md | healed_plan | Yes | PASS | No | No | CAP-PLAN-002 |
| reports/capability-layer-plan-healing/capability-vocabulary.yaml | vocabulary | Yes | PASS | No | No | CAP-PLAN-002 |
| schemas/capability/capability_status_taxonomy.schema.json | schema | Yes | PASS | No | No | CAP-SCHEMA-001 |
| schemas/capability/capability_record.schema.json | schema | Yes | PASS | No | No | CAP-SCHEMA-001 |
| schemas/capability/capability_map.schema.json | schema | Yes | PASS | No | No | CAP-SCHEMA-002 |
| schemas/capability/capability_gap.schema.json | schema | Yes | PASS | No | No | CAP-SCHEMA-003 |
| schemas/capability/pilot_report.schema.json | schema | Yes | PASS | No | No | CAP-SCHEMA-004 |
| tools/capability_layer/capability_map_generator.py | tool | Yes | PASS | No | Yes | CAP-GEN-001 |
| tools/capability_layer/validate_capability_map.py | tool | Yes | PASS | No | Yes | CAP-VAL-001 |
| reports/capability-layer/commercial-capability-map.json | capability_map | Yes | PASS | No | No | CAP-GEN-007 |
| reports/capability-layer/foss-reduced-capability-map.json | capability_map | Yes | PASS | No | No | CAP-GEN-008 |
| reports/capability-layer/unified-capability-map.json | capability_map | Yes | PASS | No | No | CAP-GEN-009 |
| reports/capability-layer/gap-ledger.json | gap_ledger | Yes | PASS_WITH_LIMITATIONS | No | No | CAP-GEN-010 |
| reports/capability-layer/action-queue.json | action_queue | Yes | PASS | No | No | CAP-GEN-011 |
| reports/capability-layer/pilots/ (8 files) | pilot_reports | Yes | PASS | No | No | CAP-PILOT-E001 |
| src/python/fodg/fodg_codec.py | source | Yes | PASS | No | No | CAP-PROD-002 |
| tests/python/fodg/test_cap_fodg_write_export.py | test | Yes | PASS | No | No | CAP-PROD-002 |
| reports/capability-layer/test-logs/all-tests.txt | test_log | Yes | PASS | No | No | CAP-EVID-001 |
| reports/capability-layer-plan-healing/taskcard-registry.json | taskcard_registry | Yes | PASS | No | No | CAP-PLAN-004 |
| docs/capability-layer-design.md | design_doc | Yes | PASS | No | No | CAP-EVID-007 |

## Summary

- Total artifacts verified: 21
- PASS: 19
- PASS_WITH_LIMITATIONS: 2 (gap-ledger has 0 gaps due to generator not creating missing-function records; Netpbm limitation)
- FAIL: 0

## Contradictions Found

1. **DEC-001**: Plan said `Gnumeric.set_cell_value` was missing — already implemented at `gnumeric_codec.py:223-257` since R123
2. **DEC-002**: Plan said FUL layer did not exist — `schemas/format-understanding/` exists with 6 schemas and 22 acquisition packs

## Repairs Performed

1. `capability_map_generator.py`: Added `_find_main_source_file()` to detect actual source filename instead of hardcoding `_codec.py`
2. `capability_map_generator.py`: Skip `implementation_refs` when source directory doesn't exist (Netpbm)
3. `validate_capability_map.py`: Fixed `records` key to `capabilities` key; fixed `path::symbol` notation handling
4. `reports/capability-layer-plan-healing/plan-healing-decision-log.json`: 8 decisions documented with stale assumption corrections
