---
artifact_id: fodt-parser-notes-v1
artifact_type: acquisition-pack
path: acquisition-packs/fodt/parser-notes.md
format_id: fodt
product_family: words
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-07"
reusable: true
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT parser planning notes. Gate 3 PASSED (Babar Raza, 2026-05-08, run044). Gate 4 parser prototype planning complete (run044): TC-0034/TC-0035, gate4-parser-prototype-plan.md, parser-requirements.md, parser-scope.md, parser-test-plan.md. Execution requires explicit Gate 4 prompt."
---

# FODT Parser Notes — Gate 4 Planning

**Format:** FODT — Flat OpenDocument Text
**Gate:** 4 (Parser Prototype)
**Status:** PLANNING_READY — Gate 3 PASSED (Babar Raza, 2026-05-08, run044); awaiting explicit Gate 4 execution prompt
**Parser approach:** ElementTree (stdlib) — reuse FODS fods_parser.py pattern

---

## Status

**Gate 4 parser prototype planning is COMPLETE (run044). Execution is blocked pending explicit Gate 4 prompt.**

Parser prototype may not be created until Gate 3 (sample corpus) is approved by a human reviewer.
This file is a planning skeleton only, based on analysis at Gate 1 scoring time.

---

## Parser Approach

FODT uses the same flat-XML structure as FODS. The `prototypes/by-format/fods/fods_parser.py`
(Gate 4, 4/4 PASS) provides the following directly reusable patterns:

- XML namespace dictionary definition
- `ElementTree.parse()` on a flat XML file
- Namespace-qualified element traversal (`.//{ns}element`)
- Attribute extraction with `elem.get("ns:attr")`
- Output data structure (dict-based neutral model)

**New work required for FODT vs FODS:**

| Component | Effort | Notes |
|---|---|---|
| `text:p` extraction | Low | Paragraph text content with `itertext()` |
| `text:h` extraction | Low | Heading with `@text:outline-level` attribute |
| `text:list` / `text:list-item` | Medium | Nested list handling, ordered vs unordered |
| `table:table` within `office:text` | Medium | Table-in-text vs FODS sheet-centric structure |
| Basic style resolution | Medium | Automatic-styles → named-styles lookup |
| Character styles (text:span) | Low-Medium | `@text:style-name` on inline elements |
| Sections (`text:section`) | Low | Named content sections |

---

## Prototype Target (Gate 4)

Minimum viable prototype for Gate 4:

```
fodt_parser.py parse FODT file → dict with:
  - document.title (from dc:title if present)
  - document.paragraphs[]: list of paragraph dicts with text, style_name, outline_level
  - document.tables[]: list of table dicts with rows/cells
  - document.lists[]: list of list dicts with items and levels
  - document.word_count: total words across all paragraphs
```

**Validation:** Against Gate 3 FODT samples (4 files, similar to FODS 4/4 PASS pattern).

---

## Implementation Path

```
prototypes/by-format/fodt/
  fodt_parser.py           (Gate 4 prototype — to be created)
  validate_against_samples.py (validation script — to be created)
  README.md                (prototype description — to be created)
  prototype-notes.md       (scoring and notes — to be created)
```

---

## Key Namespace Differences from FODS

| FODS (Spreadsheet) | FODT (Text) |
|---|---|
| `office:spreadsheet` | `office:text` |
| `table:table` (root structure) | `text:p` / `text:h` (primary elements) |
| `table:table-row` | `text:list` / `text:list-item` |
| `table:table-cell` | `table:table` (nested within text flow) |
| Cell types: string/float/boolean | Paragraph types: body/heading/list |
| Namespace: `xmlns:table` | Namespace: `xmlns:text` |

---

## Gate 4 Prerequisites

1. Gate 3 approved (samples validated)
2. Explicit Gate 4 execution prompt issued
3. Parser requirements exported from spec normalization layer
4. TC-0017 pattern followed (create parser, validate, produce prototype-notes.md)
