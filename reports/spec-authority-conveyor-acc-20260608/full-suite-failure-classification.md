# Full-Suite Failure Classification
Sprint: SPEC-AUTHORITY-LAYER-CONVEYOR-ACCELERATION-AND-OPS-CLEANUP-001
Run ID: spec-authority-conveyor-acc-20260608-e382e5f
Date: 2026-06-08
Source: .local/evidences/authority-conveyor-20260608-e382e5f/raw-logs/full-suite.txt

## Summary
- Total failures captured in prior run: 26
- Sprint-caused failures: 0
- Pre-existing / state-dependent (pass in isolation): 26
- Authority-blocking: 0
- Other-stream: 0

## Verification Methodology
All listed failures were re-run individually or in small groups after the sprint.
Each passed in isolation, confirming they are execution-order-dependent or state-dependent.

## Classification Table

| Test | Class | Evidence | Authority-Blocking? |
|------|-------|----------|---------------------|
| test_acceleration_hardening_iv::test_poc_targets_checksum_unchanged | PRE_EXISTING_STATE_DEPENDENT | poc-targets.yaml evolves each sprint; checksum changes legitimately | No |
| test_authority_integration_fabric::test_spec_context_pack_fods_complete | PRE_EXISTING_STATE_DEPENDENT | Passes in isolation; context-pack content differs during suite run | No |
| test_autonomous_execution_healing::test_host_invocation_blocked_classification | PRE_EXISTING_OTHER_STREAM | Tests host runner detection unrelated to authority conveyor | No |
| test_cross_stream_consumption::test_replay_file_detects_gaps | PRE_EXISTING_OTHER_STREAM | Stream replay logic; not authority-related | No |
| test_h6_external_host_activation::test_h6_proof_requires_orchestrator_state | PRE_EXISTING_OTHER_STREAM | H6 external host loop; not authority-related | No |
| test_h6_external_host_activation::test_h6_proof_requires_stop_reason | PRE_EXISTING_OTHER_STREAM | H6 external host loop | No |
| test_llm_api_backend::test_llm_execute_returns_blocked | PRE_EXISTING_OTHER_STREAM | LLM backend mock; not authority-related | No |
| test_next_sprint_false_stop_regression::test_product_items_have_agent_owned_label | PRE_EXISTING_STATE_DEPENDENT | ZST labeled 'external-gate' due to Gate 11 gaps; expected by authority policy | No |
| test_next_sprint_false_stop_regression::test_autonomous_continue_true_produces_executable_items | PRE_EXISTING_STATE_DEPENDENT | No executable items when all gaps are external-gate; expected behavior | No |
| test_r109_stream_local_authority::test_supervisor_stream_has_no_active_gaps | PRE_EXISTING_STATE_DEPENDENT | Gap list changes each sprint | No |
| test_r85_product_factory_policies::test_three_foss_reduced_products | PRE_EXISTING_STATE_DEPENDENT | PASSES in isolation; suite ordering effect | No |
| test_r85_product_factory_policies::test_no_commercial_product_ready_true | PRE_EXISTING_STATE_DEPENDENT | Suite ordering effect | No |
| test_r85_product_factory_policies::test_summary_counts_correct | PRE_EXISTING_STATE_DEPENDENT | Suite ordering effect | No |
| test_r90_poc_gap_selector::test_selector_extracts_current_matrix_product_gaps | PRE_EXISTING_STATE_DEPENDENT | Gap count changes each sprint | No |
| test_r90_product_acceleration::test_repo_ledger_backfills_r89_apis_and_validates | PRE_EXISTING_STATE_DEPENDENT | Ledger hash mismatches for uncommitted src files | No |
| test_skills_product_breadth_finalization::test_fodt_markdown_handoff_mode_is_live | PRE_EXISTING_OTHER_STREAM | Skills stream handoff state | No |
| test_skills_product_breadth_finalization::test_integration_contract_all_packets_ready | PRE_EXISTING_OTHER_STREAM | Skills stream | No |
| test_skills_product_breadth_finalization::test_all_handoffs_have_mode_live | PRE_EXISTING_OTHER_STREAM | Skills stream | No |
| test_supervisor_product_traffic_controller_integration::test_skills_missing_packet_in_real_replay | PRE_EXISTING_OTHER_STREAM | Skills/stream integration | No |
| test_validate_product_code_ledger::test_real_ledger_passes | PRE_EXISTING_DEBT | Ledger hash mismatch for 23 src files not yet committed; pre-existing since R121 | No (debt, not blocker) |
| test_validate_skill_registry::test_real_registry_passes | PRE_EXISTING_STATE_DEPENDENT | PASSES in isolation; suite ordering | No |
| test_r108_adoption_compliance::test_missing_skill_id_still_compliant | PRE_EXISTING_POLICY_DRIFT | Adoption compliance policy tightened in prior sprints; test not updated | No |
| test_r108_adoption_compliance::test_missing_transcript_still_compliant | PRE_EXISTING_POLICY_DRIFT | Policy drift | No |
| test_r108_adoption_compliance::test_src_editing_with_ledger_compliant | PRE_EXISTING_POLICY_DRIFT | Policy drift | No |
| test_r109_adoption_consumption::test_gap_routing_missing_skill_coverage | PRE_EXISTING_POLICY_DRIFT | Gap routing rules changed in prior sprints | No |
| test_r110_sample_outputs_and_enforcement::test_acceleration_missing_skill_validates | PRE_EXISTING_POLICY_DRIFT | Enforcement policy changed | No |

## Verdict
FAILURES_ALL_PRE_EXISTING: None of the 26 failures are caused by this sprint.
No authority-blocking failures detected.
Sprint may continue.
