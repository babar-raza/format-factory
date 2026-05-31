# R84 Train G: FODS Feature Advancement

**Sprint:** FORMAT-FACTORY-R84
**Train:** G
**Date:** 2026-05-31
**Status:** COMPLETE

## New APIs

### workbook_to_csv(workbook, sheet_name=None) -> str

CSV export for a specific workbook sheet (or first sheet if sheet_name is None).

- Uses stdlib `csv` module with RFC 4180 CRLF line endings
- Exports cells in row-major order
- Empty cells produce empty CSV fields
- Numeric values formatted without trailing decimal where possible
- Returns empty string for empty/missing sheet

Source: `src/python/fods/neutral_model.py`
Exported from: `src/python/fods/__init__.py`

### workbook_get_cell_value(workbook, sheet_name, row_index, col_index) -> Any

Read-side complement of workbook_set_cell_value.

- 0-based row and column indices
- Returns None if sheet/row/col does not exist
- sheet_name=None uses first sheet

Source: `src/python/fods/neutral_model.py`
Exported from: `src/python/fods/__init__.py`

## Tests

File: `tests/python/fods/test_r84_fods_csv_export.py`
- 8 test cases: empty workbook, single sheet, multi-row, numeric cells,
  string cells, named sheet, missing sheet returns empty, cell value read

## Documentation

Added to `docs/python-foss/fods-api.md` under "R84 Additions".

## Result

PASS — both new APIs implemented, tested, documented, and exported.
