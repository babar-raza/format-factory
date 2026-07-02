# TC-GI001-L6A-001 — Python FODS Spot-Check
# GI-FODS-NET-001 Phase 6a: Does Python FODS replicate the .NET anti-pattern?

**Date:** 2026-07-02  
**File checked:** `src/python/fods/spreadsheet_document.py`

## Finding: Python does NOT replicate GI-FODS-NET-001

### Analysis
The Python FODS module uses a functional, workbook-dict-based architecture
with no OOP instance state. Key observations:

1. **No detached dictionary-backed property stubs.** There are no `_cell_font_color = {}`
   or similar instance fields returning misleading values. The Python module has no equivalent
   of the .NET `_sheetFreezeRows`, `_cellFontColors`, or `_columnWidths` stubs.

2. **No constant-return APIs.** Python has no equivalent of Category D
   (`GetFormulaCount() => 0`, `GetImageCount() => 0`, etc.).

3. **Column width gap:** `workbook_column_width_summary` reads raw parsed attributes
   (`col.get("column_width") or col.get("style:column-width") or col.get("width")`).
   The ODF parser captures `table:table-column` raw attributes (`column_defs = dict(elem.attrib)`)
   without resolving the `table:style-name` → `style:column-width` chain.
   **Result:** Returns `None` for widths stored in `office:automatic-styles` — honest gap,
   not a misleading stub.

4. **Row style gap:** `workbook_row_style_summary` reads raw style-name attributes only.
   No style chain resolution. Same honest-gap pattern.

### Verdict
**NOT a governance incident.** Python has a capability gap (no ODF style chain resolver
for column/row dimensions), but it does not return misleading/fabricated data.
Python governance validators V44, V48, V69 are not triggered.

### Gap registration
A gap may be opened for `GAP-FODS-PY-NO-STYLE-CHAIN-001` in a future sprint if
style-chain resolution is required for the Python product. This is NOT blocking
for GI-FODS-NET-001 resolution.
