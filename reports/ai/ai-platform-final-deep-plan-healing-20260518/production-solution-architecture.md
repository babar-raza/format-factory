# Production Solution Architecture

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-DEEP-PLAN-HEALING-001
**Date:** 2026-05-18
**Gate:** 5
**Lane:** L5

---

## 1. Architecture Principle

The AI platform is a **governed acceleration layer** with a single entry point, executable contracts, deterministic validation, and full telemetry. It sits between the existing project infrastructure (gates, evidence, taskcards) and external AI services (llm.professionalize.com). It does not replace any existing authority — it provides structured AI assistance that feeds into the existing authority model.

## 2. Component Registry (17 Components)

### Component 1: AI Gateway (`tools/ai/control_plane/gateway.py`)
- **Responsibility:** Single choke point for ALL AI calls
- **Inputs:** TaskContract, caller identity, sprint context
- **Outputs:** TaskResult with authority_state=ai_draft, telemetry record
- **Storage:** None (stateless coordinator)
- **Schemas:** TaskContract, TaskResult, GatewayConfig
- **Failure modes:** Endpoint unreachable → fail closed. Schema validation fails → reject. No qualified model → ROLE_UNAVAILABLE
- **Validation tests:** Import litellm outside tools/ai/ is detected. Direct endpoint calls blocked.
- **Evidence:** Gateway call log in telemetry spool
- **Owner:** AI-PLATFORM-FOUNDATION-PLAN

### Component 2: Model Discovery Service (`tools/ai/control_plane/model_discovery.py`)
- **Responsibility:** Enumerate models from llm.professionalize.com, probe capabilities, cache results
- **Inputs:** GPT_OSS_ENDPOINT env var
- **Outputs:** ModelRegistry
- **Storage:** `.local/ai/model-registry/models-{timestamp}.json` (cache, gitignored)
- **Schemas:** DiscoveredModel, ModelRegistry
- **Failure modes:** Endpoint unreachable → use cache if <24h. Cache expired + down → fail closed. Unexpected shape → fail closed
- **Validation tests:** Mock /v1/models response. Mock empty response. Mock changed model list
- **Evidence:** Model discovery snapshot in bundle metadata
- **Owner:** AI-MODEL-DISCOVERY-AND-ROUTING

### Component 3: Role-Based Model Router (`tools/ai/control_plane/model_router.py`)
- **Responsibility:** Select best model for role based on capability requirements
- **Inputs:** ModelRole, ModelRegistry, RoleRequirements
- **Outputs:** SelectedModel (model_id, was_fallback, alternatives_count)
- **Storage:** `tools/ai/contracts/roles.yaml`
- **Schemas:** ModelRole (enum), RoleRequirement, SelectedModel
- **Failure modes:** No model meets requirements → ROLE_UNAVAILABLE. Only fallback → warn + flag
- **Validation tests:** Each role against mock registries. Fail-closed when no model qualifies
- **Evidence:** Model selection log with decision trace
- **Owner:** AI-MODEL-DISCOVERY-AND-ROUTING

### Component 4: Task Contract Registry (`tools/ai/contracts/`)
- **Responsibility:** Define and validate task contracts
- **Inputs:** Task type, caller context
- **Outputs:** Validated TaskContract
- **Storage:** `tools/ai/contracts/tasks/` (YAML per task type)
- **Schemas:** TaskContract (see control-plane-contracts-and-state-model.md)
- **Failure modes:** Unknown task type → reject. Missing fields → reject. Schema mismatch → reject
- **Validation tests:** Load all contracts; verify schema validity. Test missing fields
- **Evidence:** Contract validation report
- **Owner:** AI-PLATFORM-FOUNDATION-PLAN

### Component 5: Prompt Registry (`tools/ai/prompts/`)
- **Responsibility:** Version and hash all prompt templates
- **Inputs:** Prompt template ID
- **Outputs:** Prompt text with version hash
- **Storage:** `tools/ai/prompts/{task_type}/v{N}.yaml`
- **Schemas:** PromptTemplate (template_id, version, content_hash, variables)
- **Failure modes:** Template not found → reject. Hash mismatch → reject
- **Validation tests:** Verify all hashes match content. Test hash verification
- **Evidence:** Prompt version hash in telemetry
- **Owner:** AI-PLATFORM-FOUNDATION-PLAN

### Component 6: Schema Registry (`tools/ai/schemas/`)
- **Responsibility:** Pydantic models for all AI inputs/outputs
- **Inputs:** Schema reference from task contract
- **Outputs:** Validated Pydantic model instance
- **Storage:** `tools/ai/schemas/` (Python modules)
- **Schemas:** All input/output schemas per task type
- **Failure modes:** Output doesn't match → reject. Extra fields → strip and warn. Missing required → reject
- **Validation tests:** Invalid outputs rejected. Valid outputs accepted
- **Evidence:** Schema validation results in telemetry
- **Owner:** AI-PLATFORM-FOUNDATION-PLAN

### Component 7: Artifact Authority Lifecycle Service (`tools/ai/validators/authority_lifecycle.py`)
- **Responsibility:** Track and enforce AI artifact state transitions
- **Inputs:** Artifact ID, current state, requested transition, evidence
- **Outputs:** Transition result (accepted/rejected)
- **Storage:** `.local/ai/artifact-states.jsonl` + artifact frontmatter
- **Schemas:** ArtifactAuthorityState (12 states), TransitionRequest, TransitionResult
- **Failure modes:** Invalid transition → reject. Missing evidence → reject
- **Validation tests:** Every invalid transition rejected. Every valid transition with evidence accepted
- **Evidence:** State transition log
- **Owner:** AI-PLATFORM-FOUNDATION-PLAN

### Component 8: Retrieval/Index Manager (`tools/ai/retrieval/`)
- **Responsibility:** Per-format vector stores: create, refresh, query, stale-detect
- **Inputs:** Format namespace, query text, index version
- **Outputs:** RetrievalResult (chunk_ids, scores, metadata, stale_flag)
- **Storage:** `.local/ai/vector-stores/{format}/` (LanceDB) + manifests
- **Schemas:** RetrievalQuery, RetrievalResult, ChunkManifest, IndexMetadata
- **Failure modes:** Index not found → fail. Stale → warn + flag. Embedding model unavailable → fail. Cross-namespace without flag → reject
- **Validation tests:** Namespace isolation. Stale detection. Rebuild verification
- **Evidence:** Retrieval audit log, index metadata
- **Owner:** AI-EMBEDDING-VECTOR-STORE-FOUNDATION

### Component 9: Spec Normalization Adapter (`tools/ai/normalization/adapter.py`)
- **Responsibility:** Bridge normalization output to AI input
- **Inputs:** Format ID, spec version
- **Outputs:** List of NormalizedChunk with provenance
- **Storage:** Reads from `.local/spec-cache/{format}/{version}/normalized/chunks.jsonl`
- **Schemas:** NormalizedChunk
- **Failure modes:** Normalization not found → fail. Format incompatible → fail
- **Validation tests:** Load FODS chunks with provenance. Missing normalization → clear error
- **Evidence:** Chunk manifest hash
- **Owner:** AI-SPEC-NORMALIZATION-INTEGRATION

### Component 10: LLM Synthesis Workflow Runner (`tools/ai/synthesis/runner.py`)
- **Responsibility:** Execute Type B synthesis tasks
- **Inputs:** SynthesisTask, retrieved context, prompt template
- **Outputs:** SynthesisResult with citations, authority_state=ai_draft
- **Storage:** Sprint-specific output paths
- **Schemas:** SynthesisTask, SynthesisResult, Citation, ContradictionCheckResult
- **Failure modes:** Schema fails → reject. No citations → reject. Contradiction → flag. Eval below threshold → reject
- **Validation tests:** Known input extraction with valid citations. Wrong citations rejected
- **Evidence:** Synthesis result with provenance chain
- **Owner:** AI-GPT-OSS-SYNTHESIS-CONTROLS

### Component 11: Agentic Qwen2 Scope Runner (`tools/ai/agentic/runner.py`)
- **Responsibility:** Execute Type A low-risk agentic tasks with strict scope
- **Inputs:** AgenticTask with path_allowlist, op_allowlist, state_machine_def
- **Outputs:** AgenticResult, scope violation log
- **Storage:** `.local/ai/agentic-state/`
- **Schemas:** AgenticTask, ScopeGuardConfig, TaskStateMachine, AgenticResult
- **Failure modes:** Scope violation → immediate stop, discard output. Timeout → stop. Schema invalid → reject
- **Validation tests:** Out-of-scope read blocked. Out-of-scope write blocked. Timeout enforced
- **Evidence:** Scope violation log (empty on success), state machine trace
- **Owner:** AI-AGENTIC-QWEN2-CONTROLS

### Component 12: Telemetry Manager (`tools/ai/telemetry/`)
- **Responsibility:** Record every AI call, aggregate per-sprint, post to Agent Metrics
- **Inputs:** TelemetryRecord from gateway
- **Outputs:** Local spool entry, Agent Metrics row
- **Storage:** `.local/ai/llm-logs/` (spool) + `.local/ai/spool/posted.jsonl` (ledger)
- **Schemas:** TelemetryRecord (30 fields), AgentMetricsRow (17 fields)
- **Failure modes:** Spool write fails → AI call reports failed. Post fails → retain spool. Corruption → skip corrupt lines
- **Validation tests:** Every call produces spool entry. Aggregation math correct. Idempotency verified
- **Evidence:** Telemetry summary, post log
- **Owner:** AI-TELEMETRY-AGENT-METRICS-INTEGRATION

### Component 13: Evaluator/Regression Harness (`tools/ai/evals/`)
- **Responsibility:** Golden evals against synthesis outputs; detect quality degradation
- **Inputs:** SynthesisResult, golden eval fixtures
- **Outputs:** EvalResult (pass/fail, scores)
- **Storage:** `tools/ai/evals/fixtures/{task_type}/`
- **Schemas:** EvalFixture, EvalResult, EvalThresholds
- **Failure modes:** No fixture → warn (eval skipped). Below threshold → reject
- **Validation tests:** Known-good output passes. Known-bad output fails
- **Evidence:** Eval results in bundle
- **Owner:** AI-RISK-MITIGATION-MATRIX

### Component 14: Evidence Bundle Adapter (`tools/ai/evidence/adapter.py`)
- **Responsibility:** Generate AI-specific metadata for evidence bundles
- **Inputs:** Sprint telemetry, eval results, model discovery snapshot
- **Outputs:** Bundle metadata files
- **Storage:** Output to `bundle-metadata/`
- **Failure modes:** Missing telemetry → partial summary with gaps noted
- **Validation tests:** Bundle after AI sprint has AI metadata files
- **Evidence:** Bundle validation report
- **Owner:** AI-PLATFORM-FOUNDATION-PLAN

### Component 15: Runtime-AI Guard (`tools/ai/validators/runtime_guard.py`)
- **Responsibility:** Static analysis ensuring src/ code never imports AI modules
- **Inputs:** Source directory paths
- **Outputs:** Violation report (pass/fail with file:line)
- **Storage:** None
- **Blocked imports:** litellm, llama_index, lancedb, openai, anthropic, ollama, langchain, langgraph, tools.ai
- **Failure modes:** False positive → exclude comments/strings
- **Validation tests:** Forbidden import in src/ detected. No false positives on existing code
- **Evidence:** Scan results in bundle
- **Owner:** AI-PLATFORM-FOUNDATION-PLAN

### Component 16: Local Spool/Replay Manager (`tools/ai/telemetry/spool_manager.py`)
- **Responsibility:** Manage offline spool, replay ledger, spool drain, expiry
- **Inputs:** TelemetryRecords, spool configuration
- **Outputs:** Spool status, drain results
- **Storage:** `.local/ai/spool/`
- **Schemas:** SpoolEntry, SpoolStatus, DrainResult
- **Failure modes:** Spool file locked → wait + retry. Corrupt lines → skip + log. Full disk → fail call
- **Validation tests:** Offline accumulation. Drain on reconnect. Expiry after 7 days
- **Evidence:** Spool status in bundle
- **Owner:** AI-TELEMETRY-AGENT-METRICS-INTEGRATION

### Component 17: Citation Verifier (`tools/ai/synthesis/citation_verifier.py`)
- **Responsibility:** Verify that cited chunk_ids support claims in synthesis output
- **Inputs:** SynthesisResult, normalized chunk cache
- **Outputs:** CitationVerificationResult (per-claim scores, aggregate)
- **Storage:** None
- **Schemas:** CitationClaim, VerificationScore
- **Failure modes:** Chunk not found → reject claim. No support → reject. Partial support → flag
- **Validation tests:** Correct citations pass. Wrong citations rejected. Missing chunks fail
- **Evidence:** Verification report
- **Owner:** AI-GPT-OSS-SYNTHESIS-CONTROLS
