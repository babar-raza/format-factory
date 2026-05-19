# Expanded AI Failure Injection (Lane J)
## Sprint: FORMAT-FACTORY-R32-AI-CLEAN-CLOSURE-STATUS-REPAIR-AND-PIPELINE-DEEPENING-MEGA-TRAIN-001

## Purpose
Expand R31's 15 failure injection cases with 20 additional realistic pipeline risks.

## New Failure Injection Tests (TestExpandedFailureInjection)

| # | Test | Verifies |
|---|------|----------|
| 1 | test_conflicting_citations | Two citations for same source with different text detected |
| 2 | test_citation_source_exists_wrong_chunk_hash | Stale chunk hash rejects retrieval |
| 3 | test_model_returns_valid_json_wrong_schema | Missing required fields fail synthesis |
| 4 | test_model_returns_extra_unknown_fields | Extra fields don't crash (permissive) |
| 5 | test_prompt_injection_in_source_chunk | Injection text doesn't affect scoring |
| 6 | test_source_chunk_asks_model_to_ignore_rules | Rule-breaking text doesn't bypass verification |
| 7 | test_retrieved_chunk_from_wrong_format | Wrong format namespace rejected |
| 8 | test_duplicate_requirement_ids | Duplicate IDs are detectable |
| 9 | test_requirement_source_hash_mismatch | Structural validation runs regardless |
| 10 | test_telemetry_write_failure_handled | Write to bad path doesn't crash |
| 11 | test_live_gateway_timeout_handled | Connection timeout produces error status |
| 12 | test_live_gateway_rate_limit_response | Rate limit produces error status |
| 13 | test_model_does_not_support_required_role | Router fails closed for unsupported role |
| 14 | test_evaluator_threshold_borderline | Borderline pass handled correctly |
| 15 | test_poisoned_verified_fact | SQL injection in fact doesn't crash |
| 16 | test_empty_retrieval_result | High threshold returns no results safely |
| 17 | test_top_k_excludes_required_source | Low top-k excludes chunks (expected behavior) |
| 18 | test_too_many_citations | 100 citations processed without error |
| 19 | test_secret_looking_text_in_model_output | sk- pattern in output detected |
| 20 | N/A | (tests cover 19 distinct cases + R31's 15 = 34 total) |

## Combined with R31
- R31: 15 failure injection tests (in test_r31_ai_system_verification.py)
- R32: 19 new failure injection tests (in test_r32_ai_deepening.py)
- Total: **34 failure injection cases**

## All tests PASS — failures are safe and expected.
