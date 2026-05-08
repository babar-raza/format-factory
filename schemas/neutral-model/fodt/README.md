---
artifact_id: fodt-neutral-model-readme
artifact_type: schema
path: schemas/neutral-model/fodt/README.md
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
notes: "FODT neutral model README. Gate 5 artifact. Created run046 (2026-05-08). 7 entities, 26 field mappings. Validated 4/4 PASS against FODT samples."
---

# FODT Neutral Model v1

**Gate:** 5 — Neutral Model Defined
**Format:** FODT (Flat OpenDocument Text)
**Version:** 1.0
**Created:** run046 (2026-05-08)
**Validated:** 4/4 PASS (validate_fodt_neutral_model.py, run046)

---

## Overview

This directory contains the Gate 5 neutral model for FODT — the language-neutral intermediate
representation of parsed FODT text document content. The model bridges the prototype parser
output (`prototypes/by-format/fodt/fodt_parser.py`) and future product implementations.

---

## Entities (7)

| Entity | Description | Parser Source |
|---|---|---|
| Document | Root container: metadata + content counts + content lists | Top-level result dict |
| Block | Paragraph or heading element (text:p / text:h) | result['paragraphs'] entries |
| List | List container (text:list) | result['lists'] entries |
| ListItem | Individual list item (text:list-item) | list['items'] entries |
| Table | Table element (table:table) | result['tables'] entries |
| TableRow | Row within a table (table:table-row) | table['rows'] entries (lists) |
| TableCell | Cell within a row (table:table-cell) | cell strings within row |

---

## Field Counts

| Entity | Fields |
|---|---|
| Document | 11 (format_id, spec_version, mime_type, version_attr, word_count, block_count, list_count, table_count, blocks, lists, tables) |
| Block | 4 (element, text, style_name, outline_level) |
| List | 3 (list_style, item_count, items) |
| ListItem | 2 (text, level) |
| Table | 4 (name, row_count, column_count, rows) |
| TableRow | 1 (cells) |
| TableCell | 1 (text) |
| **Total** | **26** |

---

## Validation Rules (19)

| Rule | Entity | Severity |
|---|---|---|
| VR-F001 | Document | error |
| VR-F002 | Document | error |
| VR-F003 | Document | error |
| VR-F004 | Document | error |
| VR-F005 | Document | error |
| VR-F006 | Document | error |
| VR-F007 | Document | error |
| VR-F008 | Document | error |
| VR-F009 | Block | error |
| VR-F010 | Block | error |
| VR-F011 | Block | error |
| VR-F012 | Block | warning |
| VR-F013 | List | error |
| VR-F014 | List | error |
| VR-F015 | ListItem | error |
| VR-F016 | ListItem | error |
| VR-F017 | Table | error |
| VR-F018 | Table | error |
| VR-F019 | TableCell | error |

---

## Sample Validation Results (run046)

| Sample | Blocks | Lists | Tables | word_count | Result |
|---|---|---|---|---|---|
| minimal-document.fodt | 1 (1p) | 0 | 0 | 2 | PASS |
| headings-and-paragraphs.fodt | 7 (3h+4p) | 0 | 0 | 44 | PASS |
| list-basic.fodt | 2 (2p) | 2 (3+3 items) | 0 | 6 | PASS |
| table-basic.fodt | 2 (2p) | 0 | 1 (3x2) | 7 | PASS |

**FODT_NEUTRAL_MODEL_VALIDATION: PASS 4/4**

---

## Files

| File | Purpose |
|---|---|
| `model.yaml` | Entity and field definitions |
| `model.schema.json` | JSON Schema for parser output validation |
| `field-map.yaml` | Parser output key → neutral model field mapping |
| `coverage-matrix.yaml` | ODF element coverage (FR-001..FR-007) |
| `validation-rules.yaml` | Cross-entity semantic constraints (VR-F001..VR-F019) |
| `README.md` | This overview |

---

## FODS Reuse Notes

The FODT model follows the FODS neutral model structural pattern (same 6-file set,
same front matter schema). Reused concepts: Document metadata fields, Table/TableRow/TableCell
pattern, field-map format, coverage-matrix format, validation-rules format.

New FODT-specific concepts: Block element distinction (paragraph/heading), outline_level,
List structure, ListItem nesting level.

---

*Created by claude-sonnet-4-6, run046, 2026-05-08.*
