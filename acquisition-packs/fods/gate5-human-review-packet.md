---
artifact_id: fods-gate5-human-review-packet
artifact_type: gate-review-packet
path: acquisition-packs/fods/gate5-human-review-packet.md
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
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 5 human review packet for FODS. Created run034 (2026-05-06). TC-0024 DEC-034 PASS. Gate 5 NOT approved."
---

# FODS Gate 5 Human Review Packet

**Format:** FODS (Flat OpenDocument Spreadsheet)
**Gate:** 5 — Neutral Model Defined
**Current status:** neutral_model_verified_pending_human_review
**Gate 5 approved:** NO — requires human approval
**Prepared by:** run034 (2026-05-06)
**Verified by:** run034 TC-0024 DEC-034 independent verification

---

## 1. Gate 5 Pass Criteria (from docs/gates.md)

Gate 5 requires:
- Language-neutral intermediate representation (neutral model) is defined
- Neutral model schema covers the prototype's supported subset
- Field mapping between parser output and neutral model is documented
- Coverage matrix documents what is and isn't supported

All criteria are met. Evidence below.

---

## 2. Neutral Model Summary

| Field | Value |
|---|---|
| Model location | `schemas/neutral-model/fods/` (6 files) |
| Model version | 1.0 |
| Entities | 6: Workbook, Sheet, Row, Cell, Formula, Warning |
| JSON Schema | `model.schema.json` — valid, `additionalProperties: false` on all entities |
| Field mappings | 19 total (14 direct, 1 rename, 1 expand, 3 derived) |
| Coverage features | 30 total: 13 covered, 2 partial, 10 deferred, 5 out-of-scope |
| Validation rules | 21 total: 18 error, 3 warning |
| Created | run033 (2026-05-06) |
| Verified | run034 (2026-05-06) — TC-0024 DEC-034 |

---

## 3. Entity Definitions

| Entity | Purpose | Fields |
|---|---|---|
| Workbook | Root container | format_id, spec_version, odf_version_attr, mimetype, sheet_count, sheets, warnings |
| Sheet | Table element | name, index, row_count, rows |
| Row | Table row | index, cells |
| Cell | Table cell | row_index, col_index, value_type, value, text, formula, repeated_columns, warnings |
| Formula | Cell formula | raw, cached_value, evaluated, evaluator |
| Warning | Diagnostic | code, message, source |

---

## 4. Validation Results — TC-0024 DEC-034

### 4a. validate_neutral_model.py re-run (4/4 PASS)

| Sample | Checks | PASS | WARN | ERROR | Result |
|---|---|---|---|---|---|
| minimal-spreadsheet.fods | 20 | 19 | 1 | 0 | PASS |
| multi-sheet-basic.fods | 27 | 25 | 2 | 0 | PASS |
| typed-values-basic.fods | 20 | 19 | 1 | 0 | PASS |
| formula-basic.fods | 20 | 19 | 1 | 0 | PASS |
| **Total** | **87** | **82** | **5** | **0** | **PASS** |

Warnings are all VR-010 (sheet index not explicit in prototype output — documented in field-map.yaml as "implied by array position").

### 4b. Structural verification

| Check | Result |
|---|---|
| model.yaml defines 6 entities | PASS |
| model.schema.json is valid JSON Schema | PASS |
| model.schema.json $defs: Sheet, Row, Cell, Formula, Warning | PASS |
| field-map.yaml has 19 mappings | PASS |
| coverage-matrix.yaml totals: 13+2+10+5=30 | PASS |
| validation-rules.yaml has 21 rules (18 error, 3 warning) | PASS |

### 4c. Governance checks

| Check | Result |
|---|---|
| No forbidden paths (src/python/fods, src/net/fods, etc.) | PASS |
| No Gate 5 self-approval | PASS |
| Registry gate_5.approved_by is null | PASS |
| Registry gate_5.status is NOT 'passed' | PASS |

---

## 5. Coverage Summary

**Covered (13):** office:document root, office:body/spreadsheet, table:table, table:table-row, table:table-cell, text:p content, float values, string values, boolean values, table:formula raw, formula cached value, office:version, office:mimetype

**Partial (2):** table:covered-table-cell (warning only), table:number-columns-repeated (model field exists, prototype expands inline)

**Deferred (10):** date, time, currency, percentage value types, row repeat, column definitions, named ranges, database ranges, pivot tables, consolidation, external cell links

**Out of scope (5):** styling, automatic-styles, text:span formatting, draw:frame/images, office:scripts/macros, font declarations

---

## 6. Key Design Decisions

1. **Formula as first-class entity** — Raw formula string elevated to Formula object with raw, cached_value, evaluated, evaluator fields
2. **Warning entity** — Structured diagnostics for unexpected/unsupported content
3. **Strict schema** — `additionalProperties: false` on all entities for forward compatibility
4. **evaluated=false always** — Formula evaluation explicitly excluded from v1
5. **Value type enum includes null** — Empty cells have null value_type

---

## 7. What Gate 5 Approval Authorizes

If Gate 5 is approved:
1. TC-0025 becomes ready for execution (Gate 6 oracle comparison planning)
2. Gate 6 planning can begin (oracle tool selection, comparison methodology)
3. Gate 6 execution requires separate explicit prompt
4. No product source is created by Gate 5 approval alone
5. No release is authorized

---

## 8. What Gate 5 Approval Does NOT Authorize

- No product source code (`src/python/fods/`, `src/net/fods/`)
- No oracle comparison execution (Gate 6)
- No fuzz testing (Gate 7)
- No security review (Gate 8)
- No release (Gate 10+)

---

## 9. Evidence References

| Evidence | Location |
|---|---|
| Neutral model schema | `schemas/neutral-model/fods/model.yaml` |
| JSON Schema | `schemas/neutral-model/fods/model.schema.json` |
| Field map | `schemas/neutral-model/fods/field-map.yaml` |
| Coverage matrix | `schemas/neutral-model/fods/coverage-matrix.yaml` |
| Validation rules | `schemas/neutral-model/fods/validation-rules.yaml` |
| Model README | `schemas/neutral-model/fods/README.md` |
| Validation tool | `tools/model/validate_neutral_model.py` |
| Design notes | `acquisition-packs/fods/neutral-model-notes.md` |
| TC-0023 (execution) | `taskcards/TC-0023-fods-gate5-neutral-model-execution.md` |
| TC-0024 (verification) | `taskcards/TC-0024-fods-gate5-neutral-model-verification.md` |
| Prototype parser | `prototypes/by-format/fods/fods_parser.py` |
| Registry entry | `registry/format-registry.yaml` (gate_5 section) |

---

## 10. Gate 5 Approval Request

**Gate 5 is NOT approved.**

This packet presents the evidence for human review. Only a human can approve Gate 5.

TC-0024 DEC-034 independent verification: PASS (run034, 2026-05-06).
All acceptance criteria met. No errors. No forbidden paths. No self-approval.
