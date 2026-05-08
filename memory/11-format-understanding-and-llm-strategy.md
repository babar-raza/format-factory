---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-08
intended_location: /memory
source: Memory sprint — discussion decisions captured from human review session 2026-05-08
visibility: internal
publish_allowed: false
notes: These are strategic decisions recorded from the human review session. Must not supersede plans/master-plan.md for operational state.
---

# 11 — Format Understanding Layer and LLM Strategy

## Decision Summary (2026-05-08 memory sprint)

### 1. Gates, evidence, and taskcards are not waste

The gates, taskcards, evidence bundles, and status repair processes in this project are not waste.
They are the foundation of trustworthy format knowledge. The issue is not too much evidence —
it is that format understanding is scattered across multiple files and has not been compiled
into reusable, product-source-ready knowledge packages.

### 2. The missing layer: Format Understanding Layer

Each format that passes Gate 9 should produce a compiled set of understanding artifacts
(the Format Understanding Layer) before product source begins. Product source should consume
these compiled understanding files, not scattered evidence.

**Target per-format files:**
- `acquisition-packs/{format}/format-profile.yaml` — format classification, representation type, family
- `acquisition-packs/{format}/verified-facts.yaml` — spec-cited deterministic facts
- `acquisition-packs/{format}/implementation-requirements.yaml` — product-facing requirements derived from gates
- `acquisition-packs/{format}/parser-strategy.yaml` — parser design decisions, edge cases, reuse
- `acquisition-packs/{format}/security-surface.yaml` — compiled security findings from Gate 8
- `acquisition-packs/{format}/product-readiness.yaml` — compiled readiness from Gate 9/10

**Authority model:** These files compile and reference evidence. They do not replace specs, samples,
oracle outputs, tests, evidence bundles, or human approvals. Verified facts, citations, samples,
oracle results, tests, and human/DEC-034 approval remain the single source of truth.

**Taskcards:** FUL-001 through FUL-005 — see `taskcards/FUL-*.md`

### 3. XML-first focus; non-XML is backlog

The immediate format focus is XML-type formats (FODS, FODT, and ODF family).
Non-XML adaptability is explicitly deferred. The architecture must avoid hardcoding XML-only assumptions.

**Physical representation categories (for future profiles):**
- `text_xml` — single flat XML file (FODS, FODT)
- `zip_container` — ZIP with XML inside (ODS, ODT, DOCX, XLSX)
- `binary_records` — legacy binary (DOC, XLS)
- `compound_document` — OLE/CFB container (DOC, XLS, PPT)
- `delimited_text` — CSV and variants
- `json_like` — JSON-based formats
- `hybrid_container` — mixed structures

**Taskcards:** REP-001 through REP-005 — see `taskcards/REP-*.md`

### 4. Controlled LLM and embedding usage authorized for future work

**Authorized for future governed work:**
- LLM endpoint family: `llm.professionalize.com`
- Model families: GPT OSS, Qwen Next, embedding models
- Agents may explore available models and choose appropriately under governance
- LLMs may propose facts, summaries, mappings, edge cases, and draft code
- Embeddings/vector DB may be used as controlled retrieval (NOT truth authority)

**LLMs are NOT:**
- Gate approval authority
- Legal/spec authority
- Replacement for citations, DEC-034, or human approval
- Product release authority

**Embeddings are NOT:**
- Truth authority
- Source of uncited product requirements
- Gate approval

**Preferred embedding content:** verified-facts, implementation-requirements, citation-backed section
summaries, parser strategies, security surfaces. NOT raw uncited spec chunks alone.

**Required embedding metadata:** source hash, source path, spec version, section/chunk ID, fact ID,
model name, embedding model name, created_at, refresh policy, invalidation policy, retrieval audit log.

**No secrets committed.** No raw LLM transcripts in evidence bundles.

**Current status:** Backlog only. No embeddings or vector DB created.

**Taskcards:** LLM-001, LLM-002, EMB-001 through EMB-003 — see `taskcards/LLM-*.md`, `taskcards/EMB-*.md`

### 5. Non-Aspose format candidate registry planned

A visible registry of formats not common to Aspose or underserved by Aspose products must be maintained.
Candidates cannot be claimed as not-supported without verification from Aspose docs/API references.

**Future registry file:** `registry/non-aspose-format-candidates.yaml`

**Taskcard:** NAC-001 through NAC-004 — see `taskcards/NAC-*.md`

### 6. Discovered gaps must be captured in durable artifacts

When any agent, reviewer, or prompt identifies a missing architectural layer, missing capability, or
structural weakness that is NOT authorized for immediate execution, it must be recorded in at least one
durable local artifact (roadmap, backlog, taskcard, memory, risk/gap register, or future sprint
recommendation). It must not remain only in chat or only in an evidence bundle.

**Taskcard:** GOV-001 — see `taskcards/GOV-001-discovered-gap-backlog-capture-rule.md`

### 7. Product source consumption of compiled understanding

Product source (Phase 4+) should not begin before relevant compiled format understanding is available
or explicitly waived by the human. The compiled understanding must be reviewed and approved before
it drives product source decisions.

### 8. Architecture and policy files

- Format Understanding Layer plan: `docs/format-understanding-layer.md`
- LLM and embedding strategy: `docs/llm-and-embedding-strategy.md`
- Format representation model: `docs/format-representation-model.md`
- Non-XML adaptability backlog: covered in `docs/format-representation-model.md`
- Non-Aspose candidate registry plan: `docs/non-aspose-format-candidate-registry-plan.md`
