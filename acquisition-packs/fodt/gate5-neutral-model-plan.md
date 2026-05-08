---
artifact_id: fodt-gate5-neutral-model-plan
artifact_type: evidence
path: acquisition-packs/fodt/gate5-neutral-model-plan.md
format_id: fodt
product_family: words
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT Gate 5 neutral model planning document. Created run045 (2026-05-08). Execution requires explicit Gate 5 prompt. Gate 4 PASSED (Babar Raza, 2026-05-08, run045)."
---

# FODT Gate 5 — Neutral Model Plan

**Gate:** 5 — Neutral Model Defined
**Format:** FODT (Flat OpenDocument Text)
**Run:** run045 planning (2026-05-08)
**Prepared by:** claude-sonnet-4-6
**Status:** planning_ready — execution blocked until explicit Gate 5 prompt

---

## Prerequisites (all met)

| Prerequisite | Status |
|---|---|
| Gate 4 PASSED | PASS — Babar Raza, 2026-05-08, run045 |
| FODT_PROTOTYPE_VALIDATION 4/4 | PASS — TC-0034/TC-0035 COMPLETED |
| Gate 3 samples available | YES — 4 samples in samples/by-format/fodt/ |
| FODS neutral model reference | YES — schemas/neutral-model/fods/ (6 entities) |
| Spec cache available | YES — reuses fods/1.3/ (FODS Gate 2 waiver) |

---

## Proposed Entity Model

Based on the FODT parser output structure (from `prototypes/by-format/fodt/fodt_parser.py`),
the neutral model will define the following entities:

### Document (root)

| Field | Type | Required | Source |
|---|---|---|---|
| format_id | string | yes | Always "fodt" |
| spec_version | string | yes | "ODF 1.3" |
| mime_type | string | yes | office:mimetype attribute |
| version_attr | string | yes | office:version attribute |
| word_count | integer | yes | Computed from all text content |
| block_count | integer | yes | Count of paragraphs + headings |
| list_count | integer | yes | Count of top-level lists |
| table_count | integer | yes | Count of tables |
| blocks | Block[] | yes | Ordered list of blocks |
| lists | List[] | yes | List of top-level list structures |
| tables | Table[] | yes | List of table structures |
| errors | string[] | no | Parse errors (empty = clean) |

### Block (paragraph or heading)

| Field | Type | Required | Source |
|---|---|---|---|
| element | enum | yes | "paragraph" (text:p) or "heading" (text:h) |
| text | string | yes | Concatenated text content |
| outline_level | integer | no | text:outline-level attribute (headings only) |

### List

| Field | Type | Required | Source |
|---|---|---|---|
| list_style | enum | yes | "bullet" / "numbered" / "unknown" |
| item_count | integer | yes | Direct child items count |
| items | ListItem[] | yes | List items |

### ListItem

| Field | Type | Required | Source |
|---|---|---|---|
| text | string | yes | Concatenated text content |
| nested_list | List | no | Optional nested list |

### Table

| Field | Type | Required | Source |
|---|---|---|---|
| row_count | integer | yes | Count of table:table-row elements |
| rows | TableRow[] | yes | All rows |

### TableRow

| Field | Type | Required | Source |
|---|---|---|---|
| cells | TableCell[] | yes | All cells in row |

### TableCell

| Field | Type | Required | Source |
|---|---|---|---|
| text | string | yes | Concatenated text from text:p descendants |

---

## Sample Coverage Plan

All 4 Gate 3 samples must PASS validation:

| Sample | Key Coverage |
|---|---|
| minimal-document.fodt | Document root, single paragraph, word_count |
| headings-and-paragraphs.fodt | Block elements with element="heading" + outline_level |
| list-basic.fodt | List with bullet and numbered styles, ListItem |
| table-basic.fodt | Table, TableRow, TableCell |

---

## FODS Reuse Analysis

The FODT neutral model reuses the following patterns from the FODS model
(`schemas/neutral-model/fods/`):

| Pattern | Reused | Notes |
|---|---|---|
| model.yaml structure | Yes — adapted | Different entities but same YAML layout |
| model.schema.json pattern | Yes — adapted | Validates parse_fodt() output dict |
| field-map.yaml ODF source cross-ref | Yes — new entries | FODT ODF elements differ from FODS |
| coverage-matrix.yaml layout | Yes — adapted | Different features |
| validation-rules.yaml structure | Yes — adapted | Different rules |
| validate_neutral_model.py pattern | Yes — new file | validate_fodt_neutral_model.py |

---

## Comparison: FODS vs FODT Neutral Model

| Dimension | FODS | FODT |
|---|---|---|
| Root entity | Workbook | Document |
| Primary content | Sheet → Row → Cell | Block (para/heading) |
| List support | No | Yes (bullet/numbered) |
| Table support | Yes (full ODF table) | Yes (simplified, text only) |
| Heading support | No | Yes (outline_level) |
| Formula support | Yes | No |
| Multi-sheet | Yes | No (single document) |
| Estimated entity count | 6 | 7 |
| Estimated field count | ~25 | ~20 |

---

## Gate 5 Execution Authorization

Gate 5 execution is blocked until:
1. A human issues an explicit Gate 5 execution prompt naming "FODT Gate 5 neutral model"
2. The executing agent reads this plan and `schemas/neutral-model/fods/` as reference
3. After execution, DEC-034 independent verification must be run in a separate session
4. Human approves Gate 5 after DEC-034 PASS

---

## References

- `taskcards/TC-0037-fodt-gate5-neutral-model.md` — execution taskcard
- `schemas/neutral-model/fods/` — FODS neutral model reference
- `prototypes/by-format/fodt/fodt_parser.py` — parser output structure
- `samples/by-format/fodt/` — 4 Gate 3 validation samples
- `docs/gates.md` Gate 5 criteria
