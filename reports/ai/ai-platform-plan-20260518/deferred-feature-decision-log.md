# Deferred Feature Decision Log

**Date:** 2026-05-18

## Summary

25 candidate features classified. Full analysis in `docs/ai/deferred-ai-features-review.md`.

## Classification Summary

| Decision | Count | Items |
|----------|-------|-------|
| Foundation (Phase 1) | 6 | LiteLLM, Pydantic schemas, prompt registry, model registry, local JSONL spool, pytest evals |
| Next Phase (2-3) | 7 | LlamaIndex, LanceDB, per-format embeddings, eval harness, model benchmarks, AI-generated tests, AI evidence review |
| Defer (4+) | 6 | LangGraph, OpenTelemetry, autonomous source generation, cross-format embeddings, replay database, AI gate recommendation |
| Reject | 6 | ChromaDB, Qdrant, LangChain, Dockerized AI, runtime AI features, AI gate approval |

## Key Deferred Items with Review Gates

| Feature | Target Phase | Review Taskcard | Review Trigger |
|---------|-------------|-----------------|---------------|
| LangGraph | 6+ | AI-FOUNDATION-IMPLEMENTATION-NEXT | Multi-agent complexity justification |
| OpenTelemetry | 6+ | AI-FOUNDATION-IMPLEMENTATION-NEXT | Pipeline becomes distributed |
| Source generation | 4+ | AI-FOUNDATION-IMPLEMENTATION-NEXT | Requirements at accepted_for_source_requirements |
| Cross-format embeddings | 4+ | AI-EMBEDDING-VECTOR-STORE-FOUNDATION | Per-format isolation verified |
| Replay database | 5 | AI-FOUNDATION-IMPLEMENTATION-NEXT | At least one pipeline in production |
| AI gate recommendation | 4+ | AI-FOUNDATION-IMPLEMENTATION-NEXT | Full synthesis + eval pipeline |

## Deferred Feature Review Policy

Each deferred feature has:
1. Concrete reason for deferral
2. Risk if implemented prematurely
3. Prerequisite gates
4. Review taskcard
5. Target future phase
6. Acceptance criteria for later implementation

RISK-AI-047 (deferred feature forgotten) mitigated by: taskcard tracking, phase gate reviews, and this decision log.
