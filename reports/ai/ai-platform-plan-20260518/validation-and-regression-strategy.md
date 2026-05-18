# Validation and Regression Strategy

**Date:** 2026-05-18

## 1. Validation Layers

### Layer 1 — Schema Validation
- All AI inputs validated against Pydantic models before calls
- All AI outputs validated against Pydantic models before acceptance
- Schema violations immediately reject the output
- Schema registry tracks versions and breaking changes

### Layer 2 — Citation Verification
- Every factual claim in synthesis output must cite a source chunk ID
- Source-support verifier confirms the cited chunk contains supporting text
- Citation failures trigger output rejection and hallucination flagging

### Layer 3 — Contradiction Detection
- Synthesis output compared against existing verified facts
- Contradictions flagged for human review before resolution
- Contradiction rate tracked in telemetry

### Layer 4 — Golden Evaluations
- Per-task-type golden eval datasets
- Known-good input/output pairs
- Regression detection on model change, prompt change, or schema change
- Eval score threshold per task type (configurable)

### Layer 5 — Artifact Authority Lifecycle
- 12-state machine enforced programmatically
- No skip from ai_draft to authoritative
- Each transition requires specific validation pass
- State transition audit log

### Layer 6 — Runtime Guard
- Static import analysis on src/python/ and src/net/
- Blocks imports of tools/ai, LiteLLM, LlamaIndex, LanceDB, endpoint clients
- Runs in CI and as pre-commit check

### Layer 7 — Risk Register Validation
- Each of 48 risks has at least one automated test
- CRITICAL risks have multiple tests
- Stop conditions enforced programmatically where possible

## 2. Regression Controls

### Model Regression
- Trigger: model fingerprint change detected by discovery
- Action: run full golden eval suite; compare against baseline
- Threshold: >20% degradation triggers pause and investigation

### Prompt Regression
- Trigger: prompt version hash change
- Action: run golden evals for affected task types
- Threshold: >15% degradation triggers revert

### Schema Regression
- Trigger: schema version change
- Action: run downstream consumer compatibility tests
- Threshold: breaking change requires migration plan

### Index Regression
- Trigger: source hash change, embedding model change
- Action: re-index affected format; run retrieval eval
- Threshold: recall <60% triggers investigation

## 3. No-Runtime-AI Import Guard

Protected paths: `src/python/**`, `src/net/**`
Blocked imports: `tools/ai`, `litellm`, `llama_index`, `lancedb`, `openai`, `anthropic`, `ollama`
Blocked env refs: `GPT_OSS_ENDPOINT`, `GPT_OSS_API_KEY`
Exception: `tools/**` may import AI infrastructure

## 4. Evidence Bundle Integration

Every sprint that uses AI must include:
- Telemetry summary
- Eval results
- Citation verification stats
- Contradiction detection stats
- Artifact authority state summary
- Risk control test results

## 5. Concrete Test Matrix (25 Tests)

| # | Test | What It Proves | Phase |
|---|------|---------------|-------|
| 1 | `test_no_runtime_ai_imports_python` | src/python/ has no AI imports | 1 |
| 2 | `test_no_runtime_ai_imports_dotnet` | src/net/ has no AI package refs | 1 |
| 3 | `test_direct_endpoint_blocked` | Gateway is only entry point | 1 |
| 4 | `test_model_discovery_missing_models` | Empty /v1/models handled | 1 |
| 5 | `test_role_routing_fails_closed` | No qualified model → error | 1 |
| 6 | `test_fallback_model_recorded` | Telemetry captures fallback | 1 |
| 7 | `test_schema_validation_rejects_malformed` | Bad output rejected | 1 |
| 8 | `test_uncited_requirement_rejected` | No citations → rejected | 2 |
| 9 | `test_unsupported_citation_rejected` | Bad citation → rejected | 2 |
| 10 | `test_contradiction_detection` | Contradicts verified facts → flagged | 2 |
| 11 | `test_vector_store_format_isolation` | Cross-format query blocked | 3 |
| 12 | `test_stale_embeddings_detected` | Source hash mismatch flagged | 3 |
| 13 | `test_retrieval_replay` | Same query → same results | 3 |
| 14 | `test_telemetry_row_created` | Every AI call produces spool entry | 1 |
| 15 | `test_agent_metrics_mapping` | Spool maps to Google Sheet fields | 1 |
| 16 | `test_spool_offline_mode` | Works when posting unavailable | 1 |
| 17 | `test_prompt_version_recorded` | Telemetry includes prompt hash | 1 |
| 18 | `test_taskcard_linkage_required` | Task without taskcard rejected | 1 |
| 19 | `test_evidence_includes_ai_artifacts` | Bundle includes AI telemetry | 2 |
| 20 | `test_qwen2_scope_enforcement` | Exceeding scope → stop | 4 |
| 21 | `test_test_idea_lifecycle` | Full lifecycle enforced | 4 |
| 22 | `test_deferred_review_taskcards_exist` | Every deferred item has taskcard | 1 |
| 23 | `test_model_change_compat_check` | Fingerprint change triggers eval | 2 |
| 24 | `test_prompt_injection_neutralized` | Malicious spec content sanitized | 2 |
| 25 | `test_large_prompt_truncation_detected` | Truncation logged | 2 |

## 6. Content Validation Checks (Plan-Level)

Beyond file existence, the plan-level validation verifies:
1. All 10 plan reports have non-empty content with correct headers
2. Risk register contains exactly 48 unique RISK-AI-NNN IDs with all 12 required fields
3. All 17 production components have all 9 required specification fields
4. All 12 artifact authority states appear in transition table
5. Agent Metrics mapping covers all 17 Google Sheet fields
6. Every deferred feature has reason + prerequisite + review taskcard
7. Parallel sprint safety plan lists both owned and forbidden paths
8. Implementation roadmap has acceptance criteria per phase
9. Technology decisions have phase assignment and rationale
10. Final execution readiness review answers all 10 required questions
