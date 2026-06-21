# Schemas — Neutral Model

**Document type:** Directory Orientation — Phase 0 Foundation
**Last reviewed:** 2026-05-03

---

## Purpose

This directory contains neutral-model schemas for each format family supported by format-factory. A neutral model is a format-family-specific data structure that can represent the core data from any format in that family without being tied to any single format's encoding.

For example, the `cells/` neutral model represents spreadsheet data (sheets, rows, cells, values, basic styles) in a way that both FODS and XLSX can map into. The neutral model is the contract between the parser layer and the conversion layer.

---

## Directory Structure

```
schemas/
+-- _readme.md          This file
+-- neutral-model/      Format-family schemas (created in Phase 3, Gate 5)
    +-- cells/          Spreadsheet family (FODS, ODS, XLSX)
    +-- words/          Word processing family (ODT, DOCX)
    +-- slides/         Presentation family (ODP, PPTX)
    +-- imaging/        Imaging family (SVG, etc.)
    +-- diagram/        Diagram/CAD family
    +-- archive/        Archive family
```

The `neutral-model/` subdirectory and its family directories are created in Phase 3 when Gate 5 work begins for the first format in each family.

---

## Schema Language

**Decision (DEC-035, resolved via TC-0002, 2026-06-18):** JSON Schema Draft 7.

### Rationale

Two options were evaluated:

| Option | Pros | Cons |
|--------|------|------|
| **JSON Schema Draft 7** | Native tooling in Python (`jsonschema` library) and .NET (`JsonSchema.Net`); machine-validatable; widely understood; `$ref` for composition | More verbose than custom YAML |
| **YAML Schema (custom)** | Human-readable; less tooling overhead | No standard validation library; requires custom validator; inconsistent Python/.NET |

**Selected: JSON Schema Draft 7.** Primary driver: tooling parity between Python and .NET tracks — both have mature validation libraries consuming the same schema files. JSON Schema can be authored as YAML (YAML is a superset of JSON), preserving readability while gaining machine-validation.

### Validation Libraries

- **Python:** `jsonschema` (>=4.0) — already in project dependencies
- **.NET:** `JsonSchema.Net` (NuGet) — added when Gate 5 work begins

### File Convention

- Schema files use `.json` extension and JSON Schema Draft 7 (`"$schema": "http://json-schema.org/draft-07/schema"`)
- One schema file per neutral model family (e.g., `neutral-model/cells/cells-schema.json`)
- Sample instance documents use `.yaml` for human readability (validated against JSON Schema at CI time)

---

## Neutral Model Design Principles

A neutral model schema must satisfy:
1. **Format-neutral:** It must not expose any encoding details of any specific format (no XML element names, no proprietary field names).
2. **Lossless for core data:** All core data from any format in the family must be representable without data loss.
3. **Extensible:** The schema must be extensible for additional data structures discovered in later formats.
4. **Validated:** The schema must be machine-validatable; every sample in the corpus must be representable in the schema without validation errors.

---

## Visibility

All schemas in this directory are `visibility: internal` until Gate 9 (product mapping). They become `visibility: public` when the format reaches Gate 10.

---

## Relationship to Other Documents

- `docs/architecture.md` — context for neutral model in the system architecture
- `docs/gates.md` — Gate 5 (neutral model) pass criteria
- `docs/acquisition-workflow.md` — Stage 5: Neutral Model Design
- `taskcards/TC-0002-schema-language.md` — schema language selection decision
