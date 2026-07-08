"""
GNUMERIC analytics functions extracted from gnumeric_codec.py (TC-HEAL-FORMATS-BATCH1).
"""
from __future__ import annotations


spec_qname = "gnm:workbook"
spec_fact_ref = "FACT-GNUMERIC-001"
namespace_uri = "http://www.gnumeric.org/v10.dtd"

from pathlib import Path
from typing import Any

from .gnumeric_codec import load
from .gnumeric_workbook_stats import (
    get_column_count,
    count_nonempty_cells,
    row_count,
)


def gnumeric_sheet_summary(model: "dict[str, Any]", sheet_idx: int) -> "dict[str, Any]":
    """Return a summary dict for a sheet with row_count, col_count, and nonempty_cells."""
    return {
        "row_count": row_count(model, sheet_idx),
        "col_count": get_column_count(model, sheet_idx),
        "nonempty_cells": count_nonempty_cells(model, sheet_idx),
    }


def gnumeric_numeric_cell_count(model: "dict[str, Any]", sheet_idx: int) -> int:
    """Return the count of cells whose values are numeric (parseable as float).

    Args:
        model: Parsed Gnumeric model dict.
        sheet_idx: 0-based sheet index.

    Returns:
        Integer count of numeric cells. Returns 0 if sheet not found or empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0
    grid = sheets[sheet_idx].get("cell_grid", {})
    count = 0
    for val in grid.values():
        if val is not None and val != "":
            try:
                float(str(val))
                count += 1
            except (ValueError, TypeError):
                pass
    return count


def gnumeric_column_count(model: "dict[str, Any]", sheet_idx: int) -> int:
    """Return the number of columns (max column index + 1) in a sheet.

    Counts columns by finding the maximum column index among all occupied
    cells in the cell_grid.

    Args:
        model: Parsed Gnumeric model dict.
        sheet_idx: 0-based sheet index.

    Returns:
        Integer column count. Returns 0 if sheet not found or empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0
    grid = sheets[sheet_idx].get("cell_grid", {})
    if not grid:
        return 0
    return max(col for (row, col) in grid.keys()) + 1


def gnumeric_row_count_file(file_path: "str | bytes | Path", sheet_idx: int = 0) -> int:
    """Return the number of distinct row indices with data in the given sheet.

    Args:
        file_path: Path to a .gnumeric file.
        sheet_idx: 0-based sheet index (default 0).

    Returns:
        Integer row count. Returns 0 for empty sheets.

    Raises:
        GnumericError subclasses on parse failure.
    """
    model = load(file_path)
    return row_count(model, sheet_idx)


def gnumeric_column_count_file(file_path: "str | bytes | Path", sheet_idx: int = 0) -> int:
    """Return the number of distinct column indices with data in the given sheet.

    File-path wrapper around gnumeric_column_count(model, sheet_idx).

    Args:
        file_path: Path to a Gnumeric file.
        sheet_idx: 0-based sheet index (default 0).

    Returns:
        Integer column count.
    """
    model = load(file_path)
    return gnumeric_column_count(model, sheet_idx)


def gnumeric_cell_count_file(file_path: "str | bytes | Path", sheet_idx: int = 0) -> int:
    """Return the number of non-empty cells in a sheet, taking a file path.

    Convenience wrapper around the model-based ``count_nonempty_cells``.

    Args:
        file_path: Path to a ``.gnumeric`` file.
        sheet_idx: 0-based sheet index (default 0).

    Returns:
        Integer count of non-empty cells.
    """
    model = load(file_path)
    return count_nonempty_cells(model, sheet_idx)


def gnumeric_string_cell_count(model: "dict[str, Any]", sheet_idx: int) -> int:
    """Return the count of cells that contain non-numeric string values.

    A cell is counted as a string cell if its value cannot be converted to float.

    Args:
        model: Parsed Gnumeric model dict.
        sheet_idx: 0-based sheet index.

    Returns:
        Integer count of string cells. Returns 0 for empty sheets.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0
    grid = sheets[sheet_idx].get("cell_grid", {})
    count = 0
    for v in grid.values():
        try:
            float(v)
        except (ValueError, TypeError):
            count += 1
    return count


def gnumeric_empty_cell_count(model: "dict[str, Any]", sheet_idx: int) -> int:
    """Return the count of cells in the grid with empty or None values.

    Args:
        model: Parsed Gnumeric model dict.
        sheet_idx: 0-based sheet index.

    Returns:
        Integer count of empty cells. Returns 0 if sheet not found or empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0
    grid = sheets[sheet_idx].get("cell_grid", {})
    count = 0
    for v in grid.values():
        if v is None or v == "":
            count += 1
    return count


def gnumeric_nonempty_cell_count_file(
    file_path: "str | bytes | Path", sheet_idx: int = 0
) -> int:
    """Return the count of non-empty cells in a Gnumeric sheet (file-path API).

    Loads the file, parses it, and delegates to count_nonempty_cells.

    Args:
        file_path: Path to a .gnumeric file.
        sheet_idx: 0-based sheet index (default 0).

    Returns:
        Integer count of non-empty cells. Returns 0 for empty or missing sheets.
    """
    model = load(file_path)
    return count_nonempty_cells(model, sheet_idx)


def gnumeric_total_cell_count(file_path: "str | bytes | Path") -> int:
    """Return the total number of cells across all sheets in a Gnumeric file.

    Sums the cell count from every sheet. Counts cells stored in the
    document (entries in cell_grid), not the theoretical grid size.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Total cell count across all sheets.
    """
    model = load(file_path)
    sheets = model.get("sheets", [])
    total = 0
    for i in range(len(sheets)):
        total += count_nonempty_cells(model, i)
    return total


def gnumeric_sheet_count(file_path: "str | bytes | Path") -> int:
    """Return the number of sheets in a Gnumeric file.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Integer count of sheets.
    """
    model = load(file_path)
    return len(model.get("sheets", []))


def gnumeric_has_multiple_sheets(file_path: "str | bytes | Path") -> bool:
    """Return True if the Gnumeric file contains more than one sheet.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        True if sheet count > 1, False otherwise.
    """
    return gnumeric_sheet_count(file_path) > 1


def gnumeric_average_cells_per_sheet(file_path: "str | bytes | Path") -> float:
    """Return the average number of cells per sheet.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Float average. 0.0 if no sheets.
    """
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0.0
    total = sum(len(s.get("cell_values", [])) for s in sheets)
    return total / len(sheets)


def gnumeric_numeric_density(file_path: "str | bytes | Path") -> float:
    """Return the ratio of numeric cells to total cells.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Float between 0.0 and 1.0. 0.0 if no cells.
    """
    model = load(file_path)
    total = 0
    numeric = 0
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_values", []):
            total += 1
            try:
                float(val)
                numeric += 1
            except (ValueError, TypeError):
                pass
    if total == 0:
        return 0.0
    return numeric / total


def gnumeric_string_density(file_path: "str | bytes | Path") -> float:
    """Return the ratio of non-numeric cells to total cells.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Float between 0.0 and 1.0. 0.0 if no cells.
    """
    model = load(file_path)
    total = 0
    string_count = 0
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_values", []):
            total += 1
            try:
                float(val)
            except (ValueError, TypeError):
                string_count += 1
    if total == 0:
        return 0.0
    return string_count / total


def gnumeric_max_cell_length(file_path: "str | bytes | Path") -> int:
    """Return the length of the longest cell value string.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Integer max length. 0 if no cells.
    """
    model = load(file_path)
    max_len = 0
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_values", []):
            max_len = max(max_len, len(str(val)))
    return max_len


def gnumeric_min_cell_length(file_path: "str | bytes | Path") -> int:
    """Return the length of the shortest cell value string.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Integer min length, or 0 if no cells.
    """
    model = load(file_path)
    min_len = None
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_values", []):
            length = len(str(val))
            if min_len is None or length < min_len:
                min_len = length
    return min_len if min_len is not None else 0


def gnumeric_all_sheets_have_data(file_path: "str | bytes | Path") -> bool:
    """Return True if every sheet has at least one non-empty cell value.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        True if all sheets have data; False if any sheet is empty or has no cells.
    """
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return False
    for sheet in sheets:
        vals = [v for v in sheet.get("cell_values", []) if str(v).strip()]
        if not vals:
            return False
    return True


def gnumeric_has_any_string_cell(file_path: "str | bytes | Path") -> bool:
    """Return True if any cell contains a non-empty string value.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        True if at least one cell has a non-empty string value.
    """
    model = load(file_path)
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_values", []):
            if isinstance(val, str) and val.strip():
                return True
    return False


def gnumeric_cell_count_all_sheets(file_path: "str | bytes | Path") -> int:
    """Return total number of cells across all sheets.

    Args:
        file_path: Path to a .gnumeric (gzip-compressed XML) file.

    Returns:
        Total cell count (sum of cell_values lengths across all sheets).
    """
    model = load(file_path)
    return sum(len(sheet.get("cell_values", [])) for sheet in model.get("sheets", []))


def gnumeric_is_single_sheet(file_path: "str | bytes | Path") -> bool:
    """Return True if the workbook contains exactly one sheet."""
    model = load(file_path)
    return len(model.get("sheets", [])) == 1


def gnumeric_empty_sheet_count(file_path: "str | bytes | Path") -> int:
    """Return the number of sheets that have no non-empty cell values."""
    model = load(file_path)
    count = 0
    for sheet in model.get("sheets", []):
        vals = [v for v in sheet.get("cell_values", []) if str(v).strip()]
        if not vals:
            count += 1
    return count


def gnumeric_data_density(file_path: "str | bytes | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    total = gnumeric_total_cell_count(file_path)
    if total == 0:
        return 0.0
    model = load(file_path)
    nonempty = 0
    for sheet in model.get("sheets", []):
        for v in sheet.get("cell_values", []):
            if str(v).strip():
                nonempty += 1
    return nonempty / total


def gnumeric_max_row_count(file_path: "str | bytes | Path") -> int:
    """Return the maximum row count across all sheets. 0 if no sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0
    return max(sheet.get("row_count", 0) for sheet in sheets)


def gnumeric_min_row_count(file_path: "str | bytes | Path") -> int:
    """Return the minimum row count across all sheets. 0 if no sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0
    return min(sheet.get("row_count", 0) for sheet in sheets)


def gnumeric_has_empty_sheets(file_path: "str | bytes | Path") -> bool:
    """Return True if any sheet has zero cells."""
    return gnumeric_empty_sheet_count(file_path) > 0


def gnumeric_avg_row_count(file_path: "str | bytes | Path") -> float:
    """Return the average row count across all sheets. 0.0 if no sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0.0
    return sum(sheet.get("row_count", 0) for sheet in sheets) / len(sheets)


def gnumeric_nonempty_density(file_path: "str | bytes | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    total = gnumeric_total_cell_count(file_path)
    if total == 0:
        return 0.0
    model = load(file_path)
    nonempty = 0
    for sheet in model.get("sheets", []):
        for v in sheet.get("cell_values", []):
            if str(v).strip():
                nonempty += 1
    return nonempty / total


def gnumeric_is_empty(file_path: "str | bytes | Path") -> bool:
    """Return True if the file has no cells across all sheets."""
    return gnumeric_total_cell_count(file_path) == 0


def gnumeric_max_column_count(file_path: "str | bytes | Path") -> int:
    """Return the maximum number of columns across all sheets. 0 if no cells."""
    model = load(file_path)
    max_col = 0
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        if grid:
            col_max = max(col for (row, col) in grid.keys()) + 1
            if col_max > max_col:
                max_col = col_max
    return max_col


def gnumeric_total_string_length(file_path: "str | bytes | Path") -> int:
    """Return total length of all string cell values across all sheets."""
    model = load(file_path)
    total = 0
    for sheet in model.get("sheets", []):
        for v in sheet.get("cell_values", []):
            if isinstance(v, str):
                total += len(v)
    return total


def gnumeric_avg_cell_length(file_path: "str | bytes | Path") -> float:
    """Return average length of non-empty cell values. 0.0 if no cells."""
    model = load(file_path)
    lengths = []
    for sheet in model.get("sheets", []):
        for v in sheet.get("cell_values", []):
            s = str(v).strip()
            if s:
                lengths.append(len(s))
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def gnumeric_column_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of column counts across sheets. 0.0 if fewer than 2 sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if len(sheets) < 2:
        return 0.0
    col_counts = [sheet.get("max_col", 0) + 1 for sheet in sheets]
    mean = sum(col_counts) / len(col_counts)
    return sum((c - mean) ** 2 for c in col_counts) / len(col_counts)


def gnumeric_is_rectangular(file_path: "str | bytes | Path") -> bool:
    """Return True if all sheets have the same column count."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if len(sheets) < 2:
        return True
    col_counts = [sheet.get("max_col", 0) for sheet in sheets]
    return len(set(col_counts)) == 1


def gnumeric_min_column_count(file_path: "str | bytes | Path") -> int:
    """Return the minimum number of columns across all sheets. 0 if no cells."""
    model = load(file_path)
    col_counts = []
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        if grid:
            col_counts.append(max(col for (row, col) in grid.keys()) + 1)
        else:
            col_counts.append(0)
    if not col_counts:
        return 0
    return min(col_counts)


def gnumeric_avg_column_count(file_path: "str | bytes | Path") -> float:
    """Return the average number of columns across all sheets. 0.0 if no sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0.0
    col_counts = []
    for sheet in sheets:
        grid = sheet.get("cell_grid", {})
        if grid:
            col_counts.append(max(col for (row, col) in grid.keys()) + 1)
        else:
            col_counts.append(0)
    return sum(col_counts) / len(col_counts)


def gnumeric_has_empty_cells(file_path: "str | bytes | Path") -> bool:
    """Return True if any sheet has cells with empty or None values."""
    model = load(file_path)
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        for val in grid.values():
            if val is None or (isinstance(val, str) and not val.strip()):
                return True
    return False


def gnumeric_total_row_count(file_path: "str | bytes | Path") -> int:
    """Return total row count across all sheets."""
    model = load(file_path)
    total = 0
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        if grid:
            total += max(row for (row, col) in grid.keys()) + 1
    return total


def gnumeric_is_all_numeric(file_path: "str | bytes | Path") -> bool:
    """Return True if all cells have numeric values. False if no cells."""
    model = load(file_path)
    has_cells = False
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        for val in grid.values():
            has_cells = True
            if val is None:
                return False
            try:
                float(val)
            except (ValueError, TypeError):
                return False
    return has_cells


def gnumeric_nonempty_cell_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    model = load(file_path)
    total = 0
    nonempty = 0
    for sheet in model.get("sheets", []):
        grid = sheet.get("cell_grid", {})
        total += len(grid)
        for val in grid.values():
            if val is not None and (not isinstance(val, str) or val.strip()):
                nonempty += 1
    if total == 0:
        return 0.0
    return nonempty / total


def gnumeric_row_count_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of row counts across sheets. 0.0 if fewer than 2 sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if len(sheets) < 2:
        return 0.0
    counts = [len(s.get("cell_grid", {})) for s in sheets]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def gnumeric_sheet_name_lengths(file_path: "str | bytes | Path") -> list[int]:
    """Return list of character lengths of sheet names."""
    model = load(file_path)
    return [len(s.get("name", "")) for s in model.get("sheets", [])]


def gnumeric_max_cell_value_length(file_path: "str | bytes | Path") -> int:
    """Return the maximum character length of any cell value. 0 if no cells."""
    model = load(file_path)
    max_len = 0
    for sheet in model.get("sheets", []):
        for _key, cell in sheet.get("cell_grid", {}).items():
            val = cell.get("value", "") if isinstance(cell, dict) else cell
            if val is not None and len(str(val)) > max_len:
                max_len = len(str(val))
    return max_len


def gnumeric_is_multi_sheet(file_path: "str | bytes | Path") -> bool:
    """Return True if the workbook has more than one sheet."""
    model = load(file_path)
    return len(model.get("sheets", [])) > 1


def gnumeric_avg_numeric_value(file_path: "str | bytes | Path") -> float:
    """Return average of all numeric cell values across all sheets. 0.0 if none."""
    model = load(file_path)
    values = []
    for sheet in model.get("sheets", []):
        for _key, val in sheet.get("cell_grid", {}).items():
            if val is not None:
                try:
                    values.append(float(str(val)))
                except (ValueError, TypeError):
                    pass
    return sum(values) / len(values) if values else 0.0


def gnumeric_nonempty_row_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of rows with at least one non-empty cell to total rows in sheet 0. 0.0 if empty."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0.0
    grid = sheets[0].get("cell_grid", {})
    if not grid:
        return 0.0
    rows_with_data = set()
    all_rows = set()
    for key, val in grid.items():
        row, col = key
        all_rows.add(row)
        if val is not None and str(val).strip():
            rows_with_data.add(row)
    if not all_rows:
        return 0.0
    return len(rows_with_data) / len(all_rows)


def gnumeric_longest_row_index(file_path: "str | bytes | Path") -> int:
    """Return 0-based row index with the most non-empty cells in sheet 0. -1 if empty."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return -1
    grid = sheets[0].get("cell_grid", {})
    if not grid:
        return -1
    row_counts: dict = {}
    for key, val in grid.items():
        row, col = key
        if val is not None and str(val).strip():
            row_counts[row] = row_counts.get(row, 0) + 1
    if not row_counts:
        return -1
    return max(row_counts, key=row_counts.get)


def gnumeric_numeric_sum_all(file_path: "str | bytes | Path") -> float:
    """Return sum of all numeric cell values across all sheets."""
    model = load(file_path)
    total = 0.0
    for sheet in model.get("sheets", []):
        for _key, val in sheet.get("cell_grid", {}).items():
            if val is not None:
                try:
                    total += float(str(val))
                except (ValueError, TypeError):
                    pass
    return total


def gnumeric_empty_column_count(file_path: "str | bytes | Path") -> int:
    """Return number of entirely empty columns in sheet 0."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0
    grid = sheets[0].get("cell_grid", {})
    if not grid:
        return 0
    all_cols: set = set()
    cols_with_data: set = set()
    for key, val in grid.items():
        row, col = key
        all_cols.add(col)
        if val is not None and str(val).strip():
            cols_with_data.add(col)
    empty_cols = all_cols - cols_with_data
    return len(empty_cols)


def gnumeric_cell_count_variance(file_path: "str | bytes | Path") -> float:
    """Return variance of cell counts across sheets. 0.0 if fewer than 2 sheets."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if len(sheets) < 2:
        return 0.0
    counts = [len(s.get("cell_grid", {})) for s in sheets]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def gnumeric_max_row_length(file_path: "str | bytes | Path") -> int:
    """Return maximum number of cells in any single row across all sheets. 0 if no cells."""
    model = load(file_path)
    max_len = 0
    for sheet in model.get("sheets", []):
        from collections import Counter as _Counter
        row_counts = _Counter(key[0] for key in sheet.get("cell_grid", {}).keys())
        if row_counts:
            rc = max(row_counts.values())
            if rc > max_len:
                max_len = rc
    return max_len


def gnumeric_cell_to_row_ratio(file_path: "str | bytes | Path") -> float:
    """Return total cell count divided by row count. 0.0 if no rows."""
    rows = gnumeric_row_count_file(file_path)
    if rows == 0:
        return 0.0
    return gnumeric_total_cell_count(file_path) / rows



# ---------------------------------------------------------------------------
# Analytics functions for deepening tests (TC-F-012)
# ---------------------------------------------------------------------------

def gnumeric_string_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of non-numeric cells to all non-empty cells. 0.0 if no cells."""
    model = load(file_path)
    total = 0
    strings = 0
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_grid", {}).values():
            if val is not None and str(val).strip():
                total += 1
                try:
                    float(str(val))
                except (ValueError, TypeError):
                    strings += 1
    if total == 0:
        return 0.0
    return float(strings) / total


def gnumeric_nonempty_row_count(file_path: "str | bytes | Path") -> int:
    """Return count of rows with at least one non-empty cell in sheet 0."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0
    grid = sheets[0].get("cell_grid", {})
    nonempty_rows = set()
    for (row, col), val in grid.items():
        if val is not None and str(val).strip():
            nonempty_rows.add(row)
    return len(nonempty_rows)


def gnumeric_numeric_range(file_path: "str | bytes | Path") -> float:
    """Return max - min of all numeric cell values. 0.0 if fewer than 2 numeric values."""
    model = load(file_path)
    nums = []
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_grid", {}).values():
            if val is not None:
                try:
                    nums.append(float(str(val)))
                except (ValueError, TypeError):
                    pass
    if len(nums) < 2:
        return 0.0
    return float(max(nums) - min(nums))


def gnumeric_distinct_string_count(file_path: "str | bytes | Path") -> int:
    """Return count of distinct non-empty non-numeric string cell values."""
    model = load(file_path)
    strings = set()
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_grid", {}).values():
            if val is not None and str(val).strip():
                s = str(val).strip()
                try:
                    float(s)
                except (ValueError, TypeError):
                    strings.add(s)
    return len(strings)


def gnumeric_row_col_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of row count to column count in sheet 0. 0.0 if no columns."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0.0
    grid = sheets[0].get("cell_grid", {})
    if not grid:
        return 0.0
    rows = set(k[0] for k in grid)
    cols = set(k[1] for k in grid)
    if not cols:
        return 0.0
    return float(len(rows)) / len(cols)


def gnumeric_numeric_to_string_ratio(file_path: "str | bytes | Path") -> float:
    """Return ratio of numeric cells to string cells. 0.0 if no string cells.

    Uses isinstance check since GNUMERIC codec returns all values as Python str.
    """
    model = load(file_path)
    numeric = 0
    string_count = 0
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_grid", {}).values():
            if val is not None and str(val).strip():
                if isinstance(val, (int, float)):
                    numeric += 1
                else:
                    string_count += 1
    if string_count == 0:
        return 0.0
    return float(numeric) / string_count


def gnumeric_max_string_cell_length(file_path: "str | bytes | Path") -> int:
    """Return length of the longest non-numeric string cell value. 0 if none."""
    model = load(file_path)
    max_len = 0
    for sheet in model.get("sheets", []):
        for val in sheet.get("cell_grid", {}).values():
            if val is not None:
                s = str(val).strip()
                if s:
                    try:
                        float(s)
                    except (ValueError, TypeError):
                        if len(s) > max_len:
                            max_len = len(s)
    return max_len


def gnumeric_row_density_avg(file_path: "str | bytes | Path") -> float:
    """Return average ratio of non-empty cells per row to column count. 0.0 if no data."""
    model = load(file_path)
    sheets = model.get("sheets", [])
    if not sheets:
        return 0.0
    grid = sheets[0].get("cell_grid", {})
    if not grid:
        return 0.0
    cols = set(k[1] for k in grid)
    col_count = len(cols)
    if col_count == 0:
        return 0.0
    row_counts: dict = {}
    for (row, col), val in grid.items():
        if val is not None and str(val).strip():
            row_counts[row] = row_counts.get(row, 0) + 1
    all_rows = set(k[0] for k in grid)
    if not all_rows:
        return 0.0
    densities = [float(row_counts.get(r, 0)) / col_count for r in all_rows]
    return sum(densities) / len(densities)
