# Production Solution Architecture

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-DEEP-PRODUCTION-ARCHITECTURE-REVIEW-001
**Date:** 2026-05-18

---

## Architecture Principle

The AI platform is a **governed acceleration layer** with a single entry point, executable contracts, deterministic validation, and full telemetry. It sits between the existing project infrastructure (gates, evidence, taskcards) and external AI services (llm.professionalize.com). It does not replace any existing authority — it provides structured AI assistance that feeds into the existing authority model.

---

## Component Architecture

### 1. AI Gateway (`tools/ai/gateway.py`)
**Responsibility:** Single choke point for ALL AI calls. No AI endpoint call may bypass this module.
**Inputs:** TaskContract (Pydantic model), caller identity, sprint context.
**Outputs:** TaskResult with authority_state=ai_draft, telemetry record.
**Storage:** None (stateless coordinator).
**Schemas:** TaskContract, TaskResult, GatewayConfig.
**Failure modes:** Endpoint unreachable -> fail closed. Schema validation fails -> reject. No qualified model -> ROLE_UNAVAILABLE.
**Validation:** Test that importing litellm outside tools/ai/ is detected. Test that direct endpoint calls are blocked.
**Evidence:** Gateway call log in telemetry spool.
**Owner:** AI-PLATFORM-FOUNDATION-PLAN.

### 2. Model Discovery Service (`tools/ai/control_plane/model_discovery.py`)
**Responsibility:** Enumerate models from llm.professionalize.com, probe capabilities, cache results.
**Inputs:** Endpoint URL from GPT_OSS_ENDPOINT env var.
**Outputs:** ModelRegistry (list of discovered models with capabilities).
**Storage:** `.local/ai/model-registry/models-{timestamp}.json` (cache, gitignored).
**Schemas:** DiscoveredModel (model_id, capabilities: list[str], context_window: int, max_tokens: int, embedding_dimensions: Optional[int]).
**Failure modes:** Endpoint unreachable -> use cached registry if fresh (<24h). Cache expired + endpoint down -> fail closed. API returns unexpected shape -> log and fail closed.
**Validation:** Mock /v1/models response; verify parsing. Mock empty response; verify fail-closed. Mock changed model list; verify diff detection.
**Evidence:** Model discovery snapshot in evidence bundle metadata.
**Owner:** AI-MODEL-DISCOVERY-AND-ROUTING.

### 3. Role-Based Model Router (`tools/ai/control_plane/model_router.py`)
**Responsibility:** Select best model for a given role based on capability requirements.
**Inputs:** ModelRole enum, ModelRegistry, RoleRequirements.
**Outputs:** SelectedModel (model_id, was_fallback, alternatives_count).
**Storage:** `tools/ai/contracts/roles.yaml` (committed config defining role requirements).
**Schemas:** ModelRole (enum), RoleRequirement (min_context_window, required_capabilities, preferred_model_family, fallback_order), SelectedModel.
**Failure modes:** No model meets requirements -> ROLE_UNAVAILABLE error. Only fallback available -> log warning, proceed with flag. Role not defined -> reject.
**Validation:** Test each role against mock registries with varying model sets. Test fail-closed when no model qualifies.
**Evidence:** Model selection log with decision trace.
**Owner:** AI-MODEL-DISCOVERY-AND-ROUTING.

### 4. Task Contract Registry (`tools/ai/contracts/`)
**Responsibility:** Define and validate task contracts — what each AI task is allowed to do.
**Inputs:** Task type, caller context.
**Outputs:** Validated TaskContract.
**Storage:** `tools/ai/contracts/tasks/` (YAML per task type, committed).
**Schemas:** TaskContract (task_type, model_role, input_schema_ref, output_schema_ref, allowed_paths, allowed_ops, max_tokens, timeout_seconds, citation_required, contradiction_check, taskcard_id).
**Failure modes:** Unknown task type -> reject. Missing required fields -> reject. Schema mismatch -> reject.
**Validation:** Load all task contracts; verify schema validity. Test with missing fields; verify rejection.
**Evidence:** Task contract validation report.
**Owner:** AI-PLATFORM-FOUNDATION-PLAN.

### 5. Prompt Registry (`tools/ai/prompts/`)
**Responsibility:** Version and hash all prompt templates.
**Inputs:** Prompt template ID.
**Outputs:** Prompt text with version hash.
**Storage:** `tools/ai/prompts/{task_type}/v{N}.yaml` (committed, versioned).
**Schemas:** PromptTemplate (template_id, version, content_hash, variables, created_at).
**Failure modes:** Template not found -> reject. Hash mismatch -> reject (template modified without version bump).
**Validation:** Verify all template hashes match content. Test hash verification.
**Evidence:** Prompt version hash in telemetry.
**Owner:** AI-PLATFORM-FOUNDATION-PLAN.

### 6. Schema Registry (`tools/ai/schemas/`)
**Responsibility:** Pydantic models for all AI inputs/outputs.
**Inputs:** Schema reference from task contract.
**Outputs:** Validated Pydantic model instance.
**Storage:** `tools/ai/schemas/` (Python modules with Pydantic v2 models).
**Schemas:** All input/output schemas for every synthesis task type.
**Failure modes:** Output doesn't match schema -> reject as ai_draft_invalid. Extra fields -> strip and warn. Missing required fields -> reject.
**Validation:** Generate invalid outputs; verify rejection. Generate valid outputs; verify acceptance.
**Evidence:** Schema validation results in telemetry.
**Owner:** AI-PLATFORM-FOUNDATION-PLAN.

### 7. Artifact Authority Lifecycle Service (`tools/ai/validators/authority_lifecycle.py`)
**Responsibility:** Track and enforce AI artifact state transitions.
**Inputs:** Artifact ID, current state, requested transition, evidence.
**Outputs:** Transition result (accepted/rejected with reason).
**Storage:** `.local/ai/artifact-states.jsonl` (local state log, gitignored). Committed state in artifact frontmatter.
**Schemas:** ArtifactAuthorityState (enum of 12 states), TransitionRequest, TransitionResult, ValidTransitions (adjacency map).
**Failure modes:** Invalid transition -> reject with reason. Missing evidence for transition -> reject. Artifact not found -> reject.
**Integration with gates:** Mapping table defines which artifact states are required at each gate. Gate transitions check artifact state prerequisites.
**Validation:** Attempt every invalid transition; verify all rejected. Attempt every valid transition with evidence; verify all accepted.
**Evidence:** State transition log.
**Owner:** AI-PLATFORM-FOUNDATION-PLAN.

### 8. Retrieval/Index Manager (`tools/ai/retrieval/`)
**Responsibility:** Manage per-format vector stores: create, refresh, query, stale-detect.
**Inputs:** Format namespace, query text, index version.
**Outputs:** RetrievalResult (chunk_ids, scores, metadata, stale_flag).
**Storage:** `.local/ai/vector-stores/{format}/` (LanceDB files, gitignored). `tools/ai/manifests/{format}-vector-manifest.yaml` (committed manifest).
**Schemas:** RetrievalQuery, RetrievalResult, ChunkManifest, IndexMetadata.
**Failure modes:** Index not found -> fail (cannot silently skip retrieval). Index stale -> warn + flag results. Embedding model unavailable -> fail closed. Cross-namespace query without explicit flag -> reject.
**Validation:** Test namespace isolation (query format A, verify no format B results). Test stale detection (modify source, verify flag). Test rebuild (delete index, rebuild, verify same results).
**Evidence:** Retrieval audit log summary, index metadata snapshot.
**Owner:** AI-EMBEDDING-VECTOR-STORE-FOUNDATION.

### 9. Spec Normalization Adapter (`tools/ai/normalization/adapter.py`)
**Responsibility:** Bridge between existing spec normalization output and AI platform input.
**Inputs:** Format ID, spec version.
**Outputs:** List of NormalizedChunk with provenance.
**Storage:** Reads from `.local/spec-cache/{format}/{version}/normalized/chunks.jsonl` (existing).
**Schemas:** NormalizedChunk (chunk_id, source_path, source_hash, spec_version, section_id, chunk_text_hash, token_count).
**Failure modes:** Normalization output not found -> fail. Chunk format incompatible -> fail with version mismatch.
**Validation:** Load FODS chunks; verify provenance chain intact. Test with missing normalization output; verify clear error.
**Evidence:** Chunk manifest hash.
**Owner:** AI-SPEC-NORMALIZATION-INTEGRATION.

### 10. LLM Synthesis Workflow Runner (`tools/ai/synthesis/runner.py`)
**Responsibility:** Execute Type B synthesis tasks (extraction, test generation, security analysis).
**Inputs:** SynthesisTask (extends TaskContract), retrieved context, prompt template.
**Outputs:** SynthesisResult with citations, authority_state=ai_draft.
**Storage:** Output artifacts in sprint-specific paths.
**Schemas:** SynthesisTask, SynthesisResult, Citation, ContradictionCheckResult.
**Failure modes:** Schema validation fails -> reject output. No citations -> reject. Contradiction detected -> flag for review. Eval score below threshold -> reject.
**Validation:** Run extraction on known input; verify citations exist and are valid. Run with deliberately wrong citations; verify rejection.
**Evidence:** Synthesis result with provenance chain, eval scores.
**Owner:** AI-GPT-OSS-SYNTHESIS-CONTROLS.

### 11. Agentic Qwen2 Scope Runner (`tools/ai/agentic/runner.py`)
**Responsibility:** Execute Type A low-risk agentic tasks with strict scope enforcement.
**Inputs:** AgenticTask (extends TaskContract with path_allowlist, op_allowlist, state_machine_def).
**Outputs:** AgenticResult, scope violation log.
**Storage:** Task state in `.local/ai/agentic-state/`.
**Schemas:** AgenticTask, ScopeGuardConfig, TaskStateMachine, AgenticResult.
**Failure modes:** Scope violation -> immediate stop, discard output. State machine violation -> stop. Timeout -> stop. Output schema invalid -> reject.
**Validation:** Configure restricted scope; attempt out-of-scope file read; verify block. Attempt out-of-scope write; verify block. Test timeout enforcement.
**Evidence:** Scope violation log (should be empty on success), state machine trace.
**Owner:** AI-AGENTIC-QWEN2-CONTROLS.

### 12. Telemetry Manager (`tools/ai/telemetry/`)
**Responsibility:** Record every AI call, aggregate per-sprint, post to Agent Metrics.
**Inputs:** TelemetryRecord from gateway.
**Outputs:** Local spool entry, Agent Metrics row (when posting enabled).
**Storage:** `.local/ai/llm-logs/{sprint-id}.jsonl` (spool), `.local/ai/spool/posted.jsonl` (idempotency ledger).
**Schemas:** TelemetryRecord (30 fields), AgentMetricsRow (17 fields), PostResult.
**Agent Metrics field mapping:**
| Agent Metrics Field | Source | Aggregation |
|---|---|---|
| timestamp | Max timestamp in sprint | Per-sprint end time |
| agent_name | "format-factory-ai" | Static |
| agent_owner | "Babar Raza" | Static |
| job_type | Dominant model_role in sprint | Most frequent role |
| run_id | sprint_id + hash | Per-sprint |
| status | Worst status in sprint | success/partial/failure |
| product | "FormatFactory" | Static |
| platform | "Python" | Static |
| website | "N/A" | Not applicable |
| website_section | "N/A" | Not applicable |
| item_name | Operation type summary | "LLM calls" / "Embeddings" |
| items_discovered | Total AI calls attempted | Count |
| items_succeeded | Calls with status=success | Count |
| items_failed | Calls with status!=success | Count |
| run_duration_ms | Sprint wall-clock time | Timer |
| token_usage | Sum of total_token_count | Aggregate |
| api_calls_count | Sum of api_calls_count | Aggregate |
**Failure modes:** Spool write fails -> AI call reports as failed. Post fails -> retain in spool, retry later. Spool corrupted -> detect via line count validation, rebuild from raw logs if available.
**Validation:** Verify every AI call produces spool entry. Verify aggregation math. Verify post idempotency (same run_id not double-posted).
**Evidence:** Telemetry summary in evidence bundle, post success/failure log.
**Owner:** AI-TELEMETRY-AGENT-METRICS-INTEGRATION.

### 13. Evaluator/Regression Harness (`tools/ai/evals/`)
**Responsibility:** Run golden evals against synthesis outputs; detect quality degradation.
**Inputs:** SynthesisResult, golden eval fixtures.
**Outputs:** EvalResult (pass/fail, scores, comparison).
**Storage:** `tools/ai/evals/fixtures/{task_type}/` (committed golden data).
**Schemas:** EvalFixture, EvalResult, EvalThresholds.
**Failure modes:** No fixture for task type -> warn (eval skipped). Score below threshold -> reject output.
**Validation:** Run eval with known-good output; verify pass. Run with known-bad output; verify fail.
**Evidence:** Eval results in evidence bundle.
**Owner:** AI-RISK-MITIGATION-MATRIX.

### 14. Evidence Bundle Adapter (`tools/ai/evidence/adapter.py`)
**Responsibility:** Generate AI-specific metadata files for evidence bundles.
**Inputs:** Sprint telemetry, eval results, model discovery snapshot.
**Outputs:** Bundle metadata files (ai-telemetry-summary.md, ai-model-discovery.md, ai-eval-results.md).
**Storage:** Output to `bundle-metadata/` during bundle build.
**Failure modes:** Missing telemetry -> generate partial summary with gaps noted.
**Validation:** Build bundle after AI sprint; verify AI metadata files present and non-empty.
**Evidence:** Bundle validation report.
**Owner:** AI-PLATFORM-FOUNDATION-PLAN.

### 15. Runtime-AI Guard (`tools/ai/validators/runtime_guard.py`)
**Responsibility:** Static analysis ensuring src/ code never imports AI modules.
**Inputs:** Source directory paths to scan.
**Outputs:** Violation report (pass/fail with file:line details).
**Storage:** None.
**Blocked imports:** litellm, llama_index, lancedb, openai, anthropic, ollama, langchain, langgraph, tools.ai.
**Failure modes:** False positive (legitimate use of word "openai" in comment) -> exclude comments/strings from scan.
**Validation:** Add forbidden import to src/ test file; verify detection. Verify no false positives on existing code.
**Evidence:** Scan results in evidence bundle.
**Owner:** AI-PLATFORM-FOUNDATION-PLAN.
