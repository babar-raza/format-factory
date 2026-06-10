"""
neutral_model.py -- Neutral model builder and validator for format-factory-fods.

Builds and validates the 6-entity FODS neutral model output:
  Workbook -> Sheet -> Row -> Cell (-> Formula), Warning

Used by parser.py to assemble the final result and validate structure
before returning (IR-FODS-018).

Neutral model schema reference: schemas/neutral-model/fods/model.yaml
Gate 5 artifact: Gate 5 PASSED (Babar Raza, 2026-05-06, run035).

License: Apache-2.0
Package: format-factory-fods v0.1.0
"""

from __future__ import annotations

from typing import Any

from .constants import FORMAT_ID, SPEC_VERSION


# ---------------------------------------------------------------------------
# Warning helper
# ---------------------------------------------------------------------------

def make_warning(code: str, message: str, source: str | None = None) -> dict[str, Any]:
    """Build a structured Warning dict matching the neutral model Warning entity."""
    w: dict[str, Any] = {"code": code, "message": message}
    if source is not None:
        w["source"] = source
    return w


# ---------------------------------------------------------------------------
# Workbook builder
# ---------------------------------------------------------------------------

def build_workbook(
    odf_version_attr: str,
    mimetype: str | None,
    sheets: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    unsupported_features: list[str],
    parse_errors: list[dict[str, Any]],
    auto_styles_elem: Any | None = None,
    styles_elem: Any | None = None,
) -> dict[str, Any]:
    """Assemble the Workbook-level result dict matching the neutral model.

    Fields conform to the Workbook entity in schemas/neutral-model/fods/model.yaml.
    Additional fields (unsupported_features, parse_errors) extend the neutral
    model for product parser transparency.

    R55 TC-0055: ``auto_styles_elem`` and ``styles_elem`` hold captured
    ``office:automatic-styles`` and ``office:styles`` ET element objects.
    The writer re-emits them verbatim for style round-trip preservation.
    These fields are not JSON-serializable and are prefixed with ``_``.
    """
    wb: dict[str, Any] = {
        "format_id": FORMAT_ID,
        "spec_version": SPEC_VERSION,
        "odf_version_attr": odf_version_attr,
        "mimetype": mimetype,
        "sheet_count": len(sheets),
        "sheets": sheets,
        "warnings": warnings,
        "unsupported_features": sorted(unsupported_features),
        "parse_errors": parse_errors,
    }
    if auto_styles_elem is not None:
        wb["_auto_styles_elem"] = auto_styles_elem
    if styles_elem is not None:
        wb["_styles_elem"] = styles_elem
    return wb


# ---------------------------------------------------------------------------
# Workbook validator (IR-FODS-018)
# ---------------------------------------------------------------------------

def validate_workbook(result: dict[str, Any]) -> list[str]:
    """Validate a parse_fods() result against the neutral model structure.

    Returns a list of violation strings. Empty list means valid.
    Does NOT raise -- callers decide whether to treat violations as fatal.
    """
    violations: list[str] = []

    # Required top-level fields
    for field in ("format_id", "spec_version", "odf_version_attr", "sheet_count", "sheets", "warnings"):
        if field not in result:
            violations.append(f"Workbook missing required field: {field!r}")

    if result.get("format_id") != FORMAT_ID:
        violations.append(
            f"Workbook.format_id must be {FORMAT_ID!r}; got {result.get('format_id')!r}"
        )

    sheets = result.get("sheets")
    if not isinstance(sheets, list):
        violations.append("Workbook.sheets must be a list")
        return violations  # can't validate sheets further

    sheet_count = result.get("sheet_count")
    if sheet_count != len(sheets):
        violations.append(
            f"Workbook.sheet_count {sheet_count} != len(sheets) {len(sheets)}"
        )

    for i, sheet in enumerate(sheets):
        violations.extend(_validate_sheet(sheet, i))

    warnings = result.get("warnings")
    if not isinstance(warnings, list):
        violations.append("Workbook.warnings must be a list")

    return violations


def _validate_sheet(sheet: dict[str, Any], expected_index: int) -> list[str]:
    violations: list[str] = []
    prefix = f"Sheet[{expected_index}]"

    for field in ("name", "index", "row_count", "rows"):
        if field not in sheet:
            violations.append(f"{prefix} missing required field: {field!r}")

    if sheet.get("index") != expected_index:
        violations.append(
            f"{prefix}.index must be {expected_index}; got {sheet.get('index')!r}"
        )

    rows = sheet.get("rows")
    if not isinstance(rows, list):
        violations.append(f"{prefix}.rows must be a list")
        return violations

    row_count = sheet.get("row_count")
    if row_count != len(rows):
        violations.append(
            f"{prefix}.row_count {row_count} != len(rows) {len(rows)}"
        )

    for j, row in enumerate(rows):
        violations.extend(_validate_row(row, j, prefix))

    return violations


def _validate_row(row: dict[str, Any], expected_index: int, sheet_prefix: str) -> list[str]:
    violations: list[str] = []
    prefix = f"{sheet_prefix}.Row[{expected_index}]"

    for field in ("index", "cells"):
        if field not in row:
            violations.append(f"{prefix} missing required field: {field!r}")

    if row.get("index") != expected_index:
        violations.append(
            f"{prefix}.index must be {expected_index}; got {row.get('index')!r}"
        )

    cells = row.get("cells")
    if not isinstance(cells, list):
        violations.append(f"{prefix}.cells must be a list")

    return violations


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
# Find sheet by name (R59 — new capability)
# ---------------------------------------------------------------------------

def find_sheet_by_name(workbook: dict[str, Any], name: str) -> "dict[str, Any] | None":
    """Return the first sheet dict whose name matches, or None.

    Case-sensitive match. Useful for programmatic access to named sheets
    without iterating manually. Returns the full sheet dict from the
    neutral model (including rows and cells).

    Added in R59 Train G as a product deepening capability.
    """
    for sheet in workbook.get("sheets", []):
        if sheet.get("name") == name:
            return sheet
    return None


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


# ---------------------------------------------------------------------------
# Workbook cell editor (R76 — product deepening: edit and save)
# ---------------------------------------------------------------------------

def workbook_set_cell_value(
    workbook: dict[str, Any],
    sheet_name: str,
    row_idx: int,
    col_idx: int,
    value: Any,
    value_type: str | None = None,
) -> tuple[bool, str]:
    """Set a cell value in the neutral model workbook.

    Mutates the workbook dict in-place. This enables an edit-and-save workflow:
        wb = parse_fods(path)
        ok, msg = workbook_set_cell_value(wb, "Sheet1", 0, 0, "Updated")
        if ok:
            write_fods(wb, out_path)

    Args:
        workbook: A neutral model workbook dict from parse_fods().
        sheet_name: The name of the sheet to edit.
        row_idx: 0-based row index.
        col_idx: 0-based column index.
        value: The new cell value. Strings, ints, and floats are supported.
        value_type: Optional explicit value type: "string", "float", "boolean".
            Inferred from value type if not provided.

    Returns:
        (success: bool, message: str) — success=True if the cell was found and updated.
        Returns (False, reason) if the sheet, row, or cell was not found.

    Note: This function modifies only the ``value`` and ``value_type`` fields.
    Formula attributes (``formula``) are cleared when a new plain value is set.
    Style attributes and other metadata are preserved.

    Added in R76 Train F as a product deepening capability (edit-and-save workflow).
    """
    if not isinstance(workbook, dict):
        return False, "workbook must be a dict"

    sheets = workbook.get("sheets", [])
    target_sheet = None
    for sheet in sheets:
        if sheet.get("name") == sheet_name:
            target_sheet = sheet
            break

    if target_sheet is None:
        return False, f"Sheet {sheet_name!r} not found"

    rows = target_sheet.get("rows", [])
    if row_idx < 0 or row_idx >= len(rows):
        return False, f"Row index {row_idx} out of range (sheet has {len(rows)} rows)"

    cells = rows[row_idx].get("cells", [])
    if col_idx < 0 or col_idx >= len(cells):
        return False, f"Column index {col_idx} out of range (row has {len(cells)} cells)"

    cell = cells[col_idx]
    if not isinstance(cell, dict):
        return False, f"Cell at ({row_idx}, {col_idx}) is not a dict"

    # Infer value_type if not provided
    if value_type is None:
        if isinstance(value, bool):
            value_type = "boolean"
        elif isinstance(value, (int, float)):
            value_type = "float"
        else:
            value_type = "string"

    cell["value"] = value
    cell["value_type"] = value_type
    # Clear formula when setting a plain value (formula no longer applies)
    if "formula" in cell:
        cell["formula"] = None

    return True, f"Cell ({row_idx}, {col_idx}) updated to {value!r} (type: {value_type})"


def workbook_warnings_for_unsupported_edit(
    workbook: dict[str, Any],
    sheet_name: str,
    row_idx: int,
    col_idx: int,
) -> list[str]:
    """Return warnings about unsupported cell features that may be lost on edit/save.

    Checks the target cell for features that the writer may not preserve perfectly:
    - Merged cells (span attributes)
    - Conditional formatting
    - Data validation rules
    - Non-standard value types

    Returns a list of warning strings. Empty list means no unsupported features detected.

    Added in R76 Train F as a product deepening capability (edit safety disclosure).
    """
    warnings: list[str] = []

    sheets = workbook.get("sheets", [])
    target_sheet = next((s for s in sheets if s.get("name") == sheet_name), None)
    if target_sheet is None:
        return [f"Sheet {sheet_name!r} not found"]

    rows = target_sheet.get("rows", [])
    if row_idx >= len(rows):
        return [f"Row {row_idx} out of range"]

    cells = rows[row_idx].get("cells", [])
    if col_idx >= len(cells):
        return [f"Column {col_idx} out of range"]

    cell = cells[col_idx]
    if not isinstance(cell, dict):
        return ["Cell is not a standard dict"]

    if cell.get("merge") or cell.get("span") or cell.get("table:number-columns-spanned"):
        warnings.append("Cell has merge/span metadata — merged cell layout may change on save")
    if cell.get("formula"):
        warnings.append(
            "Cell has a formula — formula will be cleared when set_cell_value replaces it with a plain value"
        )
    vtype = cell.get("value_type", "")
    if vtype not in ("string", "float", "boolean", "", None):
        warnings.append(f"Non-standard value_type {vtype!r} — may not round-trip perfectly")

    return warnings


# ---------------------------------------------------------------------------
# R77 Train I — Sheet management APIs
# ---------------------------------------------------------------------------


def workbook_add_sheet(
    workbook: dict[str, Any],
    sheet_name: str,
    position: int | None = None,
) -> tuple[bool, str]:
    """Add a new empty sheet to the workbook.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_name: Name for the new sheet.
        position: 0-based insert position. None means append.

    Returns:
        (success, message) tuple.

    Added in R77 Train I as a sheet-management product capability.
    """
    if not sheet_name or not sheet_name.strip():
        return False, "Sheet name must not be empty"

    sheets = workbook.get("sheets", [])
    existing_names = [s.get("name", "") for s in sheets]
    if sheet_name in existing_names:
        return False, f"Sheet {sheet_name!r} already exists"

    new_sheet: dict[str, Any] = {
        "name": sheet_name,
        "rows": [],
        "auto_updatable": False,
    }

    if position is None or position >= len(sheets):
        sheets.append(new_sheet)
    else:
        sheets.insert(max(0, position), new_sheet)

    workbook["sheets"] = sheets
    return True, f"Sheet {sheet_name!r} added at position {position if position is not None else len(sheets) - 1}"


def workbook_rename_sheet(
    workbook: dict[str, Any],
    old_name: str,
    new_name: str,
) -> tuple[bool, str]:
    """Rename an existing sheet.

    Args:
        workbook: Parsed FODS workbook dict.
        old_name: Current sheet name.
        new_name: Desired new sheet name.

    Returns:
        (success, message) tuple.

    Added in R77 Train I as a sheet-management product capability.
    """
    if not new_name or not new_name.strip():
        return False, "New sheet name must not be empty"

    sheets = workbook.get("sheets", [])
    existing_names = [s.get("name", "") for s in sheets]

    if old_name not in existing_names:
        return False, f"Sheet {old_name!r} not found"
    if new_name in existing_names and new_name != old_name:
        return False, f"Sheet {new_name!r} already exists"

    for sheet in sheets:
        if sheet.get("name") == old_name:
            sheet["name"] = new_name
            return True, f"Sheet renamed from {old_name!r} to {new_name!r}"

    return False, "Unexpected: sheet not found during rename"


def workbook_remove_sheet(
    workbook: dict[str, Any],
    sheet_name: str,
) -> tuple[bool, str]:
    """Remove a sheet from the workbook.

    This is a destructive operation. If the workbook has only one sheet,
    the removal is rejected to avoid an invalid empty workbook.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_name: Name of the sheet to remove.

    Returns:
        (success, message) tuple.

    Added in R77 Train I as a sheet-management product capability.
    """
    sheets = workbook.get("sheets", [])

    if len(sheets) <= 1:
        return False, "Cannot remove the only sheet in a workbook"

    before = len(sheets)
    workbook["sheets"] = [s for s in sheets if s.get("name") != sheet_name]
    after = len(workbook["sheets"])

    if before == after:
        return False, f"Sheet {sheet_name!r} not found"

    return True, f"Sheet {sheet_name!r} removed ({before} -> {after} sheets)"


def workbook_to_csv(
    workbook: dict[str, Any],
    sheet_name: str | None = None,
) -> str:
    """Export a workbook sheet as CSV text.

    If sheet_name is None, exports the first sheet. Returns the CSV as a
    plain string with CRLF line endings per RFC 4180.

    Cells are quoted if they contain commas, double-quotes, or newlines.
    Numeric and string values are both supported. Formula tokens are exported
    as empty strings (formula evaluation is unsupported in this track).

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_name: Name of the sheet to export, or None for the first sheet.

    Returns:
        CSV text string.

    Added in R84 Train G as FODS product feature advancement.
    """
    import io
    import csv as _csv

    sheets = workbook.get("sheets", [])
    if not sheets:
        return ""

    target = None
    if sheet_name is None:
        target = sheets[0]
    else:
        for s in sheets:
            if s.get("name") == sheet_name:
                target = s
                break
        if target is None:
            return ""

    rows = target.get("rows", [])
    buf = io.StringIO()
    writer = _csv.writer(buf, lineterminator="\r\n")
    for row in rows:
        cells = row.get("cells", [])
        csv_row = []
        for cell in cells:
            v = cell.get("value")
            if v is None:
                csv_row.append("")
            else:
                csv_row.append(str(v))
        writer.writerow(csv_row)
    return buf.getvalue()


def workbook_get_cell_value(
    workbook: dict[str, Any],
    sheet_name: str,
    row_index: int,
    col_index: int,
) -> Any:
    """Return the value of a cell at (row_index, col_index) in the named sheet.

    Indices are 0-based. Returns None if the sheet, row, or cell does not
    exist or is out of range.

    This is the read-side complement of workbook_set_cell_value and is
    primarily useful for roundtrip verification in installed-package workflows.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_name: Name of the sheet.
        row_index: 0-based row index.
        col_index: 0-based column index within the row.

    Returns:
        Cell value (str, float, int, bool) or None.

    Added in R84 Train G as FODS product feature advancement.
    """
    sheets = workbook.get("sheets", [])
    target = None
    for s in sheets:
        if s.get("name") == sheet_name:
            target = s
            break
    if target is None:
        return None

    rows = target.get("rows", [])
    if row_index < 0 or row_index >= len(rows):
        return None

    cells = rows[row_index].get("cells", [])
    if col_index < 0 or col_index >= len(cells):
        return None

    return cells[col_index].get("value")


def workbook_find_cells(
    workbook: dict[str, Any],
    value: Any,
    case_sensitive: bool = False,
) -> list[dict[str, Any]]:
    """Find all cells whose value matches the given search value.

    Searches across all sheets. String comparisons are case-insensitive by
    default. Non-string values are compared with equality.

    Aligned with ODF 1.3 spreadsheet content model (FACT-FODS-001): cell values
    are stored in the workbook neutral model under sheets → rows → cells.

    Args:
        workbook: Parsed FODS workbook dict.
        value: Value to search for (string, number, bool, etc.).
        case_sensitive: If True, string matching is case-sensitive. Default False.

    Returns:
        List of match dicts, each containing:
            sheet_name (str): Name of the sheet.
            row_index (int): 0-based row index.
            col_index (int): 0-based column index.
            value: The cell value that matched.

    Added in Sprint FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-PROGRESS-AND-FORMAT-BACKFILL-MEGA-TRAIN-001
    as FODS product feature advancement (authority: P6, FACT-FODS-001).
    """
    matches: list[dict[str, Any]] = []
    is_str_search = isinstance(value, str)
    compare_value = value.lower() if (is_str_search and not case_sensitive) else value

    for sheet in workbook.get("sheets", []):
        sheet_name = sheet.get("name", "")
        for row_idx, row in enumerate(sheet.get("rows", [])):
            for col_idx, cell in enumerate(row.get("cells", [])):
                cell_val = cell.get("value")
                if cell_val is None:
                    continue
                if is_str_search and isinstance(cell_val, str):
                    compare_cell = cell_val if case_sensitive else cell_val.lower()
                    if compare_cell == compare_value:
                        matches.append({
                            "sheet_name": sheet_name,
                            "row_index": row_idx,
                            "col_index": col_idx,
                            "value": cell_val,
                        })
                else:
                    if cell_val == value:
                        matches.append({
                            "sheet_name": sheet_name,
                            "row_index": row_idx,
                            "col_index": col_idx,
                            "value": cell_val,
                        })

    return matches


def workbook_count_matching_cells(
    workbook: dict[str, Any],
    value: Any,
    case_sensitive: bool = False,
) -> int:
    """Count the number of cells whose value matches the given search value.

    Convenience wrapper around workbook_find_cells that returns only the count.
    Aligned with ODF 1.3 spreadsheet content model (FACT-FODS-001).

    Args:
        workbook: Parsed FODS workbook dict.
        value: Value to search for.
        case_sensitive: If True, string matching is case-sensitive. Default False.

    Returns:
        Integer count of matching cells across all sheets.

    Added in Sprint FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-DOGFOOD-FEATURES-AND-BACKFILL-001
    (authority: P6, FACT-FODS-001).
    """
    return len(workbook_find_cells(workbook, value, case_sensitive=case_sensitive))


def workbook_to_html(workbook: dict[str, Any], sheet_index: int = 0) -> str:
    """Export a FODS workbook sheet as an HTML table string.

    Cell values are HTML-escaped.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        HTML string containing a <table> element. Empty string if sheet not found.
    """
    from html import escape
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return ""
    sheet = sheets[sheet_index]
    rows = sheet.get("rows", [])
    if not rows:
        return "<table></table>"

    lines = ["<table>"]
    for row in rows:
        lines.append("  <tr>")
        for cell in row.get("cells", []):
            val = cell.get("value", "")
            if val is None:
                val = ""
            lines.append(f"    <td>{escape(str(val))}</td>")
        lines.append("  </tr>")
    lines.append("</table>")
    return "\n".join(lines)
