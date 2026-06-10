# RCA Layer Implementation Inventory
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001
# Lane: A

## Discovered Implementation Path
`tools/requirements_authority/` — 15 Python modules

## Subsystem Coverage Matrix

| Subsystem | Module | Status | Notes |
|-----------|--------|--------|-------|
| ProductRequirementRegistry | models.py + graph_store.py | PRESENT | GraphNode with ProductRequirement type |
| CapabilityClaimRegistry | models.py + graph_store.py | PRESENT | GraphNode with CapabilityClaim type |
| UnsupportedFeatureLedger | models.py + graph_store.py | PRESENT | GraphNode with UnsupportedFeature type |
| CapabilityDeltaSystem | capability_delta.py | PRESENT | CapabilityDeltaValidator, 12-step promotion |
| CapabilityCoverageEvaluator | coverage_evaluator.py | PRESENT | OPERATION_MIN_PROOF, 9 proof classes, 10 levels |
| OverclaimDetector | overclaim_detector.py | PRESENT | 10 patterns, 10 remediation actions |
| StalenessInvalidationEngine | staleness_invalidator.py | PRESENT | 12 triggers, propagation chain |
| PocReadinessComputer | poc_readiness.py | PRESENT | compute_all(), Netpbm retained, SVG rejected |
| MainstreamGapQueueGenerator | mainstream_gap_queue.py | PRESENT | 11-step algorithm, 15 entry fields |
| SupervisorVerdictPacketGenerator | supervisor_verdict_packet.py | PRESENT | 16-field packet, 9 decisions |
| PocTargetsSyncProposalGenerator | poc_targets_sync_proposal.py | PRESENT | PROHIBITION enforced |
| EvidenceGraphImporter | import_existing_state.py | PRESENT | 5 import rules, Phase 0+1 |
| GoldenReplaySuite | run_replay_fixtures.py | PRESENT | 6 fixture packs, determinism test |
| Graph store / JSONL | graph_store.py | PRESENT | SHA-256 hash, save/load nodes+edges |
| Graph validator | validators.py | PRESENT | 8 invariants |
| CLI validator | validate_requirements_authority.py | PRESENT | Overall: PASS (previously verified) |

## All Subsystems: PRESENT
## Missing: None
## Unverified: None (all run in this pilot)

## Safe Execution Paths
1. `python tools/requirements_authority/validate_requirements_authority.py` — CLI validator
2. `python reports/requirement-capability-real-pilot-r1/_rca_pilot_driver.py` — this pilot
3. `python -m pytest tests/supervisor/test_r100_*.py` — 48 tests

## Pilot Run Summary
- 81 nodes built (all 18 node types used)
- 102 edges built (all major edge types used)
- 20 capability claims across 5 pilots
- 0 validation errors
- 0 overclaim errors (after 1 remediation: netpbm:save direction write_only → read_write)
- 1 stale claim (synthetic: zst:old-compress)
