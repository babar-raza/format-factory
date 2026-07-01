---
artifact_id: TC-0016-fods-vector-index-pilot
artifact_type: taskcard
path: taskcards/TC-0016-fods-vector-index-pilot.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-05"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODS vector index pilot taskcard. Implements Tier 3 vector search for FODS spec. Created run027 (2026-05-05). NOT_STARTED — blocked by TC-0015 evaluation results and human approval."
---

# TC-0016: FODS Vector Index Pilot

**Taskcard ID:** TC-0016
**Phase:** 3 (infrastructure sprint)
**Gate:** None — infrastructure, not gated
**Status:** not_started
**Created:** 2026-05-05 (run027)
**Created by:** claude-sonnet-4-6 (run027)
**Blocking:** Tier 3 vector search availability for Gate 4+ spec queries
**Blocked by:** TC-0015 evaluation results + human approval of TC-0016

---

## STOP — Authorization Required

**This taskcard must not be executed until:**
1. TC-0015 evaluation report is reviewed and approved by a human.
2. TC-0015 recommendation is YES (implement Tier 3).
3. A human issues an explicit TC-0016 execution prompt naming this taskcard.

Current state (run027):
- TC-0015: not_started (blocked by human review)
- Tier 3 vector index: does not exist
- No embeddings created

---

## Objective

Implement the FODS Tier 3 vector index as defined in `docs/ai/spec-retrieval-strategy.md`.
The pilot creates:
1. A production embedding tool: `tools/spec-normalize/build_vector_index.py`
2. A FODS vector index stored locally: `.local/spec-cache/fods/1.3/normalized/vector-index/`
3. An extended query tool that adds `--semantic` mode to `query_normalized_spec.py`
4. A validation test: 10 EQ queries from TC-0015 pass recall target

---

## Prerequisites

- [x] Spec Navigation Layer complete — `chunks.jsonl` (940 chunks) (run026)
- [x] `docs/ai/spec-retrieval-strategy.md` — Hybrid Retrieval Strategy (run027)
- [ ] TC-0015 evaluation completed and recommendation is YES
- [ ] Human review and approval of TC-0015 evaluation report
- [ ] Explicit TC-0016 execution prompt issued by human

---

## Scope

### In scope

1. `tools/spec-normalize/build_vector_index.py` — embedding tool
   - Input: `chunks.jsonl` + `text.txt`
   - Output: `.local/spec-cache/{format_id}/{version}/normalized/vector-index/embeddings.npy` + `index.faiss` or equivalent
   - Embedding model: as selected in TC-0015 evaluation
   - Format isolated: `--format-id` required
2. Update `query_normalized_spec.py` to add `--semantic <query_text>` mode (Tier 3)
3. Validation: all 10 EQ queries from TC-0015 achieve ≥ TC-0015 baseline recall

### Out of scope — FORBIDDEN

- Remote LLM endpoint calls for embeddings — FORBIDDEN (local models only)
- Committing the vector index to git — FORBIDDEN (`.local/` only, never committed)
- Using Tier 3 for Gate evidence before TC-0016 is independently verified — FORBIDDEN
- Building multi-format index — FORBIDDEN (format isolation required)
- Using a cloud vector database (Pinecone, Weaviate, Chroma cloud, etc.) — FORBIDDEN (local-only index only)
- Mixing FODS embeddings with any other format's embeddings in the same index — FORBIDDEN
- Reusing a stale index if the source SHA-256 of `chunks.jsonl`, `text.txt`, or the FODS spec PDF has changed — FORBIDDEN (must rebuild from current source)

---

## Implementation Plan

### `build_vector_index.py`

```python
# Interface (not implementation — design only)
# python build_vector_index.py --normalized-dir <dir> --format-id <id> [--model <model-name>]
# Reads: chunks.jsonl (chunk metadata), text.txt (full spec text)
# For each chunk: extract text from text.txt using start_page/end_page, embed, store
# Writes: .local/spec-cache/{format_id}/{version}/normalized/vector-index/
#   embeddings.npy  — numpy array shape (N, dim)
#   chunk_ids.json  — ordered list of chunk_id → index mapping
#   index_meta.yaml — model name, dim, chunk count, format_id, spec_hash, built_at
```

### `query_normalized_spec.py` extension

```
--semantic "natural language query"
```
Returns: top-K chunks with `chunk_id`, `section_ids`, `similarity_score`, `excerpt`.
Each result includes provenance: `spec_version`, `source_hash`, `retrieval_method: tier3_vector`.

### Vector Index Storage Schema

```yaml
# index_meta.yaml
format_id: fods
spec_version: "ODF 1.3"
source_hash: "sha256:92cfe64..."
model_name: "all-MiniLM-L6-v2"  # or nomic-embed-text
model_dim: 384
chunk_count: 940
built_at: "2026-05-05T..."
local_only: true
do_not_commit: true
```

---

## Acceptance Criteria

- [ ] `tools/spec-normalize/build_vector_index.py` — builds FODS vector index
- [ ] `.local/spec-cache/fods/1.3/normalized/vector-index/` — index built and validated
- [ ] `query_normalized_spec.py --semantic` mode works
- [ ] 10 EQ queries from TC-0015: Tier 3 recall meets TC-0015 baseline target
- [ ] `index_meta.yaml` includes source_hash matching FODS spec SHA-256
- [ ] Index is format-isolated: `--format-id fods` required
- [ ] No vector index committed to git
- [ ] Independent verification sprint (DEC-034) completed
- [ ] Human review of pilot results

---

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TC-0015 evaluation | not_started | Must complete first — provides model selection + recall baseline |
| Embedding library | not_checked | sentence-transformers or FAISS — to be confirmed in TC-0015 |
| Local embedding model | not_checked | nomic-embed-text (Ollama) or all-MiniLM-L6-v2 (pip) |
| chunks.jsonl | DONE (run026) | 940 FODS chunks (local-only) |

---

## Related Files

- `docs/ai/spec-retrieval-strategy.md` — strategy (includes Tier 3 design)
- `taskcards/TC-0015-spec-retrieval-strategy-evaluation.md` — prerequisite evaluation
- `.local/spec-cache/fods/1.3/normalized/chunks.jsonl` — chunk metadata (local-only)
- `.local/spec-cache/fods/1.3/normalized/text.txt` — full spec text (local-only)
- `tools/spec-normalize/query_normalized_spec.py` — to be extended with --semantic
