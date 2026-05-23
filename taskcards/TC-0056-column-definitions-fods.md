# TC-0056: Column Definitions Preservation — FODS Python Writer

**ID:** TC-0056-column-definitions-fods
**Gap ID:** TC-COLDEF-001
**Status:** CLOSED_VERIFIED
**Priority:** Low
**Format:** FODS
**Track:** Python FOSS
**Sprint origin:** R49 (preservation matrix gap)
**Sprint target:** R52 or later

## Gap Description

Python FODS writer discards `table:table-column` elements on write. Column width, optimal
width flag, and default cell style are lost. The output has no column definition elements.

## Evidence

- Preservation matrix: `reports/r49/preservation-matrix-fods.md`
- Gap ID: TC-COLDEF-001

## Acceptance Criteria

1. When round-tripping a FODS file with explicit column definitions, the
   `<table:table-column>` elements are preserved in the output.
2. `table:column-width`, `table:optimal-width`, and `table:default-cell-style-name`
   attributes are preserved verbatim.
3. At least 2 new tests covering column-definition round-trip.

## Fix Scope

- `src/python/fods/parser.py`: capture column definitions per sheet
- `src/python/fods/writer.py`: emit `<table:table-column>` before row data

## Note

Column definitions are tracked as LOW priority (cosmetic, not data-impacting).
Python FOSS track focuses on data correctness; full layout fidelity is .NET commercial.

## Closure

**Closed:** R55, 2026-05-23
**Sprint:** FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
**Evidence:**
- `table:table-column` attributes captured per-sheet as `column_defs` list in `src/python/fods/parser.py`
- Writer `_write_sheet()` emits `<table:table-column>` before row data via `col_el.set()`
- Column definition elements appear before `table:table-row` (ODF ordering requirement met)
- 6 tests in `tests/python/fods/test_r55_fods_style_coldef.py` (`TestColumnDefsCapture`)
- All tests pass. `table:default-cell-style-name` and other attributes preserved on round-trip.
**Status:** CLOSED_VERIFIED
