# Spec Retrieval and RAG Policy

**Document type:** Normative retrieval policy
**Authority level:** Normative (extends docs/spec-retrieval-strategy.md)
**Created:** 2026-05-13

---

## Purpose

This document extends `docs/spec-retrieval-strategy.md` with specific RAG (Retrieval-Augmented Generation) governance for commercial implementation work. The existing three-tier retrieval strategy remains authoritative; this document adds AI-specific guardrails.

---

## Existing Policy (Read First)

Full retrieval strategy: `docs/spec-retrieval-strategy.md`

Summary of existing three-tier hierarchy:
- **Tier 1 (Deterministic):** Direct index lookup by section/element name → authoritative
- **Tier 2 (Lexical):** Full-text search over normalized spec → authoritative with citation
- **Tier 3 (Vector/RAG):** Semantic similarity search → candidate retrieval only (NOT authorized for gate evidence as of 2026-05-13)

---

## RAG Authorization Status

| Retrieval Type | Status | Gate Evidence |
|---------------|--------|---------------|
| Tier 1 deterministic | AUTHORIZED | YES |
| Tier 2 lexical | AUTHORIZED | YES with citation |
| Tier 3 vector/RAG | DESIGN ONLY (taskcards TC-0015, TC-0016) | NO — not yet authorized |

**Tier 3 vector search is NOT yet authorized for gate evidence production.** It may be used for local exploration and draft proposal generation only.

---

## Local Spec Artifacts (Immutable Sources)

All retrieval operates over local artifacts only:

| Artifact | Location | Provenance |
|----------|----------|-----------|
| Spec PDF | `.local/spec-cache/fods/1.3/` | SHA-256 verified, OASIS ODF 1.3 |
| Normalized text | `.local/spec-normalize/fods/text.txt` | Derived from PDF, build-time |
| Chunk index | `.local/spec-normalize/fods/pages.jsonl` | Derived, 782 pages |
| Citation map | Built by `tools/spec-normalize/build_citation_map.py` | Deterministic |

**Spec PDFs are immutable source artifacts.** They are never modified, never committed, and never sent to remote AI endpoints without explicit legal review and human authorization.

---

## RAG Guardrails

When using any retrieval-augmented generation:

1. **Source first:** Every retrieved chunk must cite: file path + page number or section ID
2. **Candidate, not truth:** Retrieval finds candidates. Spec text is the truth.
3. **Local only:** No spec text transmitted to remote endpoints without authorization (AGENTS.md §T9)
4. **Validate citations:** AI-produced citations must be spot-checked against actual spec text
5. **Reject hallucinations:** If AI cites a spec claim that cannot be located in the local spec, classify as `REJECTED_UNSOURCED`
6. **No vector DB commits:** Vector indexes and embedding files are local working artifacts; must not be committed unless explicitly approved
7. **Evidence bundles exclude vector DB:** Include retrieval summaries and cited sources, not raw index files

---

## Provenance Requirements for RAG Output

Any spec claim produced via RAG that feeds into authority files must include:

```yaml
claim: "FODS sheet names are stored in table:table/@table:name"
provenance:
  retrieval_tier: 2  # or 1, not 3 for gate evidence
  source_file: ".local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf"
  page: 142
  section: "9.1.2"
  chunk_hash: "sha256:..."
  validated: true
  validated_by: "agent+human spot-check"
```

---

## Embedding Policy (Extends docs/llm-and-embedding-strategy.md)

- Embeddings may be created over: normalized spec text, verified facts, requirements YAML
- Embeddings must NOT be created over: raw LLM transcripts, uncommitted drafts
- Embedding model preference: local models first (e.g., nomic-embed-text, all-MiniLM-L6-v2)
- Remote embedding APIs: require explicit authorization and must not receive spec text
- Index files: stored in `.local/embeddings/` — gitignored, never committed
- Index rebuild triggers: spec update, normalization change, schema change

---

## RAG Output Lifecycle

```
Spec chunk retrieved
  → chunk_hash logged
  → citation extracted (file + page + section)
  → AI synthesizes claim from chunk
  → claim validated against raw spec text (spot-check)
  → claim classified: ACCEPTED / REJECTED_UNSOURCED / NEEDS_REVIEW
  → accepted claims → schema-validated artifact
  → artifact → implementation or test
  → implementation → deterministic test
  → test PASS → authority file may reference
```

---

## Cross-References

- Three-tier retrieval hierarchy: `docs/spec-retrieval-strategy.md`
- LLM and embedding strategy: `docs/llm-and-embedding-strategy.md`
- Spec content in prompts (LLM rules): `AGENTS.md §T9`
- AI operating model: `docs/ai-usage-operating-model.md`
- Spec normalization: `tools/spec-normalize/` + `docs/specification-normalization.md`
