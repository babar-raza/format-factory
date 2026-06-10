# Validator Regression Hardening

Sprint: FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
Date: 2026-06-05

## Test File

Path: tests/supervisor/test_validate_dotnet_dogfood_architecture.py

## Test Results (12-test run)

| # | Test Name | Result |
|---|-----------|--------|
| T1 | test_t1_blocked_gap_ledger_has_four_entries | PASS |
| T2 | test_t2_all_ledger_entries_skill_invocation_false | PASS |
| T3 | test_t3_all_ledger_entries_have_correct_blocker_type | PASS |
| T4 | test_t4_all_ledger_entries_future_decision_required | PASS |
| T5 | test_t5_routing_matrix_all_blocked | PASS |
| T6 | test_t6_actionable_candidates_not_empty | PASS |
| T7 | test_t7_actionable_candidates_not_in_blocked_ledger | PASS |
| T8 | test_t8_top_gap_table_four_entries_score_125 | PASS |
| T9 | test_t9_architecture_decision_record_contains_decision | PASS |
| T10 | test_t10_target_writer_matrix_all_missing | PASS |
| T11 | test_t11_export_policy_blocked_classification_correct | PASS |
| T12 | test_t12_export_policy_no_blocked_gap_in_candidates | PASS |

**Summary: 12/12 PASSED**

## Broader Suite Result

Run command: `.local/venv/Scripts/python -m pytest tests/supervisor -q --tb=no`

- Total passed: 1765
- Total failed: 9

### Pre-existing Failures (all present before this sprint)

1. `tests/supervisor/acceleration/test_acceleration_hardening_iv.py::TestNoProductSourceEdits::test_poc_targets_checksum_unchanged`
2. `tests/supervisor/test_cross_stream_consumption.py::TestCrossStreamConsumptionIntegration::test_replay_file_detects_gaps`
3. `tests/supervisor/test_r90_product_acceleration.py::test_repo_ledger_backfills_r89_apis_and_validates`
4. `tests/supervisor/test_skills_product_breadth_finalization.py::TestFodtMarkdownHandoff::test_fodt_markdown_handoff_mode_is_live`
5. `tests/supervisor/test_skills_product_breadth_finalization.py::TestSkillsIntegrationContract::test_integration_contract_all_packets_ready`
6. `tests/supervisor/test_skills_product_breadth_finalization.py::TestHardeningSprintCompatibility::test_all_handoffs_have_mode_live`
7. `tests/supervisor/test_supervisor_product_traffic_controller_integration.py::TestCrossStreamConsumptionBridge::test_skills_missing_packet_in_real_replay`
8. `tests/supervisor/test_validate_product_code_ledger.py::TestLedgerValidatorPositive::test_real_ledger_passes`
9. `tests/supervisor/test_validate_skill_registry.py::TestRegistryValidatorPositive::test_real_registry_passes`

None of these 9 failures were introduced by this sprint. All were present in the inherited baseline.

## Local Verdict

ACCEPT — 12/12 tests pass. No regressions introduced.
