# Lane B: Control-Plane Hardening

## Changes
1. Added `NO_FALLBACK_ROLES` set containing `agentic_low_risk` and `security_analysis`
2. Added `load_role_requirements()` to load role constraints from `roles.yaml`
3. Router now enforces:
   - `restricted_to: qwen2_only` — filters to qwen models only for agentic_low_risk
   - `requires_embedding: true` — filters to embedding-capable models for embedding_retrieval
4. No-fallback roles fail closed immediately without trying any chat model
5. Updated existing Phase 2 tests that expected fallback for restricted roles

## Tests Added (10)
- test_agentic_low_risk_no_fallback
- test_security_analysis_no_fallback
- test_summarization_allows_fallback
- test_qwen2_restriction_for_agentic
- test_embedding_restriction
- test_completely_empty_models
- test_role_mismatch_all_models
- test_load_from_contracts
- test_missing_contracts_dir
- Updated 2 existing Phase 2 tests

## Lane B Status: CLOSED_VERIFIED
