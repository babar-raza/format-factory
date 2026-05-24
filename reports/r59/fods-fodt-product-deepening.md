# R59 Train G — FODS/FODT Product Deepening

**Sprint:** FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Status:** COMPLETE
**Date:** 2026-05-24

---

## New Capabilities

### FODS (2 new — src/python/fods/neutral_model.py)

#### 1. `workbook_type_distribution(workbook)`
Returns the distribution of cell `value_type` attributes across all sheets.
- `by_type: dict[str, int]` — count per type label (float, string, boolean, percentage, date, empty, etc.)
- `total_cells: int`
- `per_sheet: list[dict]` — per-sheet breakdown with same `by_type` structure

Useful for schema inference and format triage pipelines.

#### 2. `find_sheet_by_name(workbook, name)`
Returns the first sheet dict with the given name (case-sensitive), or `None`.
Useful for programmatic access to named sheets without manual iteration.

### FODT (2 new — src/python/fodt/neutral_model.py)

#### 3. `document_heading_outline(document)`
Returns an ordered list of all headings: `[{"level": int, "text": str, "index": int}, ...]`
Respects `content` list (document-order) if present.
Useful for table-of-contents generation and document navigation.

#### 4. `document_text_content(document, separator="\n")`
Returns all text content from blocks, list items, and table cells as a single string.
Configurable separator. Respects `content` list if present.
Useful for full-text extraction and search indexing.

---

## Public API Export

All 4 new functions added to `__all__` in respective `__init__.py` files:
- `fods`: `workbook_type_distribution`, `find_sheet_by_name`
- `fodt`: `document_heading_outline`, `document_text_content`

---

## Tests

**tests/python/fods/test_r59_fods_deepening.py** — 13 tests (7 type_distribution + 6 find_sheet)
**tests/python/fodt/test_r59_fodt_deepening.py** — 17 tests (8 heading_outline + 9 text_content)

**30/30 PASS**

Key coverage:
- Empty workbook/document edge cases
- Mixed type distribution with per-sheet breakdown
- Formula cells counted by value_type not formula presence
- Case-sensitive name matching
- Content-list override (respects document order)
- Custom separators
- Empty text filtering

---

## Verdict

**TRAIN_G_COMPLETE** — 4 new product capabilities (2 FODS + 2 FODT) implemented.
All 30 tests PASS. Public API exported. No regressions.
