---
artifact_id: fods-neutral-model-notes
artifact_type: acquisition-pack
path: acquisition-packs/fods/neutral-model-notes.md
format_id: fods
product_family: cells
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-06"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 5 neutral model design notes for FODS. Created run033 (2026-05-06)."
---

# FODS Neutral Model — Design Notes

**Gate:** 5 (Neutral Model Defined)
**Created:** 2026-05-06 (run033)
**Model version:** 1.0

## Design Decisions

### 1. Entity Hierarchy: Workbook > Sheet > Row > Cell

The neutral model follows the same hierarchy as the prototype parser output and the ODF XML structure. This was chosen for simplicity and direct traceability to both the spec (table:table > table:table-row > table:table-cell) and parser output.

### 2. Formula as Separate Entity

The prototype outputs formulas as flat strings. The neutral model elevates Formula to a first-class entity with `raw`, `cached_value`, `evaluated`, and `evaluator` fields. This prepares for future formula evaluation support without changing the model structure.

In v1, `evaluated` is always `false` and `evaluator` is always `null`. The `cached_value` field preserves the document's cached result (from `office:value`).

### 3. Warning Entity

Warnings are modeled as structured objects rather than plain strings. This allows programmatic filtering by warning code and consistent error handling across product implementations.

### 4. Prototype-to-Model Transform

The field map (field-map.yaml) documents 19 mappings:
- 14 direct (no transform needed)
- 1 rename (`format` → `format_id`)
- 1 expand (formula string → Formula object)
- 3 derived (fields not in prototype but in model: row_index, repeated_columns, cell warnings)

The prototype output is deliberately close to the neutral model. Product code needs minimal transformation.

### 5. Coverage Decisions

**Covered in v1:** Core data path — workbook structure, sheets, rows, cells, float/string/boolean values, formulas (raw + cached), text content, mimetype, version attributes.

**Deferred:** Date, time, currency, percentage value types. Row/column repeat compression (prototype expands inline). Named ranges, column definitions, consolidation ranges.

**Out of scope:** Styling, formatting, macros, embedded objects, font declarations. These are not relevant to the cells data extraction mission.

### 6. Value Type Handling

The model supports the same 7 ODF value types as the spec: float, string, boolean, date, time, currency, percentage. In v1, only float, string, and boolean are fully extracted. The remaining types are recognized (in the enum) but extraction of type-specific attributes (office:date-value, office:time-value, etc.) is deferred to product implementation.

### 7. Repeated Columns

The prototype expands repeated cells inline (each repeated cell gets its own Cell entry). The model includes a `repeated_columns` field for roundtrip fidelity — product code should preserve the original `table:number-columns-repeated` value when it exists.

## Security Baseline

The neutral model itself has no security implications — it is a data schema definition. Security concerns are addressed at the parser level (Gate 4 parser-notes.md) and will be formally assessed at Gate 8.

Key parser security properties preserved by the model:
- stdlib-only XML parsing (no external entity expansion)
- No formula evaluation (no code execution risk)
- No macro extraction (office:scripts ignored)
- No external data source resolution

## Limitations

1. No explicit sheet index in prototype output — derived from array position
2. Formula evaluation not supported (v1)
3. Date/time/currency/percentage extraction incomplete
4. No roundtrip export capability (model is read-only in v1)
5. Styling and formatting not modeled
