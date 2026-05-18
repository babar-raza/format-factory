# Technology Decision Report

**Date:** 2026-05-18

## Summary

Full technology evaluation is documented in `docs/ai/ai-technology-decision-record.md` and `docs/ai/deferred-ai-features-review.md`. This report summarizes key decisions.

## Foundation Stack (Phase 1)

| Component | Purpose | Risk | Mitigation |
|-----------|---------|------|------------|
| LiteLLM | Provider abstraction, routing | Lock-in (RISK-AI-031) | Wrapped behind project abstractions |
| Pydantic v2 | Schema validation, contracts | Minimal | Widely adopted, stable API |
| Agent Metrics (local spool) | Telemetry | Post failure (RISK-AI-017) | Offline spool with retry |
| pytest | Golden evals, regression | None | Already project standard |

## Deferred Stack

| Component | Phase | Reason |
|-----------|-------|--------|
| LlamaIndex | 3 | Not needed until embedding phase |
| LanceDB | 3 | Not needed until embedding model verified |
| Agent Metrics (posting) | 5 | Local spool first |
| LangGraph | 6+ | Not needed at current scale |

## Rejected

| Component | Reason |
|-----------|--------|
| ChromaDB | Server-based; global state |
| Qdrant/Weaviate | Server vector DB; Docker |
| LangChain | Heavy; frequent breaking changes |
| Docker AI | Not needed; .venv only |
| Runtime AI | Product code must be AI-free |

## 25-Item Classification

See `docs/ai/deferred-ai-features-review.md` for the full 25-item implement/defer/reject classification with reasons, risks, prerequisites, review taskcards, and acceptance criteria.
