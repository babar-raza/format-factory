# R60 Train G — FODS/FODT Product Deepening

**Sprint:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

---

## New Capabilities

### FODS (2 new — src/python/fods/neutral_model.py)

#### 1. `workbook_sheet_summary(workbook)`
Returns a compact per-sheet summary as a list of dicts:
- `name: str`, `index: int`, `row_count: int`
- `cell_count: int` (total cells including empty)
- `non_empty_count: int` (cells with value != None)
- `formula_count: int` (cells with formula attribute)

Useful for quick structural overview without full iteration.
**Added in R60 Train G.**

#### 2. `workbook_empty_rows(workbook)`
Returns empty-row statistics:
- `total_empty_rows: int` (across all sheets)
- `per_sheet: list[dict]` — per-sheet breakdown with `empty_row_count`, `total_row_count`

A row is empty when all its cells have value == None or it has no cells.
Useful for data quality assessment and sparse-data detection.
**Added in R60 Train G.**

### FODT (2 new — src/python/fodt/neutral_model.py)

#### 3. `document_word_count(document)`
Returns approximate word count by category:
- `total_words: int`
- `block_words: int` (from paragraphs + headings)
- `list_words: int` (from list items)
- `table_words: int` (from table cells)

Uses str.split() for whitespace-based tokenization. Respects content list.
Useful for content analysis and document triage.
**Added in R60 Train G.**

#### 4. `document_table_summary(document)`
Returns a compact summary of all tables as a list of dicts:
- `index: int` (0-based position)
- `row_count: int`, `column_count: int` (max across rows), `cell_count: int`

Respects content list (document-order) if present.
Useful for table triage and structural analysis.
**Added in R60 Train G.**

---

## Public API Export

All 4 new functions added to `__all__` in respective `__init__.py` files.
All 4 available from installed wheel (proven in Train D).

---

## Tests

**tests/python/fods/test_r60_fods_deepening.py** — 19 tests (9 sheet_summary + 10 empty_rows)
**tests/python/fodt/test_r60_fodt_deepening.py** — 19 tests (11 word_count + 8 table_summary)

**38/38 PASS**

Key coverage:
- Empty workbook/document edge cases
- Multi-sheet totals and per-sheet breakdown
- Row with no cells treated as empty
- Content list override (document-order)
- Uneven table column counts (max computed)
- All combinations of runs/plain text in blocks

---

## Total R59+R60 FODS API count: 5 (workbook_stats + 2 R59 + 2 R60)
## Total R59+R60 FODT API count: 5 (document_stats + 2 R59 + 2 R60)

**TRAIN_G_COMPLETE — 4 new product capabilities (2 FODS + 2 FODT). 38/38 PASS.**
