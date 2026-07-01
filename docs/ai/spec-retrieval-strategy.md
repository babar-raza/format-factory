---
artifact_id: spec-retrieval-strategy-v1
artifact_type: documentation
path: docs/spec-retrieval-strategy.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-05"
reusable: true
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Hybrid Spec Retrieval Strategy document. Defines deterministic→lexical→vector search hierarchy for normalized spec artifacts. Created run027."
---

# Hybrid Spec Retrieval Strategy

**Document type:** Design Policy
**Created:** run027 (2026-05-05)
**Status:** Proposed — awaiting human review (TC-0015) before implementation

---

## 1. Purpose

This document defines how agents retrieve information from normalized specification artifacts.
The strategy is a three-tier hierarchy: deterministic lookup → lexical search → (future) vector
search. It applies to all format acquisition work using the Spec Navigation Layer built in run026.

Agents **must** use this hierarchy. Jumping to vector search before deterministic and lexical
lookups are exhausted is not permitted. Format isolation rules prevent cross-format query
bleed. All retrieval results must include source provenance (spec version + SHA-256 hash).

---

## 2. Retrieval Tiers

### Tier 1 — Deterministic (always first)

**Use when:** The agent knows an exact section number or element name.

| Tool | Invocation | When to Use |
|---|---|---|
| `query_normalized_spec.py --section` | `--section "3.1.2"` | Known section ID from spec or prior citation |
| `query_normalized_spec.py --element` | `--element "office:document"` | Known XML element name |
| `query_normalized_spec.py --page` | `--page 90` | Known page number from citation |

**Rules:**
- Always attempt Tier 1 before any other tier.
- Tier 1 results include cited page, section ID, and source hash — use these in all evidence artifacts.
- If Tier 1 returns results, do not fall through to Tier 2 unless additional context is needed.

---

### Tier 2 — Lexical (keyword search)

**Use when:** The agent does not have an exact section number, but knows relevant keywords.

| Tool | Invocation | When to Use |
|---|---|---|
| `query_normalized_spec.py --keyword` | `--keyword "table:formula"` | Searching by element, attribute, or concept name |
| `query_normalized_spec.py --sample-req` | `--sample-req minimal` | Structured requirement lookup by category |

**Rules:**
- Use Tier 2 only if Tier 1 returns no results or insufficient context.
- Lexical results are returned with page and section context. Verify the result is from the correct section before citing.
- Keyword queries may return false positives (TOC hits). Check that the result text describes the concept, not just references it.
- Log the query in the run record as: `SPEC_QUERY: lexical keyword="<kw>" result_count=N format_id=fods`.

---

### Tier 3 — Vector / Semantic Search (future — not yet implemented)

**Use when:** Tiers 1 and 2 fail to surface relevant content for a complex, natural-language question.

**Current status:** NOT IMPLEMENTED. Evaluation design only (TC-0015, TC-0016).

**Design intent:**
- Embeddings are computed from `chunks.jsonl` (940 FODS chunks, metadata only — no full text in index).
- Full chunk text is retrieved from `text.txt` using `start_page`/`end_page` stored in the chunk record.
- Each embedding is stored with: `chunk_id`, `format_id`, `start_page`, `end_page`, `section_ids`, `word_count`.
- Vector index is **format-isolated** — one index per format, never shared across formats.
- Query returns top-K chunks with: `chunk_id`, `section_ids`, `similarity_score`, `excerpt`.

**Provenance requirement (Tier 3):** Every vector query result used in an evidence artifact must include:
- `chunk_id` (stable ID from `chunks.jsonl`)
- `spec_version` (ODF 1.3 for FODS)
- `source_hash` (sha256 of original PDF, stored in chunk record)
- `retrieval_method: vector`
- `similarity_score`

**Gate restriction:** Tier 3 vector search may not be used for Gate evidence until TC-0016 pilot is complete and independently verified. Until then, all Gate evidence must cite Tier 1 or Tier 2 results only.

---

## 3. Search Hierarchy Decision Flow

```
Agent has a spec question
        |
        v
Step 1: Is exact section number known?
        YES → Tier 1: --section <id>
        NO  → Step 2
        |
        v
Step 2: Is exact element/attribute name known?
        YES → Tier 1: --element <name>
        NO  → Step 3
        |
        v
Step 3: Is a keyword (term, concept, element name fragment) known?
        YES → Tier 2: --keyword <term>
        NO  → Step 4
        |
        v
Step 4: Is the question a structured sample requirement?
        YES → Tier 2: --sample-req <category>
        NO  → Step 5
        |
        v
Step 5: Tier 3 (if implemented and authorized)
        NOT YET AVAILABLE → Log gap and use Tier 1/2 with best available term
```

---

## 4. Format Isolation Rules

Each normalized spec and its index are **strictly isolated by format_id**. This prevents
incorrect spec text from bleeding into evidence for a different format.

Rules:
1. Every query tool call must specify `--format-id <id>` (e.g. `--format-id fods`).
2. Tier 3 vector indexes are one-per-format. A FODS index must never be queried for XLSX evidence.
3. `sections.jsonl`, `chunks.jsonl`, `pages.jsonl` are stored under `.local/spec-cache/{format_id}/{version}/normalized/`.
4. If querying for a format not yet normalized, stop and log a gap — do not use a different format's index.

---

## 5. Local-First Policy

All retrieval operates on locally cached spec artifacts in `.local/spec-cache/`. No remote
calls are made during spec retrieval. This applies to all three tiers.

**Rationale:**
- Network availability must not block acquisition work.
- Spec content must be pinned to a specific version (ODF 1.3 for FODS).
- SHA-256 verification requires the local file to be unchanged.

**Re-download policy:** Spec re-download is governed by `docs/python-foss/specification-cache.md` and
requires explicit execution prompt authorization. It is not triggered by retrieval queries.

---

## 6. Provenance Requirements for Evidence Artifacts

Any spec excerpt or requirement cited in an evidence artifact (spec-evidence.md, legal-notes.md,
parser-notes.md, Gate evidence bundle) must include:

```yaml
spec_citation:
  section_id: "3.1.2"      # From query result
  page: 90                   # From query result
  source_hash: "sha256:92cfe64..."  # From query tool output
  spec_version: "ODF 1.3"
  retrieval_method: "tier1_section"  # tier1_section | tier1_element | tier2_keyword | tier2_sample_req | tier3_vector
```

Evidence artifacts that cite spec content without provenance are incomplete and must be updated
before the associated gate is submitted for human review.

---

## 7. Evaluation Design (Tier 3 — Future)

Before Tier 3 is implemented, the following evaluation must be completed (TC-0015):

| Evaluation Step | Owner | Status |
|---|---|---|
| Select embedding model (local-first: e.g. sentence-transformers, nomic-embed-text) | Developer | not_started |
| Build FODS chunk embeddings from `chunks.jsonl` + `text.txt` (pilot: 940 chunks) | Developer | not_started |
| Evaluate recall: does vector search surface correct section for 10 known test queries? | Developer | not_started |
| Compare vector recall vs. lexical recall on same 10 queries | Developer | not_started |
| Evaluate false positive rate (wrong section returned as top-1) | Developer | not_started |
| Document latency (indexing time, query time on Windows 11, no GPU) | Developer | not_started |
| Evaluate index size and storage requirements | Developer | not_started |
| Propose final design: embedding model, index library (e.g. FAISS, Chroma, hnswlib), storage format | Developer | not_started |
| Human review of evaluation results before TC-0016 is authorized | Human | not_started |

**TC-0015** governs this evaluation sprint. **TC-0016** governs the FODS vector index pilot
implementation (only after TC-0015 evaluation is reviewed and approved by human).

---

## 8. Interaction with AGENTS.md

Agents operating in Phase 3+ must:
1. Use the query tools listed in this document rather than scanning `text.txt` directly.
2. Follow the tier hierarchy: Tier 1 → Tier 2 → (future) Tier 3.
3. Include spec citation provenance in all evidence artifacts.
4. Never use a different format's index for FODS evidence.

AGENTS.md Section W (Normalization Layer) governs the underlying tools. This document
governs the retrieval strategy layered on top of those tools.

---

## 9. Files Referenced

| File | Location | Purpose |
|---|---|---|
| `sections.jsonl` | `.local/spec-cache/fods/1.3/normalized/` | 884 FODS spec sections (local-only) |
| `chunks.jsonl` | `.local/spec-cache/fods/1.3/normalized/` | 940 chunks metadata (local-only) |
| `page-map.yaml` | `.local/spec-cache/fods/1.3/normalized/` | 705 pages → section mapping (local-only) |
| `text.txt` | `.local/spec-cache/fods/1.3/normalized/` | Full extracted spec text (local-only) |
| `query_normalized_spec.py` | `tools/spec-normalize/` | Tier 1 + Tier 2 query tool |
| `build_section_index.py` | `tools/spec-normalize/` | Builds sections.jsonl + page-map.yaml |
| `build_chunk_index.py` | `tools/spec-normalize/` | Builds chunks.jsonl |
| `export_sample_requirements.py` | `tools/spec-normalize/` | Exports sample-requirements.yaml |

---

## 10. Revision History

| Run | Change |
|---|---|
| run027 | Document created. Tier 1 + Tier 2 implemented. Tier 3 evaluation design. TC-0015 + TC-0016 planned. |
