# Taskcard: AI-EMBEDDING-VECTOR-STORE-FOUNDATION

## Objective
Implement embedding/retrieval foundation: LanceDB integration, format-segregated namespaces, chunk manifests, stale-index detection, retrieval audit logging, and embedding model fingerprinting.

## Status
`implemented_blocked_dependency` — namespace_manager.py with format-segregated namespaces, stale-index detection, and cross-namespace rejection implemented in R27 (cb7e05c). Blocked on LanceDB dependency. 9 tests pass.

## Prerequisites
- AI-PLATFORM-FOUNDATION-PLAN Phase 1 operational
- AI-MODEL-DISCOVERY-AND-ROUTING: embedding model discovered
- Normalized spec artifacts available for at least one format
- AI-SPEC-NORMALIZATION-INTEGRATION: normalization produces chunkable artifacts

## Allowed Scope
- Implement `tools/ai/retrieval/embedding_manager.py`
- Implement `tools/ai/retrieval/vector_store.py` (LanceDB wrapper)
- Implement `tools/ai/retrieval/chunk_manifest.py`
- Implement `tools/ai/retrieval/stale_detector.py`
- Implement `tools/ai/retrieval/audit_log.py`
- Create `.local/ai/vector-stores/{format}/` structure
- Create tests in `tests/ai/test_retrieval.py`

## Forbidden Scope
- No product source changes
- No global/shared vector stores
- No cross-format queries without explicit namespace specification
- No embedding indexes committed to git
- No raw spec PDFs embedded (normalized artifacts only)

## Gates
1. LanceDB installed and operational in .venv
2. Embedding model discovered and fingerprinted
3. One format (FODS) fully indexed with chunk manifest
4. Format namespace isolation verified (no cross-contamination)
5. Stale-index detection triggers on source change
6. Retrieval audit log operational
7. Dimension stability check implemented

## Evidence Requirements
- Index metadata for FODS namespace
- Chunk manifest sample
- Namespace isolation test results
- Stale detection test results
- Retrieval audit log samples

## Validation Requirements
- `tests/ai/test_retrieval.py` passes
- Namespace isolation test: zero cross-format results

## Closeout Criteria
- One format fully indexed and retrievable
- All namespace isolation tests pass
- Stale detection operational

## Next Transition
On closeout: Per-format embedding available for acquisition pipeline. Cross-format embeddings deferred to Phase 4+.
