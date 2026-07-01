# LLM and Embedding Strategy

**Document type:** Backlog / Strategy
**Status:** Backlog only. No LLM calls or embeddings created in this sprint.
**Created:** 2026-05-08 (memory sprint)
**Last updated:** 2026-05-08
**Visibility:** internal

---

## 1. Purpose

This document describes the authorized strategy for using LLM and embedding services in future
format-factory sprints. The intent is to accelerate format understanding work â€” especially the
Format Understanding Layer â€” while maintaining deterministic authority over facts, gate decisions,
and product requirements.

---

## 2. Endpoint and Model Families

### 2.1 Authorized Endpoint

`llm.professionalize.com` is the intended endpoint family for future governed LLM and embedding work.

### 2.2 Known Model Families

| Family | Type | Intended use |
|---|---|---|
| GPT OSS | LLM | Fact extraction, spec summarization, requirement drafting, code generation |
| Qwen Next | LLM | Same â€” alternative when GPT OSS is unavailable or less suitable |
| Embedding models | Embedding | Retrieval over verified facts, implementation requirements, section summaries |

Agents may inspect available models through environment-configured credentials and endpoint metadata
when a future sprint authorizes execution. Model choice must be recorded with: model name, task type,
reason, fallback, and validation performed.

**No model is chosen or called in this memory sprint.**

### 2.3 2026-05-09 architecture direction

The latest AI module, embedding retrieval, state-management, workflow orchestration, source
generation, and no-drift design direction is captured in
`memory/15-ai-modules-and-state-management-architecture-20260509.md`.

That memory file refines this strategy with conceptual module layouts for governed LLM access,
retrieval, and the Format Factory State Manager. It is design direction only. It does not mean
`endpoint_client.py`, `model_discovery.py`, `router.py`, retrieval indexes, embeddings, vector DBs,
state manager code, LangGraph, Prefect, Temporal, Dagster, or product source have been implemented.

---

## 3. Secret Policy

The following rules are permanent and apply to all sprints:

1. Do not commit API keys, endpoint tokens, or model secrets to the repository.
2. Do not print secrets in logs, evidence bundles, or run records.
3. Use environment variables only (`LLM_ENDPOINT`, `LLM_API_KEY`, etc. â€” names TBD by LLM-001).
4. Redact endpoint headers and tokens in all stored logs.
5. Raw prompts/responses must not be bundled in evidence bundles by default.
6. LLM-generated outputs stored as evidence must be summarized, validated, and non-secret.

---

## 4. LLM Allowed Future Uses

When a future sprint explicitly authorizes LLM use, allowed tasks include:

| Task | Notes |
|---|---|
| Candidate fact extraction | From normalized spec chunks â€” not raw PDF text |
| Spec section summarization | With spec citation required in output |
| Requirement drafting | For review and validation against gate evidence |
| Parser strategy drafting | For human and deterministic review |
| Neutral model mapping suggestions | Human must approve all mappings |
| Malformed/fuzz case suggestions | Must be added to fuzz fixture set with provenance |
| Oracle-difference explanation | Descriptive only â€” not authoritative |
| Product-boundary review | For comparison against tier map |
| Code/test draft generation | Under deterministic validation (tests must pass) |

---

## 5. LLM Prohibited Authority

LLMs must never be treated as authority for:

| Prohibited use | Reason |
|---|---|
| Gate approval | Gates 1-10: agent-owned policy gates (AGENTS.md §AG5). Gate 11 G11-G: Babar Raza |
| Legal or spec authority | Citations and official specs are authoritative |
| Replacing citations | Every verified fact needs a spec citation |
| Replacing DEC-034 | Independent verification must be human-agent |
| Replacing human approval | No LLM approval for product decisions |
| Product release authority | Human sign-off required |

No LLM-generated fact becomes verified without citation and deterministic or human verification.

---

## 6. Embedding Allowed Future Uses

When a future sprint explicitly authorizes embedding/retrieval work, allowed uses include:

| Use | Notes |
|---|---|
| Retrieval over verified-facts.yaml | With provenance preserved |
| Retrieval over implementation-requirements.yaml | With source gate and spec citation |
| Retrieval over citation-backed section summaries | Not raw uncited spec text |
| Similarity search across formats | For reuse analysis |
| Agent context retrieval | For Format Understanding Layer compilation |

---

## 7. Embedding Prohibited Use

| Prohibited use | Reason |
|---|---|
| Truth authority | Embeddings are retrieval, not truth |
| Uncited product requirements | All requirements need gate-backed citations |
| Gate approval | Not a gate authority |
| Source generation from embedding-only facts | Facts need deterministic verification first |

---

## 8. Verified-Facts-First Embedding Strategy

Embedding indexes should be built preferably from:
1. `verified-facts.yaml` per format (gate-backed, cited)
2. `implementation-requirements.yaml` per format (gate-derived)
3. Citation-backed section summaries from the spec normalization layer
4. Parser strategy notes with spec references
5. Security surface entries with mitigation status

**Not** from raw uncited spec chunks or raw evidence bundle text alone.

---

## 9. Required Embedding Metadata

Every embedding index entry must include:

| Field | Purpose |
|---|---|
| `source_hash` | SHA-256 of the source document |
| `source_path` | Path in repo or spec cache |
| `spec_version` | ODF version or equivalent |
| `section_id` / `chunk_id` | Navigation layer ID |
| `fact_id` | If from verified-facts.yaml |
| `model_name` | LLM model name |
| `embedding_model_name` | Embedding model name |
| `created_at` | ISO-8601 timestamp |
| `refresh_policy` | When to rebuild (e.g., on spec version change) |
| `invalidation_policy` | What invalidates this entry |
| `retrieval_audit_log` | Log of retrievals (local, not committed) |

---

## 10. Controls Summary

| Control | Rule |
|---|---|
| No raw secrets | Never in repo, logs, or bundles |
| No full raw spec text in bundles | Forbidden by base contract |
| No embeddings/vector DB in repo | Forbidden by base contract patterns |
| No embeddings in .local committed | Not tracked by git |
| Retrieval audit log | Local only |
| LLM output storage | Summarized + validated, not raw |
| Model choice record | Stored in run evidence |

---

## 11. Backlog Taskcards

| Taskcard | Title | Status |
|---|---|---|
| LLM-001 | Model discovery and endpoint preflight for llm.professionalize.com | proposed_pending_human_approval |
| LLM-002 | Controlled LLM proposal workflow | proposed_pending_human_approval |
| EMB-001 | Embedding/retrieval architecture design | proposed_pending_human_approval |
| EMB-002 | Verified-facts-first embedding pilot | proposed_pending_human_approval |
| EMB-003 | Retrieval audit and invalidation controls | proposed_pending_human_approval |

See `taskcards/LLM-001-*.md` and `taskcards/EMB-001-*.md` for full definitions.

---

## 12. Execution Status

**BACKLOG ONLY.** No LLM calls, no embeddings, no vector DB created in this memory sprint.
Implementation of any item in this document requires an explicit human-authorized execution prompt.

---

## 13. AI Module and FFSM Design Direction (added 2026-05-09)

The detailed AI module and state-management architecture direction is captured in:
memory/15-ai-modules-and-state-management-architecture-20260509.md

The key planned module layouts (design only -- no code exists):

**tools/llm/ (planned -- not yet created):**
- endpoint_client.py: Governed LLM client -- requires LLM-001 authorization
- call_log.yaml: Audit log schema
- schemas/: Schema validation for LLM outputs
- prompts/: Versioned prompt templates
- replay/: Deterministic replay support

**tools/retrieval/ (planned -- not yet created):**
- embed.py: Embedding generation -- requires EMB-001 authorization
- index.py: Vector index build/update
- query.py: Retrieval query interface
- audit_log.yaml: Retrieval audit schema

**tools/state/ / FFSM (planned -- not yet created):**
- ffsm.py: State manager core
- transitions.py: Validated state transition logic
- schema/: State schemas

The FFSM authority hierarchy is in docs/current-state-and-evidence-authority.md Section 8.

**Current status:** DESIGN ONLY. No code exists in tools/llm/, tools/retrieval/, or tools/state/.
No LangGraph, Prefect, Temporal, or Dagster is installed or imported. Implementation requires
explicit human-authorized taskcards (LLM-001, EMB-001, plus FFSM taskcard not yet created).
