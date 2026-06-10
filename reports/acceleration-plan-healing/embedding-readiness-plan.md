# Embedding Readiness Plan

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04

---

## Approval Gate Condition

Embedding-based retrieval (vector search replacing TF-IDF in source_pattern_miner.py)
may only be activated when ALL of the following are true:

1. Supervisor approval in `.supervisor/policies.yaml` (explicit embedding gate entry)
2. Embedding model identified and approved (local or gateway-served)
3. Vector store selected and privacy-reviewed (no source code sent to external service)
4. Pilot design completed and reviewed (see below)
5. Format isolation test passes for embedding retrieval (fods query never returns fodt chunks)
6. Embedding store is read-only to all AI tools (no self-indexing)

## Pilot Design (FODS + LanceDB + Read-Only)

| Component | Design |
|-----------|--------|
| Format | FODS (smallest .NET format src corpus — safe for pilot) |
| Vector store | LanceDB (local-first, no external network calls required) |
| Embedding model | Gateway-served (via approved gateway_chat()) — no direct model import |
| Index scope | `src/net/fods/` only — no cross-format indexing in pilot |
| Query isolation | LanceDB table per format — fods table, fodt table, etc. (no shared namespace) |
| Index update | Manual trigger only — no auto-reindex on src/ change |
| Fallback | TF-IDF lexical retrieval (current source_pattern_miner.py behavior) |
| Pilot gate | 10 test queries; format isolation verified; latency < 2s per query |

## What Changes vs Current

| Current (TF-IDF) | Pilot (Embedding) |
|------------------|-------------------|
| Lexical keyword match | Semantic similarity match |
| In-memory, no persistence | LanceDB local file store |
| No embedding model needed | Gateway embedding call per indexing run |
| Fast (milliseconds) | Slightly slower (vector search + embedding latency) |
| Lower recall for synonyms | Higher recall for semantic matches |

## What Does NOT Change

- Format namespace isolation (enforced by table-per-format in LanceDB)
- src/ files are never modified
- All output carries authority_state: ai_draft
- Fallback to TF-IDF if embedding store unavailable

## This Sprint

Embedding readiness plan is written but NOT activated. Current source_pattern_miner.py
uses TF-IDF lexical retrieval. LanceDB is not installed. Embedding model not configured.

Next steps: Supervisor reviews this plan; if approved, Skills stream pilots LanceDB
integration with FODS corpus first.
