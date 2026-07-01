---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-08
intended_location: /memory
source: Memory sprint â€” discussion decisions captured from human review session 2026-05-08
visibility: internal
publish_allowed: false
notes: These are strategic decisions recorded from the human review session. Must not supersede plans/master-plan.md for operational state.
---

# 11 â€” Format Understanding Layer and LLM Strategy

## Decision Summary (2026-05-08 memory sprint)

### 1. Gates, evidence, and taskcards are not waste

The gates, taskcards, evidence bundles, and status repair processes in this project are not waste.
They are the foundation of trustworthy format knowledge. The issue is not too much evidence â€”
it is that format understanding is scattered across multiple files and has not been compiled
into reusable, product-source-ready knowledge packages.

### 2. The missing layer: Format Understanding Layer

Each format that passes Gate 9 should produce a compiled set of understanding artifacts
(the Format Understanding Layer) before product source begins. Product source should consume
these compiled understanding files, not scattered evidence.

**Target per-format files:**
- `acquisition-packs/{format}/format-profile.yaml` â€” format classification, representation type, family
- `acquisition-packs/{format}/verified-facts.yaml` â€” spec-cited deterministic facts
- `acquisition-packs/{format}/implementation-requirements.yaml` â€” product-facing requirements derived from gates
- `acquisition-packs/{format}/parser-strategy.yaml` â€” parser design decisions, edge cases, reuse
- `acquisition-packs/{format}/security-surface.yaml` â€” compiled security findings from Gate 8
- `acquisition-packs/{format}/product-readiness.yaml` â€” compiled readiness from Gate 9/10

**Authority model:** These files compile and reference evidence. They do not replace specs, samples,
oracle outputs, tests, evidence bundles, or human approvals. Verified facts, citations, samples,
oracle results, tests, and human/DEC-034 approval remain the single source of truth.

**Taskcards:** FUL-001 through FUL-005 â€” see `taskcards/FUL-*.md`

### 3. XML-first focus; non-XML is backlog

The immediate format focus is XML-type formats (FODS, FODT, and ODF family).
Non-XML adaptability is explicitly deferred. The architecture must avoid hardcoding XML-only assumptions.

**Physical representation categories (for future profiles):**
- `text_xml` â€” single flat XML file (FODS, FODT)
- `zip_container` â€” ZIP with XML inside (ODS, ODT, DOCX, XLSX)
- `binary_records` â€” legacy binary (DOC, XLS)
- `compound_document` â€” OLE/CFB container (DOC, XLS, PPT)
- `delimited_text` â€” CSV and variants
- `json_like` â€” JSON-based formats
- `hybrid_container` â€” mixed structures

**Taskcards:** REP-001 through REP-005 â€” see `taskcards/REP-*.md`

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

**Taskcards:** LLM-001, LLM-002, EMB-001 through EMB-003 â€” see `taskcards/LLM-*.md`, `taskcards/EMB-*.md`

### 5. Non-Aspose format candidate registry planned

A visible registry of formats not common to Aspose or underserved by Aspose products must be maintained.
Candidates cannot be claimed as not-supported without verification from Aspose docs/API references.

**Future registry file:** `registry/non-aspose-format-candidates.yaml`

**Taskcard:** NAC-001 through NAC-004 â€” see `taskcards/NAC-*.md`

### 6. Discovered gaps must be captured in durable artifacts

When any agent, reviewer, or prompt identifies a missing architectural layer, missing capability, or
structural weakness that is NOT authorized for immediate execution, it must be recorded in at least one
durable local artifact (roadmap, backlog, taskcard, memory, risk/gap register, or future sprint
recommendation). It must not remain only in chat or only in an evidence bundle.

**Taskcard:** GOV-001 â€” see `taskcards/GOV-001-discovered-gap-backlog-capture-rule.md`

### 7. Product source consumption of compiled understanding

Product source (Phase 4+) should not begin before relevant compiled format understanding is available
or explicitly waived by the human. The compiled understanding must be reviewed and approved before
it drives product source decisions.

### 8. Architecture and policy files

- Format Understanding Layer plan: `docs/python-foss/format-understanding-layer.md`
- LLM and embedding strategy: `docs/ai/llm-and-embedding-strategy.md`
- Format representation model: `docs/python-foss/format-representation-model.md`
- Non-XML adaptability backlog: covered in `docs/python-foss/format-representation-model.md`
- Non-Aspose candidate registry plan: `docs/python-foss/non-aspose-format-candidate-registry-plan.md`

## 2026-05-09 AI direction refinement

This section records updated direction from the ChatGPT supervision session on 2026-05-09.
See `memory/14-ai-supervision-and-three-pilot-direction-20260509.md` for full context.

### Foundation-first strategy preserved

The original plan to introduce LLMs at later stages after the foundation was laid correctly remains
right. However, the LLM implementation design needs refinement before operational rollout.

The project must resolve these design questions before implementing LLM client code:

1. How are LLM calls governed (budget, authorization, caching)?
2. How are LLM outputs converted to schema-validated artifacts?
3. How are LLM calls audited (run IDs, prompt hashes, model versions)?
4. How do LLM proposals get reviewed, cited, and promoted to facts?
5. How are failed or low-confidence LLM outputs handled?

These decisions must be captured in LLM-001 and related taskcards before any LLM client code is
created. The code must not precede the design.

### LLM should move from backlog-only toward governed acceleration

After closure hygiene and readiness work (run050 closure, S-F2F-02C, etc.), LLMs should move from
backlog-only status toward an operational role in:

- FUL compilation (proposing candidate facts and requirements)
- Test generation (from FUL artifacts and oracle results)
- Failure repair (analyzing failing tests with governed prompts)
- Playbook review queue assistance
- Phase 4 source generation from approved FUL packages

This is a gradual, governed rollout, not a sudden activation. Each capability must be authorized
through a specific taskcard and explicit human approval.

### AI roles clarified

The following must guide all LLM integration work:

- AI may propose. Deterministic evidence decides.
- FUL (Format Understanding Layer) is the prompt substrate for source generation.
  AI must not generate source from raw imagination.
- Embeddings retrieve cited artifacts, not truth.
  Vector/embedding results must point back to cited facts and spec sections.
- AI outputs must become schema-validated artifacts before they are treated as authority.
  A raw LLM response is not a verified fact. It is a proposal.

### Current implementation status

**No LLM client code exists.** No embeddings created. No vector DB created. Status: backlog.
LLM-001, EMB-001 remain proposed_pending_human_approval.

This section records intent, not completion.

## 2026-05-09 LLM module architecture refinement

The detailed architecture direction is now captured in `memory/15-ai-modules-and-state-management-architecture-20260509.md`. That file is required reading before LLM, embedding, state management, no-drift, workflow orchestration, or AI-assisted source generation work.

The planned LLM layer is a governed module family, not an ad hoc endpoint call. The design includes:

- approved endpoint access through an endpoint client
- model discovery for local and remote availability checks
- model registry records for capability and task suitability
- model routing by governed task type
- prompt runner controls for templates, schemas, retries, caching, and logging
- response schemas before model output can affect artifacts
- run ledger entries with model, template, input hashes, output artifacts, and validation status
- cache behavior to avoid repeated calls for identical inputs
- safety checks for secrets, copyrighted spec text, unapproved endpoints, and unsupported tasks
- provenance links from model output back to source artifacts and evidence

FUL remains the prompt substrate for source generation. AI may draft from approved `format-profile.yaml`, `verified-facts.yaml`, `implementation-requirements.yaml`, `parser-strategy.yaml`, `security-surface.yaml`, `product-readiness.yaml`, neutral model schemas, approved samples, scope constraints, forbidden behaviors, and test requirements. AI must not generate product source from imagination or promote prototypes directly into product source.

Embeddings retrieve cited artifacts, not truth. Retrieval must return source artifact path, source hash, chunk ID, and provenance. Embedding hits are pointers to evidence and must not become verified facts without deterministic review.

This section records architecture direction only. No LLM endpoint clients, model discovery tools, model routers, prompt runners, embeddings, vector DBs, state manager code, or orchestration components were implemented by the memory sync sprint.
