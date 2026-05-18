# AI Technology Decision Record

**Version:** 1.0
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized
**Authority:** docs/ai/ai-platform-operating-model.md

---

## 1. Purpose

Record technology selection decisions for the AI platform. Each decision includes rationale, requirements, risks, and validation criteria.

## 2. Decisions

### TDR-AI-001: LiteLLM — Provider/Router Layer

**Decision:** IMPLEMENT IN FOUNDATION (Phase 1)

**Purpose:**
- OpenAI-compatible endpoint support for llm.professionalize.com
- Provider abstraction (single call path for all models)
- Model routing and fallback
- Token usage capture per call
- Centralized API call path

**Requirements:**
- Must work in `.venv` (pip install)
- No Docker dependency
- No global service process
- No secrets in config files
- Environment variable configuration only

**Rationale:** LiteLLM provides the abstraction needed for role-based routing without building a custom provider layer. It supports the OpenAI-compatible API that llm.professionalize.com exposes.

**Risks:** Framework lock-in (RISK-AI-031). Mitigated by wrapping behind project abstractions.

**Validation:** Successful model discovery and call through LiteLLM to llm.professionalize.com endpoint.

### TDR-AI-002: LlamaIndex — Ingestion/Retrieval Framework

**Decision:** IMPLEMENT IN NEXT PHASE (Phase 3)

**Purpose:**
- Document ingestion pipeline
- Node/chunk transformation
- Retrieval abstractions

**Requirements:**
- Must be wrapped by Format Factory provenance contracts
- Must not replace project authority model
- Ingestion must produce manifested chunks with hashes

**Rationale:** LlamaIndex provides mature ingestion and retrieval abstractions. However, it adds complexity and is not needed until embedding/retrieval (Phase 3). Foundation phases can proceed without it.

**Risk if implemented now:** Premature dependency; adds complexity before core control plane is stable.

**Prerequisite:** Phase 1 control plane operational; Phase 2 synthesis pipeline stable.

**Review Taskcard:** AI-EMBEDDING-VECTOR-STORE-FOUNDATION

### TDR-AI-003: LanceDB — Local Vector Store

**Decision:** IMPLEMENT IN NEXT PHASE (Phase 3)

**Purpose:**
- Persistent project-local vector store
- Metadata columns alongside vectors
- Format-segregated indexes
- Embedded mode (no server)

**Requirements:**
- Database under `.local/ai/vector-stores/`
- No global vector store
- Format namespace isolation
- Python API, pip installable
- No Docker dependency

**Rationale:** LanceDB meets all requirements: embedded, persistent, metadata-rich, Python-native. Preferred over alternatives (see rejected technologies below).

**Risk if implemented now:** Vector store not useful until embedding model verified and spec normalization produces chunks.

**Prerequisite:** Embedding model discovered (Phase 1); normalized spec chunks available.

**Review Taskcard:** AI-EMBEDDING-VECTOR-STORE-FOUNDATION

### TDR-AI-004: Pydantic v2 — Schema Validation

**Decision:** IMPLEMENT IN FOUNDATION (Phase 1)

**Purpose:**
- AI request/response schemas
- Task contracts
- Artifact validation
- JSON Schema export for documentation

**Requirements:**
- v2 (not v1) for performance and JSON Schema support
- All AI inputs and outputs must have Pydantic models
- Schema registry built on Pydantic models

**Rationale:** Pydantic v2 is the standard for Python data validation. Already used by LiteLLM and LlamaIndex. No alternative provides equivalent JSON Schema export and validation speed.

**Risks:** Minimal — widely adopted, stable API.

**Validation:** All AI task contracts defined as Pydantic models.

### TDR-AI-005: Agent Metrics — Canonical Telemetry

**Decision:** IMPLEMENT IN FOUNDATION (Phase 1 local spool, Phase 5 full integration)

**Purpose:**
- Canonical metrics/analytics sink for AI usage
- Token usage, API calls, status, job type, run ID
- Agent/product/format metadata

**Requirements:**
- Do not reinvent telemetry as JSONL-only
- Local JSONL as offline spool, replay ledger, evidence artifact
- Final design aligns to Agent Metrics API fields
- Collector/poster patterns from aspose.net where useful

**Rationale:** Agent Metrics is the existing analytics product. Local JSONL-only telemetry would create a parallel system without aggregation or dashboards.

**Phase 1:** Local JSONL spool with Agent Metrics-aligned schema.
**Phase 5:** Agent Metrics poster integration.

### TDR-AI-006: pytest — Deterministic Tests and Evals

**Decision:** IMPLEMENT IN FOUNDATION (Phase 1)

**Purpose:**
- Deterministic test runner for golden evals
- Regression controls for AI output quality
- No-runtime-AI import guards as test assertions
- Test generation output validation

**Rationale:** pytest is already the project's Python test framework. Golden evals are pytest tests that validate AI output against known-good baselines.

### TDR-AI-007: Existing Evidence/Taskcard/Gate System

**Decision:** PRESERVE AND INTEGRATE (All phases)

**Purpose:**
- Authority and acceptance model
- No AI layer may bypass the existing gate system
- Evidence bundles include AI artifacts
- Taskcards track AI work

**Rationale:** The existing system is proven and hardened. The AI platform must integrate with it, not replace it.

## 3. Rejected Technologies

### ChromaDB
**Decision:** REJECT
**Reason:** Server-based architecture; global state; not as well suited for embedded project-local use as LanceDB.

### Qdrant
**Decision:** REJECT
**Reason:** Server vector DB; Docker recommended; unnecessary complexity for project-local use.

### LangGraph
**Decision:** DEFER WITH REASON
**Reason:** Agent orchestration framework. Current agentic work uses Claude/Codex directly. LangGraph adds complexity without clear benefit at current scale. May be revisited if multi-agent orchestration complexity increases.
**Risk if implemented now:** Over-engineering; framework lock-in for orchestration layer.
**Target phase:** Phase 6+ if needed.
**Review taskcard:** AI-FOUNDATION-IMPLEMENTATION-NEXT

### LangChain
**Decision:** REJECT
**Reason:** Heavy abstraction with frequent breaking changes. LiteLLM + LlamaIndex provide the needed functionality with less coupling. LangChain's broad scope conflicts with the project's need for precise, governed AI usage.

### OpenTelemetry traces
**Decision:** DEFER WITH REASON
**Reason:** Standard distributed tracing. Not needed until AI pipeline spans multiple services. Current architecture is single-process.
**Target phase:** Phase 6+ if pipeline becomes distributed.

### Dockerized AI infrastructure
**Decision:** REJECT
**Reason:** Adds operational complexity. All tools must run in `.venv` without Docker. The project is developer-local, not a deployed service.

### Server vector DBs (Qdrant, Weaviate, Milvus)
**Decision:** REJECT
**Reason:** Require server processes. Project needs embedded, file-based vector store.

### Broad repo-wide embedding of everything
**Decision:** REJECT
**Reason:** Premature; wasteful. Embed only normalized spec artifacts per format, on demand.

### Autonomous code generation
**Decision:** DEFER WITH REASON
**Reason:** AI-generated code must pass full authority lifecycle. Direct autonomous generation without review gates is prohibited. Structured code assistance through the synthesis pipeline is Phase 4+.
**Target phase:** Phase 4+.

### Runtime AI dependencies
**Decision:** REJECT
**Reason:** Product runtime packages must be AI-free (RISK-AI-019).

### AI gate approval
**Decision:** REJECT
**Reason:** Governance prohibition (GOVERNANCE.md 26.10). Gates require human approval.

### Automatic publication/release decisions
**Decision:** REJECT
**Reason:** Release decisions require human authority.

## 4. Deferred Feature Summary

| Feature | Decision | Target Phase | Review Taskcard |
|---------|----------|-------------|-----------------|
| LlamaIndex | Next phase | Phase 3 | AI-EMBEDDING-VECTOR-STORE-FOUNDATION |
| LanceDB | Next phase | Phase 3 | AI-EMBEDDING-VECTOR-STORE-FOUNDATION |
| Agent Metrics full posting | Next phase | Phase 5 | AI-TELEMETRY-AGENT-METRICS-INTEGRATION |
| LangGraph | Defer | Phase 6+ | AI-FOUNDATION-IMPLEMENTATION-NEXT |
| OpenTelemetry | Defer | Phase 6+ | AI-FOUNDATION-IMPLEMENTATION-NEXT |
| Autonomous code generation | Defer | Phase 4+ | AI-FOUNDATION-IMPLEMENTATION-NEXT |
| Cross-format embeddings | Defer | Phase 4+ | AI-EMBEDDING-VECTOR-STORE-FOUNDATION |
| Eval harness (comprehensive) | Next phase | Phase 2 | AI-GPT-OSS-SYNTHESIS-CONTROLS |
| Model benchmark suite | Next phase | Phase 2 | AI-MODEL-DISCOVERY-AND-ROUTING |
| Replay database | Defer | Phase 5 | AI-FOUNDATION-IMPLEMENTATION-NEXT |

## 5. Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/ai/ai-platform-operating-model.md` | Parent platform model |
| `docs/ai/deferred-ai-features-review.md` | Full deferred feature analysis |
| `docs/ai/ai-risk-register.md` | RISK-AI-031 (framework lock-in) |
