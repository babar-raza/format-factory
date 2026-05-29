# R73 FODS/FODT Product Advancement

**Sprint:** FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Train:** D

---

## Summary

4 product improvements implemented (2 FODS + 2 FODT). 16 new tests, all passing.
Existing 848 FODS/FODT tests: all still passing.

---

## FODS Improvements

### FODS Improvement 1: Merged Cell Span Metadata Preservation

**Files changed:** `src/python/fods/constants.py`, `src/python/fods/parser.py`
**Tests:** `tests/python/fods/test_r73_fods_merged_cell_span.py` (8 tests)

**What changed:**
- Added `ATTR_COL_SPAN = table:number-columns-spanned` constant
- Added `ATTR_ROW_SPAN = table:number-rows-spanned` constant
- In `_process_row_elem`: reads `table:number-columns-spanned` and `table:number-rows-spanned` from each cell element
- Cell dict now includes `col_span` key when value > 1, `row_span` key when value > 1
- Default (span=1) cells do NOT get these keys (compact output preserved)

**Why this matters:**
Merged cells are common in real-world spreadsheets. Previously, the parser captured the presence of covered cells (via `is_covered`) but did not capture the span dimensions of the originating cell. Consumers had no way to know how many columns/rows a cell spans. This improvement gives consumers accurate span information for rendering/conversion.

**ODF 1.3 reference:** Section 9.1.4 (table:table-cell attributes)

### FODS Improvement 2: Formula Cell Deterministic Warning Code

**Files changed:** `src/python/fods/constants.py`, `src/python/fods/parser.py`
**Tests:** `tests/python/fods/test_r73_fods_merged_cell_span.py` (3 tests, including negative test)

**What changed:**
- Added `WARN_FORMULA_CELL = "FORMULA_CELL"` constant
- In `_process_row_elem`: when a cell has a `table:formula` attribute, emits `WARN_FORMULA_CELL` warning with location info and adds `"formula"` to `unsupported_features`
- Formula string is still captured in cell dict (IR-FODS-008 preserved)

**Why this matters:**
Previously, formulas were captured silently (IR-FODS-008: capture, don't eval). Consumers had no standardized way to detect formula presence except iterating all cells. The `WARN_FORMULA_CELL` warning code provides a deterministic signal that the workbook contains formulas, enabling consumers to show appropriate messages.

---

## FODT Improvements

### FODT Improvement 1: Footnote/Endnote Detection Warning

**Files changed:** `src/python/fodt/constants.py`, `src/python/fodt/parser.py`
**Tests:** `tests/python/fodt/test_r73_fodt_note_and_cell_span.py` (4 tests)

**What changed:**
- Added `QN_TEXT_NOTE = text:note` qualified name constant
- Added `WARN_NOTE_ELEMENT = "NOTE_ELEMENT"` constant
- In `_handle_text_child`: when a `text:note` element is encountered, emits `WARN_NOTE_ELEMENT` warning with note-class info ("footnote" or "endnote") and adds `"footnote-endnote"` to `unsupported_features`
- Note body content is not preserved in neutral model (too deep for Tier 0-2)

**Why this matters:**
Footnotes and endnotes are common in professional documents. Previously, `text:note` elements were silently dropped (fell through to the else clause). This left consumers unaware that the document had notes. The new warning provides transparency about note presence without requiring full note rendering support.

**ODF 1.3 reference:** Section 6.3 (text:note)

### FODT Improvement 2: Table Cell Span Preservation

**Files changed:** `src/python/fodt/constants.py`, `src/python/fodt/parser.py`
**Tests:** `tests/python/fodt/test_r73_fodt_note_and_cell_span.py` (4 tests)

**What changed:**
- Added `ATTR_TABLE_COL_SPAN = table:number-columns-spanned` constant
- Added `ATTR_TABLE_ROW_SPAN = table:number-rows-spanned` constant
- Added `_safe_int_fodt()` helper function
- In `_extract_table`: reads span attributes from table cells; adds `col_span`/`row_span` to cell dicts when value > 1
- Regular cells (span=1) are unchanged (compact output preserved)

**Why this matters:**
FODT tables can have merged cells (like FODS). The previous `_extract_table` only captured cell text content (`{"text": ...}`). Adding span information enables consumers to correctly reconstruct the table layout.

**ODF 1.3 reference:** Section 9.1.4

---

## Test Results

| Test File | Tests | Result |
|---|---|---|
| test_r73_fods_merged_cell_span.py | 8 | 8 PASS |
| test_r73_fodt_note_and_cell_span.py | 8 | 8 PASS |
| All existing FODS/FODT tests | 848 | 848 PASS |

New tests: **16** (all PASS)
Regressions: **0**

---

## Capability Claims

- FODS: "merged-cell span metadata" — NOW CAPTURED (col_span, row_span when >1)
- FODS: "formula cell detection" — NOW DETERMINISTIC (WARN_FORMULA_CELL warning code)
- FODT: "footnote/endnote detection" — NOW DETERMINISTIC (WARN_NOTE_ELEMENT warning code)
- FODT: "table cell span" — NOW CAPTURED (col_span, row_span when >1)

All capabilities are Tier 0-2 transparency improvements. No full fidelity claims.

FODS_FODT_ADVANCEMENT: COMPLETE_16_NEW_TESTS_0_REGRESSIONS
