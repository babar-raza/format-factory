# R27 Adversarial Review

## 25 Adversarial Questions

### Authority and Lifecycle
1. **Can an AI draft skip to authoritative status?** NO. test_no_skip_draft_to_authoritative proves this. VALID_TRANSITIONS enforces sequential chain.
2. **Can a transition occur without evidence?** NO. transition_with_evidence() requires non-empty evidence_path. Test: test_requires_evidence_path.
3. **Can a rejected artifact be revived?** NO. rejected is terminal. Test: test_rejected_is_terminal, test_cannot_transition_from_terminal.
4. **Can accepted_for_planning jump to accepted_for_source_requirements?** NO. Test: test_accepted_planning_not_source.
5. **Can SynthesisResult have authority != ai_draft?** NO. run_synthesis() always sets ai_draft. Test: test_authority_never_escalated.

### Model Routing and Safety
6. **Can agentic_low_risk fall back to GPT?** NO. NO_FALLBACK_ROLES enforces fail_closed. Test: test_agentic_low_risk_no_fallback.
7. **Can security_analysis fall back to any model?** NO. Same enforcement. Test: test_security_analysis_no_fallback.
8. **Can a non-Qwen model run agentic tasks?** NO. ScopedRunner.validate_model() rejects non-qwen. Test: test_non_qwen_rejected.
9. **Can an agentic task commit code?** NO. FORBIDDEN_OPERATIONS includes "commit". Test: test_all_dangerous_ops_in_set.
10. **Can an agentic task access src/python/?** NO if not in path_allowlist. Test: test_forbidden_path_discards.

### Product Source Integrity
11. **Can litellm appear in src/python/?** NO. Runtime guard detects it. Test: test_dirty_src_with_ai_import.
12. **Can GPT_OSS_API_KEY appear in src/net/?** NO. Forbidden env refs in contract. Runtime guard enforces.
13. **Can tools.ai be imported in product source?** NO. Forbidden import in contract.
14. **Can llm.professionalize.com appear in product source?** NO. Forbidden URL ref.

### Secrets and Telemetry
15. **Can API keys leak into telemetry?** NO. validate_spool_record() checks for sk- and Bearer. Test: test_secret_in_payload.
16. **Can drain payloads contain Bearer tokens?** NO. validate_drain_payload() detects them. Test: test_bearer_token_detected.
17. **Can secret_redaction miss a known env var?** Low risk. _SECRET_ENV_VARS list is maintained, and env var values are redacted if present.
18. **Can Agent Metrics post without env vars?** NO. is_agent_metrics_configured() checks both vars.

### Embeddings and Retrieval
19. **Can FODS embeddings query FODT namespace?** NO. CrossNamespaceError. Test: test_cross_namespace_rejected.
20. **Can a stale index serve results?** Stale detection via detect_stale_index(). But query() doesn't automatically check — callers must check.
21. **Can embeddings be created without normalized chunks?** NO. Lane E's fail-closed ensures NormalizationNotAvailable.

### Evidence and Governance
22. **Can a test proposal be written directly to product tests?** NO. ProposalReviewer only tracks metadata. No file write mechanism.
23. **Can emergency_blocker_bundle remain true after completion?** Not anymore — Lane A repaired this.
24. **Can this sprint self-approve Gate 11?** NO. No gate approval code exists. G11-G remains NOT_STARTED.
25. **Can this sprint push to remote?** NO. No git push command anywhere in implementation.

## Adversarial Verdict: 25/25 NO DEFECT
