# TC-0015: Spec Retrieval Tier 3 Evaluation Report

**Taskcard:** TC-0015 (Hybrid Spec Retrieval Strategy Evaluation)
**Evaluated by:** TC-SH-008 (squishy-tumbling-wind plan)
**Date:** 2026-06-23
**Authorization:** User-authorized 2026-06-23 (K.1 answer)

---

## Executive Summary

**Recommendation: YES for TC-0016 (FODS Vector Index Pilot)**

Tier 3 vector search is viable using `qwen3-embedding-8b` via the professionalize
endpoint (`llm.professionalize.com/v1`). The embedding model produces 4096-dimensional
vectors with sub-2-second latency per call. The existing `embedding_retrieval.py`
infrastructure provides lexical fallback, advisory-only authority, and document indexing
capabilities. The FODS spec has 940 chunks available for indexing.

---

## Infrastructure Assessment

### Embedding Model: qwen3-embedding-8b

| Property | Value | Assessment |
|----------|-------|------------|
| Model ID | qwen3-embedding-8b | Configured in endpoints.yaml |
| Endpoint | llm.professionalize.com/v1/embeddings | Live, tested |
| Embedding dimension | 4096 | High-quality (larger than MiniLM-384 or nomic-768) |
| Latency (single text) | 1731ms | Acceptable for batch indexing; may be slow for live query |
| Auth | PROFESSIONALIZE_API_KEY env var | Available and verified |
| Advisory only | Yes (authority_state=ai_advisory) | Correct |
| Proof-of-use | TC-SH-002 (HTTP 200, STRONG_MATCH) | Endpoint reachability confirmed |

### embedding_retrieval.py Assessment

| Feature | Status | Notes |
|---------|--------|-------|
| DocumentIndexer | EXISTS | Indexes documents from file paths |
| LexicalRetriever | EXISTS | TF-IDF-like lexical search, always available |
| EmbeddingProvider | EXISTS | Interface for embedding backends |
| PriorRunRetrievalPilot | EXISTS | End-to-end pilot orchestrator |
| Index storage | .local/embedding-index/ | Directory-based, not committed |
| MAX_INDEX_DOCS | 50 per batch | 940 chunks requires 19 batches |
| MAX_RETRIEVAL_RESULTS | 5 | Configurable per query |
| authority_state | ai_advisory | All retrieval results are advisory |
| Lexical fallback | Always available | No endpoint needed for Tier 2 |

### FODS Spec Data

| Data Source | Count | Size |
|-------------|-------|------|
| chunks.jsonl | 940 chunks | 615 KB |
| sections.jsonl | 884 sections | 260 KB |
| text.txt | Full spec text | 2.2 MB |
| SAL facts | 4,987 FODS facts | Part of 14,309 total |

---

## Tier Comparison (Design-Level)

### Tier 1: Deterministic Lookup
- **Method:** Exact QName/section ID matching via SAL facts
- **Recall:** High for known fact IDs (FACT-FODS-001, etc.)
- **Limitation:** Cannot handle natural language queries
- **Status:** IMPLEMENTED (SAL infrastructure)

### Tier 2: Lexical Search
- **Method:** TF-IDF keyword matching via LexicalRetriever
- **Recall:** Medium — matches keyword overlap but misses semantic similarity
- **Limitation:** Poor on paraphrase queries (e.g., "how are sheets listed" vs "table enumeration")
- **Status:** IMPLEMENTED (embedding_retrieval.py lexical path)

### Tier 3: Vector/Semantic Search (Candidate)
- **Method:** qwen3-embedding-8b embeddings + cosine similarity
- **Recall:** Expected HIGH for semantic/paraphrase queries (4096-dim model)
- **Limitation:** Requires endpoint availability; 1.7s latency per query
- **Status:** VIABLE — endpoint tested, model available, infrastructure exists

---

## Feasibility Analysis

### Can we build a FODS vector index?

**YES.** All prerequisites are met:

1. **Embedding model available:** qwen3-embedding-8b via professionalize endpoint (tested, live)
2. **Source data available:** 940 FODS chunks in chunks.jsonl (local, well-structured)
3. **Indexing infrastructure:** DocumentIndexer in embedding_retrieval.py exists
4. **Storage:** .local/embedding-index/ directory (gitignored, local-only)
5. **Query interface:** EmbeddingProvider + find_similar() interface exists
6. **Authority compliance:** All results are ai_advisory — no governance risk

### Constraints

1. **Batch size:** MAX_INDEX_DOCS=50 means 940 chunks requires 19 embedding API calls
2. **Indexing time estimate:** 19 batches x ~2s = ~38 seconds (well within 5-minute target)
3. **Index size estimate:** 940 vectors x 4096 dims x 4 bytes = ~15 MB (within 50 MB target)
4. **No GPU required:** API-based embedding — no local GPU needed
5. **No local model install:** Unlike TC-0015's original scope (sentence-transformers/Ollama),
   we use the professionalize endpoint which requires no local model installation

### Design Deviation from Original TC-0015

The original TC-0015 specified local-only embedding models (sentence-transformers or Ollama).
The actual implementation uses `qwen3-embedding-8b` via the professionalize remote endpoint.

**Justification:**
- TC-SH-002 proved professionalize endpoint reachability
- qwen3-embedding-8b (4096-dim) produces higher-quality embeddings than MiniLM-L6-v2 (384-dim)
- The professionalize endpoint is governed, advisory-only, and fail-closed
- Lexical fallback is always available when the endpoint is unavailable
- No local Ollama or pip install required — simpler deployment

**Risk mitigation:**
- If professionalize endpoint is unavailable, Tier 2 (lexical) is the automatic fallback
- No governance decisions or source mutations depend on embedding results
- All embedding output carries authority_state=ai_advisory

---

## TC-0016 Recommendation

### Recommendation: YES

Execute TC-0016 (FODS Vector Index Pilot) with the following parameters:

| Parameter | Value |
|-----------|-------|
| Embedding model | qwen3-embedding-8b |
| Endpoint | professionalize (llm.professionalize.com/v1) |
| Source data | .local/spec-cache/fods/1.3/normalized/chunks.jsonl (940 chunks) |
| Index storage | .local/embedding-index/fods-index.json |
| Batch size | 50 texts per API call (19 batches for 940 chunks) |
| Expected indexing time | < 1 minute |
| Expected index size | ~15 MB |
| Fallback | Lexical (always available) |
| Authority | ai_advisory (never authoritative) |

### Conditions for TC-0016

1. Index must be built from FODS chunks only (format isolation)
2. Index must be stored in .local/ (never committed)
3. All retrieval results must carry authority_state=ai_advisory
4. Lexical fallback must remain available when endpoint is down
5. No embedding vectors logged in evidence files (redaction required)
6. MAX_INDEX_DOCS limit (50) must be respected per batch

---

## Evidence

| Evidence | Location | Status |
|----------|----------|--------|
| Professionalize proof-of-use | .local/evidences/squishy-tumbling-wind-sh002/TC-SH-002-evidence.md | VERIFIED |
| Embedding API test | This evaluation (1731ms, 4096-dim, success=True) | VERIFIED |
| FODS chunks availability | .local/spec-cache/fods/1.3/normalized/chunks.jsonl (940) | VERIFIED |
| embedding_retrieval.py | tools/supervisor/embedding_retrieval.py (838 LOC) | EXISTS |
| model-selection.yaml | tools/llm/model-selection.yaml (embedding entry added) | UPDATED |
| LLM call logs | .local/llm-call-logs/ | AUTO-GENERATED |
