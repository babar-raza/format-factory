---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run010; updated run012 with source-layout expectation
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 03 — Architecture and Product Tracks

## High-level architecture

`format-factory` consists of these layers:

```text
Living Master Plan
Agent Governance Layer
Specification Acquisition and Local Cache Layer
Spec Navigation Layer (run026: 884 sections, 940 chunks, query tooling)
Hybrid Spec Retrieval Strategy (run027: Tier 1 deterministic → Tier 2 lexical → Tier 3 vector/future)
Persistent Artifact Model
Format Acquisition Pipeline
Evidence, Legal, Security, and Oracle Validation
Neutral Model Layer
Open-source Release Control Layer
Python OSS Product Track
.NET OSS Product Track
.NET Commercial Product Track
```

## Hybrid Spec Retrieval Strategy (added run027)

Agents query the normalized spec using a 3-tier hierarchy. See `docs/spec-retrieval-strategy.md` for full policy.

| Tier | Method | Tool invocation | When to use |
|---|---|---|---|
| 1 | Deterministic | `query_normalized_spec.py --section`, `--element`, `--page` | Known section number or element name |
| 2 | Lexical (keyword) | `query_normalized_spec.py --keyword`, `--sample-req` | Known keyword; no exact section |
| 3 | Vector/semantic | Not yet implemented (TC-0015, TC-0016) | Complex natural-language question after Tier 1+2 fail |

Rules:
- Always attempt Tier 1 before Tier 2 or Tier 3.
- Every query must specify `--format-id fods` (format isolation — no cross-format bleed).
- All retrieval is local-only (`.local/spec-cache/`). No remote calls during retrieval.
- Every result cited in Gate evidence must include `spec_citation` provenance block (see `docs/spec-retrieval-strategy.md` §6).
- Tier 3 vector search is NOT yet available. TC-0015 evaluates it; TC-0016 implements it (both blocked by human review).

## Product-neutral acquisition layer

The acquisition layer must not be tied to one product implementation too early.

It produces reusable artifacts:

- format registry entries
- scoring evidence
- spec and legal evidence
- cached spec metadata
- sample provenance
- parser notes
- prototype outputs
- neutral model schemas
- oracle comparison reports
- fuzz/security reports
- product mapping taskcards

This layer feeds all product tracks.

## Product tracks

| Track | Purpose | Language | Feature ceiling | Status |
|---|---|---|---|---|
| Acquisition layer | Gather reusable format truth | Mostly Python and Markdown/YAML | N/A | Active in Phase 0+ |
| Python FOSS product | Public adoption with controlled features | Python 3.11+ | Tier 0-4 | Phase 4+ |
| .NET product | Full-feature commercial capability; .NET FOSS packaging TBD | net8.0/net10.0 | Tier 0-6 | Phase 4+ with gate and DD3 controls |

**Note:** The source-layout expectation below was propagated to the master plan in run011. `plans/master-plan.md` v2.8 uses format-first layout (`src/python/{format}/`, `src/net/{format}/`). Old paths (`src/python/open-source/`, `src/dotnet/open-source/`, `src/dotnet/commercial/`) are marked OBSOLETE in all governance docs. This is the current operational layout.

## Feature tiers

| Tier | Meaning | Typical track |
|---|---|---|
| 0 | Detect format | OSS + commercial |
| 1 | Read metadata and structure | OSS + commercial |
| 2 | Import core content | OSS + commercial |
| 3 | Export basic content | OSS + commercial |
| 4 | Roundtrip common files | OSS ceiling |
| 5 | Commercial-grade full fidelity | Commercial |
| 6 | Advanced repair, optimization, recovery, exotic cases | Commercial |

## Important separation rules

- Acquisition packs are not product code.
- Prototypes are evidence, not product code.
- Product code must be written from neutral model contracts and validated evidence, not promoted directly from prototypes.
- Commercial source is physically and logically isolated.
- Open-source code must never include commercial stubs, hidden flags, or disabled commercial features.

## Implementation authorization model

Gate 9 does not write product source.

Gate 9 produces product mapping and implementation taskcards.

After Gate 9, an explicit Phase 4 implementation prompt may authorize source creation.

Gate 10 checks OSS readiness after OSS source exists.

Gate 11 checks commercial readiness after commercial source exists and review is complete.

---

## Source layout (propagated run011, confirmed run013)

**Authority note:** This section records the source layout as confirmed by run011 propagation and run013 verification. `plans/master-plan.md` v2.8+ uses this layout as the operational standard.

### End-state source layout

- `src/net/{format}/` for the .NET product workspace per format.
  - Example: `src/net/odp/`
  - Covers full .NET implementation scope (commercial/full-feature by default; FOSS packaging deferred — DEC-033).

- `src/python/{format}/` for the Python FOSS product workspace per format.
  - Example: `src/python/odp/`
  - Python path: FOSS with controlled features (Tier 0-4 ceiling; Apache 2.0 / MIT).

### Old layout (OBSOLETE — do not use)

```text
src/python/open-source/   — OBSOLETE
src/dotnet/open-source/   — OBSOLETE
src/dotnet/commercial/    — OBSOLETE
```

These paths must NEVER be created. They are marked as OBSOLETE in all governance docs, AGENTS.md, and the master plan. The format-first layout above is the only valid target.

### Status

| Item | Status |
|------|--------|
| Human expectation captured | run012 memory stream |
| Master plan propagation | COMPLETED — run011 (master-plan.md v2.8) |
| Memory reconciliation | COMPLETED — run013 |
| .NET FOSS packaging decision | DEFERRED — DEC-033 (must resolve before Gate 10 .NET release) |

### .NET FOSS packaging question

Whether the .NET track includes a separate FOSS-tier packaging model (parallel to Python FOSS) is not yet decided. The human's current statement says `src/net/{format}` covers the .NET product workspace without specifying FOSS/commercial split at the folder level. If a .NET FOSS package is desired, the master plan must explicitly authorize and describe the separation model before any source folder is created.

### Repeatability principle

The human emphasizes that planning and grounding must be solid before implementation. Rushing to create source layout before the master plan propagates the new model creates post-implementation fixes. Do not create source folders speculatively.

### Agentic workflow routes

The system must process any file format through repeatable agentic workflows. Supported workflow routes (all governed by AGENTS.md and commands/skills):

- Claude Code in VS Code (primary executor)
- ChatGPT Codex (optional)
- Local endpoints such as Ollama (governed by endpoint policy)
- External endpoint `llm.professionalize.com` (governed by endpoint policy)
- Keys managed via system environment (never committed; `.env` is gitignored)

Any LLM or agent route must produce the same evidence artifacts, follow the same gate model, and produce the same evidence bundles. Repeatability matters more than speed.
