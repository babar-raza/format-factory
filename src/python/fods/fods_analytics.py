"""
fods_analytics.py -- Analytics functions for the FODS neutral model.

These functions compute statistics and summaries from parsed FODS workbook dicts.
Extracted from neutral_model.py to maintain module responsibility separation.

All functions accept a workbook dict as returned by parse_fods() and return
structured analytics data suitable for content assessment pipelines.

License: Apache-2.0
Package: format-factory-fods v0.1.0
"""

from __future__ import annotations

from typing import Any




# ---------------------------------------------------------------------------
# Workbook statistics (R57 — new capability)
# ---------------------------------------------------------------------------

def workbook_stats(workbook: dict[str, Any]) -> dict[str, Any]:
    """Return cell-level statistics for a parsed FODS workbook.

    Returns a dict with:
      sheet_count: int
      total_rows: int
      total_cells: int     (all cells including empty)
      non_empty_cells: int  (cells where value is not None)
      formula_cells: int    (cells with a table:formula attribute)
      per_sheet: list[dict] (per-sheet breakdown)

    Added in R57 Train E as a new product capability.
    Useful for format triage and content assessment pipelines.
    """
    stats: dict[str, Any] = {
        "sheet_count": 0,
        "total_rows": 0,
        "total_cells": 0,
        "non_empty_cells": 0,
        "formula_cells": 0,
        "per_sheet": [],
    }
    sheets = workbook.get("sheets", [])
    stats["sheet_count"] = len(sheets)
    for sheet in sheets:
        rows = sheet.get("rows", [])
        total_cells = sum(len(row.get("cells", [])) for row in rows)
        non_empty = sum(
            1 for row in rows
            for cell in row.get("cells", [])
            if cell.get("value") is not None
        )
        formula = sum(
            1 for row in rows
            for cell in row.get("cells", [])
            if cell.get("formula") is not None
        )
        stats["total_rows"] += len(rows)
        stats["total_cells"] += total_cells
        stats["non_empty_cells"] += non_empty
        stats["formula_cells"] += formula
        stats["per_sheet"].append({
            "name": sheet.get("name", ""),
            "index": sheet.get("index", 0),
            "row_count": len(rows),
            "total_cells": total_cells,
            "non_empty_cells": non_empty,
            "formula_cells": formula,
        })
    return stats




# ---------------------------------------------------------------------------
# Workbook type distribution (R59 — new capability)
# ---------------------------------------------------------------------------

def workbook_type_distribution(workbook: dict[str, Any]) -> dict[str, Any]:
    """Return a distribution of cell value_types across the workbook.

    Counts how many cells have each value_type (float, int, string, boolean,
    percentage, currency, date, time, and empty/None). Useful for schema
    inference and format triage pipelines.

    Returns a dict with:
      by_type: dict[str, int]  — count per value_type label (empty = no value)
      total_cells: int
      per_sheet: list[dict]   — per-sheet breakdown with same by_type structure

    Added in R59 Train G as a product deepening capability.
    """
    total_by_type: dict[str, int] = {}
    total_cells = 0
    per_sheet = []

    for sheet in workbook.get("sheets", []):
        sheet_by_type: dict[str, int] = {}
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                vtype = cell.get("value_type") or ("empty" if cell.get("value") is None else "unknown")
                total_by_type[vtype] = total_by_type.get(vtype, 0) + 1
                sheet_by_type[vtype] = sheet_by_type.get(vtype, 0) + 1
                total_cells += 1
        per_sheet.append({
            "name": sheet.get("name", ""),
            "index": sheet.get("index", 0),
            "by_type": sheet_by_type,
        })

    return {
        "by_type": total_by_type,
        "total_cells": total_cells,
        "per_sheet": per_sheet,
    }




# ---------------------------------------------------------------------------
# Workbook sheet summary (R60 — new capability)
# ---------------------------------------------------------------------------

def workbook_sheet_summary(workbook: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a compact per-sheet summary of the workbook.

    Each entry in the returned list is a dict with:
      name: str
      index: int
      row_count: int
      cell_count: int       (total cells including empty)
      non_empty_count: int  (cells where value is not None)
      formula_count: int    (cells with a formula attribute)

    Useful for quick structural overview without iterating all data.
    Added in R60 Train G as a product deepening capability.
    """
    summary = []
    for sheet in workbook.get("sheets", []):
        rows = sheet.get("rows", [])
        cell_count = sum(len(row.get("cells", [])) for row in rows)
        non_empty = sum(
            1 for row in rows
            for cell in row.get("cells", [])
            if cell.get("value") is not None
        )
        formula = sum(
            1 for row in rows
            for cell in row.get("cells", [])
            if cell.get("formula") is not None
        )
        summary.append({
            "name": sheet.get("name", ""),
            "index": sheet.get("index", 0),
            "row_count": len(rows),
            "cell_count": cell_count,
            "non_empty_count": non_empty,
            "formula_count": formula,
        })
    return summary




# ---------------------------------------------------------------------------
# Workbook empty rows (R60 — new capability)
# ---------------------------------------------------------------------------

def workbook_empty_rows(workbook: dict[str, Any]) -> dict[str, Any]:
    """Return empty-row statistics for the workbook.

    A row is "empty" if all its cells have value == None (or it has no cells).

    Returns a dict with:
      total_empty_rows: int           (across all sheets)
      per_sheet: list[dict]           (per-sheet breakdown)
        Each entry: {name, index, empty_row_count, total_row_count}

    Useful for data quality assessment and sparse-data detection.
    Added in R60 Train G as a product deepening capability.
    """
    total_empty = 0
    per_sheet = []
    for sheet in workbook.get("sheets", []):
        rows = sheet.get("rows", [])
        empty = sum(
            1 for row in rows
            if all(cell.get("value") is None for cell in row.get("cells", []))
        )
        total_empty += empty
        per_sheet.append({
            "name": sheet.get("name", ""),
            "index": sheet.get("index", 0),
            "empty_row_count": empty,
            "total_row_count": len(rows),
        })
    return {
        "total_empty_rows": total_empty,
        "per_sheet": per_sheet,
    }




# ---------------------------------------------------------------------------
# Workbook formula list (R61 — new capability)
# ---------------------------------------------------------------------------

def workbook_formula_list(workbook: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a flat list of all formula cells in the workbook.

    Each entry contains:
      sheet_name: str          (name of the containing sheet)
      sheet_index: int         (0-based sheet index)
      row_index: int           (0-based row index)
      col_index: int           (0-based column index within row)
      formula: str             (formula expression, e.g. '=SUM(A1:A10)')
      value: Any               (cached value if present, else None)

    Useful for formula auditing, dependency analysis, and re-computation.
    Added in R61 Train G as a product deepening capability.
    """
    results: list[dict[str, Any]] = []
    for sheet in workbook.get("sheets", []):
        sheet_name = sheet.get("name", "")
        sheet_index = sheet.get("index", 0)
        for row_idx, row in enumerate(sheet.get("rows", [])):
            for col_idx, cell in enumerate(row.get("cells", [])):
                formula = cell.get("formula")
                if formula is not None:
                    results.append({
                        "sheet_name": sheet_name,
                        "sheet_index": sheet_index,
                        "row_index": row_idx,
                        "col_index": col_idx,
                        "formula": formula,
                        "value": cell.get("value"),
                    })
    return results




# ---------------------------------------------------------------------------
# Workbook cell range (R61 — new capability)
# ---------------------------------------------------------------------------

def workbook_cell_range(
    workbook: dict[str, Any],
    sheet_index: int = 0,
    row_start: int = 0,
    row_end: int | None = None,
    col_start: int = 0,
    col_end: int | None = None,
) -> list[list[Any]]:
    """Return a 2D list of cell values from a rectangular range in a sheet.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_index: 0-based index of the sheet to read.
        row_start: First row to include (0-based, inclusive).
        row_end: Last row to include (0-based, inclusive); None = last row.
        col_start: First column to include (0-based, inclusive).
        col_end: Last column to include (0-based, inclusive); None = last col.

    Returns:
        List of rows, each row is a list of cell values (None if empty).

    Useful for slicing tabular data, exporting ranges to CSV, and
    data pipeline integration.
    Added in R61 Train G as a product deepening capability.
    """
    sheets = workbook.get("sheets", [])
    if sheet_index >= len(sheets):
        return []
    sheet = sheets[sheet_index]
    rows = sheet.get("rows", [])

    row_slice = rows[row_start:None if row_end is None else row_end + 1]
    result = []
    for row in row_slice:
        cells = row.get("cells", [])
        col_slice = cells[col_start:None if col_end is None else col_end + 1]
        result.append([cell.get("value") for cell in col_slice])
    return result




# ---------------------------------------------------------------------------
# Workbook merged cell summary (R62 — new capability)
# ---------------------------------------------------------------------------

def workbook_merged_cell_summary(workbook: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a list of merged-cell annotations across all sheets.

    Each entry contains:
      sheet_name: str        — name of the containing sheet
      sheet_index: int       — 0-based sheet index
      row_index: int         — 0-based row index of the merged anchor cell
      col_index: int         — 0-based column index of the merged anchor cell
      merge_info: Any        — raw merge metadata from the cell (if present)

    Detects cells that carry a 'merge' or 'span' attribute.
    Returns an empty list if no merge annotations are found (most FODS files
    do not use cell merging).
    Added in R62 Train H as a product deepening capability (merged cell metadata).
    """
    results: list[dict[str, Any]] = []
    for sheet_idx, sheet in enumerate(workbook.get("sheets", [])):
        sheet_name = sheet.get("name", f"Sheet{sheet_idx + 1}")
        for row_idx, row in enumerate(sheet.get("rows", [])):
            for col_idx, cell in enumerate(row.get("cells", [])):
                merge = cell.get("merge") or cell.get("span") or cell.get("table:number-columns-spanned")
                if merge:
                    results.append({
                        "sheet_name": sheet_name,
                        "sheet_index": sheet_idx,
                        "row_index": row_idx,
                        "col_index": col_idx,
                        "merge_info": merge,
                    })
    return results




# ---------------------------------------------------------------------------
# Workbook sheet order (R62 — new capability)
# ---------------------------------------------------------------------------

def workbook_sheet_order(workbook: dict[str, Any]) -> list[str]:
    """Return the ordered list of sheet names as they appear in the workbook.

    Useful for verifying that sheet order is preserved across parse/write cycles
    and for building ordered navigation in document viewers.

    Returns:
        List of sheet name strings in parse order.
        Returns empty list for empty workbooks.
    Added in R62 Train H as a product deepening capability (sheet order preservation).
    """
    return [
        sheet.get("name", f"Sheet{i + 1}")
        for i, sheet in enumerate(workbook.get("sheets", []))
    ]




# ---------------------------------------------------------------------------
# Workbook numeric summary (R63 Train H — new capability)
# ---------------------------------------------------------------------------

def workbook_numeric_summary(workbook: dict[str, Any]) -> dict[str, Any]:
    """Return per-sheet numeric statistics across all numeric cells.

    Scans all cells with value_type 'float' or 'int' and computes per-sheet
    and workbook-level statistics. Returns:
      total_numeric_cells: int  — total count of numeric cells
      per_sheet: list[dict]     — per-sheet stats with keys:
        sheet_name: str
        numeric_count: int
        min_value: float | None
        max_value: float | None
        sum_value: float

    Returns workbook-level aggregate in 'total_numeric_cells', 'global_min',
    'global_max', 'global_sum'.
    Added in R63 Train H as a product deepening capability (numeric range analysis).
    """
    per_sheet: list[dict[str, Any]] = []
    all_values: list[float] = []

    for sheet in workbook.get("sheets", []):
        sheet_name = sheet.get("name", "")
        values: list[float] = []
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                vtype = cell.get("value_type", "")
                val = cell.get("value")
                if vtype in ("float", "int") and val is not None:
                    try:
                        values.append(float(val))
                    except (TypeError, ValueError):
                        pass
        per_sheet.append({
            "sheet_name": sheet_name,
            "numeric_count": len(values),
            "min_value": min(values) if values else None,
            "max_value": max(values) if values else None,
            "sum_value": sum(values),
        })
        all_values.extend(values)

    return {
        "total_numeric_cells": len(all_values),
        "global_min": min(all_values) if all_values else None,
        "global_max": max(all_values) if all_values else None,
        "global_sum": sum(all_values),
        "per_sheet": per_sheet,
    }




# ---------------------------------------------------------------------------
# Workbook column width summary (R63 Train H — new capability)
# ---------------------------------------------------------------------------

def workbook_column_count(workbook: dict[str, Any]) -> dict[str, Any]:
    """Return the maximum column width (non-empty cell count) per sheet.

    Scans all rows to determine the widest row per sheet. This is useful for
    understanding the actual used range without loading cell coordinates.

    Returns:
      per_sheet: list[dict] — per-sheet results with keys:
        sheet_name: str
        max_columns: int     — widest row (max number of non-None cells in any row)
        row_count: int        — number of rows in the sheet
      total_sheets: int

    Added in R63 Train H as a product deepening capability (column count / used range).
    """
    per_sheet: list[dict[str, Any]] = []
    for sheet in workbook.get("sheets", []):
        sheet_name = sheet.get("name", "")
        rows = sheet.get("rows", [])
        max_cols = 0
        for row in rows:
            cells = row.get("cells", [])
            non_empty = sum(1 for c in cells if c.get("value") is not None)
            if non_empty > max_cols:
                max_cols = non_empty
        per_sheet.append({
            "sheet_name": sheet_name,
            "max_columns": max_cols,
            "row_count": len(rows),
        })
    return {
        "per_sheet": per_sheet,
        "total_sheets": len(per_sheet),
    }




# ---------------------------------------------------------------------------
# Workbook row style summary (R64 Train H — new capability)
# ---------------------------------------------------------------------------

def workbook_row_style_summary(workbook: dict[str, Any]) -> dict[str, list[str]]:
    """Return a dict mapping sheet names to lists of row style attributes.

    Scans all rows in each sheet for a 'style' or 'table:style-name' attribute.
    If a row carries such an attribute, the style name string is appended to the
    sheet's list. Rows without styles are omitted.

    Returns:
        dict[str, list[str]] — {sheet_name: [style_name, ...]}
        Sheets with no styled rows appear as empty lists.

    Useful for understanding row-level formatting, conditional formatting
    detection, and style inventory across sheets.
    Added in R64 Train H as a product deepening capability (row style metadata).
    """
    result: dict[str, list[str]] = {}
    for sheet in workbook.get("sheets", []):
        sheet_name = sheet.get("name", "")
        styles: list[str] = []
        for row in sheet.get("rows", []):
            style = row.get("style") or row.get("table:style-name") or row.get("style_name")
            if style:
                styles.append(str(style))
        result[sheet_name] = styles
    return result




# ---------------------------------------------------------------------------
# Workbook formula edit policy (R64 Train H — new capability)
# ---------------------------------------------------------------------------

def workbook_formula_edit_policy(workbook: dict[str, Any]) -> dict[str, Any]:
    """Return formula edit policy statistics for the workbook.

    Counts the total number of formula cells and classifies each as editable
    or locked. In the current implementation, all formula cells are treated
    as editable (no cell-protection metadata is parsed yet).

    Returns:
        total_formulas: int       — total formula cells across all sheets
        editable_formulas: int    — formulas that are editable
        locked_formulas: int      — formulas that are locked (currently always 0)
        policy: str               — 'all_editable' or 'mixed' or 'all_locked' or 'no_formulas'

    Useful for spreadsheet auditing and formula protection analysis.
    Added in R64 Train H as a product deepening capability (formula edit policy).
    """
    total = 0
    locked = 0

    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                formula = cell.get("formula")
                if formula is not None:
                    total += 1
                    # Future: check cell.get("protected") or cell.get("table:protected")
                    if cell.get("protected") or cell.get("table:protected"):
                        locked += 1

    editable = total - locked
    if total == 0:
        policy = "no_formulas"
    elif locked == 0:
        policy = "all_editable"
    elif editable == 0:
        policy = "all_locked"
    else:
        policy = "mixed"

    return {
        "total_formulas": total,
        "editable_formulas": editable,
        "locked_formulas": locked,
        "policy": policy,
    }




# ---------------------------------------------------------------------------
# Workbook named range list (R65 Train H — new capability)
# ---------------------------------------------------------------------------

def workbook_named_range_list(workbook: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a list of defined named ranges found in the workbook.

    Scans for named ranges stored in the neutral model under
    'named_ranges' (a list of dicts) or 'table:named-range' entries.
    Each entry in the returned list contains:
      name: str              — the defined name (e.g. 'SalesData')
      cell_range: str        — the cell range expression (e.g. 'Sheet1.A1:C10')
      base_cell: str | None  — the base cell address if specified

    Returns:
        list[dict] — all named ranges found. Empty list if none.

    Useful for understanding workbook structure, formula dependency analysis,
    and range-based data extraction.
    Added in R65 Train H as a product deepening capability (named range inventory).
    """
    results: list[dict[str, Any]] = []

    # Check explicit named_ranges list (parser may populate this)
    for nr in workbook.get("named_ranges", []):
        if isinstance(nr, dict):
            results.append({
                "name": nr.get("name", nr.get("table:name", "")),
                "cell_range": nr.get("cell_range", nr.get("table:cell-range-address", "")),
                "base_cell": nr.get("base_cell", nr.get("table:base-cell-address")),
            })
        elif isinstance(nr, str):
            results.append({"name": nr, "cell_range": "", "base_cell": None})

    # Also check for named ranges embedded in sheets (some parsers store them per-sheet)
    for sheet in workbook.get("sheets", []):
        for nr in sheet.get("named_ranges", []):
            if isinstance(nr, dict):
                results.append({
                    "name": nr.get("name", nr.get("table:name", "")),
                    "cell_range": nr.get("cell_range", nr.get("table:cell-range-address", "")),
                    "base_cell": nr.get("base_cell", nr.get("table:base-cell-address")),
                })

    return results




# ---------------------------------------------------------------------------
# Workbook column style summary (R65 Train H — new capability)
# ---------------------------------------------------------------------------

def workbook_column_style_summary(workbook: dict[str, Any]) -> dict[str, list[str]]:
    """Return a dict mapping sheet names to lists of column style attributes.

    Scans all columns in each sheet for a 'style' or 'table:style-name'
    attribute. Columns are found in the sheet's 'columns' list (if the parser
    populates it). If no columns metadata exists, examines the first row's
    cells for column-level style hints.

    Returns:
        dict[str, list[str]] — {sheet_name: [style_name, ...]}
        Sheets with no styled columns appear as empty lists.

    Useful for understanding column-level formatting, width detection,
    and style inventory across sheets.
    Added in R65 Train H as a product deepening capability (column style metadata).
    """
    result: dict[str, list[str]] = {}
    for sheet in workbook.get("sheets", []):
        sheet_name = sheet.get("name", "")
        styles: list[str] = []

        # Primary: check explicit columns list
        columns = sheet.get("columns", [])
        for col in columns:
            if isinstance(col, dict):
                style = (
                    col.get("style")
                    or col.get("table:style-name")
                    or col.get("style_name")
                )
                if style:
                    styles.append(str(style))

        # Fallback: check first row cells for column_style attribute
        if not styles:
            rows = sheet.get("rows", [])
            if rows:
                first_row = rows[0]
                for cell in first_row.get("cells", []):
                    col_style = cell.get("column_style") or cell.get("table:column-style")
                    if col_style:
                        styles.append(str(col_style))

        result[sheet_name] = styles
    return result




# ---------------------------------------------------------------------------
# Workbook style family list (R66 Train H — new capability)
# ---------------------------------------------------------------------------

def workbook_style_family_list(workbook: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a list of style families and their style counts from the workbook.

    Scans the workbook for style metadata stored in '_auto_styles_elem' and
    '_styles_elem' (ET elements captured by the parser) or in 'auto_styles'
    and 'styles' dicts (if the parser populates them as plain dicts).

    Each entry in the returned list contains:
      family_name: str     -- the style:family attribute (e.g. 'table-cell', 'table')
      style_count: int     -- number of styles in that family

    Returns:
        list[dict] -- style families found. Empty list if no style metadata.

    Useful for style inventory, format complexity assessment, and style cleanup.
    Added in R66 Train H as a product deepening capability (style family inventory).
    """
    family_counts: dict[str, int] = {}

    # Check for plain-dict style metadata (parser may populate these)
    for key in ("auto_styles", "styles", "_auto_styles", "_styles"):
        styles_data = workbook.get(key)
        if isinstance(styles_data, list):
            for style in styles_data:
                if isinstance(style, dict):
                    family = style.get("family") or style.get("style:family") or "unknown"
                    family_counts[family] = family_counts.get(family, 0) + 1
        elif isinstance(styles_data, dict):
            for family, items in styles_data.items():
                if isinstance(items, list):
                    family_counts[family] = family_counts.get(family, 0) + len(items)
                elif isinstance(items, int):
                    family_counts[family] = family_counts.get(family, 0) + items

    # Check for ET element objects (not JSON-serializable, prefixed with _)
    for elem_key in ("_auto_styles_elem", "_styles_elem"):
        elem = workbook.get(elem_key)
        if elem is not None and hasattr(elem, "iter"):
            try:
                ns = {"style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0"}
                for style_elem in elem.iter("{urn:oasis:names:tc:opendocument:xmlns:style:1.0}style"):
                    family = style_elem.get("{urn:oasis:names:tc:opendocument:xmlns:style:1.0}family", "unknown")
                    family_counts[family] = family_counts.get(family, 0) + 1
            except Exception:
                pass

    return [
        {"family_name": family, "style_count": count}
        for family, count in sorted(family_counts.items())
    ]




# ---------------------------------------------------------------------------
# Workbook data validation summary (R66 Train H — new capability)
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
    Added in R66 Train H as a product deepening capability (data validation inventory).
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
    Added in R75 Train G as a product advancement capability.
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
    Added in R75 Train G as a product advancement capability.
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

    Aligned with ODF 1.3 spreadsheet content model (FACT-FODS-001).

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

    Spec authority: FACT-FODS-005 — Rows are <table:table-row> children of <table:table>.

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

    Spec authority: FACT-FODS-006 — Cells are <table:table-cell> children of <table:table-row>.
                    FACT-FODS-007 — Cell text is in <text:p> children of <table:table-cell>.

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

