# Format Understanding Layer

**Document type:** Architecture / Product Readiness Layer
**Status:** Active. FUL-001, FUL-002, and FUL-003 are complete for the current FODS/FODT track; FUL-004 and FUL-005 remain follow-up work.
**Created:** 2026-05-08 (memory sprint)
**Last updated:** 2026-05-11
**Visibility:** internal

---

## 1. Purpose

The Format Understanding Layer compiles scattered format knowledge, gathered across gates 1-9, into reusable, product-source-ready artifacts.

The goal is that Phase 4 source work can be driven by clean, pre-approved format understanding files rather than by re-reading raw gate evidence, scattered acquisition pack files, prototype notes, or evidence bundles.

---

## 2. Problem Statement

As of 2026-05-11, FODS has passed Gates 1-10 and FODT has passed Gates 1-9. FODT Gate 10 is planning verified with Python source implemented pending human review.

Both formats have extensive evidence: spec normalization, neutral models, oracle reports, fuzz reports, security reports, tier maps, product planning files, and compiled Format Understanding Layer files.

Without the Format Understanding Layer, a product developer needs to read many files to answer basic questions:

- What facts about this format are definitively verified?
- What are the parser requirements and design decisions?
- What is the security surface and how was it mitigated?
- What features belong to which tier?
- What is the product readiness status?

The Format Understanding Layer compiles those answers into six structured per-format files.

---

## 3. Scope

Immediate scope:

- FODS: Gates 1-10 passed, FUL-002 complete, Phase 4 Python source created.
- FODT: Gates 1-9 passed, Gate 10 planning_verified, FUL-003 complete, Python source implemented pending human review.

Deferred scope:

- Non-XML formats. See [docs/python-foss/format-representation-model.md](format-representation-model.md).

---

## 4. Per-Format Files

Each format that passes Gate 9 should produce all six files:

| File | Purpose | Gate inputs |
|---|---|---|
| `acquisition-packs/{format}/format-profile.yaml` | Format classification, representation type, family, spec citation | Gate 1 scoring, Gate 2 legal, spec cache |
| `acquisition-packs/{format}/verified-facts.yaml` | Spec-cited deterministic facts about structure, parsing, encoding | Gate 2 spec, Gate 3 samples, Gate 4 prototype notes, spec workbench |
| `acquisition-packs/{format}/implementation-requirements.yaml` | Product-facing parser requirements derived from gates | Gate 4 parser requirements, Gate 5 neutral model, Gate 6 oracle differences |
| `acquisition-packs/{format}/parser-strategy.yaml` | Parser design decisions, reuse from ODF family, edge cases, known limitations | Gate 4 prototype, Gate 6 oracle, Gate 7 fuzz |
| `acquisition-packs/{format}/security-surface.yaml` | Compiled security findings, mitigations, deferred items | Gate 7 fuzz report, Gate 8 security report |
| `acquisition-packs/{format}/product-readiness.yaml` | Compiled readiness: tier map, feature list, OSS ceiling, known gaps | Gate 9 tier map, Gate 10 product planning |

---

## 5. Authority Model

The Format Understanding Layer files compile and reference evidence. They do not replace:

- Published specifications in `.local/spec-cache/`
- Sample corpus in `samples/by-format/`
- Oracle reports in `acquisition-packs/`
- Test results and fuzz reports
- Evidence bundles
- Human gate approvals in `registry/format-registry.yaml`
- The operational state in `plans/master-plan.md`

The Format Understanding Layer is an aggregation layer, not a higher authority layer. If a compiled claim conflicts with a source citation, gate approval, registry entry, or master-plan state, the higher authority wins.

---

## 6. Inputs Per Format

| Input | Source |
|---|---|
| Spec text | `.local/spec-cache/` and normalization layer |
| Spec citations | `tools/spec-normalize/` citation maps |
| Sample corpus | `samples/by-format/{format}/` |
| Parser prototype | `prototypes/by-format/{format}/` |
| Neutral model | `schemas/neutral-model/{format}/` |
| Oracle comparison report | `acquisition-packs/{format}/gate6-oracle-comparison-report.md` |
| Fuzz report | `acquisition-packs/{format}/gate7-*` |
| Security report | `reports/security/{format}.md` |
| Product mapping | `acquisition-packs/{format}/tier-map.yaml` |
| Gate evidence | `taskcards/` and `acquisition-packs/{format}/gate*-human-review-packet.md` |

---

## 7. Outputs

Clean, pre-approved format understanding files enable:

1. Phase 4 Python FOSS source development without re-reading raw evidence.
2. Future Phase 4 .NET product source development without re-reading raw evidence.
3. Future LLM-assisted code generation grounded in verified facts.
4. Cross-format comparison and reuse analysis.

---

## 8. Taskcard Status

| Taskcard | Title | Status |
|---|---|---|
| FUL-001 | Format Understanding Layer schema and design | Completed |
| FUL-002 | FODS compiled understanding package | Completed |
| FUL-003 | FODT compiled understanding package | Completed |
| FUL-004 | Product-source consumption of compiled understanding | Follow-up |
| FUL-005 | Format understanding ongoing update and invalidation rules | Follow-up |

---

## 9. Relationship To Product Source

Product source should not be created before compiled format understanding is available or explicitly waived.

Current status:

- FODS source was created after the relevant gate and understanding work.
- FODT source was implemented after Gate 9 and Gate 10 planning verification, pending human review.
- Future formats should keep this dependency explicit.

---

## 10. Relationship To LLM And Embedding Strategy

When LLM assistance is used for Phase 4 development in the future, it should be grounded in `verified-facts.yaml` and `implementation-requirements.yaml`, not raw spec text or scattered evidence files.

Embedding indexes, when built, should preferably use compiled understanding files rather than raw uncited spec chunks.

---

## 11. Schema References

| Schema | Path |
|---|---|
| Format Profile | `schemas/format-understanding/format-profile.schema.yaml` |
| Verified Facts | `schemas/format-understanding/verified-facts.schema.yaml` |
| Implementation Requirements | `schemas/format-understanding/implementation-requirements.schema.yaml` |
| Parser Strategy | `schemas/format-understanding/parser-strategy.schema.yaml` |
| Security Surface | `schemas/format-understanding/security-surface.schema.yaml` |
| Product Readiness | `schemas/format-understanding/product-readiness.schema.yaml` |
