# R64 Train H — FODS/FODT Product Advancement

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

## FODS New Capabilities (2)

### 1. workbook_row_style_summary(tree)

Returns a dict mapping sheet names to lists of row style attributes (rows with `table:style-name`).

- Implementation: `src/python/fods/neutral_model.py`
- Export: `src/python/fods/__init__.py`
- Tests: `tests/python/fods/test_r64_fods_advancement.py`

### 2. workbook_formula_edit_policy(tree)

Returns dict with `total_formulas`, `editable_formulas`, `locked_formulas` counts.

- Implementation: `src/python/fods/neutral_model.py`
- Export: `src/python/fods/__init__.py`
- Tests: `tests/python/fods/test_r64_fods_advancement.py`

## FODT New Capabilities (2)

### 1. document_table_cell_span_summary(tree)

Returns dict with `total_cells`, `cells_with_colspan`, `cells_with_rowspan`.

- Implementation: `src/python/fodt/neutral_model.py`
- Export: `src/python/fodt/__init__.py`
- Tests: `tests/python/fodt/test_r64_fodt_advancement.py`

### 2. document_text_field_warnings(tree)

Returns list of warning strings for detected text:placeholder, text:date, text:page-number fields.

- Implementation: `src/python/fodt/neutral_model.py`
- Export: `src/python/fodt/__init__.py`
- Tests: `tests/python/fodt/test_r64_fodt_advancement.py`

## API Count Update

- FODS: 13 exported APIs (11 R63 + 2 R64)
- FODT: 13 exported APIs (11 R63 + 2 R64)

## Installed Wheel Proof

Both new FODS and FODT functions are accessible from installed wheel in clean venv (Train D proof).

---

FODS_FODT_PRODUCT_ADVANCEMENT_STATUS: COMPLETE
