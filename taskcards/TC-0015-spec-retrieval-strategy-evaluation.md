---
artifact_id: TC-0015-spec-retrieval-strategy-evaluation
artifact_type: taskcard
path: taskcards/TC-0015-spec-retrieval-strategy-evaluation.md
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
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Hybrid Spec Retrieval Strategy evaluation taskcard. Evaluates Tier 3 vector search design. Created run027 (2026-05-05). NOT_STARTED — blocked by human review of TC-0015 scope and docs/spec-retrieval-strategy.md."
---

# TC-0015: Hybrid Spec Retrieval Strategy Evaluation

**Taskcard ID:** TC-0015
**Phase:** 3 (planning / research sprint)
**Gate:** None — infrastructure research, not gated
**Status:** not_started
**Created:** 2026-05-05 (run027)
**Created by:** claude-sonnet-4-6 (run027)
**Blocking:** TC-0016 (FODS vector index pilot)
**Blocked by:** Human review and approval of `docs/spec-retrieval-strategy.md` + explicit TC-0015 execution prompt

---

## STOP — Authorization Required

**This taskcard must not be executed until:**
1. A human reviews `docs/spec-retrieval-strategy.md` and issues an explicit TC-0015 execution prompt.
2. TC-0015 is explicitly assigned to an agent in the execution prompt.

Current state (run027):
- Tier 1 and Tier 2 retrieval: IMPLEMENTED (run026 Navigation Layer)
- Tier 3 vector search: DESIGN ONLY (this taskcard)
- No embeddings, no vector DB, no model calls

---

## Objective

Evaluate whether adding Tier 3 vector / semantic search to the Spec Retrieval Stack improves
spec navigation recall for complex queries that Tier 1 (deterministic) and Tier 2 (lexical)
fail to answer adequately.

Produce an evaluation report: `docs/spec-retrieval-evaluation-report.md`.
This report is the prerequisite for TC-0016 (FODS vector index pilot implementation).

---

## Prerequisites

- [x] Spec Navigation Layer complete — `chunks.jsonl` (940 chunks), `sections.jsonl` (884 sections) (run026)
- [x] `docs/spec-retrieval-strategy.md` drafted — Hybrid Retrieval Strategy (run027)
- [ ] Human review and approval of `docs/spec-retrieval-strategy.md`
- [ ] Explicit TC-0015 execution prompt issued by human

---

## Scope

### In scope

1. Design and execute a 10-query evaluation against FODS spec
2. For each query: run Tier 1, Tier 2, (candidate Tier 3 model) and compare recall
3. Select candidate embedding model (local-first: sentence-transformers or nomic-embed-text)
4. Build a proof-of-concept chunk embedding set (940 FODS chunks only — no index tool created yet)
5. Evaluate: recall, false positive rate, latency, storage size
6. Produce evaluation report with recommendation: YES/NO for TC-0016

### Out of scope — FORBIDDEN

- Building a production vector index — FORBIDDEN (TC-0016)
- Calling any remote LLM endpoint for embeddings — FORBIDDEN (local-only models only)
- Storing embeddings in committed files — FORBIDDEN (local-only, `.local/`)
- Using evaluation results to alter any Gate evidence before TC-0016 is approved — FORBIDDEN
- Using a cloud vector database (Pinecone, Weaviate, Chroma cloud, etc.) — FORBIDDEN (local-only)
- Mixing FODS embeddings with any other format's embeddings — FORBIDDEN (format isolation required)
- Reusing a stale embedding if the source `chunks.jsonl` or `text.txt` SHA-256 has changed — FORBIDDEN (must rebuild)

---

## Evaluation Design

### 10 Test Queries (to be executed against FODS spec)

| Query ID | Query | Expected Section | Difficulty |
|---|---|---|---|
| EQ-001 | "What is the root element for flat XML spreadsheets?" | §3.1.2 | Easy (Tier 1 deterministic) |
| EQ-002 | "How are sheets enumerated in a spreadsheet document?" | §9.4 | Medium (Tier 2 lexical) |
| EQ-003 | "What namespace prefix is used for formula attributes?" | §9.4 (oooc: prefix) | Medium (Tier 2 lexical) |
| EQ-004 | "What are the conformance requirements for ODF spreadsheet documents?" | §2.2.4 | Hard (Tier 2 multi-keyword) |
| EQ-005 | "How is a boolean cell value represented?" | §9.4 (office:value-type=boolean) | Hard (Tier 2/3) |
| EQ-006 | "How are repeated empty columns handled?" | §9.1.5 | Hard (Tier 2/3) |
| EQ-007 | "What is the most frequently cross-referenced attribute section?" | §20.8.3 | Hard (semantic only) |
| EQ-008 | "Describe the styles inheritance model for cells" | Multiple sections | Very hard (semantic only) |
| EQ-009 | "How does ODF 1.3 define text:p within table cells?" | §5.1.3, §9.4 | Hard (Tier 2/3) |
| EQ-010 | "What XML namespaces are required for a conforming FODS document?" | §3.1.2 | Medium (Tier 1/2) |

### Evaluation Metrics

| Metric | Definition | Target |
|---|---|---|
| Tier 1 recall | % of queries where Tier 1 returns the correct section as top-1 | Baseline |
| Tier 2 recall | % of queries where Tier 2 returns the correct section in top-3 | Baseline |
| Tier 3 recall (candidate) | % of queries where vector top-1 is correct section | Must exceed Tier 2 recall for hard queries |
| Tier 3 false positive rate | % of vector top-1 results pointing to irrelevant section | Must be < 20% |
| Tier 3 indexing time | Time to embed 940 chunks on Windows 11 (no GPU) | < 5 minutes |
| Tier 3 query latency | Time per query | < 1 second |
| Index size on disk | Size of embeddings file | < 50 MB |

---

## Steps (to be executed after explicit TC-0015 prompt)

1. Read `AGENTS.md` and `docs/spec-retrieval-strategy.md`.
2. Read `plans/master-plan.md` to confirm TC-0015 execution is authorized.
3. For EQ-001 to EQ-010, run Tier 1 and Tier 2 queries using existing tools. Record results.
4. Select candidate embedding model: prefer `nomic-embed-text` (local Ollama) or `all-MiniLM-L6-v2` (sentence-transformers, no Ollama required).
5. Build proof-of-concept chunk embeddings from `chunks.jsonl` + `text.txt` (local-only, `.local/`).
6. Run all 10 queries against candidate vector index. Record top-3 results + similarity scores.
7. Compute recall, false positive rate, latency, storage size.
8. Document findings in `docs/spec-retrieval-evaluation-report.md`.
9. Produce recommendation: YES or NO for TC-0016.
10. Request human review of evaluation report before TC-0016 is authorized.

---

## Acceptance Criteria

- [ ] 10-query evaluation table: Tier 1, Tier 2, Tier 3 (candidate) recall scores
- [ ] Candidate embedding model selected and documented
- [ ] Proof-of-concept embeddings built (local-only, not committed)
- [ ] `docs/spec-retrieval-evaluation-report.md` produced with metrics
- [ ] Recommendation for TC-0016: YES or NO with rationale
- [ ] Independent verification sprint completed (DEC-034)
- [ ] Human review of evaluation report

---

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| Spec Navigation Layer | DONE (run026) | chunks.jsonl, sections.jsonl, text.txt |
| `docs/spec-retrieval-strategy.md` | DONE (run027) | Human review pending |
| Local embedding model available | NOT CHECKED | Requires local Ollama or pip install sentence-transformers |
| TC-0016 | not_started | Blocked by this taskcard |

---

## Related Files

- `docs/spec-retrieval-strategy.md` — retrieval strategy design (prerequisite)
- `.local/spec-cache/fods/1.3/normalized/chunks.jsonl` — 940 FODS chunks (local-only)
- `.local/spec-cache/fods/1.3/normalized/text.txt` — full spec text (local-only)
- `tools/spec-normalize/query_normalized_spec.py` — Tier 1 + Tier 2 query tool
- `taskcards/TC-0016-fods-vector-index-pilot.md` — next step (blocked by this)
