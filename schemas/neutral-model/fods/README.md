---
artifact_id: fods-neutral-model-readme
artifact_type: schema-documentation
path: schemas/neutral-model/fods/README.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-06"
reusable: true
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODS neutral model README. Created run033 (2026-05-06). Gate 5 artifact."
---

# FODS Neutral Model — v1

**Format:** FODS (Flat OpenDocument Spreadsheet)
**Gate:** 5 — Neutral Model Defined
**Version:** 1.0
**Created:** run033 (2026-05-06)
**Status:** pending independent verification

## Purpose

This directory contains the neutral intermediate model for FODS parsed content. The model is language-neutral and serialization-neutral — it defines the logical structure that any FODS parser should produce, regardless of implementation language (Python, .NET, etc.).

## Files

| File | Purpose |
|---|---|
| `model.yaml` | Entity and field definitions |
| `model.schema.json` | JSON Schema for validation |
| `field-map.yaml` | Maps prototype parser output fields to model fields |
| `coverage-matrix.yaml` | Maps model entities to samples, requirements, and parser output |
| `validation-rules.yaml` | Constraints and invariants |

## Design Decisions

1. **No formula evaluation.** Formulas are stored as raw strings with optional cached values.
2. **No style resolution.** Styles are out of scope for v1.
3. **Unsupported features become warnings.** Merged cells, charts, images, macros produce warning entries, not crashes.
4. **JSON/YAML serializable.** All model fields use primitive types or lists/maps of primitives.
5. **Language-neutral.** Field names use snake_case; types use JSON-compatible names (string, number, boolean, null, array, object).

## Scope

Tier 0-1 features only (matching Gate 4 prototype):
- Workbook metadata (format, version, mimetype)
- Sheet enumeration with names
- Row/cell iteration with typed values
- Formula detection (raw text + cached value)
- Warning collection for unsupported features

## Out of Scope (v1)

- Style/formatting
- Conditional formatting
- Merged cell expansion
- Charts/images/macros
- Annotations/comments
- Date/time value types (not in Gate 3 samples)
