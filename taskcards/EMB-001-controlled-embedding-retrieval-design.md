---
taskcard_id: EMB-001
title: Embedding and Retrieval Architecture Design
status: proposed_pending_human_approval
created: 2026-05-08
sprint: memory-sprint-format-understanding-llm-strategy
visibility: internal
relationship_to_main_sprint: backlog — not a MAIN SPRINT gate
relationship_to_product_source: not a product source task; future input to Phase 4 tooling
---

# EMB-001 — Controlled Embedding/Retrieval Architecture Design

## Purpose

Design the architecture for controlled embedding and retrieval over verified format knowledge.
Establishes what gets embedded, how provenance is tracked, and how retrieval is audited.

## Scope

- Define the embedding index schema (source_hash, source_path, spec_version, chunk_id, fact_id, etc.)
- Define the retrieval API for agents (query, result format, provenance return)
- Define refresh and invalidation policy (when to rebuild after gate changes or spec updates)
- Define the local storage layout (.local/embeddings/{format}/)
- Define the audit log format for retrievals
- Define which model families are candidates (from LLM-001)
- Write architecture document: docs/embedding-retrieval-architecture.md

## Blocked On

- LLM-001 approved (model discovery needed before design can be finalized)
- FUL-001 approved (FUL files are preferred source content)

## Out of Scope

- Actual embedding generation — that is EMB-002
- Vector DB or ChromaDB/FAISS/Qdrant — not authorized until EMB-001 design approved
- Production LLM calls
- Any src/ product source

## Allowed Files

- docs/embedding-retrieval-architecture.md (new)
- schemas/embedding/ — embedding schema definitions (new directory, YAML/JSON schema only)
- plans/master-plan.md (update backlog section)
- evidence bundle

## Forbidden Files

- .local/embeddings/ (write) — no actual embeddings in this sprint
- .local/vector/ (write) — no vector DB in this sprint
- *.faiss, *.db, *.chroma, *.sqlite — forbidden
- src/python/fods/, src/net/fods/

## Acceptance Criteria

1. Architecture document written with all required sections.
2. Embedding schema defined with all required provenance fields.
3. Retrieval API defined.
4. Invalidation policy documented.
5. DEC-034 PASS.
6. Human approval.

## Future Trigger

Human authorizes EMB-001 after LLM-001 and FUL-001 are approved.

## Status

proposed_pending_human_approval — no embeddings created in this memory sprint.
