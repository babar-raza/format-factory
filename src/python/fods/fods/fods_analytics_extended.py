"""fods_analytics_extended.py — Extended analytics functions for the FODS neutral model.

Extended analytics built on top of fods_analytics.py.
This module contains no class definitions, no domain model types,
and no ODF spec_qname assignments.

License: Apache-2.0
Package: format-factory-fods v0.1.0
"""
from __future__ import annotations

from typing import Any

from .fods_analytics import fods_sheet_count

def fods_formula_count(workbook: dict[str, Any]) -> int:
    """Return the total number of formula cells across all sheets.

    Uses the same traversal logic as ``workbook_formula_list`` but returns
    only the count, which is cheaper for large workbooks.
    """
    count = 0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None and cell.get("formula") is not None:
                    count += 1
    return count


def fods_total_cell_count(workbook: dict[str, Any]) -> int:
    """Return the total number of non-empty cells across all sheets.

    A cell is considered non-empty if it exists in the neutral model
    and has a non-None value or text content.
    """
    count = 0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None:
                    val = cell.get("value")
                    txt = cell.get("text")
                    if val is not None or txt is not None:
                        count += 1
    return count


def fods_empty_cell_count(workbook: dict[str, Any]) -> int:
    """Return the count of empty cells across all sheets.

    A cell is empty if it is None or has both value and text as None.
    """
    count = 0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is None:
                    count += 1
                else:
                    val = cell.get("value")
                    txt = cell.get("text")
                    if val is None and txt is None:
                        count += 1
    return count


def fods_has_formulas(workbook: dict[str, Any]) -> bool:
    """Return True if the workbook contains at least one formula cell."""
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None and cell.get("formula"):
                    return True
    return False


def fods_sheet_names(workbook: dict[str, Any]) -> list[str]:
    """Return a list of sheet names in the workbook.

    Args:
        workbook: Parsed FODS workbook dict.

    Returns:
        List of sheet name strings.
    """
    return [s.get("name", "") for s in workbook.get("sheets", [])]


def fods_string_cell_count(workbook: dict[str, Any]) -> int:
    """Return the total number of string-type cells across all sheets.

    Args:
        workbook: Parsed FODS workbook dict.

    Returns:
        Integer count.
    """
    count = 0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None:
                    vt = cell.get("value_type", "")
                    if vt == "string":
                        count += 1
    return count


def fods_numeric_cell_count(workbook: dict[str, Any]) -> int:
    """Return the total number of numeric (float/int) cells across all sheets.

    Args:
        workbook: Parsed FODS workbook dict.

    Returns:
        Integer count of cells with value_type 'float'.
    """
    count = 0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None and cell.get("value_type") == "float":
                    count += 1
    return count


def fods_max_row_count(workbook: dict[str, Any]) -> int:
    """Return the maximum number of rows across all sheets.

    Args:
        workbook: Parsed FODS workbook dict.

    Returns:
        Integer: max row count, or 0 if there are no sheets.
    """
    sheets = workbook.get("sheets", [])
    if not sheets:
        return 0
    return max(len(sheet.get("rows", [])) for sheet in sheets)


def fods_avg_cells_per_sheet(workbook: dict[str, Any]) -> float:
    """Return the average number of non-empty cells per sheet.

    Args:
        workbook: Parsed FODS workbook dict.

    Returns:
        Float average cells per sheet, or 0.0 if there are no sheets.
    """
    sheets = workbook.get("sheets", [])
    if not sheets:
        return 0.0
    total = fods_total_cell_count(workbook)
    return total / len(sheets)


def fods_has_empty_sheets(workbook: dict[str, Any]) -> bool:
    """Return True if any sheet contains no non-empty cells.

    Args:
        workbook: Parsed FODS workbook dict.

    Returns:
        True if at least one sheet has zero non-empty cells.
    """
    for sheet in workbook.get("sheets", []):
        cell_count = 0
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None:
                    cell_count += 1
        if cell_count == 0:
            return True
    return False


def fods_all_sheets_have_data(workbook: dict[str, Any]) -> bool:
    """Return True if every sheet has at least one non-empty cell.

    Args:
        workbook: Parsed FODS workbook dict.

    Returns:
        True if all sheets have at least one non-empty cell.
    """
    sheets = workbook.get("sheets", [])
    if not sheets:
        return False
    for sheet in sheets:
        has_data = False
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None:
                    has_data = True
                    break
            if has_data:
                break
        if not has_data:
            return False
    return True


def fods_max_string_length(workbook: dict[str, Any]) -> int:
    """Return the maximum length of any string cell value across all sheets.

    Args:
        workbook: Parsed FODS workbook dict.

    Returns:
        Maximum string cell value length, or 0 if no string cells exist.
    """
    max_len = 0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None and isinstance(cell.get("value"), str):
                    max_len = max(max_len, len(cell["value"]))
    return max_len


def fods_numeric_density(workbook: dict[str, Any]) -> float:
    """Return the ratio of numeric cells to total cells. 0.0 if no cells."""
    total = fods_total_cell_count(workbook)
    if total == 0:
        return 0.0
    numeric = fods_numeric_cell_count(workbook)
    return numeric / total


def fods_data_density(workbook: dict[str, Any]) -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    total = fods_total_cell_count(workbook)
    if total == 0:
        return 0.0
    empty = fods_empty_cell_count(workbook)
    return (total - empty) / total


def fods_string_density(workbook: dict[str, Any]) -> float:
    """Return ratio of string cells to total cells. 0.0 if no cells."""
    total = fods_total_cell_count(workbook)
    if total == 0:
        return 0.0
    strings = fods_string_cell_count(workbook)
    return strings / total


def fods_is_single_sheet(workbook: dict[str, Any]) -> bool:
    """Return True if the workbook contains exactly one sheet."""
    return fods_sheet_count(workbook) == 1


def fods_is_multi_sheet(workbook: dict[str, Any]) -> bool:
    """Return True if the workbook contains more than one sheet."""
    return fods_sheet_count(workbook) > 1


def fods_min_row_count(workbook: dict[str, Any]) -> int:
    """Return the minimum row count across all sheets. 0 if no sheets."""
    sheets = workbook.get("sheets", [])
    if not sheets:
        return 0
    return min(len(s.get("rows", [])) for s in sheets)


def fods_max_col_count(workbook: dict[str, Any]) -> int:
    """Return the maximum column count across all sheets. 0 if no sheets."""
    sheets = workbook.get("sheets", [])
    if not sheets:
        return 0
    max_cols = 0
    for s in sheets:
        for row in s.get("rows", []):
            cols = len(row.get("cells", []))
            if cols > max_cols:
                max_cols = cols
    return max_cols


def fods_empty_sheet_count(workbook: dict[str, Any]) -> int:
    """Return the count of sheets with zero rows."""
    sheets = workbook.get("sheets", [])
    return sum(1 for s in sheets if len(s.get("rows", [])) == 0)


def fods_total_row_count(workbook: dict[str, Any]) -> int:
    """Return the total number of rows across all sheets."""
    sheets = workbook.get("sheets", [])
    return sum(len(s.get("rows", [])) for s in sheets)


def fods_avg_col_count(workbook: dict[str, Any]) -> float:
    """Return average column count across all rows. 0.0 if no rows."""
    sheets = workbook.get("sheets", [])
    counts = []
    for s in sheets:
        for row in s.get("rows", []):
            counts.append(len(row.get("cells", [])))
    if not counts:
        return 0.0
    return sum(counts) / len(counts)


def fods_is_single_cell(workbook: dict[str, Any]) -> bool:
    """Return True if the workbook contains exactly one cell across all sheets."""
    return fods_total_cell_count(workbook) == 1


def fods_nonempty_sheet_count(workbook: dict[str, Any]) -> int:
    """Return the number of sheets that contain at least one cell."""
    return fods_sheet_count(workbook) - fods_empty_sheet_count(workbook)


def fods_has_string_cells(workbook: dict[str, Any]) -> bool:
    """Return True if any cell contains a string value."""
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None:
                    vt = cell.get("value_type", "")
                    if vt == "string":
                        return True
                    txt = cell.get("text", "")
                    if txt and not cell.get("value"):
                        return True
    return False


def fods_row_count_variance(workbook: dict[str, Any]) -> float:
    """Return variance of row counts across sheets. 0.0 if fewer than 2 sheets."""
    sheets = workbook.get("sheets", [])
    if len(sheets) < 2:
        return 0.0
    counts = [len(s.get("rows", [])) for s in sheets]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def fods_avg_string_length(workbook: dict[str, Any]) -> float:
    """Return average character length of string cell values. 0.0 if none."""
    lengths = []
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None:
                    vt = cell.get("value_type", "")
                    txt = cell.get("text", "")
                    if vt == "string" or (txt and not cell.get("value")):
                        lengths.append(len(txt))
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def fods_col_count_variance(workbook: dict[str, Any]) -> float:
    """Return variance of column counts across sheets. 0.0 if fewer than 2 sheets."""
    sheets = workbook.get("sheets", [])
    if len(sheets) < 2:
        return 0.0
    counts = []
    for sheet in sheets:
        max_cols = 0
        for row in sheet.get("rows", []):
            cells = row.get("cells", [])
            if len(cells) > max_cols:
                max_cols = len(cells)
        counts.append(max_cols)
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def fods_cell_to_sheet_ratio(workbook: dict[str, Any]) -> float:
    """Return total cell count divided by sheet count. 0.0 if no sheets."""
    sheets = workbook.get("sheets", [])
    if not sheets:
        return 0.0
    total = sum(
        sum(len(row.get("cells", [])) for row in sheet.get("rows", []))
        for sheet in sheets
    )
    return total / len(sheets)


def fods_avg_numeric_value(workbook: dict[str, Any]) -> float:
    """Return average of all numeric cell values across all sheets. 0.0 if none."""
    values = []
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None and cell.get("value_type") in ("float", "integer"):
                    try:
                        v = cell.get("value")
                        if v is not None:
                            values.append(float(v))
                    except (ValueError, TypeError):
                        pass
    return sum(values) / len(values) if values else 0.0


def fods_nonempty_row_ratio(workbook: dict[str, Any], sheet_index: int = 0) -> float:
    """Return ratio of non-empty rows to total rows in a sheet. 0.0 if no rows."""
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return 0.0
    rows = sheets[sheet_index].get("rows", [])
    if not rows:
        return 0.0
    nonempty = sum(
        1 for row in rows
        if any(
            cell is not None and str(cell.get("text", "")).strip()
            for cell in row.get("cells", [])
        )
    )
    return nonempty / len(rows)


def fods_longest_row_index(workbook: dict[str, Any], sheet_index: int = 0) -> int:
    """Return 0-based index of the row with the most non-empty cells. -1 if no rows."""
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return -1
    rows = sheets[sheet_index].get("rows", [])
    if not rows:
        return -1
    best_idx, best_count = 0, 0
    for i, row in enumerate(rows):
        count = sum(
            1 for cell in row.get("cells", [])
            if cell is not None and str(cell.get("text", "")).strip()
        )
        if count > best_count:
            best_count = count
            best_idx = i
    return best_idx


def fods_numeric_sum_all(workbook: dict[str, Any]) -> float:
    """Return sum of all numeric cell values across all sheets."""
    total = 0.0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None and cell.get("value_type") in ("float", "integer"):
                    try:
                        v = cell.get("value")
                        if v is not None:
                            total += float(v)
                    except (ValueError, TypeError):
                        pass
    return total


def fods_empty_column_count(workbook: dict[str, Any], sheet_index: int = 0) -> int:
    """Return number of columns that are entirely empty in a sheet."""
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return 0
    rows = sheets[sheet_index].get("rows", [])
    if not rows:
        return 0
    max_cols = max((len(row.get("cells", [])) for row in rows), default=0)
    empty_count = 0
    for col_idx in range(max_cols):
        col_empty = all(
            col_idx >= len(row.get("cells", []))
            or row["cells"][col_idx] is None
            or not str(row["cells"][col_idx].get("text", "")).strip()
            for row in rows
        )
        if col_empty:
            empty_count += 1
    return empty_count


def fods_numeric_cell_ratio(workbook: dict[str, Any]) -> float:
    """Return ratio of numeric cells to total non-empty cells. 0.0 if none."""
    total = 0
    numeric = 0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell is not None and cell.get("text", "").strip():
                    total += 1
                    if cell.get("value_type") in ("float", "currency", "percentage"):
                        numeric += 1
    if total == 0:
        return 0.0
    return numeric / total


def fods_max_row_cell_count(workbook: dict[str, Any], sheet_index: int = 0) -> int:
    """Return maximum number of cells in any row. 0 if no rows."""
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return 0
    rows = sheets[sheet_index].get("rows", [])
    if not rows:
        return 0
    return max(len(row.get("cells", [])) for row in rows)


def fods_formula_cell_count(workbook: dict[str, Any], sheet_index: int = 0) -> int:
    """Return count of cells that have a formula attribute. 0 if none."""
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return 0
    count = 0
    for row in sheets[sheet_index].get("rows", []):
        for cell in row.get("cells", []):
            if cell is not None and cell.get("formula"):
                count += 1
    return count


def fods_sheet_row_variance(workbook: dict[str, Any]) -> float:
    """Return variance of row counts across sheets. 0.0 if fewer than 2 sheets."""
    sheets = workbook.get("sheets", [])
    if len(sheets) < 2:
        return 0.0
    counts = [len(s.get("rows", [])) for s in sheets]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)
