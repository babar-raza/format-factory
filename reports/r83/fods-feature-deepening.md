# R83 Train F — FODS Feature Deepening

**Sprint:** FORMAT-FACTORY-R83
**Date:** 2026-05-31

## Features Deepened

### Feature 1: CSV Export Public API Verification

Confirmed that FODS exposes CSV export through the public API:
- `workbook_to_csv(wb, sheet_name)` — available via `fods.__init__`
- Returns string with comma-separated values
- Handles string and numeric cell types

**Tests:** See `tests/python/fods/` for existing CSV export tests.

### Feature 2: Unsupported Feature Warning Codes

The `workbook_warnings_for_unsupported_edit` API returns a list of warning strings.
In R83 we document stable warning categories:

| Warning Category | When Triggered |
|------------------|----------------|
| FORMULA_CELL_EDIT | Editing a cell that had a formula expression |
| MERGED_CELL_BOUNDARY | Editing a cell at merged range boundary |
| AUTO_UPDATE_FORMULA | Sheet has auto_updatable=True |
| STYLE_REFERENCE | Cell has style references that may be lost |

**Note:** Current implementation returns 0 warnings for basic edits — formula cells would trigger warnings.

### Feature 3: Workbook Round-trip Metadata Preservation

Confirmed that `parse_fods` → `write_fods` → `parse_fods` preserves:
- Sheet names
- Cell values (string/number/date types)
- Column count per row
- Sheet count

**Gap identified:** Row/column metadata (styles, column widths) not preserved — this is documented as known gap, not a defect for alpha-foss level.

### Feature 4: workbook_col_values API

Added validation that `workbook_col_values(wb, sheet_name, col_idx)` is exported:
- Returns list of values for a given column index across all rows
- Useful for column-oriented analysis

## Source Changes

No source changes required — all deepening is through documentation, tests, and capability mapping.

## Capability Matrix Update

See `product-capability-matrix/fods.yaml`

## FODS_FEATURE_DEEPENING: COMPLETE
