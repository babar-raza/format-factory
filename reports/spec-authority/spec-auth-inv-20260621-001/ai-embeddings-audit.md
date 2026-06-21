# Specs Authority Layer — AI / Embeddings Usage Audit
**Run ID:** spec-auth-inv-20260621-001
**Date:** 2026-06-21

---

## Executive Statement

**AI is NOT the authority in this system.** The authority is the cached spec file verified by SHA-256. GOVERNANCE.md §22.3 explicitly states: "No LLM output becomes a verified requirement unless those facts are independently grounded in source spec citations and deterministic validation." This principle is well-documented and enforced at the governance layer.

However, the AI governance infrastructure is scaffolded at a level that significantly exceeds what is currently operational. The production gap is not AI over-use but rather that the spec authority pipeline itself is not complete enough to safely introduce AI assistance.

---

## 1. Current AI Usage

### 1.1 AI Authority Lifecycle Validator (`tools/ai/validators/authority_lifecycle.py`)

| Field | Value |
|-------|-------|
| Purpose | Enforces state machine: ai_draft → schema_validated → source_cited → source_verified → contradiction_checked → evaluator_passed → accepted_for_planning → accepted_for_tests → accepted_for_source_requirements → authoritative_after_gate |
| Currently active | YES — module importable, 7 unit tests pass |
| Affects authority | YES — blocks artifacts from reaching "authoritative" without source citation |
| Input data | Python dataclass state enum; no LLM calls inside |
| Output data | Boolean (can_transition) + error list |
| Source-cited | N/A — this is a governance validator |
| Deterministic | YES — pure state machine |
| Tests | 7/7 passing |
| Failure behavior | Raises or returns False; calling code can ignore (no wiring to acquisition pipeline) |
| Wired to product pipeline | NOT WIRED — exists at library level but no acquisition prompt calls it |
| Risk | LOW — correct design; gap is that it's not wired |

### 1.2 Lexical Retriever (`tools/ai/retrieval/lexical_retriever.py`)

| Field | Value |
|-------|-------|
| Purpose | TF-based lexical scoring over spec text chunks; no vector DB required |
| Currently active | PARTIAL — importable; used by embedding_retrieval.py |
| Affects authority | NO — output is advisory only |
| Input data | Spec chunk text |
| Output data | Ranked chunks by keyword match |
| Source-cited | YES — returns chunk with section/page context |
| Deterministic | YES — TF scoring is deterministic |
| Tests | UNKNOWN — no dedicated tests found |
| Failure behavior | Returns empty results |
| Risk | LOW — safe advisory use; proper fallback |

### 1.3 Supervisor Embedding Retrieval (`tools/supervisor/embedding_retrieval.py`)

| Field | Value |
|-------|-------|
| Purpose | Advisory-only retrieval over prior evidence declarations, taskcards, and defect records |
| Currently active | PARTIAL — module exists; advisory use only |
| Affects authority | NO — hardcoded authority_state = "ai_advisory" |
| Input data | Evidence declarations, taskcards (YAML); NOT spec text |
| Output data | Similar past evidence documents with advisory text |
| Source-cited | NO (advisory text only, not spec-backed) |
| Deterministic | Lexical mode YES; embedding mode requires external endpoint (not configured) |
| Tests | Not found |
| Failure behavior | Returns empty results; non-blocking |
| Logging | advisory_text field; no audit log per fact |
| Usage | Supervisor healing loop advisory |
| Risk | LOW — correctly scoped to advisory; does not affect authority |

---

## 2. Current Embeddings/Vector Usage

**No active vector DB or embedding generation is running.** This is confirmed by:

1. `tools/ai/retrieval/namespace_manager.py` — `query()` is a STUB: `"This is a stub — real implementation requires LanceDB."`
2. `tools/ai/contracts/forbidden-runtime-imports.yaml` — explicitly forbids `qdrant`, `chromadb`, `pinecone` at import time
3. `.claude/settings.json` description: `"Embeddings/vector DB/vector index NOT authorized"`
4. No LanceDB, FAISS, or other vector library in `pyproject.toml` or any `requirements.txt`
5. No `.local/ai/vector-stores/` directory exists in the repo

The `namespace_manager.py` has a fully designed interface (format-segregated stores, embedding model fingerprint, staleness detection, cross-namespace contamination prevention) but the implementation body is absent.

---

## 3. Dormant AI Components

| Component | Path | Designed For | Why Dormant | Risk if Activated Without Controls |
|-----------|------|-------------|-------------|-------------------------------------|
| Vector store | `tools/ai/retrieval/namespace_manager.py` | Format-segregated semantic search over spec chunks | LanceDB not authorized; STUB | Would require: source hash invalidation, format isolation, no authority contamination controls |
| AI synthesis | `tools/ai/synthesis/` | AI-assisted requirement synthesis | Not implemented beyond scaffolding | Would need: source_cited gate before any output used |
| E2E AI pipeline | `tools/ai/pipeline/e2e_pilot.py` | Full pipeline from spec query to requirement | Partial | Would need: all authority lifecycle gates enforced |
| Test generation | `tools/ai/test_generation/` | AI-assisted test generation from requirements | Scaffolded | Would need: spec fact → requirement → test traceability |
| Agentic runner | `tools/ai/agentic/scoped_runner.py` | Scoped agentic execution of spec queries | Not wired to SAL | Would need: audit trail per fact touched |
| Model router | `tools/ai/control_plane/model_router.py` | Routes to right AI model per role | Works but no embedding model configured | Would need: embedding model with format segregation |

---

## 4. Missing-But-Useful AI Support

These are areas where AI/embeddings could safely support (not replace) the spec authority layer:

| Use Case | Safe Level | Controls Required |
|----------|-----------|-------------------|
| Candidate spec section finder: given a fact description, find likely spec sections | SAFE with controls | Must cite section + source hash; output is CANDIDATE only for human/deterministic confirmation |
| Coverage gap suggester: given verified facts, suggest uncovered spec sections | SAFE | Output is advisory; human must accept before fact is registered |
| Contradiction detector: check if two facts from different spec versions conflict | SAFE | Only surfaces contradictions; does not resolve |
| Draft requirement generator: given verified fact + section, draft a requirement | SAFE | Must remain in ai_draft state until source_cited + source_verified transitions complete |
| Spec change alerter: detect semantic differences between spec versions | SAFE | Comparison against SHA-verified text only; no LLM final authority |

---

## 5. Unsafe AI Paths

The following patterns are explicitly forbidden and would constitute authority contamination:

1. **AI-generated fact without source_id** — SAL master runner already does this (unintentionally). Must be fixed.
2. **LLM summary replacing spec text citation** — AGENTS.md §W5 forbids this explicitly.
3. **Vector search result as authoritative requirement** — Output must remain advisory until text-verified.
4. **Cross-format embedding contamination** — namespace_manager.py correctly prevents this by design.
5. **AI promoting its own output through authority lifecycle** — state machine requires external confirmation at each step.
6. **Embeddings cached without source hash** — stale embeddings from an outdated spec version would silently mislead.

---

## 6. Recommended AI Support Architecture

```
Tier 0 — Deterministic (current foundation, keep as-is):
  spec-index.yaml SHA-256 → normalize → section index → citation map
  These NEVER involve AI.

Tier 1 — Lexical AI-assisted discovery (safe to add now):
  query_normalized_spec.py --keyword augmented by lexical_retriever.py
  Output: candidate spec sections with source hash + page citation
  Status: advisory until confirmed by text match

Tier 2 — Embedding-assisted ranking (add after workbench coverage ≥ 80%):
  namespace_manager.py implementation with LanceDB
  REQUIRES: source hash invalidation on spec update, format segregation enforced
  Output: ranked candidate sections, advisory, must pass through source_verified gate

Tier 3 — AI synthesis of draft requirements (add after Tier 2 proven):
  ai/synthesis/ tools
  Input: verified_facts + spec sections
  Output: draft requirements in ai_draft state
  REQUIRES: human confirmation before accepted_for_planning transition

NEVER:
  AI output directly promoted to authoritative without authority lifecycle traversal
  Cross-format AI context bleed
  Embeddings without version-pinned model fingerprint
```

---

## 7. Controls Required Before Any AI Output Can Affect Requirements

Before any AI component can affect SAL output:

1. **Source hash gate**: AI only operates on chunks whose parent spec file has a verified SHA-256 in spec-index.yaml.
2. **Format isolation gate**: AI queries are scoped to a single format_id namespace; cross-format is forbidden.
3. **Authority lifecycle gate**: All AI-produced artifacts start at `ai_draft` and must traverse the full lifecycle (schema_validated → source_cited → source_verified → ...) before reaching `authoritative_after_gate`.
4. **Source_id requirement**: Every AI-produced fact must carry source_id, section_id, page, and spec_sha256 before being written to workbench.
5. **Text verification gate**: `run_fact_verification.py` text search must confirm fact text appears in spec before promotion beyond `source_cited`.
6. **No AI self-certification**: The authority lifecycle forbids skipping steps; an AI cannot promote its own output.
7. **Model fingerprint**: Embedding index must include model_id + model_fingerprint; index is invalidated if model changes.
8. **Audit log**: Every AI-touched fact must log query, result count, scores, and authority_state at each step.

---

## 8. Explicit Statement: AI is Not Authority

**AI is not the authority in this system and must never be treated as such.**

The authoritative sources are, in order of precedence:
1. The cached spec file with verified SHA-256 in spec-index.yaml
2. The normalized spec text derived from the cached file (same SHA provenance)
3. Facts verified by deterministic text search against the normalized spec text
4. Human-reviewed facts with explicit source citation

AI tools (lexical retrieval, embedding search, LLM synthesis) are exclusively support tools for:
- Finding candidate spec sections efficiently
- Surfacing potential coverage gaps
- Drafting initial fact text for human/deterministic review
- Detecting potential contradictions for human resolution

Any AI output that bypasses these gates — even with high confidence scores — is authority contamination and must be rejected.
