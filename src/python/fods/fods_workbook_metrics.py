"""fods_workbook_metrics.py — Extracted workbook metric functions for the FODS neutral model.

Split out of fods_analytics.py (TC-PA-017 monolith healing) to keep each source
module under the 800-LOC architecture cap. These are pure analytics functions that
operate on the parsed FODS workbook dict as returned by parse_fods(); behavior is
unchanged from the original definitions in fods_analytics.py. Re-exported from
fods_analytics.py, so every public name remains importable from its original path.

License: Apache-2.0
Package: format-factory-fods v0.1.0
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Workbook data validation summary
# ---------------------------------------------------------------------------

def workbook_data_validation_summary(workbook: dict[str, Any]) -> dict[str, Any]:
    """Return a summary of data validations found in the workbook.

    Scans for data validation metadata stored in:
    - 'data_validations' list at workbook level
    - 'content-validations' or 'table:content-validations' element data
    - per-cell 'validation' or 'table:content-validation-name' attributes

    Returns:
      validation_count: int              -- number of distinct validation rules
      validated_cell_ranges: list[str]   -- cell range expressions that have validations

    Useful for spreadsheet auditing and data integrity analysis.
    """
    validation_count = 0
    validated_cell_ranges: list[str] = []

    # Check explicit data_validations list
    validations = workbook.get("data_validations", [])
    if isinstance(validations, list):
        for v in validations:
            if isinstance(v, dict):
                validation_count += 1
                cell_range = (
                    v.get("cell_range")
                    or v.get("table:cell-range-address")
                    or v.get("range")
                    or ""
                )
                if cell_range:
                    validated_cell_ranges.append(str(cell_range))

    # Check content-validations at workbook level
    for key in ("content_validations", "content-validations", "table:content-validations"):
        cv = workbook.get(key)
        if isinstance(cv, list):
            for item in cv:
                if isinstance(item, dict):
                    validation_count += 1
                    name = item.get("name") or item.get("table:name") or ""
                    if name:
                        validated_cell_ranges.append(str(name))

    # Scan cells for validation attributes
    for sheet in workbook.get("sheets", []):
        sheet_name = sheet.get("name", "")
        for row_idx, row in enumerate(sheet.get("rows", [])):
            for col_idx, cell in enumerate(row.get("cells", [])):
                val_name = (
                    cell.get("validation")
                    or cell.get("table:content-validation-name")
                )
                if val_name and str(val_name) not in validated_cell_ranges:
                    validated_cell_ranges.append(str(val_name))

    return {
        "validation_count": validation_count,
        "validated_cell_ranges": validated_cell_ranges,
    }




def workbook_column_width_summary(workbook: dict[str, Any]) -> list[dict[str, Any]]:
    """Return column width information per sheet.

    Scans each sheet's column definitions for explicit width attributes stored
    under 'column_width', 'style:column-width', or 'width' keys. Columns
    without explicit width are reported as None.

    Returns a list of per-sheet dicts:
      sheet_name: str                -- name of the sheet
      column_count: int              -- total columns with explicit widths
      widths: list[str | None]       -- width value per column (None if absent)

    Useful for layout-sensitive spreadsheet processing and round-trip testing.
    """
    result: list[dict[str, Any]] = []
    for sheet in workbook.get("sheets", []):
        sheet_name = sheet.get("name", "")
        columns = sheet.get("columns", [])
        widths: list[Any] = []
        for col in columns:
            if isinstance(col, dict):
                width = (
                    col.get("column_width")
                    or col.get("style:column-width")
                    or col.get("width")
                )
                widths.append(str(width) if width is not None else None)
            else:
                widths.append(None)
        result.append({
            "sheet_name": sheet_name,
            "column_count": len([w for w in widths if w is not None]),
            "widths": widths,
        })
    return result




def workbook_cell_type_matrix(workbook: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a per-sheet summary of cell value types.

    For each sheet, counts cells by their value_type field:
    - "float" / "percentage" / "currency" → numeric
    - "string" / "text" → text
    - "formula" (cells with a formula attribute) → formula
    - "boolean" → boolean
    - "date" / "time" → datetime
    - None / missing → empty

    Returns a list of per-sheet dicts:
      sheet_name: str         -- name of the sheet
      total_cells: int        -- total non-empty cells
      by_type: dict[str, int] -- count per type label

    Useful for data profiling and format migration analysis.
    """
    result: list[dict[str, Any]] = []
    for sheet in workbook.get("sheets", []):
        sheet_name = sheet.get("name", "")
        by_type: dict[str, int] = {}
        total_cells = 0
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if not isinstance(cell, dict):
                    continue
                # Check for formula first
                if cell.get("formula") or cell.get("table:formula"):
                    label = "formula"
                else:
                    vtype = (
                        cell.get("value_type")
                        or cell.get("office:value-type")
                        or "empty"
                    )
                    vtype = str(vtype).lower()
                    if vtype in ("float", "percentage", "currency"):
                        label = "numeric"
                    elif vtype in ("string", "text"):
                        label = "text"
                    elif vtype in ("boolean",):
                        label = "boolean"
                    elif vtype in ("date", "time"):
                        label = "datetime"
                    else:
                        label = "empty"
                if label != "empty":
                    total_cells += 1
                by_type[label] = by_type.get(label, 0) + 1
        result.append({
            "sheet_name": sheet_name,
            "total_cells": total_cells,
            "by_type": by_type,
        })
    return result




def workbook_numeric_density(workbook: dict[str, Any], sheet_index: int = 0) -> float:
    """Return the ratio of numeric cells to total non-empty cells in a sheet.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 if no non-empty cells.
    """
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return 0.0
    sheet = sheets[sheet_index]
    nonempty = 0
    numeric = 0
    for row in sheet.get("rows", []):
        for cell in row.get("cells", []):
            val = cell.get("value")
            if val is not None and val != "":
                nonempty += 1
                if isinstance(val, (int, float)):
                    numeric += 1
    if nonempty == 0:
        return 0.0
    return numeric / nonempty




def workbook_count_nonempty_cells(
    workbook: dict[str, Any],
    sheet_index: int = 0,
) -> int:
    """Count cells with non-None, non-empty-string values in a sheet.

    Aligned with ODF 1.3 spreadsheet content model (SAL-FODS-00001).

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Count of non-empty cells. Returns 0 if sheet not found.
    """
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return 0
    sheet = sheets[sheet_index]
    count = 0
    for row in sheet.get("rows", []):
        for cell in row.get("cells", []):
            val = cell.get("value")
            if val is not None and val != "":
                count += 1
    return count




def workbook_total_numeric_value(
    workbook: dict[str, Any],
    sheet_index: int = 0,
) -> float:
    """Return the sum of all numeric cell values in a sheet.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Float sum of all numeric (int or float) cell values.
        Returns 0.0 if sheet not found or has no numeric cells.
    """
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return 0.0
    sheet = sheets[sheet_index]
    total = 0.0
    for row in sheet.get("rows", []):
        for cell in row.get("cells", []):
            val = cell.get("value")
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                total += val
    return total




def fods_sheet_count(workbook: dict[str, Any]) -> int:
    """Return the number of sheets in the workbook.

    Args:
        workbook: Parsed FODS workbook dict.

    Returns:
        Integer count of sheets. Returns 0 for an empty or invalid workbook.
    """
    return len(workbook.get("sheets", []))




def workbook_row_count(workbook: dict[str, Any], sheet_index: int = 0) -> int:
    """Return the number of rows in a sheet.

    Spec authority: SAL-FODS-00005 — Rows are <table:table-row> children of <table:table>.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        Integer count of rows in the sheet. Returns 0 if sheet not found.
    """
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return 0
    return len(sheets[sheet_index].get("rows", []))




def workbook_cell_text_at(
    workbook: dict[str, Any],
    sheet_index: int,
    row_index: int,
    col_index: int,
) -> str:
    """Return the text content of a cell at the given position.

    Spec authority: SAL-FODS-00006 — Cells are <table:table-cell> children of <table:table-row>.
                    SAL-FODS-00007 — Cell text is in <text:p> children of <table:table-cell>.

    The neutral model stores cell text in cell["value"] when value_type is "string" or
    in the "text" key when present. Returns empty string for out-of-bounds or empty cells.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_index: 0-based sheet index.
        row_index: 0-based row index.
        col_index: 0-based column index.

    Returns:
        String text of the cell, or "" if not found or cell has no text content.
    """
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return ""
    rows = sheets[sheet_index].get("rows", [])
    if row_index < 0 or row_index >= len(rows):
        return ""
    cells = rows[row_index].get("cells", [])
    if col_index < 0 or col_index >= len(cells):
        return ""
    cell = cells[col_index]
    if cell is None:
        return ""
    text = cell.get("text") or cell.get("value")
    if text is None:
        return ""
    return str(text)



# ---------------------------------------------------------------------------
# Analytics functions for deepening tests (TC-F-012)
# ---------------------------------------------------------------------------

def fods_numeric_range(workbook):
    """Return max - min of all numeric cell values. 0.0 if fewer than 2 numeric values."""
    nums = []
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                val = cell.get("value")
                if val is not None:
                    try:
                        nums.append(float(val))
                    except (ValueError, TypeError):
                        pass
    if len(nums) < 2:
        return 0.0
    return float(max(nums) - min(nums))


def fods_column_density(workbook):
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    total = 0
    nonempty = 0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                total += 1
                if cell.get("value") is not None:
                    nonempty += 1
    if total == 0:
        return 0.0
    return float(nonempty) / total


def fods_empty_row_count(workbook):
    """Return count of rows where all cells are None/empty."""
    count = 0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            cells = row.get("cells", [])
            if not cells or all(c.get("value") is None for c in cells):
                count += 1
    return count


def fods_distinct_value_count(workbook):
    """Return count of distinct non-None cell values across all sheets."""
    values = set()
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                val = cell.get("value")
                if val is not None:
                    values.add(str(val))
    return len(values)


def fods_empty_row_percentage(workbook):
    """Return ratio of empty rows to total rows. 0.0 if no rows."""
    total = 0
    empty = 0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            total += 1
            cells = row.get("cells", [])
            if not cells or all(c.get("value") is None for c in cells):
                empty += 1
    if total == 0:
        return 0.0
    return float(empty) / total


def fods_cell_value_total(workbook):
    """Return sum of all numeric cell values. 0.0 if no numeric cells."""
    total = 0.0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                val = cell.get("value")
                if val is not None:
                    try:
                        total += float(val)
                    except (ValueError, TypeError):
                        pass
    return total
