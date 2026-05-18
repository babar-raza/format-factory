# Deferred AI Features Review

**Version:** 1.0
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized
**Authority:** docs/ai/ai-platform-operating-model.md

---

## 1. Purpose

Formal review of each AI candidate technology/feature. Every item is classified as: implement in foundation, implement in next phase, defer with reason, or reject. No vague "later" or "optional."

## 2. Classification Matrix

| # | Feature | Decision | Phase | Reason | Risk if Implemented Now | Prerequisite | Review Taskcard | Acceptance Criteria |
|---|---------|----------|-------|--------|------------------------|--------------|-----------------|---------------------|
| 1 | LiteLLM | Foundation | 1 | Core provider abstraction needed for all AI calls | N/A — minimal risk | None | AI-PLATFORM-FOUNDATION-PLAN | LiteLLM installed; model call succeeds through abstraction |
| 2 | LlamaIndex | Next phase | 3 | Ingestion/retrieval framework; not needed until embedding phase | Premature dependency; complexity without value | Phase 1 control plane stable | AI-EMBEDDING-VECTOR-STORE-FOUNDATION | Document ingestion produces manifested chunks |
| 3 | LanceDB | Next phase | 3 | Vector store; not needed until embeddings ready | Storage without content; premature optimization | Embedding model verified; spec chunks available | AI-EMBEDDING-VECTOR-STORE-FOUNDATION | Format-segregated indexes operational |
| 4 | ChromaDB | Reject | N/A | Server-based; global state; poor fit for project-local embedded use | Architectural mismatch; server dependency | N/A | N/A | N/A |
| 5 | Qdrant | Reject | N/A | Server vector DB; Docker dependency; overkill | Infrastructure overhead | N/A | N/A | N/A |
| 6 | LangGraph | Defer | 6+ | Agent orchestration; not needed at current scale | Over-engineering; framework lock-in for orchestration | Multi-agent complexity justification | AI-FOUNDATION-IMPLEMENTATION-NEXT | Clear multi-agent use case documented |
| 7 | LangChain | Reject | N/A | Heavy abstraction; frequent breaking changes; scope too broad | Coupling; upgrade churn; abstraction misalignment | N/A | N/A | N/A |
| 8 | Pydantic schemas | Foundation | 1 | Core schema validation for all AI I/O | N/A — essential | None | AI-PLATFORM-FOUNDATION-PLAN | All AI task contracts as Pydantic models |
| 9 | Agent Metrics external posting | Next phase | 5 | Canonical telemetry sink; local spool first | Dependency on external service availability | Local spool operational; schema aligned | AI-TELEMETRY-AGENT-METRICS-INTEGRATION | Telemetry posted and visible in Agent Metrics |
| 10 | Local JSONL spool | Foundation | 1 | Offline buffer; replay ledger; evidence | N/A — essential | None | AI-TELEMETRY-AGENT-METRICS-INTEGRATION | JSONL records written for every AI call |
| 11 | OpenTelemetry traces | Defer | 6+ | Distributed tracing; not needed for single-process pipeline | Unnecessary complexity | Pipeline becomes distributed | AI-FOUNDATION-IMPLEMENTATION-NEXT | Tracing spans visible in collector |
| 12 | Prompt registry | Foundation | 1 | Versioned prompt management; drift prevention | N/A — essential for reproducibility | None | AI-PLATFORM-FOUNDATION-PLAN | Prompts versioned with hash tracking |
| 13 | Model registry | Foundation | 1 | Discovered model capability tracking | N/A — essential for routing | None | AI-MODEL-DISCOVERY-AND-ROUTING | Discovered models stored with capabilities |
| 14 | Automatic source generation | Defer | 4+ | Code from requirements; requires full authority lifecycle | Code from unverified requirements is dangerous | Requirements at `accepted_for_source_requirements` state | AI-FOUNDATION-IMPLEMENTATION-NEXT | Generated code passes review and test gates |
| 15 | AI-generated tests | Next phase | 2 | Test idea generation; mandatory but needs eval framework | Without eval: low-quality tests accepted | Eval framework operational | AI-TEST-GENERATION-INTEGRATION | Generated tests pass reviewer filter; accepted tests in suite |
| 16 | AI evidence review | Next phase | 2 | Sprint evidence gap analysis | Without controls: false confidence in evidence | Synthesis pipeline operational | AI-GPT-OSS-SYNTHESIS-CONTROLS | Evidence gaps identified match manual review |
| 17 | AI gate recommendation | Defer | 4+ | AI suggests gate readiness; human decides | False confidence; pressure on human approver | Full synthesis + eval pipeline | AI-FOUNDATION-IMPLEMENTATION-NEXT | Recommendations accurate vs. manual assessment |
| 18 | Autonomous gate approval | Reject | N/A | Governance prohibition (GOVERNANCE.md 26.10) | Governance violation | N/A | N/A | N/A |
| 19 | Runtime AI features | Reject | N/A | Product code must be AI-free | Runtime dependency; deployment complexity | N/A | N/A | N/A |
| 20 | Full-repo embeddings | Reject | N/A | Wasteful; premature; most repo content not useful for retrieval | Storage waste; noise in retrieval | N/A | N/A | N/A |
| 21 | Per-format embeddings | Next phase | 3 | Embed normalized spec artifacts per format | Without normalization: garbage in | Spec normalization producing chunks | AI-EMBEDDING-VECTOR-STORE-FOUNDATION | One format fully indexed |
| 22 | Cross-format embeddings | Defer | 4+ | Cross-format pattern retrieval | Contamination risk without isolation controls | Per-format indexes stable; isolation verified | AI-EMBEDDING-VECTOR-STORE-FOUNDATION | Cross-format queries isolated; no contamination |
| 23 | Replay database | Defer | 5 | Full pipeline replay tracking | Not needed until pipelines are running | At least one pipeline in production use | AI-FOUNDATION-IMPLEMENTATION-NEXT | Any pipeline run replayable from manifest |
| 24 | Eval harness | Next phase | 2 | Golden eval suite for synthesis quality | Without evals: no regression detection | Synthesis pipeline producing outputs | AI-GPT-OSS-SYNTHESIS-CONTROLS | Eval suite covering each synthesis task type |
| 25 | Model benchmark suite | Next phase | 2 | Compare model quality for each role | Without benchmarks: routing based on assumptions | At least 2 models discovered | AI-MODEL-DISCOVERY-AND-ROUTING | Benchmark results for each role × model |

## 3. Implementation Priority Order

1. **Phase 1 (Foundation):** LiteLLM, Pydantic schemas, prompt registry, model registry/discovery, local JSONL spool, runtime guard
2. **Phase 2 (Synthesis):** GPT-OSS synthesis pipeline, eval harness, AI-generated tests, AI evidence review, model benchmarks
3. **Phase 3 (Retrieval):** LlamaIndex, LanceDB, per-format embeddings, chunk manifests
4. **Phase 4 (Agentic + Advanced):** Qwen2 controlled agentic, automatic source generation, cross-format embeddings, AI gate recommendation
5. **Phase 5 (Telemetry + Replay):** Agent Metrics full posting, replay database
6. **Phase 6+ (Future):** LangGraph, OpenTelemetry, additional orchestration

## 4. Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/ai/ai-platform-operating-model.md` | Phase definitions |
| `docs/ai/ai-technology-decision-record.md` | Technology rationale |
| `docs/ai/ai-risk-register.md` | Implementation risks |
