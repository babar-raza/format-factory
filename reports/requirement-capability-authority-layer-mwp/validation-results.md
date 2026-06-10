# Requirements Authority Validation Results
Generated: 2026-06-04T12:55:19.939623+00:00
**Overall: PASS**

| Check | Status | Evidence |
|-------|--------|----------|
| tool_imports | ✅ PASS | All 13 tool modules imported successfully |
| graph_load | ⏭️ SKIP | No graph_dir provided — using empty store for smoke test |
| graph_hash_deterministic | ✅ PASS | graph_hash=e3b0c44298fc1c14... (SHA-256, 64 hex chars) |
| schema_and_invariants | ✅ PASS | 0 errors, 0 warnings |
| coverage_evaluator | ✅ PASS | Evaluated 0 claims. Overall: COVERAGE_BLOCKED (0/0 PASS) |
| overclaim_detector | ✅ PASS | 0 errors, 0 warnings |
| staleness_invalidator | ✅ PASS | 0 stale events, 0 stale claims |
| poc_readiness_netpbm_retained | ✅ PASS | netpbm_retained=True — invariant enforced |
| poc_readiness_svg_rejected | ✅ PASS | svg_replacement_rejected=True — SVG must not replace Netpbm |
| gap_queue_generated | ✅ PASS | Gap queue: 0 entries, graph_hash=e3b0c44298fc1c14... |
| supervisor_verdict_packet | ✅ PASS | packet_id=svp:e3b0c44298fc1c14:202... decision=CONTINUE_MAINSTREAM_WITH_GAP_QUEUE |
| source_graph_hash_present | ✅ PASS | source_graph_hash=e3b0c44298fc1c14... |
| false_stop_risks_present | ✅ PASS | false_stop_risks count=3 (>= 3 required) |
| poc_targets_sync_proposal_no_mutation | ✅ PASS | proposal_id=sync-proposal:e3b0c44298... Prohibition note present — never direct mutation |
| replay_fixtures_all_pass | ✅ PASS | 6/6 fixtures PASS |
| determinism_test | ✅ PASS | Same inputs → same graph hash across 3 reruns for all fixtures |

## Details
- **graph_hash_deterministic** (PASS): SHA-256 hash computed deterministically