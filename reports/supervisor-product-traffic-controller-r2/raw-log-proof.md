# Raw Log Proof — Lane B

## Sprint
`FORMAT-FACTORY-SUPERVISOR-PRODUCT-TRAFFIC-CONTROLLER-R2-...`

## Raw Logs Captured

| Test File | Raw Log | Tests | Exit Code |
|-----------|---------|-------|-----------|
| test_supervisor_product_traffic_controller_integration.py | raw-logs/raw-test-integration.txt | 17 passed | 0 |
| test_cross_stream_consumption.py | raw-logs/raw-test-cross-stream.txt | 9 passed | 0 |
| test_continuation_state_integration.py | raw-logs/raw-test-continuation.txt | 11 passed | 0 |
| test_external_tool_governance_integration.py | raw-logs/raw-test-ext-governance.txt | 16 passed | 0 |
| ALL TARGETED (combined) | raw-logs/raw-test-all-targeted.txt | 53 passed | 0 |
| FULL supervisor suite | raw-logs/raw-test-full-supervisor-suite.txt | 1253 passed, 12 failed | 1 |

## Targeted Tests: 53 PASSED, 0 FAILED ✓

## Full Supervisor Suite: Inherited Failures

The 12 failures in the full supervisor suite are ALL inherited/pre-existing:

| File | Failure Type | Sprint That Introduced |
|------|-------------|----------------------|
| acceleration/test_r113_ai_implementation_designer.py (5 failures) | PathLib ValueError — tmp_path not in repo root | Acceleration R113 (pre-existing) |
| acceleration/test_r113_ai_learning_loop.py (4 failures) | PathLib ValueError — tmp_path not in repo root | Acceleration R113 (pre-existing) |
| acceleration/test_r113_ai_sprint_manager.py (2 failures) | Missing ModelRouter attr / field missing | Acceleration R113 (pre-existing) |
| test_validate_skill_registry.py (1 failure) | Skill registry validation assertion | Skills sprint (pre-existing) |

**Classification: INHERITED_FAILURES_NOT_CAUSED_BY_THIS_SPRINT**

This sprint touched: generate_stream_routing_packet.py, check_cross_stream_consumption.py,
and 4 test files in tests/supervisor/ (none of the failing files).

## Evidence Quality Impact

Adding raw logs to declaration will allow TC-TEST-001 to be graded ACCEPTED_VERIFIED
(currently ACCEPTED_WITH_LIMITATIONS due to path-only evidence).

Expected evidence_quality_score after fix: > 0.0 (at least 1/11 items verified).

## Verdict
**RAW_LOG_PROOF_COMPLETE** — All 53 targeted tests proven by raw logs. 12 inherited failures isolated and classified.
