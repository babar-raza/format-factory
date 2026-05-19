# R27 Independent Verification Report

## IV Questions and Answers

### 1. Are all Phase 2+ features actually implemented or merely documented?
**IMPLEMENTED with evidence:**
- Lane B: model_router.py modified, 10 tests pass
- Lane C: synthesis/runner.py created, 11 tests pass
- Lane D: authority_lifecycle.py enhanced, 12 tests pass
- Lane E: normalization/adapter.py created, 8 tests pass
- Lane F: retrieval/namespace_manager.py created, 9 tests pass (fixture mode)
- Lane G: telemetry/drain.py created, 6 tests pass (dry-run mode)
- Lane H: test_generation/proposal.py created, 10 tests pass
- Lane I: agentic/scoped_runner.py created, 9 tests pass (fixture mode)
- Lane J: validators/risk_controls.py created, 7 tests pass

### 2. Are any taskcards overstated?
**NO.** Taskcards use precise status:
- `phase2_implemented_fixture_mode` for synthesis (needs env for live)
- `phase3_foundation_implemented_blocked_dependency` for embedding (needs LanceDB)
- `phase2_implemented_blocked_env` for telemetry (needs Agent Metrics endpoint)
- `phase2_implemented_blocked_no_model` for agentic (needs Qwen2 model)

### 3. Are all AI outputs still non-authoritative until validated?
**YES.** Proven by:
- `SynthesisResult.authority_state` always starts as `ai_draft` (test: test_authority_never_escalated)
- `GeneratedTestProposal.validate()` rejects non-ai_draft initial state (test: test_wrong_initial_authority)
- `transition_with_evidence()` requires evidence_path (test: test_requires_evidence_path)

### 4. Can any fallback silently select an unsafe model?
**NO.** Proven by:
- `NO_FALLBACK_ROLES = {agentic_low_risk, security_analysis}` fail closed
- Test: test_agentic_low_risk_no_fallback, test_security_analysis_no_fallback
- Fallback is only allowed for low-risk roles (summarization, evidence_review)

### 5. Can Qwen2 mutate repo state?
**NO.** Proven by:
- `FORBIDDEN_OPERATIONS` includes commit, push, delete_file, write_src, etc.
- `ScopedRunner.run()` discards output on scope violation
- Test: test_forbidden_path_discards, test_non_qwen_model_discards_output

### 6. Can embeddings cross-contaminate formats?
**NO.** Proven by:
- `CrossNamespaceError` raised on cross-format query attempts
- Test: test_cross_namespace_rejected, test_per_format_isolation

### 7. Can telemetry leak secrets?
**NO.** Proven by:
- `validate_drain_payload()` checks for sk- and Bearer patterns
- Test: test_secret_in_payload, test_bearer_token_detected
- `secret_redaction.py` redacts known env var values

### 8. Can product source import AI?
**NO.** Proven by:
- Runtime guard: 0 violations in src/python/ and src/net/
- `forbidden-runtime-imports.yaml` lists all AI libraries
- Test: test_clean_src, test_dirty_src_with_ai_import

### 9. Are evidence contracts clean?
**YES.** Phase 1 contract `emergency_blocker_bundle` repaired from true to false.

### 10. Are live tests correctly separated from fixture tests?
**YES.** All new tests are fixture/offline. Live endpoint tests classified as BLOCKED_MISSING_ENV.

### 11. Are missing env vars classified honestly?
**YES.** Three distinct blocked classifications:
- BLOCKED_MISSING_ENV (GPT_OSS_ENDPOINT, AGENT_METRICS_ENDPOINT)
- BLOCKED_MISSING_DEPENDENCY (LanceDB)
- BLOCKED_NO_MODEL (Qwen2 live agentic)

## IV Verdict: PASS — No defects found
