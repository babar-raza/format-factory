"""
GNUMERIC analytics functions extracted from gnumeric_codec.py (TC-HEAL-FORMATS-BATCH1).
"""
from __future__ import annotations


spec_qname = "gnm:workbook"
spec_fact_ref = "SAL-GNUMERIC-00001"
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


# ---------------------------------------------------------------------------
# Re-export extracted functions (TC-PA-017 monolith healing — pure refactor)
# ---------------------------------------------------------------------------
from .gnumeric_metrics import *  # noqa: F401,F403,E402
