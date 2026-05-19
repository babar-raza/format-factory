# Deterministic Retrieval Baseline (Lane E)
## Sprint: FORMAT-FACTORY-R32-AI-CLEAN-CLOSURE-STATUS-REPAIR-AND-PIPELINE-DEEPENING-MEGA-TRAIN-001

## Purpose
R31 admitted retrieval was return-all. R32 implements a deterministic local retrieval baseline with lexical scoring.

## Implementation
- **File:** tools/ai/retrieval/lexical_retriever.py
- **Method:** TF-IDF lexical scoring with stop word removal
- **Features:**
  - Tokenization with stop word filter
  - Term frequency (TF) computation per chunk
  - Inverse document frequency (IDF) across corpus
  - TF-IDF cosine-like scoring per chunk
  - Format namespace filtering (rejects wrong format_id)
  - Provenance validation (rejects chunks with missing provenance)
  - Staleness detection (rejects chunks with mismatched source_hash)
  - Top-k selection with configurable threshold
  - Explainable score report (matched terms, explanation per chunk)

## Key Classes
- `ScoredChunk` — chunk + score + matched_terms + explanation
- `RetrievalResult` — complete result with ranking metadata

## Key Function
- `retrieve(query, chunks, format_id, top_k, threshold, ...)` — main entry point

## Tests (in test_r32_ai_deepening.py)
1. `test_relevant_chunk_ranked_first` — FODS header chunk ranks high for "FODS spreadsheet XML"
2. `test_irrelevant_chunk_excluded_below_threshold` — weather chunk excluded
3. `test_top_k_limits_results` — top_k=2 returns at most 2
4. `test_stale_chunk_rejected` — mismatched source_hash excluded
5. `test_wrong_namespace_rejected` — FODT chunks excluded when querying fods
6. `test_missing_provenance_rejected` — chunk without source_path excluded
7. `test_empty_query_returns_nothing` — empty string returns 0
8. `test_explainable_score_report` — each result has explanation
9. `test_result_to_dict_serializable` — JSON serialization works

## LanceDB/Vector Status
LanceDB is still not installed. This lexical baseline provides functional ranked retrieval without vector embeddings. When LanceDB becomes available, it can supplement or replace lexical scoring.
