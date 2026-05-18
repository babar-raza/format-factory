# AI Risk Register and Control Matrix

**Version:** 1.0
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized
**Authority:** docs/ai/ai-platform-operating-model.md

---

## 1. Purpose

Comprehensive risk register for all AI/LLM/Embedding operations in Format Factory. Each risk has identification, controls, validation, and stop conditions.

## 2. Risk Matrix

### RISK-AI-001: Model Availability Drift

| Field | Value |
|-------|-------|
| **Description** | llm.professionalize.com removes or renames a model the pipeline depends on |
| **Affected Layer** | Control Plane — Model Discovery |
| **Severity** | HIGH |
| **Likelihood** | MEDIUM — endpoint is actively maintained |
| **Detection** | Model discovery returns different model list than previous run |
| **Prevention** | Role-based routing (not hardcoded model names); model discovery on every invocation |
| **Mitigation** | Fail closed when required role capability unavailable; log ROLE_UNAVAILABLE |
| **Validation Test** | Simulate model removal; verify pipeline stops cleanly |
| **Evidence Artifact** | Model discovery diff in telemetry |
| **Owner/Taskcard** | AI-MODEL-DISCOVERY-AND-ROUTING |
| **Stop Condition** | If no model meets minimum for ANY required role: pipeline cannot proceed |

### RISK-AI-002: Model Behavior Drift

| Field | Value |
|-------|-------|
| **Description** | Model produces different quality outputs after provider update |
| **Affected Layer** | Synthesis, Agentic |
| **Severity** | HIGH |
| **Likelihood** | MEDIUM |
| **Detection** | Golden eval regression; output quality metrics degradation |
| **Prevention** | Model fingerprint tracking; regression eval on model change |
| **Mitigation** | Fallback to previous known-good model if available; pause pipeline |
| **Validation Test** | Run golden evals after model fingerprint change |
| **Evidence Artifact** | Eval regression report |
| **Owner/Taskcard** | AI-GPT-OSS-SYNTHESIS-CONTROLS |
| **Stop Condition** | If eval score drops >20% from baseline: stop synthesis tasks |

### RISK-AI-003: Endpoint API Shape Changes

| Field | Value |
|-------|-------|
| **Description** | llm.professionalize.com changes API response format or endpoints |
| **Affected Layer** | Control Plane |
| **Severity** | HIGH |
| **Likelihood** | LOW |
| **Detection** | Capability probe returns unexpected schema; HTTP errors |
| **Prevention** | LiteLLM abstraction layer; schema validation on API responses |
| **Mitigation** | Fail closed; log endpoint shape change; human investigation |
| **Validation Test** | Mock API shape change; verify graceful failure |
| **Evidence Artifact** | Endpoint probe failure log |
| **Owner/Taskcard** | AI-MODEL-DISCOVERY-AND-ROUTING |
| **Stop Condition** | If API shape change affects >1 role: pause all AI operations |

### RISK-AI-004: Model Auto-Selection Choosing Wrong Model

| Field | Value |
|-------|-------|
| **Description** | Role-based routing selects a model that technically meets criteria but produces poor results |
| **Affected Layer** | Control Plane — Model Router |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Eval scores for routed model below threshold |
| **Prevention** | Capability probing includes quality benchmarks, not just feature flags |
| **Mitigation** | Override routing with explicit model preference per role; human review |
| **Validation Test** | Benchmark each discovered model against golden evals for each role |
| **Evidence Artifact** | Model benchmark comparison |
| **Owner/Taskcard** | AI-MODEL-DISCOVERY-AND-ROUTING |
| **Stop Condition** | If auto-selected model fails >30% of golden evals: override required |

### RISK-AI-005: Fallback Model Silently Changing Output Quality

| Field | Value |
|-------|-------|
| **Description** | Pipeline falls back to secondary model without user awareness of quality impact |
| **Affected Layer** | Synthesis, Agentic |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | `fallback_model_used: true` in telemetry; evidence bundle flag |
| **Prevention** | Fallback logged prominently; evidence bundle notes fallback usage |
| **Mitigation** | Human review of fallback outputs; re-run with preferred model when available |
| **Validation Test** | Trigger fallback; verify telemetry and evidence capture |
| **Evidence Artifact** | Fallback usage report in evidence bundle |
| **Owner/Taskcard** | AI-MODEL-DISCOVERY-AND-ROUTING |
| **Stop Condition** | If fallback model quality < 70% of primary: fail closed instead |

### RISK-AI-006: Hallucinated Requirements

| Field | Value |
|-------|-------|
| **Description** | LLM generates requirements not supported by source spec |
| **Affected Layer** | Synthesis |
| **Severity** | CRITICAL |
| **Likelihood** | HIGH — inherent LLM behavior |
| **Detection** | Source-support verifier finds no backing for cited chunk; contradiction detector flags |
| **Prevention** | Mandatory citation; source-support verification; artifact authority lifecycle |
| **Mitigation** | Reject output; flag as hallucination; human review |
| **Validation Test** | Inject known-hallucinated output; verify rejection |
| **Evidence Artifact** | Hallucination rejection log |
| **Owner/Taskcard** | AI-GPT-OSS-SYNTHESIS-CONTROLS |
| **Stop Condition** | If hallucination rate > 10% per batch: pause synthesis, review prompt |

### RISK-AI-007: Source-Citation Mismatch

| Field | Value |
|-------|-------|
| **Description** | LLM cites a chunk ID but the claim is not supported by that chunk |
| **Affected Layer** | Synthesis |
| **Severity** | HIGH |
| **Likelihood** | MEDIUM |
| **Detection** | Source-support verifier |
| **Prevention** | Citation verification mandatory before any output acceptance |
| **Mitigation** | Reject claim; log mismatch; investigate pattern |
| **Validation Test** | Provide output with incorrect citations; verify rejection |
| **Evidence Artifact** | Citation verification report |
| **Owner/Taskcard** | AI-GPT-OSS-SYNTHESIS-CONTROLS |
| **Stop Condition** | If >20% citations fail verification in a batch: stop and review |

### RISK-AI-008: Retrieval Missing Relevant Spec Chunks

| Field | Value |
|-------|-------|
| **Description** | Vector retrieval returns results that miss the most relevant spec sections |
| **Affected Layer** | Retrieval |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Manual spot-check against known-relevant chunks; recall evaluation |
| **Prevention** | Retrieval eval suite with known query-answer pairs |
| **Mitigation** | Increase top-K; improve chunking strategy; add keyword pre-filter |
| **Validation Test** | Golden retrieval test set per format |
| **Evidence Artifact** | Retrieval recall metrics |
| **Owner/Taskcard** | AI-EMBEDDING-VECTOR-STORE-FOUNDATION |
| **Stop Condition** | If recall < 60% on golden set: do not use for synthesis input |

### RISK-AI-009: Irrelevant Vector Retrieval

| Field | Value |
|-------|-------|
| **Description** | Retrieval returns chunks that are syntactically similar but semantically irrelevant |
| **Affected Layer** | Retrieval |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Precision evaluation on golden set; synthesis output quality degradation |
| **Prevention** | Metadata filtering; minimum similarity threshold |
| **Mitigation** | Add re-ranking step; tighter similarity threshold; better chunking |
| **Validation Test** | Golden precision test set per format |
| **Evidence Artifact** | Retrieval precision metrics |
| **Owner/Taskcard** | AI-EMBEDDING-VECTOR-STORE-FOUNDATION |
| **Stop Condition** | If precision < 50% on golden set: review chunking and embedding model |

### RISK-AI-010: Stale Embeddings

| Field | Value |
|-------|-------|
| **Description** | Spec updated but vector index not refreshed; retrieval returns outdated chunks |
| **Affected Layer** | Retrieval |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Stale-index detector (source hash mismatch) |
| **Prevention** | Automatic stale detection on every retrieval; source hash comparison |
| **Mitigation** | Flag results as potentially_stale; trigger refresh |
| **Validation Test** | Modify source; verify stale detection triggers |
| **Evidence Artifact** | Stale index warning in telemetry |
| **Owner/Taskcard** | AI-EMBEDDING-VECTOR-STORE-FOUNDATION |
| **Stop Condition** | If stale index used for gate evidence: evidence is INVALID |

### RISK-AI-011: Cross-Format Vector Contamination

| Field | Value |
|-------|-------|
| **Description** | Chunks from one format appear in another format's retrieval results |
| **Affected Layer** | Retrieval |
| **Severity** | HIGH |
| **Likelihood** | LOW (if namespaces enforced) |
| **Detection** | Namespace isolation test; retrieval audit log review |
| **Prevention** | Format namespace isolation in LanceDB; no implicit cross-namespace queries |
| **Mitigation** | Rebuild contaminated index; review indexing code |
| **Validation Test** | Query format A namespace; verify zero results from format B |
| **Evidence Artifact** | Namespace isolation test results |
| **Owner/Taskcard** | AI-EMBEDDING-VECTOR-STORE-FOUNDATION |
| **Stop Condition** | If contamination detected: halt all retrieval until isolation verified |

### RISK-AI-012: Vector Store Corruption

| Field | Value |
|-------|-------|
| **Description** | LanceDB files corrupted on disk; retrieval returns errors or wrong results |
| **Affected Layer** | Retrieval |
| **Severity** | MEDIUM |
| **Likelihood** | LOW |
| **Detection** | LanceDB read errors; checksum validation failure |
| **Prevention** | Manifest hash validation; periodic integrity checks |
| **Mitigation** | Rebuild index from source; log corruption event |
| **Validation Test** | Corrupt index file; verify detection and rebuild |
| **Evidence Artifact** | Corruption detection and rebuild log |
| **Owner/Taskcard** | AI-EMBEDDING-VECTOR-STORE-FOUNDATION |
| **Stop Condition** | If corruption detected: rebuild before any retrieval |

### RISK-AI-013: Prompt Drift

| Field | Value |
|-------|-------|
| **Description** | Prompt templates modified without version tracking; output quality changes silently |
| **Affected Layer** | Synthesis, Agentic |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Prompt version hash change in telemetry; regression eval |
| **Prevention** | Prompt registry with immutable versioned templates |
| **Mitigation** | Regression eval on prompt change; rollback to previous version |
| **Validation Test** | Modify prompt; verify hash change detected and eval triggered |
| **Evidence Artifact** | Prompt version change log |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | If prompt change causes >15% eval degradation: revert |

### RISK-AI-014: Schema Drift

| Field | Value |
|-------|-------|
| **Description** | Output schemas evolve without backward compatibility; downstream consumers break |
| **Affected Layer** | All |
| **Severity** | MEDIUM |
| **Likelihood** | LOW |
| **Detection** | Schema validation failures in downstream consumers |
| **Prevention** | Schema registry with version control; breaking change review |
| **Mitigation** | Schema migration path; versioned consumers |
| **Validation Test** | Change schema; verify downstream compatibility check runs |
| **Evidence Artifact** | Schema version history |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | N/A — schema changes are planned operations |

### RISK-AI-015: Output Parser Fragility

| Field | Value |
|-------|-------|
| **Description** | LLM output slightly deviates from expected format; parser fails |
| **Affected Layer** | Synthesis |
| **Severity** | LOW |
| **Likelihood** | HIGH |
| **Detection** | Schema validation failure; parser exception |
| **Prevention** | JSON mode enforcement; Pydantic validation with clear error messages |
| **Mitigation** | Structured output mode; retry once; if still fails, reject |
| **Validation Test** | Feed malformed output; verify graceful failure |
| **Evidence Artifact** | Parse failure log |
| **Owner/Taskcard** | AI-GPT-OSS-SYNTHESIS-CONTROLS |
| **Stop Condition** | If parse failure rate > 30%: investigate model or prompt |

### RISK-AI-016: Telemetry Loss

| Field | Value |
|-------|-------|
| **Description** | AI calls complete but telemetry records lost (disk full, write error) |
| **Affected Layer** | Telemetry |
| **Severity** | MEDIUM |
| **Likelihood** | LOW |
| **Detection** | Gap in telemetry sequence; missing records in evidence |
| **Prevention** | Write telemetry before returning result; verify write success |
| **Mitigation** | Reconstruct from API call logs if available; flag gap in evidence |
| **Validation Test** | Simulate disk write failure; verify telemetry loss detected |
| **Evidence Artifact** | Telemetry gap report |
| **Owner/Taskcard** | AI-TELEMETRY-AGENT-METRICS-INTEGRATION |
| **Stop Condition** | N/A — telemetry loss does not stop pipeline but must be reported |

### RISK-AI-017: Agent Metrics Post Failure

| Field | Value |
|-------|-------|
| **Description** | Cannot reach Agent Metrics; telemetry accumulates locally |
| **Affected Layer** | Telemetry |
| **Severity** | LOW |
| **Likelihood** | MEDIUM |
| **Detection** | `posted_to_agent_metrics: false` in records; spool growth |
| **Prevention** | Offline spool with retry policy |
| **Mitigation** | Drain spool on next successful connection; spool expiry after 7 days |
| **Validation Test** | Block Agent Metrics; verify spool accumulation and drain |
| **Evidence Artifact** | Spool status in evidence bundle |
| **Owner/Taskcard** | AI-TELEMETRY-AGENT-METRICS-INTEGRATION |
| **Stop Condition** | N/A — local JSONL provides backup |

### RISK-AI-018: Secret Leakage

| Field | Value |
|-------|-------|
| **Description** | API keys or credentials appear in logs, telemetry, evidence, or committed files |
| **Affected Layer** | All |
| **Severity** | CRITICAL |
| **Likelihood** | LOW (if controls followed) |
| **Detection** | Secret scanner in pre-commit; telemetry field review |
| **Prevention** | Keys in .env only; endpoint_identity strips auth; no secrets in telemetry schema |
| **Mitigation** | Rotate compromised key immediately; scrub from history |
| **Validation Test** | Attempt to log with secret in field; verify rejection |
| **Evidence Artifact** | Secret scan results |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | If secret detected in committed file: IMMEDIATE remediation |

### RISK-AI-019: Runtime Package Importing AI Layer

| Field | Value |
|-------|-------|
| **Description** | Product code in `src/` accidentally imports tools/ai or AI framework modules |
| **Affected Layer** | Runtime Isolation |
| **Severity** | HIGH |
| **Likelihood** | LOW (if guard enforced) |
| **Detection** | Runtime guard static analysis; import scanning |
| **Prevention** | `tools/ai/validators/runtime_guard.py` runs in CI |
| **Mitigation** | Remove import; fix dependency |
| **Validation Test** | Add AI import to src/ file; verify guard catches it |
| **Evidence Artifact** | Runtime guard scan results |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | If guard fails: block commit/merge |

### RISK-AI-020: AI Output Becoming Authority

| Field | Value |
|-------|-------|
| **Description** | AI-generated artifact treated as authoritative without passing lifecycle gates |
| **Affected Layer** | All |
| **Severity** | CRITICAL |
| **Likelihood** | MEDIUM |
| **Detection** | Authority lifecycle enforcement; artifact state tracking |
| **Prevention** | All AI output starts as ai_draft; no skip in lifecycle |
| **Mitigation** | Revert authority claim; re-validate through lifecycle |
| **Validation Test** | Attempt to mark ai_draft as authoritative; verify rejection |
| **Evidence Artifact** | Authority state transition log |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | If unvalidated AI output found in authority files: IMMEDIATE review |

### RISK-AI-021: Agentic Qwen2 Exceeding Task Scope

| Field | Value |
|-------|-------|
| **Description** | Qwen2 agent accesses files or performs operations outside its allowlist |
| **Affected Layer** | Agentic |
| **Severity** | HIGH |
| **Likelihood** | MEDIUM |
| **Detection** | Scope monitor; file access audit |
| **Prevention** | Path allowlist enforcement; operation allowlist; scope guard |
| **Mitigation** | Stop agent immediately; discard output; log violation |
| **Validation Test** | Configure agent with restricted scope; attempt out-of-scope access |
| **Evidence Artifact** | Scope violation log |
| **Owner/Taskcard** | AI-AGENTIC-QWEN2-CONTROLS |
| **Stop Condition** | If scope violation detected: stop agent, reject all output |

### RISK-AI-022: Direct Endpoint Call Bypassing Gateway

| Field | Value |
|-------|-------|
| **Description** | Code calls llm.professionalize.com directly instead of through the AI platform layer |
| **Affected Layer** | All |
| **Severity** | HIGH |
| **Likelihood** | MEDIUM |
| **Detection** | Import scanning; code review; endpoint URL grep |
| **Prevention** | All AI calls through tools/ai/ only; static analysis enforcement |
| **Mitigation** | Refactor to use platform layer; add to import blocklist |
| **Validation Test** | Scan for direct endpoint imports outside tools/ai/ |
| **Evidence Artifact** | Gateway bypass scan results |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | If bypass detected: block until refactored |

### RISK-AI-023: Cost/Token Analytics Missing

| Field | Value |
|-------|-------|
| **Description** | Token usage and costs not tracked; budget overruns undetected |
| **Affected Layer** | Telemetry |
| **Severity** | MEDIUM |
| **Likelihood** | LOW (if telemetry implemented) |
| **Detection** | Missing token_count fields in telemetry; Agent Metrics gap |
| **Prevention** | Mandatory token count fields in every telemetry record |
| **Mitigation** | Reconstruct from API provider usage dashboard |
| **Validation Test** | Verify all telemetry records have non-zero token counts |
| **Evidence Artifact** | Token usage summary in evidence bundle |
| **Owner/Taskcard** | AI-TELEMETRY-AGENT-METRICS-INTEGRATION |
| **Stop Condition** | N/A — tracking gap, not safety issue |

### RISK-AI-024: Nondeterministic Reruns

| Field | Value |
|-------|-------|
| **Description** | Same inputs produce different outputs across reruns (expected for LLMs but must be managed) |
| **Affected Layer** | Synthesis, Retrieval |
| **Severity** | MEDIUM |
| **Likelihood** | HIGH — inherent LLM behavior |
| **Detection** | Replay manifest comparison; output hash differences |
| **Prevention** | Temperature=0 where possible; seed parameters; replay manifests |
| **Mitigation** | Accept nondeterminism but require golden eval pass on each run |
| **Validation Test** | Run same pipeline twice; compare outputs; verify both pass evals |
| **Evidence Artifact** | Replay comparison report |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | N/A — managed through eval gates, not prevented |

### RISK-AI-025: Stale Local Cache Reuse

| Field | Value |
|-------|-------|
| **Description** | Cached LLM responses reused after input changes; stale output treated as current |
| **Affected Layer** | Synthesis |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Input hash comparison; cache key validation |
| **Prevention** | Cache keyed on input hash + model fingerprint + prompt version |
| **Mitigation** | Cache invalidation on any key component change |
| **Validation Test** | Change input; verify cache miss and fresh call |
| **Evidence Artifact** | Cache hit/miss statistics |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | If stale cache used for gate evidence: evidence INVALID |

### RISK-AI-026: Evidence Bundle Missing AI Artifacts

| Field | Value |
|-------|-------|
| **Description** | Evidence bundle built without including AI telemetry, provenance, or validation results |
| **Affected Layer** | Evidence |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Evidence bundle validation checks for AI artifact presence |
| **Prevention** | Bundle builder checks for AI artifacts when AI was used in sprint |
| **Mitigation** | Rebuild bundle with missing artifacts |
| **Validation Test** | Build bundle after AI sprint; verify AI artifacts present |
| **Evidence Artifact** | Bundle validation report |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | If AI artifacts missing from bundle: rebuild required |

### RISK-AI-027: Taskcard State Mismatch

| Field | Value |
|-------|-------|
| **Description** | AI task completes but taskcard not updated; state drift between actual and recorded |
| **Affected Layer** | Control Plane |
| **Severity** | LOW |
| **Likelihood** | MEDIUM |
| **Detection** | Consistency check between AI task state and taskcard status |
| **Prevention** | Task state machine updates taskcard as part of state transition |
| **Mitigation** | Manual taskcard sync; consistency checker |
| **Validation Test** | Complete task; verify taskcard auto-updated |
| **Evidence Artifact** | Taskcard state history |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | N/A — administrative gap, not safety issue |

### RISK-AI-028: Generated Tests Low Quality/Noisy

| Field | Value |
|-------|-------|
| **Description** | AI-generated tests are trivial, redundant, or test wrong behavior |
| **Affected Layer** | Test Generation |
| **Severity** | MEDIUM |
| **Likelihood** | HIGH |
| **Detection** | Test review gate; coverage analysis; mutation testing |
| **Prevention** | Test ideas cite requirements; deterministic reviewer filters quality |
| **Mitigation** | Reject low-quality tests; refine prompt; human review |
| **Validation Test** | Generate tests; verify reviewer filters catch trivial tests |
| **Evidence Artifact** | Test generation quality report |
| **Owner/Taskcard** | AI-TEST-GENERATION-INTEGRATION |
| **Stop Condition** | If >50% generated tests rejected by reviewer: review prompt strategy |

### RISK-AI-029: Source Generation Before Verified Requirements

| Field | Value |
|-------|-------|
| **Description** | AI generates code from requirements that have not completed verification lifecycle |
| **Affected Layer** | Synthesis |
| **Severity** | CRITICAL |
| **Likelihood** | MEDIUM |
| **Detection** | Requirement authority state check before code generation |
| **Prevention** | Code generation gated on requirement state >= accepted_for_source_requirements |
| **Mitigation** | Reject code generated from unverified requirements |
| **Validation Test** | Attempt code gen from ai_draft requirement; verify rejection |
| **Evidence Artifact** | Requirement state gate log |
| **Owner/Taskcard** | AI-GPT-OSS-SYNTHESIS-CONTROLS |
| **Stop Condition** | If unverified requirements used for code: code is INVALID |

### RISK-AI-030: Package/Release Decision Influenced by Unverified AI

| Field | Value |
|-------|-------|
| **Description** | Release readiness or package publication decision based on AI analysis that was not validated |
| **Affected Layer** | All |
| **Severity** | CRITICAL |
| **Likelihood** | LOW |
| **Detection** | Release checklist requires human verification of all AI inputs |
| **Prevention** | No AI output may influence release without authority lifecycle completion |
| **Mitigation** | Revert release decision; re-validate |
| **Validation Test** | Verify release checklist blocks on unverified AI inputs |
| **Evidence Artifact** | Release readiness verification log |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | If release based on unverified AI: IMMEDIATE halt |

### RISK-AI-031: Framework Lock-In

| Field | Value |
|-------|-------|
| **Description** | Deep dependency on LiteLLM/LlamaIndex/LanceDB makes replacement costly |
| **Affected Layer** | All |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Dependency audit; abstraction layer coverage review |
| **Prevention** | Wrap frameworks behind project abstractions; minimize direct API surface |
| **Mitigation** | Replacement feasibility assessment; abstraction thickening |
| **Validation Test** | Count direct framework imports outside wrapper modules |
| **Evidence Artifact** | Dependency audit report |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | N/A — managed through abstraction, not prevented |

### RISK-AI-032: Dependency/Version Drift

| Field | Value |
|-------|-------|
| **Description** | AI framework versions drift across environments; behavior differences |
| **Affected Layer** | All |
| **Severity** | LOW |
| **Likelihood** | MEDIUM |
| **Detection** | Version pinning in requirements; CI environment check |
| **Prevention** | Pin all AI framework versions in requirements.txt/pyproject.toml |
| **Mitigation** | Sync versions; rebuild .venv |
| **Validation Test** | Compare installed versions against pinned versions |
| **Evidence Artifact** | Dependency version report |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | N/A — operational hygiene |

### RISK-AI-033: .venv Environment Drift

| Field | Value |
|-------|-------|
| **Description** | Local .venv diverges from expected state; AI tools behave differently |
| **Affected Layer** | All |
| **Severity** | LOW |
| **Likelihood** | MEDIUM |
| **Detection** | Environment fingerprint comparison; pip freeze diff |
| **Prevention** | Environment setup script; version pinning; documentation |
| **Mitigation** | Rebuild .venv from pinned requirements |
| **Validation Test** | Fresh .venv build; verify all AI tools functional |
| **Evidence Artifact** | Environment setup log |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | N/A — operational hygiene |

### RISK-AI-034: Local Vector DB Not Reproducible

| Field | Value |
|-------|-------|
| **Description** | Vector index cannot be recreated from source; lost if disk fails |
| **Affected Layer** | Retrieval |
| **Severity** | MEDIUM |
| **Likelihood** | LOW |
| **Detection** | Rebuild test from manifest; compare against existing index |
| **Prevention** | Source/chunk manifests tracked; rebuild script documented |
| **Mitigation** | Rebuild from normalized spec artifacts + manifest |
| **Validation Test** | Delete index; rebuild; verify retrieval results match |
| **Evidence Artifact** | Rebuild comparison report |
| **Owner/Taskcard** | AI-EMBEDDING-VECTOR-STORE-FOUNDATION |
| **Stop Condition** | N/A — rebuild always possible from source |

### RISK-AI-035: Embedding Model Dimension Change

| Field | Value |
|-------|-------|
| **Description** | New embedding model version produces different dimension count; existing indexes incompatible |
| **Affected Layer** | Retrieval |
| **Severity** | HIGH |
| **Likelihood** | LOW |
| **Detection** | Dimension stability check during model discovery |
| **Prevention** | Dimension check before any embedding operation |
| **Mitigation** | Rebuild all indexes with new model; or continue with old model |
| **Validation Test** | Simulate dimension change; verify rebuild triggered |
| **Evidence Artifact** | Dimension change detection log |
| **Owner/Taskcard** | AI-EMBEDDING-VECTOR-STORE-FOUNDATION |
| **Stop Condition** | If dimension mismatch detected: no retrieval until resolved |

### RISK-AI-036: Data Retention/Privacy Concern

| Field | Value |
|-------|-------|
| **Description** | Spec content sent to remote endpoint; retention/privacy unclear |
| **Affected Layer** | Synthesis |
| **Severity** | HIGH |
| **Likelihood** | MEDIUM |
| **Detection** | Input content review; endpoint privacy policy audit |
| **Prevention** | Local-first processing; normalized artifacts only; spec content rules |
| **Mitigation** | Switch to local models for sensitive content |
| **Validation Test** | Verify no raw spec PDFs sent to remote endpoints |
| **Evidence Artifact** | Content transmission audit |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | If unauthorized spec transmission detected: stop remote calls |

### RISK-AI-037: Large-Context Prompt Truncation

| Field | Value |
|-------|-------|
| **Description** | Input exceeds model context window; truncated without warning |
| **Affected Layer** | Synthesis |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Token count check before call; compare input tokens vs context window |
| **Prevention** | Pre-call token count validation; chunked processing for large inputs |
| **Mitigation** | Split input; process in chunks; merge outputs |
| **Validation Test** | Send oversized input; verify graceful chunking |
| **Evidence Artifact** | Token overflow handling log |
| **Owner/Taskcard** | AI-GPT-OSS-SYNTHESIS-CONTROLS |
| **Stop Condition** | N/A — handled by chunking |

### RISK-AI-038: Prompt Injection from Specs/Samples

| Field | Value |
|-------|-------|
| **Description** | Malicious content in spec files or samples manipulates LLM behavior |
| **Affected Layer** | Synthesis, Agentic |
| **Severity** | HIGH |
| **Likelihood** | LOW |
| **Detection** | Output validation; unexpected behavior patterns; security review |
| **Prevention** | Input sanitization; structured prompts with clear boundaries; output validation |
| **Mitigation** | Reject suspicious output; flag for security review |
| **Validation Test** | Include injection attempt in test input; verify output unaffected |
| **Evidence Artifact** | Injection test results |
| **Owner/Taskcard** | AI-RISK-MITIGATION-MATRIX |
| **Stop Condition** | If injection successful: stop processing that input source |

### RISK-AI-039: Malicious Sample Content Influencing AI

| Field | Value |
|-------|-------|
| **Description** | Format sample files contain adversarial content that biases AI analysis |
| **Affected Layer** | Synthesis |
| **Severity** | MEDIUM |
| **Likelihood** | LOW |
| **Detection** | Sample provenance verification; output anomaly detection |
| **Prevention** | Samples from trusted sources only; content review before AI processing |
| **Mitigation** | Exclude suspicious samples; re-run with clean samples |
| **Validation Test** | Include adversarial sample; verify detection |
| **Evidence Artifact** | Sample provenance report |
| **Owner/Taskcard** | AI-RISK-MITIGATION-MATRIX |
| **Stop Condition** | If adversarial sample detected: exclude and re-analyze |

### RISK-AI-040: LLM Evaluation False Confidence

| Field | Value |
|-------|-------|
| **Description** | Eval suite passes but does not actually test the failure modes that matter |
| **Affected Layer** | All |
| **Severity** | HIGH |
| **Likelihood** | MEDIUM |
| **Detection** | Eval suite coverage review; adversarial eval additions |
| **Prevention** | Diverse eval suite including edge cases and adversarial examples |
| **Mitigation** | Continuously expand eval suite; human review of eval relevance |
| **Validation Test** | Review eval suite for coverage gaps; add missing cases |
| **Evidence Artifact** | Eval coverage analysis |
| **Owner/Taskcard** | AI-RISK-MITIGATION-MATRIX |
| **Stop Condition** | N/A — continuous improvement |

### RISK-AI-041: Qwen2 Produces Structurally Valid but Semantically Wrong Output

| Field | Value |
|-------|-------|
| **Description** | Qwen2 agentic output passes schema validation but is semantically incorrect (e.g., misclassifies a format, wrong sorting order) |
| **Affected Layer** | Agentic |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Spot-check against known-correct answers; semantic eval suite |
| **Prevention** | Golden eval for each agentic task type; minimum accuracy threshold |
| **Mitigation** | Reject output; escalate to GPT-OSS or human |
| **Validation Test** | Provide known-answer task; verify output matches |
| **Evidence Artifact** | Semantic accuracy test results |
| **Owner/Taskcard** | AI-AGENTIC-QWEN2-CONTROLS |
| **Stop Condition** | If semantic accuracy < 80%: stop Qwen2 for that task type |

### RISK-AI-042: GPT-OSS Produces Plausible but Factually Wrong Requirements

| Field | Value |
|-------|-------|
| **Description** | GPT-OSS synthesis generates requirements that sound correct and pass schema validation but do not match the actual spec content |
| **Affected Layer** | Synthesis |
| **Severity** | HIGH |
| **Likelihood** | MEDIUM |
| **Detection** | Source-support verifier; human spot-check of cited sections |
| **Prevention** | Mandatory citation with source-support verification; contradiction detector |
| **Mitigation** | Reject requirement; flag as plausible-hallucination; human review |
| **Validation Test** | Compare generated requirements against manually extracted requirements |
| **Evidence Artifact** | Requirement accuracy comparison report |
| **Owner/Taskcard** | AI-GPT-OSS-SYNTHESIS-CONTROLS |
| **Stop Condition** | If >15% of requirements fail source-support verification: stop and review prompt |

### RISK-AI-043: Schema-Valid Output Contains Unsupported Claims

| Field | Value |
|-------|-------|
| **Description** | AI output conforms to schema but includes claims not supported by any input source |
| **Affected Layer** | Synthesis, Agentic |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Source-citation completeness check; unsupported-claim scanner |
| **Prevention** | Every factual field in output schema requires citation; fields without citations flagged |
| **Mitigation** | Strip unsupported claims; flag for human review |
| **Validation Test** | Submit output with uncited claims; verify scanner detects them |
| **Evidence Artifact** | Unsupported claim detection log |
| **Owner/Taskcard** | AI-GPT-OSS-SYNTHESIS-CONTROLS |
| **Stop Condition** | If >20% of claims unsupported: reject entire output |

### RISK-AI-044: Contradiction with Existing Verified Facts Not Detected

| Field | Value |
|-------|-------|
| **Description** | AI output contradicts facts already in verified-facts.yaml but contradiction detector misses it |
| **Affected Layer** | Synthesis |
| **Severity** | MEDIUM |
| **Likelihood** | LOW-MEDIUM |
| **Detection** | Manual cross-reference; contradiction detector regression tests |
| **Prevention** | Contradiction detector tested against known-contradiction dataset |
| **Mitigation** | Expand contradiction test set; add missed case; re-validate output |
| **Validation Test** | Inject known contradictions; verify detection rate |
| **Evidence Artifact** | Contradiction detection recall metrics |
| **Owner/Taskcard** | AI-GPT-OSS-SYNTHESIS-CONTROLS |
| **Stop Condition** | If contradiction detection recall < 90%: do not use contradiction_checked state |

### RISK-AI-045: Global Vector Cache Pollution

| Field | Value |
|-------|-------|
| **Description** | Shared .local directory or misconfigured path causes vector store data from one project/environment to leak into another |
| **Affected Layer** | Retrieval |
| **Severity** | MEDIUM |
| **Likelihood** | LOW |
| **Detection** | Vector store path validation; project-root anchoring check |
| **Prevention** | Vector stores anchored to repo root; path validated on every access |
| **Mitigation** | Rebuild contaminated store; enforce path validation |
| **Validation Test** | Attempt to open vector store from different project root; verify rejection |
| **Evidence Artifact** | Path validation test results |
| **Owner/Taskcard** | AI-EMBEDDING-VECTOR-STORE-FOUNDATION |
| **Stop Condition** | If cross-project data detected: delete and rebuild all stores |

### RISK-AI-046: Local Telemetry/Spool File Corruption

| Field | Value |
|-------|-------|
| **Description** | JSONL spool files become corrupted (partial writes, encoding issues); telemetry data lost |
| **Affected Layer** | Telemetry |
| **Severity** | MEDIUM |
| **Likelihood** | LOW |
| **Detection** | JSONL parse check on spool read; line count validation |
| **Prevention** | Atomic writes (write to temp, rename); flush after each record |
| **Mitigation** | Skip corrupt lines; log corruption warning; continue with remaining records |
| **Validation Test** | Corrupt a spool file; verify graceful handling |
| **Evidence Artifact** | Spool corruption handling test results |
| **Owner/Taskcard** | AI-TELEMETRY-AGENT-METRICS-INTEGRATION |
| **Stop Condition** | N/A — graceful degradation, not a stop condition |

### RISK-AI-047: Deferred Feature Forgotten After Classification

| Field | Value |
|-------|-------|
| **Description** | A feature classified as "defer" is never revisited because no review trigger fires |
| **Affected Layer** | Control Plane |
| **Severity** | MEDIUM |
| **Likelihood** | MEDIUM |
| **Detection** | Phase gate review checks deferred feature list |
| **Prevention** | Each deferred feature has a review taskcard and target phase; phase gate includes deferred review |
| **Mitigation** | Re-evaluate deferred features at each phase transition |
| **Validation Test** | Phase gate checklist includes "review deferred features" item |
| **Evidence Artifact** | Deferred feature review log per phase |
| **Owner/Taskcard** | AI-FOUNDATION-IMPLEMENTATION-NEXT |
| **Stop Condition** | N/A — administrative gap, not safety issue |

### RISK-AI-048: Non-AI Sprint Accidentally Depends on AI Layer

| Field | Value |
|-------|-------|
| **Description** | Acquisition or commercial sprint code starts importing from tools/ai/ before AI platform is stable |
| **Affected Layer** | All |
| **Severity** | HIGH |
| **Likelihood** | LOW-MEDIUM |
| **Detection** | Import scanning across tools/ excluding tools/ai/; dependency graph analysis |
| **Prevention** | AI platform modules not importable from outside tools/ai/ until stable; import guard |
| **Mitigation** | Remove dependency; refactor to avoid AI import |
| **Validation Test** | Scan non-AI tools/ for tools/ai imports; verify zero hits |
| **Evidence Artifact** | Cross-dependency scan results |
| **Owner/Taskcard** | AI-PLATFORM-FOUNDATION-PLAN |
| **Stop Condition** | If dependency detected: block until refactored |

## 3. Summary Statistics

| Severity | Count |
|----------|-------|
| CRITICAL | 5 (RISK-AI-006, 018, 020, 029, 030) |
| HIGH | 12 (001, 002, 003, 007, 011, 019, 021, 022, 035, 038, 042, 048) |
| MEDIUM | 22 |
| LOW | 9 |
| **Total** | **48** |

## 4. Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/ai/ai-platform-operating-model.md` | Parent platform model |
| `plans/master-plan.md` | Existing risks R-007, R-013, R-021 |
| `docs/ai/agentic-qwen2-control-policy.md` | Qwen2-specific risk controls |
| `docs/ai/gpt-oss-synthesis-control-policy.md` | GPT-OSS-specific risk controls |
| `docs/ai/embedding-and-vector-store-policy.md` | Retrieval risk controls |
