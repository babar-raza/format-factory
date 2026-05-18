# Retrieval, Vector Store, and Replay Design Review

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-DEEP-PLAN-HEALING-001
**Date:** 2026-05-18
**Gate:** 5
**Lane:** L5

---

## 1. Vector Store Architecture

### 1.1 Storage Layout

```
.local/ai/vector-stores/
  {format}/                      # e.g., fods/, fodt/
    index/                       # LanceDB table files
    manifest.yaml                # Chunk manifest with hashes
    metadata.yaml                # Index metadata (model, dimensions, timestamp)
```

### 1.2 Format Namespace Isolation

- Each format has its own LanceDB table in its own directory
- Cross-namespace queries are **rejected by default**
- Explicit `cross_format=True` flag required (and logged) for cross-format queries
- Namespace isolation test: query format A, verify zero results from format B

### 1.3 Index Lifecycle

| State | Description | Transition |
|-------|-------------|------------|
| not_created | No index exists | → building (on first indexing request) |
| building | Index being created from normalized chunks | → ready (on completion) |
| ready | Index available for queries | → stale (on source hash mismatch) |
| stale | Source has changed; index may return outdated results | → rebuilding (on refresh) |
| rebuilding | Index being recreated from updated source | → ready (on completion) |
| corrupted | Read errors or checksum failure | → rebuilding (on rebuild) |

### 1.4 Stale Detection Algorithm

On every retrieval operation:
```
1. Load manifest.yaml for target format
2. For each source chunk in manifest:
   a. Compute current source file hash
   b. Compare against manifest.source_hash
3. If ANY hash mismatch: flag index as stale
4. If stale: set stale_flag=True on all retrieval results
5. Log stale detection in retrieval audit log
6. Do NOT block retrieval — return results with stale warning
7. Exception: if stale index used for gate evidence, evidence is INVALID
```

## 2. Embedding Model Governance

### 2.1 Dimension Stability

When model discovery detects an embedding model:
```
1. Record embedding_dimensions from discovery
2. Compare against previous index metadata.dimensions
3. If dimensions changed:
   a. Log DIMENSION_CHANGE warning
   b. Flag ALL existing indexes as incompatible
   c. Do NOT auto-rebuild (human decision required)
   d. Options: rebuild all indexes OR continue with old model
4. If dimensions match: proceed normally
```

### 2.2 Model Fingerprinting

Every vector index manifest records:
```
IndexMetadata:
  format: str
  embedding_model_id: str
  embedding_model_fingerprint: Optional[str]
  embedding_dimensions: int
  created_at: datetime
  source_manifest_hash: str      # Hash of chunk manifest
  chunk_count: int
  last_query_at: Optional[datetime]
  rebuild_count: int
```

## 3. Spec Normalization Adapter

### 3.1 Purpose

Bridge between existing spec normalization output and AI retrieval input. The normalization pipeline is deterministic and local-only (GOVERNANCE.md 16.5). The adapter loads its output for AI consumption.

### 3.2 Input

Normalized chunks from `.local/spec-cache/{format}/{version}/normalized/chunks.jsonl`

### 3.3 Output Schema

```
NormalizedChunk:
  chunk_id: str                  # Unique chunk identifier
  source_path: str               # Path to source spec file
  source_hash: str               # SHA-256 of source file
  spec_version: str              # Spec version identifier
  section_id: str                # Spec section reference
  chunk_text_hash: str           # SHA-256 of chunk text
  token_count: int               # Approximate token count
```

### 3.4 Failure Modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Normalization output not found | File not found | Fail — cannot create index without source |
| Chunk format incompatible | Schema validation failure | Fail — log version mismatch |
| Source file moved/renamed | Source path check fails | Fail — re-normalize required |
| Zero chunks loaded | Empty result check | Fail — log empty normalization |

## 4. Retrieval Audit Log

Every retrieval operation writes:
```
RetrievalAuditEntry:
  timestamp: datetime
  query_text_hash: str           # SHA-256 of query (not raw text)
  format: str
  index_version: str
  embedding_model_id: str
  results_count: int
  top_score: float
  stale_flag: bool
  cross_format_flag: bool
  retrieval_duration_ms: int
  sprint_id: str
  taskcard_id: str
```

Storage: `.local/ai/retrieval-audit-log.jsonl` (append-only, gitignored)

## 5. Replay Design

### 5.1 Purpose

Prove that a past retrieval can be reproduced: same query against same index yields same results.

### 5.2 Replay Manifest

```
ReplayManifest:
  sprint_id: str
  retrieval_entries: list[RetrievalAuditEntry]
  index_metadata: IndexMetadata
  chunk_manifest_hash: str
  embedding_model_fingerprint: str
```

### 5.3 Replay Test

```
1. Load replay manifest
2. Verify index metadata matches current index
3. Re-run each query from manifest
4. Compare result chunk_ids against manifest results
5. If match: replay PASS
6. If mismatch: log diff, flag as non-reproducible
```

### 5.4 What Breaks Replay

| Breaker | Detection | Prevention |
|---------|-----------|------------|
| Index rebuilt with different model | Fingerprint mismatch | Version index with model fingerprint |
| Source chunks changed | Chunk manifest hash mismatch | Detect stale before replay |
| LanceDB version upgrade | Query behavior change | Pin LanceDB version |
| Embedding model weights updated | Fingerprint/dimension check | Lock model for sprint duration |

## 6. Incremental Refresh Design

When source spec is updated (new sections added, existing sections modified):

```
1. Detect changed chunks via source_hash comparison
2. Remove stale embeddings for changed chunks
3. Generate new embeddings for changed chunks only
4. Update manifest with new hashes
5. Verify index integrity after partial update
6. Log refresh details in audit log
```

Full rebuild required when:
- Embedding model changes
- Chunking strategy changes
- More than 50% of chunks changed
- Index corruption detected
