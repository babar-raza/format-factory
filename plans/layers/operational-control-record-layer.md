# L29 — Operational Control Record Discovery Layer

## Layer Identity

| Field | Value |
|---|---|
| layer_id | L29 |
| canonical_name | Operational Control Record Discovery Layer |
| plane | GOVERNANCE |
| mission_id | FF-CTRL-OCRD-001 |
| status | GOVERNED_OPERATIONAL |
| health | HEALTHY |
| maturity_current | 4 |
| maturity_target | 5 |

## Purpose

This layer discovers, inventories, and indexes the existing operational control structures
that govern autonomous sprint execution. It provides:

1. **Control Layer Inventory** — YAML documentation of all 14 existing control layers
   (continuation signal, plan lock system, gap ledger, skill registry, etc.)
2. **Control Feature Inventory** — 22 observable features with authority effects and behaviors
3. **Feature Parity Register** — disposition of all features: REUSE_AS_IS, REUSE_WITH_VALIDATION,
   or REPLICATE_IN_ENHANCED_LAYER
4. **SQLite Schema v4** — 7 new tables: control_layers, control_features,
   control_feature_consumers, feature_parity_results, quarantines, trust_registry, plans
5. **Control Index Integration** — ControlLayerIngestor, ContradictionIngestor, PlanIngestor
   registered in sync.py (18 total ingestors)
6. **Composite Views** — get_task_context, get_resume_context, get_product_context,
   get_control_feature_context for AI-native query patterns
7. **Query CLI Extensions** — 7 new subcommands: control-layers, task-context, resume-context,
   trust-status, contradictions, parity-status, quarantine
8. **Governance Validators V176-V181** — 6 new validators in
   governance_validators_control_layer.py
9. **22 Pilot Tests** — PASS 22/22 across 4 test files

## Key Artifacts

| Artifact | Purpose |
|---|---|
| `reports/control-layer/operational-control-baseline.yaml` | Discovery baseline |
| `reports/control-layer/existing-control-layers.yaml` | 14 control layer entries |
| `reports/control-layer/existing-control-features.yaml` | 22 observable features |
| `reports/control-layer/control-feature-consumers.yaml` | Consumer map per feature |
| `reports/control-layer/feature-parity-register.yaml` | Parity disposition register |
| `docs/architecture-decisions/ADR-001-control-layer-component.md` | Storage architecture decision |
| `tools/supervisor/control_index/schema.sql` | SQLite schema v4 (7 new tables) |
| `tools/supervisor/control_index/upstream_validator.py` | Pre-ingest validation |
| `tools/supervisor/control_index/ingestors/control_layer_ingestor.py` | Layer ingestor |
| `tools/supervisor/control_index/ingestors/contradiction_ingestor.py` | Contradiction ingestor |
| `tools/supervisor/control_index/ingestors/plan_ingestor.py` | Plan ingestor |
| `tools/supervisor/control_index/views.py` | Composite view functions |
| `tools/supervisor/governance_validators_control_layer.py` | V176-V181 validators |
| `tests/supervisor/test_pilots_group_ab.py` | Pilots 1-6 (22/22 PASS) |
| `tests/supervisor/test_pilots_group_cd.py` | Pilots 7-11 |
| `tests/supervisor/test_pilots_group_ef.py` | Pilots 12-16 |
| `tests/supervisor/test_pilots_group_gh.py` | Pilots 17-22 |

## Skills

| Skill ID | Command | Purpose |
|---|---|---|
| discover-existing-control-layers | /discover-existing-control-layers | Baseline discovery |
| inventory-existing-control-features | /inventory-existing-control-features | Feature inventory |
| verify-control-feature-parity | /verify-control-feature-parity | Parity assessment |
| build-task-context | /build-task-context | Task-scoped query |
| build-resume-context | /build-resume-context | Session resume context |
| build-product-context | /build-product-context | Product-scoped query |
| rebuild-operational-index | /rebuild-operational-index | Full index rebuild |
| validate-operational-index | /validate-operational-index | Index validation |
| quarantine-invalid-artifact | /quarantine-invalid-artifact | Quarantine management |
| audit-enhanced-control-layer | /audit-enhanced-control-layer | Post-enhancement audit |

## Validators

| ID | Name | Enforcement |
|---|---|---|
| V176 | validate_evidence_paths_resolve | FAIL + blocks_sprint if missing |
| V177 | validate_receipt_claimed_before_closure | WARN (advisory) |
| V178 | validate_no_quarantined_plan_source | FAIL + blocks_sprint if quarantined |
| V179 | validate_contradiction_signal_checked | WARN (advisory) |
| V180 | validate_gap_not_exhausted | WARN (advisory) |
| V181 | validate_sync_report_fresh | WARN (advisory) |

## Governance Validators Count

`_EXPECTED_VALIDATOR_COUNT = 181` (updated in governance_validator_runner.py on 2026-07-12)

## Layer Dependencies

| Direction | Layers |
|---|---|
| Upstream (producers) | L09 (State/Continuation), L11 (Supervisor Sprint), L12 (Validation Policy) |
| Downstream (consumers) | L11 (Supervisor Sprint — uses control_index_warnings in check_continuation) |

## Handoffs

| Handoff ID | Type | Producer → Consumer |
|---|---|---|
| HO-009 | control index → supervisor sprint | L29 → L11: control-index.db queried by check_continuation.py |

## Completion Criteria

- [x] TC-OCRD-C1: Discovery + 5-YAML baseline (14 control layers)
- [x] TC-OCRD-C2: Feature inventory + ADR-001 (22 features, 22 consumers)
- [x] TC-OCRD-C3: Schema v4 (7 new tables + migration)
- [x] TC-OCRD-C4: Control layer ingestors (3 new ingestors, 18 total)
- [x] TC-OCRD-C5: Composite views (4 view functions)
- [x] TC-OCRD-C6: Governance validators V176-V181 (6 validators)
- [x] TC-OCRD-C7: Query CLI extensions (7 new subcommands)
- [x] TC-OCRD-C8: 22 Pilot tests (22/22 PASS)
- [x] TC-OCRD-C9: Permanent layer plan L29 + index updates

## Taskcard History

| TC-ID | Title | Status | Closed At |
|---|---|---|---|
| TC-OCRD-C1 | Control Layer Baseline Discovery | CLOSED | 2026-07-12 |
| TC-OCRD-C2 | Feature Inventory + ADR | CLOSED | 2026-07-12 |
| TC-OCRD-C3 | Schema v4 Tables | CLOSED | 2026-07-12 |
| TC-OCRD-C4 | Control Layer Ingestors | CLOSED | 2026-07-12 |
| TC-OCRD-C5 | Composite Views | CLOSED | 2026-07-12 |
| TC-OCRD-C6 | Validators V176-V181 | CLOSED | 2026-07-12 |
| TC-OCRD-C7 | Query CLI Extensions | CLOSED | 2026-07-12 |
| TC-OCRD-C8 | 22 Pilot Tests | CLOSED | 2026-07-12 |
| TC-OCRD-C9 | Permanent Layer Plan L29 | CLOSED | 2026-07-12 |

## Notes

- **Consumer map bug fix (2026-07-12):** `control_layer_ingestor.py` consumer parsing
  navigates `cdata.get("control_feature_consumers")` before iterating feature entries.
  The YAML has a top-level `control_feature_consumers:` wrapper key.
- **Schema v4 migration:** `_migrate_v3_add_control_tables` uses `CREATE TABLE IF NOT EXISTS`
  throughout — fully idempotent (Pilot 17 verified).
- **trust_registry:** Future enforcement point for content authenticity. Currently no
  UNTRUSTED entries in production; test infrastructure validates warning emission.
- **Next enhancement cycle:** Add trust_registry population from actual artifact signatures;
  extend quarantine lifecycle (RESOLVED/EXPIRED status transitions).
