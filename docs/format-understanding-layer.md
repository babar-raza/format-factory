# Format Understanding Layer

**Document type:** Backlog / Architecture Planning
**Status:** Proposed — not yet implemented. Requires FUL-001 design taskcard before execution.
**Created:** 2026-05-08 (memory sprint)
**Last updated:** 2026-05-08
**Visibility:** internal

---

## 1. Purpose

The Format Understanding Layer compiles scattered format knowledge — gathered across gates 1–9 —
into reusable, product-source-ready artifacts. Each format that passes Gate 9 should produce a
compiled set of understanding files before product source begins.

The goal is that product source (Phase 4+) can be driven by a clean, pre-approved set of
format-specific understanding files rather than by reading raw gate evidence, scattered acquisition
pack files, prototype notes, or evidence bundles.

---

## 2. Problem Statement

As of run048 (2026-05-08), FODS has passed Gates 1–10 and FODT has passed Gates 1–8.
Both formats have extensive evidence: spec normalization, neutral models, oracle reports, fuzz reports,
security reports, tier maps, and product planning files.

However, this knowledge is spread across:
- `acquisition-packs/fods/` and `acquisition-packs/fodt/` (12–20+ files each)
- `schemas/neutral-model/fods/` and `schemas/neutral-model/fodt/`
- `reports/security/`
- `prototypes/by-format/`
- Gate planning files and human review packets

A product developer starting Phase 4 Python source work needs to know:
- What facts about this format are definitively verified?
- What are the parser requirements and design decisions?
- What is the security surface and how was it mitigated?
- What features belong to which tier?
- What is the product readiness status?

Currently, getting this information requires reading 20+ files. The Format Understanding Layer
compiles it into 6 structured per-format files.

---

## 3. Scope

### 3.1 Immediate Scope

XML-type formats that have passed Gate 9:
- FODS (Gate 9 PASSED — run047)
- FODT (Gate 9 planning_ready — TC-0048 not started)

### 3.2 Deferred Scope

Non-XML formats are backlog only. See `docs/format-representation-model.md`.

---

## 4. Per-Format Target Files

Each format that passes Gate 9 should produce all six files:

| File | Purpose | Gate inputs |
|---|---|---|
| `acquisition-packs/{format}/format-profile.yaml` | Format classification, representation type, family, spec citation | Gate 1 scoring, Gate 2 legal, spec cache |
| `acquisition-packs/{format}/verified-facts.yaml` | Spec-cited deterministic facts about structure, parsing, encoding | Gate 2 spec, Gate 3 samples, Gate 4 prototype notes, spec workbench |
| `acquisition-packs/{format}/implementation-requirements.yaml` | Product-facing parser requirements derived from gates | Gate 4 parser requirements, Gate 5 neutral model, Gate 6 oracle differences |
| `acquisition-packs/{format}/parser-strategy.yaml` | Parser design decisions, reuse from ODF family, edge cases, known limitations | Gate 4 prototype, Gate 6 oracle, Gate 7 fuzz |
| `acquisition-packs/{format}/security-surface.yaml` | Compiled security findings, mitigations, deferred items | Gate 7 fuzz report, Gate 8 security report |
| `acquisition-packs/{format}/product-readiness.yaml` | Compiled readiness: tier map, feature list, OSS ceiling, known gaps | Gate 9 tier map, Gate 10 product planning |

### 4.1 Format Profile Schema (planned)

```yaml
format_id: fods
display_name: "Flat OpenDocument Spreadsheet"
physical_representation: text_xml
family: cells
spec_body: OASIS
spec_version: "ODF 1.3"
legal_category: 1
legal_status: royalty_free
royalty_free_basis: "OASIS RF on Limited Terms"
xml_namespace_root: "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
single_file: true
container_model: none
encoding: UTF-8
notes: ""
```

### 4.2 Verified Facts Schema (planned)

Each fact must include: `fact_id`, `statement`, `spec_citation`, `evidence_source`, `confidence`.

### 4.3 Implementation Requirements Schema (planned)

Each requirement must include: `req_id`, `tier`, `description`, `source_gate`, `priority`, `status`.

---

## 5. Authority Model

The Format Understanding Layer files compile and reference evidence. They do not replace:
- Published specifications in `.local/spec-cache/`
- Sample corpus in `samples/by-format/`
- Oracle reports in `acquisition-packs/`
- Test results and fuzz reports
- Evidence bundles
- Human gate approvals in `registry/format-registry.yaml`

The Format Understanding Layer is an **aggregation layer** — not a new authority layer.

If a verified-facts.yaml claim conflicts with a spec citation, the spec citation wins.
If an implementation-requirements.yaml entry conflicts with a gate approval, the gate wins.

---

## 6. Inputs Per Format

| Input | Source |
|---|---|
| Spec text | `.local/spec-cache/` + normalization layer |
| Spec citations | `tools/spec-normalize/` citation maps |
| Sample corpus | `samples/by-format/{format}/` |
| Parser prototype | `prototypes/by-format/{format}/` |
| Neutral model | `schemas/neutral-model/{format}/` |
| Oracle comparison report | `acquisition-packs/{format}/gate6-oracle-comparison-report.md` |
| Fuzz report | `acquisition-packs/{format}/gate7-*.md` |
| Security report | `reports/security/{format}.md` |
| Product mapping | `acquisition-packs/{format}/tier-map.yaml` |
| Gate evidence | `taskcards/` + `acquisition-packs/{format}/gate*-human-review-packet.md` |

---

## 7. Outputs

Clean, pre-approved format understanding files that enable:
1. Phase 4 Python FOSS source development without re-reading raw evidence
2. Phase 4 .NET product source development without re-reading raw evidence
3. LLM-assisted code generation (future) grounded in verified facts
4. Cross-format comparison and reuse analysis

---

## 8. Required Future Taskcards

| Taskcard | Title | Trigger |
|---|---|---|
| FUL-001 | Format Understanding Layer schema and design | Before any per-format compilation |
| FUL-002 | FODS compiled understanding package | After FUL-001 design approved; FODS Gate 9 PASSED |
| FUL-003 | FODT compiled understanding package | After FUL-001 design approved; FODT Gate 9 PASSED |
| FUL-004 | Product-source consumption of compiled understanding | After FUL-002 or FUL-003 complete |
| FUL-005 | Format understanding ongoing update and invalidation rules | After FUL-001 design approved |

See `taskcards/FUL-*.md` for full taskcard definitions.

---

## 9. Relationship to Product Source

**Do not create product source before compiled format understanding is available or explicitly waived.**

The only exceptions:
1. The human explicitly waives the requirement and records the waiver in the decision register.
2. A future sprint shows that the existing gate evidence is sufficient and explicitly maps it to
   the implementation-requirements.yaml format.

---

## 10. Relationship to LLM and Embedding Strategy

See `docs/llm-and-embedding-strategy.md`.

When LLM assistance is used for Phase 4 development (future), it should be grounded in verified-facts.yaml
and implementation-requirements.yaml from the Format Understanding Layer, not in raw spec text or
scattered evidence files.

Embedding indexes (when built, future) should preferably be built from compiled understanding files
rather than from raw uncited spec chunks.

---

## 11. Status

**Current status:** Backlog only. No per-format FUL files created in this sprint.
FUL-001 design taskcard is proposed_pending_human_approval.
