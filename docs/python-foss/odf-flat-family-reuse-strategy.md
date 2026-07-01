---
artifact_id: odf-flat-family-reuse-strategy
artifact_type: plan
path: docs/python-foss/odf-flat-family-reuse-strategy.md
visibility: internal
publish_allowed: false
generated_by: claude
generated_at: "2026-05-07"
notes: "ODF flat family reuse strategy document. Created run039 (2026-05-07). Documents pipeline reuse from FODS acquisition to future ODF flat family formats."
---

# ODF Flat Family Reuse Strategy

**Document type:** Planning Reference
**Created:** 2026-05-07 (run039)
**Status:** Pre-Gate 1 planning (no format beyond FODS has been approved for acquisition)
**Authority:** This document is informational only. No acquisition may begin for any new format without explicit human Gate 1 approval.

---

## 1. Purpose

The FODS acquisition has produced a substantial set of reusable artifacts — spec cache, normalization tools, oracle tooling, evidence contract system, sample/prototype patterns. This document maps which of those assets can be reused for future ODF flat family formats (FODT, FODP, FODG, FODB), and what new investment each would require.

This is a planning document. It does not authorize any acquisition, spec download, or Gate 1 scoring for any format other than FODS.

---

## 2. ODF Flat Family Overview

The ODF Flat family consists of flat XML equivalents of ODF container (ZIP) formats:

| Format | MIME Type | Equivalent ZIP | Family |
|---|---|---|---|
| FODS | `application/vnd.oasis.opendocument.spreadsheet-flat-xml` | ODS | Cells |
| FODT | `application/vnd.oasis.opendocument.text-flat-xml` | ODT | Words |
| FODP | `application/vnd.oasis.opendocument.presentation-flat-xml` | ODP | Slides |
| FODG | `application/vnd.oasis.opendocument.graphics-flat-xml` | ODG | Diagram |
| FODB | `application/vnd.oasis.opendocument.base-flat-xml` | ODB | Archive |

All five formats:
- Are governed by the OASIS ODF Technical Committee
- Use ODF 1.3 as the primary specification
- Share the same flat XML document structure (`<office:document>` root element)
- Are natively supported by LibreOffice (the approved oracle provider)
- Are Legal Category 1 (RF) — no royalty or implementation restriction

---

## 3. Reusable Assets from FODS Acquisition

### 3.1 Spec Cache (HIGH reuse potential)

| Asset | Location | Reusable For |
|---|---|---|
| ODF 1.3 Part 3 PDF (24.27 MB) | `.local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf` | All ODF formats (same spec body) |
| Normalized text | `.local/spec-cache/fods/1.3/normalized/text.txt` | All ODF formats |
| Page index | `.local/spec-cache/fods/1.3/normalized/pages.jsonl` (782 pages) | All ODF formats |
| Section index | `.local/spec-cache/fods/1.3/normalized/sections.jsonl` (884 sections) | All ODF formats |
| Chunk index | `.local/spec-cache/fods/1.3/normalized/chunks.jsonl` (940 chunks) | All ODF formats |
| Citation map | `.local/spec-cache/fods/1.3/normalized/citations.yaml` | All ODF formats |

**What changes per format:** The sections and chunks that are most relevant will differ. FODS focused on table/cell sections; FODT will focus on text/paragraph sections; FODP on draw/presentation sections. The spec cache itself does not need to be re-downloaded or re-normalized.

### 3.2 Spec Navigation Layer (HIGH reuse potential)

| Tool | Location | Reuse |
|---|---|---|
| `query_normalized_spec.py` | `tools/spec-normalize/` | YES — same tool, different query parameters |
| `build_section_index.py` | `tools/spec-normalize/` | YES — idempotent (already built for ODF 1.3) |
| `build_chunk_index.py` | `tools/spec-normalize/` | YES — idempotent |
| `export_sample_requirements.py` | `tools/spec-normalize/` | PARTIAL — adapt sample requirements per format |

### 3.3 Oracle Provider (FULL reuse for FODT/FODP/FODG)

| Asset | Location | Reuse |
|---|---|---|
| Oracle harness | `tools/oracle/` (6 files) | YES — LibreOffice supports all ODF flat formats |
| Provider registry | `tools/oracle/provider_registry.yaml` | PARTIAL — add FODT/FODP/FODG as supported formats |
| Environment checker | `tools/oracle/validate_oracle_environment.py` | YES — same LibreOffice binary |
| Harness self-test | `tools/oracle/self_test_oracle_harness.py` | PARTIAL — extend synthetic fixtures for new format |
| Operator handoff | `acquisition-packs/fods/oracle-operator-handoff.md` | PARTIAL — adapt per-format section |

**Note on FODB:** LibreOffice Base headless export support for FODB needs verification. The oracle reuse claim for FODB is `UNCERTAIN` (see candidate shortlist). All other formats have confirmed LibreOffice support.

### 3.4 Evidence Contract System (FULL reuse)

| Asset | Location | Reuse |
|---|---|---|
| `build_evidence_bundle.py` | `tools/evidence/` | YES — format-neutral |
| `validate_evidence_bundle.py` | `tools/evidence/` | YES — format-neutral |
| `check_current_state_consistency.py` | `tools/evidence/` | YES — format-neutral |
| Contract templates | `tools/evidence/contracts/` | PARTIAL — create new contract per run |
| Negative tests | `tests/evidence/` | YES — already run for any format |

### 3.5 Prototype Pattern (HIGH reuse)

| Asset | Location | Reuse |
|---|---|---|
| `fods_parser.py` | `prototypes/by-format/fods/` | PARTIAL — same ElementTree pattern; adapt for new XML elements |
| `validate_against_samples.py` | `prototypes/by-format/fods/` | PARTIAL — adapt for new format sample paths |

The FODS prototype established:
- How to parse flat XML with Python stdlib (`xml.etree.ElementTree`)
- The validate-against-samples pattern
- The 4-sample test corpus approach

For FODT, a new `fodt_parser.py` would be created at `prototypes/by-format/fodt/` following the same pattern but targeting paragraph/text/style elements instead of table/cell elements.

### 3.6 Neutral Model (FAMILY-SPECIFIC)

| Format | Can Reuse FODS Model? | New Model Required |
|---|---|---|
| FODT | NO — different family (Words vs Cells) | YES — Words family neutral model |
| FODP | NO — different family (Slides vs Cells) | YES — Slides family neutral model |
| FODG | NO — different family (Diagram vs Cells) | YES — Diagram family neutral model |
| FODB | NO — different family (Archive vs Cells) | YES — Archive/Database family neutral model |

The FODS Cells neutral model (`schemas/neutral-model/fods/`) is not reusable for other families. However, the model structure (entity/field-map/coverage-matrix/validation-rules/README pattern) can be reused as a template.

### 3.7 Sample Pattern (HIGH reuse)

| Asset | Location | Reuse |
|---|---|---|
| `create_fods_samples.py` | `tools/samples/` | PARTIAL — adapt for new format XML structure |
| `validate_fods_samples.py` | `tools/samples/` | PARTIAL — adapt validation rules |
| 4-sample corpus pattern | `samples/by-format/fods/` | YES — same 4-sample approach; create `samples/by-format/fodt/` |
| Provenance pattern | `samples/_provenance.yaml` | YES — add new format entries |

---

## 4. New Investment Required Per Format

### 4.1 FODT (HIGH PRIORITY)

| Phase | New Work Required |
|---|---|
| Gate 2 (Spec Evidence) | ODF 1.3 Part 2 spec sections on text/paragraph elements; patent search waived (same spec body as FODS) |
| Gate 3 (Samples) | 4+ synthetic FODT samples: minimal-text.fodt, multi-paragraph.fodt, styled-text.fodt, table-in-text.fodt |
| Gate 4 (Prototype) | `prototypes/by-format/fodt/fodt_parser.py` — ElementTree, text/paragraph/heading/style extraction |
| Gate 5 (Neutral Model) | Words family neutral model: entity types (Document, Section, Paragraph, Table, Style, List) |
| Gate 6 (Oracle) | LibreOffice headless FODT export — same oracle harness, extend for text element comparison |
| Acquisition Pack | `acquisition-packs/fodt/` — parallel to `acquisition-packs/fods/` |

**Estimated new file count:** ~25 committed files + local artifacts

### 4.2 FODP (MEDIUM PRIORITY)

Similar to FODT but requires Slides family neutral model. Lower priority — acquire after FODT Gate 6 completes.

### 4.3 FODG (LOW PRIORITY)

Diagram/drawing model significantly more complex. Lower community demand. Evaluate after FODT.

### 4.4 FODB (DEFER)

Very low community demand. Oracle support uncertain. Not recommended for next acquisition.

---

## 5. Pipeline Reuse Estimation

| Phase | FODS Cost | FODT Reuse | FODT New Work | Net Savings |
|---|---|---|---|---|
| Phase 0 (Governance) | 41 files | ~100% reuse (governance already in place) | Minor updates | HIGH |
| Phase 1 (Scoring) | Gate 1 scoring | Scoring model reused; spec evidence partially reused | New FODT score sheet | HIGH |
| Phase 2 (Spec Cache) | 24.27 MB download + normalization | 100% reuse (same spec already cached) | No new download | VERY HIGH |
| Phase 3 (Samples) | 4 samples + validation | Pattern reused | New FODT samples | MEDIUM |
| Phase 3 (Prototype) | fods_parser.py | ElementTree pattern reused | New fodt_parser.py | MEDIUM |
| Phase 3 (Neutral Model) | FODS Cells model (7 files) | Template structure reused | New Words model | MEDIUM |
| Phase 3 (Oracle) | Oracle harness | Full reuse (same LibreOffice) | Extend for text comparison | HIGH |

**Overall estimate:** FODT acquisition would require approximately 40-50% of the FODS acquisition effort, due to spec cache, oracle, governance, and pattern reuse.

---

## 6. WIP Limit Impact

Per `docs/gates.md` WIP limits:
- Gates 4-6: maximum 2 formats simultaneously
- Gates 1-3: maximum 3 formats simultaneously

Current state (as of run039):
- FODS: Gate 6 (1/2 slots, Gates 4-6)
- All other formats: None in pipeline

FODT Gate 1 scoring can begin without affecting FODS Gate 6 work. Once FODT passes Gate 1, it would occupy a Gates 1-3 slot (0/3 currently used), not a Gates 4-6 slot. It would only consume a Gates 4-6 slot when it enters Gate 4.

---

## 7. Governance Notes

1. This document is informational only. It does not authorize any work beyond candidate evaluation.
2. No acquisition pack may be created for FODT, FODP, FODG, or FODB until a human explicitly authorizes Gate 1 scoring by format name.
3. No ODF specs for new formats may be downloaded — the ODF 1.3 spec is already cached, and no new format requires a new spec download.
4. All new acquisition work must follow AGENTS.md governing rules and the DEC-034 independent verification requirement.

---

## 8. Related Files

- `registry/candidates/odf-flat-family-shortlist.yaml` — candidate shortlist (run038)
- `registry/candidates/fodt-gate1-scoring-package.yaml` — FODT Gate 1 scoring evidence (run039)
- `acquisition-packs/_candidate-shortlists/odf-flat-family-next-candidates.md` — human-readable summary (run038)
- `taskcards/TC-0028-next-format-candidate-shortlist.md` — shortlist taskcard
- `taskcards/TC-0029-fodt-gate1-scoring-preparation.md` — FODT Gate 1 prep taskcard
- `docs/ai/oracle-provider-strategy.md` — oracle provider strategy (run037)
- `tools/oracle/provider_registry.yaml` — approved oracle providers
