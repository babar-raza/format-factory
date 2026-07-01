# AI Platform Operating Model

**Version:** 1.0
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized
**Authority:** plans/master-plan.md, GOVERNANCE.md 26.10, AGENTS.md AF12
**Sprint:** FORMAT-FACTORY-AI-LLM-EMBEDDING-PLAN-MEMORY-SYNC-001

---

## 1. Purpose

This document defines the generic, segregated, reusable, production-grade AI/LLM/Embedding platform layer for Format Factory. All AI usage in the project — agentic reasoning, LLM transformation, embeddings/retrieval — must flow through this governed substrate rather than ad hoc direct endpoint calls.

The platform is designed once and hardened deeply. It is not a collection of isolated tools but a unified infrastructure with contracts, schemas, model discovery, role routing, validators, telemetry, task state, evidence integration, replay capability, and regression controls.

## 2. Core Principle

**AI is accelerator, not authority.** This principle from `docs/ai/ai-usage-operating-model.md` remains the foundation. The platform layer enforces this structurally, not just by policy.

## 3. AI Usage Categories

The platform supports three core AI usage types plus one mandatory control plane.

### 3.1 Type A — Agentic Reasoning / Task Execution

**Purpose:** AI agents that perform multi-step tasks, make decisions within bounded scope, and produce work artifacts.

**Preferred models:**
- HIGH-RISK agentic work (repo mutations, evidence generation, gate preparation): Claude/Codex outside the llm.professionalize.com endpoint layer.
- LOW-RISK agentic work (classification, sorting, simple extraction): Qwen2 through llm.professionalize.com, under strict controls.

**Required controls for all agentic work:**
1. Role contract — defines what the agent is allowed to do
2. Task contract — defines the specific job, inputs, outputs, success criteria
3. Allowed file/path scope — explicit allowlist of files the agent may read/write
4. Allowed operation scope — explicit allowlist of operations (read, write, create, delete)
5. Output schema — Pydantic/JSON schema for all structured outputs
6. State-machine guard — task must follow defined state transitions
7. Validator checks — deterministic validation of all outputs before acceptance
8. Independent verification — DEC-034 applies to agentic outputs that affect authority files
9. Evidence bundle — all agentic work must produce evidence artifacts
10. Rollback/stop rules — conditions under which the agent must stop and revert
11. Model capability check — verify model meets minimum capability for the role
12. Run telemetry — all calls logged per telemetry policy
13. No direct authority over gates/releases — agent output is advisory
14. No uncontrolled repo mutations — all changes through governed paths

**Qwen2 additional controls:** See `docs/ai/agentic-qwen2-control-policy.md`.

**Output authority:** Agentic output is advisory until validated by deterministic checks and accepted through task state transitions.

### 3.2 Type B — LLM Transformation / Synthesis

**Purpose:** LLM calls that transform, extract, summarize, analyze, or synthesize information from specs, requirements, evidence, and code.

**Preferred model:** GPT-OSS through llm.professionalize.com, subject to model discovery and capability verification.

**Use cases:**
- Spec understanding and section mapping
- Requirement extraction from normalized spec artifacts
- Test idea generation from requirements and samples
- Security analysis of format parsing code
- Evidence review and gap identification
- Summary generation for sprint reports
- Parser strategy drafting from spec chunks
- Release-readiness review assistance

**Required controls:**
1. Prompt/task contract — defines input, expected output, constraints
2. Pydantic/JSON schema validation — all outputs must conform to declared schema
3. Cited source chunk requirement — every claim must cite a specific source chunk
4. Source-support verifier — deterministic check that cited chunk supports the claim
5. Contradiction detector — check output against existing verified facts
6. Artifact authority state — output tagged with lifecycle state (ai_draft, etc.)
7. Deterministic acceptance gate — schema + citation + contradiction checks must pass
8. Evaluator/regression suite — golden evals for each synthesis task type
9. Taskcard linkage — every synthesis run linked to a taskcard
10. Provenance manifest — input hashes, model fingerprint, prompt version, output hash
11. Evidence inclusion — synthesis artifacts included in evidence bundles

**Output authority:** LLM synthesis output is not authoritative until it passes verification and state transition rules. See `docs/ai/ai-artifact-authority-lifecycle.md`.

### 3.3 Type C — Embeddings / Retrieval

**Purpose:** Vector-based retrieval for spec chunks, evidence lookup, requirement matching, and cross-format knowledge reuse.

**Preferred source:** Embedding model through llm.professionalize.com, discovered dynamically.

**Use cases:**
- Spec section retrieval by semantic similarity
- Evidence lookup across sprints and formats
- Chunk ranking for relevance to a query
- Similar-format requirement lookup
- Replayable RAG pipelines
- Cross-format memory reuse (with namespace isolation)

**Vector store requirements:**
- Segregated by format (namespace isolation)
- Permanent and project-local (under `.local/ai/vector-stores/`)
- Reusable across reruns without rebuild
- Replayable — same inputs produce same index
- Hash-invalidated when source documents or chunks change
- Never global or shared outside the repository

**Vector store must support:**
- Format-level namespaces (e.g., `fods`, `fodt`, `zst`)
- Versioned source/chunk manifests per namespace
- Embedding model fingerprint per index
- Index version tracking
- Rebuild/refresh rules and triggers
- Stale-index detection (source hash mismatch)
- Retrieval audit logs
- Evidence bundle summaries

**Output authority:** Embeddings retrieve context only. They are never authority. Retrieved chunks must be validated against source before use in claims.

### 3.4 Mandatory Control Plane

This is not a fourth model type. It is the governing infrastructure around all AI usage.

**Components:**
1. **Endpoint/model discovery** — dynamic enumeration of available models at llm.professionalize.com
2. **Role-based model routing** — map AI roles to appropriate models based on capability
3. **Task contracts** — Pydantic schemas defining every AI task's inputs, outputs, constraints
4. **Prompt registry** — versioned, immutable prompt templates with hash tracking
5. **Schema registry** — centralized Pydantic/JSON schemas for all AI inputs and outputs
6. **Artifact authority states** — lifecycle tracking per `docs/ai/ai-artifact-authority-lifecycle.md`
7. **Validators** — deterministic checks for schema conformance, citation validity, contradiction detection
8. **Evaluators** — golden eval suites for regression testing of AI outputs
9. **Telemetry** — per-call logging mapped to Agent Metrics per `docs/ai/ai-telemetry-and-agent-metrics-policy.md`
10. **Usage analytics** — token counts, cost estimates, model selection frequency
11. **Replay manifests** — reproducibility records for every AI pipeline run
12. **Risk controls** — per `docs/ai/ai-risk-register.md`
13. **Evidence bundle integration** — AI artifacts automatically included in evidence bundles
14. **Taskcard integration** — every AI run linked to active taskcard
15. **No-runtime-AI guards** — static analysis preventing AI imports in product code
16. **Deferred-feature review mechanism** — per `docs/ai/deferred-ai-features-review.md`

## 4. Platform Architecture

### 4.1 Directory Layout

```
tools/ai/                          # AI platform infrastructure (repo tools only)
  control_plane/
    model_discovery.py             # Dynamic model enumeration
    model_router.py                # Role-based model selection
    capability_probe.py            # Endpoint capability verification
    task_contract.py               # Task contract schemas and validation
    prompt_registry.py             # Versioned prompt management
    schema_registry.py             # Centralized schema management
  agentic/
    agent_runner.py                # Governed agent execution
    task_state_machine.py          # State transitions for agentic tasks
    scope_guard.py                 # File/operation scope enforcement
    rollback.py                    # Revert mechanisms
  synthesis/
    synthesis_runner.py            # LLM transformation pipeline
    citation_verifier.py           # Source-citation validation
    contradiction_detector.py      # Cross-reference contradiction check
    evaluator.py                   # Golden eval runner
  retrieval/
    embedding_manager.py           # Embedding generation and management
    vector_store.py                # LanceDB wrapper with namespace isolation
    chunk_manifest.py              # Versioned chunk tracking
    stale_detector.py              # Source-hash change detection
    audit_log.py                   # Retrieval operation logging
  telemetry/
    call_logger.py                 # Per-call JSONL logging
    agent_metrics_poster.py        # Agent Metrics integration
    spool_manager.py               # Offline spool management
  validators/
    schema_validator.py            # Pydantic schema enforcement
    authority_lifecycle.py         # Artifact state transition enforcement
    runtime_guard.py               # Import analysis for runtime isolation
  contracts/                       # Task contract YAML definitions
  prompts/                         # Versioned prompt templates
  schemas/                         # Pydantic model definitions
  evals/                           # Golden evaluation datasets

.local/ai/                         # Local AI runtime state (gitignored)
  vector-stores/                   # LanceDB databases per format
    fods/
    fodt/
    zst/
    ...
  llm-logs/                        # Per-call telemetry JSONL
  spool/                           # Offline Agent Metrics spool
  cache/                           # Prompt/response cache
  model-registry/                  # Discovered model capabilities
```

### 4.2 Segregation Boundaries

**Runtime product code** (`src/python/**`, `src/net/**`) MUST NOT import or call:
- `tools/ai/**`
- LiteLLM, LlamaIndex, LanceDB runtime modules
- llm.professionalize.com endpoints
- GPT_OSS_ENDPOINT, GPT_OSS_API_KEY environment variables
- Any OpenAI/Anthropic/Ollama endpoint client

**Repo tools and acquisition pipeline** (`tools/**`, acquisition scripts) MAY use the AI platform.

**Static enforcement:** `tools/ai/validators/runtime_guard.py` performs import analysis on `src/` to detect violations. This check runs in CI and as a pre-commit validation.

### 4.3 Environment Configuration

All endpoint configuration comes from system environment variables:
- `GPT_OSS_API_KEY` — API key for llm.professionalize.com
- `GPT_OSS_ENDPOINT` — Base URL for llm.professionalize.com

No model names, endpoints, or credentials may be hardcoded in pipeline tools. The platform discovers available models dynamically through the control plane.

## 5. Implementation Phases

### Phase 1 — Control Plane Foundation
- Model discovery and capability probing
- Role-based routing with fail-closed behavior
- Task contract schema definitions
- Prompt registry scaffold
- Telemetry logging (local JSONL)
- Runtime guard static analysis
- **Gate:** Control plane operational with at least one endpoint verified

### Phase 2 — Synthesis Pipeline
- GPT-OSS synthesis runner with citation verification
- Contradiction detector
- Schema validation for all output types
- Golden eval framework
- Artifact authority lifecycle enforcement
- **Gate:** At least one synthesis task (e.g., spec extraction) passing full validation pipeline

### Phase 3 — Embedding/Retrieval Foundation
- LanceDB integration with format namespaces
- Chunk manifest generation from normalized specs
- Embedding model discovery and fingerprinting
- Stale-index detection
- Retrieval audit logging
- **Gate:** One format (FODS) fully indexed with reproducible retrieval

### Phase 4 — Agentic Integration
- Qwen2 controlled agentic runner
- Task state machine with scope guards
- Rollback mechanisms
- DEC-034 integration for agentic outputs
- **Gate:** One low-risk agentic task completing full lifecycle

### Phase 5 — Telemetry and Analytics
- Agent Metrics integration
- Offline spool-to-metrics pipeline
- Usage analytics dashboard fields
- Cost estimation
- **Gate:** Telemetry flowing to Agent Metrics for at least one pipeline

### Phase 6 — Hardening and Regression
- Full evaluator suite across all task types
- Replay manifests for all pipelines
- Risk register validation tests
- Cross-format embedding isolation tests
- **Gate:** All risk register items have at least one validation test

## 6. What This Document Does NOT Authorize

- No AI implementation code may be written until this plan is reviewed and accepted.
- No endpoint calls may be made.
- No vector databases may be created.
- No runtime product code may be changed.
- No gates may be approved based on this plan.
- This plan must be reviewed by human authority before Phase 1 begins.

## 7. Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/ai/model-routing-and-discovery-policy.md` | Model discovery and routing details |
| `docs/ai/agentic-qwen2-control-policy.md` | Qwen2 agentic controls |
| `docs/ai/gpt-oss-synthesis-control-policy.md` | GPT-OSS synthesis controls |
| `docs/ai/embedding-and-vector-store-policy.md` | Embedding/vector store specification |
| `docs/ai/ai-telemetry-and-agent-metrics-policy.md` | Telemetry and Agent Metrics |
| `docs/ai/ai-risk-register.md` | Risk register and control matrix |
| `docs/ai/ai-artifact-authority-lifecycle.md` | Artifact state machine |
| `docs/ai/ai-assisted-acquisition-pipeline.md` | Acquisition pipeline integration |
| `docs/ai/ai-technology-decision-record.md` | Technology selection decisions |
| `docs/ai/deferred-ai-features-review.md` | Deferred feature classification |
| `docs/ai/ai-usage-operating-model.md` | Existing AI operating model (preserved) |
| `docs/ai/spec-retrieval-and-rag-policy.md` | Existing RAG policy (preserved) |
| `docs/ai/llm-and-embedding-strategy.md` | Existing strategy (superseded by this platform model) |
| `plans/master-plan.md` | Section 14, 37, 39 |
| `AGENTS.md` | Sections H, AF12, AF16 |
| `GOVERNANCE.md` | Sections 26.10, 26.14 |
