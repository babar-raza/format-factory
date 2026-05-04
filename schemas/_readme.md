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

The schema language for neutral-model schemas is decided in Phase 1 via TC-0002. The decision will be recorded in this file and in `plans/master-plan.md` (Decision DEC-008). Until TC-0002 is complete, "YAML or JSON Schema" is the placeholder. Do not create schema files until DEC-008 is resolved.

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
