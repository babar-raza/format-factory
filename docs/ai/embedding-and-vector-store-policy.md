# Embedding and Vector Store Policy

**Version:** 1.0
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized
**Authority:** docs/ai/ai-platform-operating-model.md

---

## 1. Purpose

Define the architecture, governance, and operational rules for embeddings and vector stores in Format Factory. Vector stores are permanent, project-local, format-segregated, replayable, and hash-invalidated. They are retrieval aids, never authority.

## 2. Vector Store Architecture

### 2.1 Storage Location

All vector stores live under `.local/ai/vector-stores/` (gitignored). Structure:

```
.local/ai/vector-stores/
  fods/
    index/                    # LanceDB table files
    manifest.yaml             # Source/chunk manifest
    metadata.yaml             # Index metadata
  fodt/
    index/
    manifest.yaml
    metadata.yaml
  zst/
    ...
  _shared/                    # Cross-format indexes (if needed, with strict controls)
```

### 2.2 Format Namespace Isolation

- Each format has its own namespace (directory + LanceDB table prefix)
- Cross-format queries require explicit namespace specification
- No implicit cross-namespace retrieval
- `_shared/` namespace only created if justified by a taskcard with human approval
- Cross-format contamination is a RISK (RISK-AI-011) with specific controls

### 2.3 Technology Selection

Preferred: **LanceDB** or similarly suitable local vector store.

Requirements:
- Persistent on-disk storage (no in-memory only)
- Metadata columns alongside vectors
- Python API
- No server process required (embedded mode)
- No Docker dependency
- Works in `.venv`

See `docs/ai/ai-technology-decision-record.md` for full technology evaluation.

## 3. Index Lifecycle

### 3.1 Index Creation

1. Source documents identified (normalized spec artifacts per `docs/python-foss/specification-normalization.md`)
2. Chunk manifest generated — lists every chunk with:
   - chunk_id
   - source_path
   - source_hash (SHA-256)
   - section_id
   - page_range (if applicable)
   - chunk_text_hash
   - chunk_token_count
3. Embedding model discovered and fingerprinted
4. Embeddings generated for all chunks
5. Vectors stored in LanceDB with metadata columns
6. Index metadata recorded:
   - index_version
   - embedding_model_id
   - embedding_model_fingerprint
   - embedding_dimensions
   - chunk_count
   - source_manifest_hash
   - created_at
   - format_namespace

### 3.2 Index Refresh

Triggers for refresh:
- Source document hash changes (spec updated)
- Chunk manifest hash changes (chunking strategy updated)
- Embedding model changes (new model discovered)
- Manual refresh requested by taskcard

Refresh process:
1. Detect stale sources (compare current source hashes vs. manifest)
2. Re-chunk only changed sources
3. Re-embed only changed chunks
4. Update LanceDB table (upsert)
5. Update manifest and metadata
6. Log refresh in telemetry

### 3.3 Stale Index Detection

On every retrieval operation:
1. Check source manifest hashes against current source files
2. If any source hash mismatches: flag index as potentially stale
3. Log `STALE_INDEX_WARNING: {format_namespace}` in telemetry
4. Retrieval may still proceed but results tagged as `potentially_stale`
5. Evidence bundles must note stale index usage

### 3.4 Index Versioning

Every index rebuild increments the index_version. Previous versions are retained (disk space permitting) for replay comparison. Version history tracked in metadata.yaml.

## 4. Embedding Model Requirements

### 4.1 Model Selection

- Auto-detected through model discovery at llm.professionalize.com
- Must have embedding capability confirmed by capability probe
- Dimension count must be stable (no variable-dimension models)
- If dimension changes between model versions, all indexes must be rebuilt

### 4.2 Dimension Stability Check

Before using a discovered embedding model:
1. Check if existing indexes use different dimensions
2. If mismatch: do NOT mix dimensions in same index
3. Option A: Rebuild all indexes with new model
4. Option B: Continue with existing model if still available
5. Decision logged in telemetry and evidence

### 4.3 Model Fingerprinting

Every embedding operation records:
- embedding_model_id
- embedding_model_fingerprint
- embedding_dimensions
- endpoint_identity (without secrets)

## 5. Retrieval Operations

### 5.1 Query Flow

1. Query text embedded using same model as index
2. Similarity search within specified format namespace
3. Top-K results returned with metadata
4. Results tagged with retrieval_tier: 3 (vector/semantic)
5. Results are CONTEXT ONLY — not authority

### 5.2 Retrieval Audit Log

Every retrieval operation logged to `.local/ai/retrieval-audit-log.jsonl`:
- timestamp
- query_text_hash (not full text)
- format_namespace
- index_version
- embedding_model_id
- top_k
- result_count
- result_chunk_ids
- result_similarity_scores
- stale_index_flag
- taskcard_id
- sprint_id

### 5.3 RAG Pipeline Integration

When used in a RAG pipeline:
1. Retrieved chunks passed to synthesis model as context
2. Synthesis model must cite chunk_ids in output
3. Citation verifier confirms chunk_ids match retrieval results
4. Source-support verifier confirms cited chunks support the claims
5. Full provenance chain: source → chunk → embedding → retrieval → synthesis → validation

## 6. Prohibited Uses

- Embeddings MUST NOT be treated as authority
- Vector similarity scores MUST NOT be used as evidence of correctness
- Cross-format retrieval without explicit namespace specification is FORBIDDEN
- Global/shared vector stores outside the repository are FORBIDDEN
- Raw spec PDFs MUST NOT be embedded directly — use normalized artifacts only
- Embedding indexes MUST NOT be committed to git

## 7. Evidence Bundle Integration

Evidence bundles should include (when AI retrieval was used):
- Retrieval audit log summary (not full log)
- Index metadata snapshot
- Chunk manifest hash
- Stale index warnings if any
- Retrieval statistics (query count, average result count)

## 8. Replayability

For any retrieval-dependent pipeline:
1. Record the exact index version used
2. Record all query texts (hashed)
3. Record all retrieval results
4. Given same index version + same queries, results must be deterministic
5. Replay manifest links pipeline run to specific index state

## 9. Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/ai/ai-platform-operating-model.md` | Parent platform model, Type C |
| `docs/ai/model-routing-and-discovery-policy.md` | Embedding model routing |
| `docs/ai/ai-technology-decision-record.md` | LanceDB selection rationale |
| `docs/python-foss/specification-normalization.md` | Source artifacts for embedding |
| `docs/ai/spec-retrieval-and-rag-policy.md` | Existing RAG tier policy |
| `docs/ai/ai-risk-register.md` | RISK-AI-008 through RISK-AI-012 |
