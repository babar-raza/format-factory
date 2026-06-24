"""Gnumeric workbook statistics and aggregation functions.

Derived analytics, aggregation, and row/column query operations on
Gnumeric neutral model dicts. These functions operate on already-parsed
model data.

spec_concept: Gnumeric XML cell/sheet workbook statistics
"""
from __future__ import annotations

from typing import Any

from .gnumeric_codec import set_cell_value


def sum_column(model: dict[str, Any], sheet_idx: int, col_idx: int) -> float:
    """Return the numeric sum of all values in a column (non-numeric values skipped).

    Returns 0.0 if sheet_idx is out of range or column is empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0.0
    grid = sheets[sheet_idx].get("cell_grid", {})
    total = 0.0
    for (r, c), v in grid.items():
        if c == col_idx:
            try:
                total += float(v)
            except (ValueError, TypeError):
                pass
    return total


def fill_column(
    model: dict[str, Any], sheet_idx: int, col_idx: int, values: list
) -> dict[str, Any]:
    """Return a new model with values written into a column starting at row 0 (immutable).

    Returns the original model unchanged if sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return model
    result = model
    for row_idx, value in enumerate(values):
        result = set_cell_value(result, sheet_idx, row_idx, col_idx, str(value))
    return result


def sum_row(model: dict[str, Any], sheet_idx: int, row_idx: int) -> float:
    """Return the numeric sum of all values in a row (non-numeric values skipped).

    Returns 0.0 if sheet_idx is out of range or row is empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0.0
    grid = sheets[sheet_idx].get("cell_grid", {})
    total = 0.0
    for (r, c), v in grid.items():
        if r == row_idx:
            try:
                total += float(v)
            except (ValueError, TypeError):
                pass
    return total


def get_all_values(model: dict[str, Any], sheet_idx: int) -> list[str]:
    """Return a list of all non-empty cell values in the sheet.

    Returns [] if sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return []
    grid = sheets[sheet_idx].get("cell_grid", {})
    return [v for v in grid.values() if v]


def clear_sheet(model: dict[str, Any], sheet_idx: int) -> dict[str, Any]:
    """Return a new model with all cells in the sheet cleared (immutable).

    Returns the original model unchanged if sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return model
    new_sheets = []
    for i, sheet in enumerate(sheets):
        if i == sheet_idx:
            new_sheets.append({**sheet, "cell_grid": {}, "cell_count": 0, "cell_values": []})
        else:
            new_sheets.append(sheet)
    total = sum(s["cell_count"] for s in new_sheets)
    return {**model, "sheets": new_sheets, "cell_count": total}


def get_sheet_as_rows(model: dict[str, Any], sheet_idx: int) -> list[list[str]]:
    """Return sheet data as a list of rows (each row is a list of strings).

    Returns [] if sheet_idx is out of range or the sheet is empty.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return []
    grid = sheets[sheet_idx].get("cell_grid", {})
    if not grid:
        return []
    max_row = max(r for r, _ in grid)
    max_col = max(c for _, c in grid)
    return [
        [grid.get((r, c), "") for c in range(max_col + 1)]
        for r in range(max_row + 1)
    ]


def fill_row(
    model: dict[str, Any], sheet_idx: int, row_idx: int, values: list
) -> dict[str, Any]:
    """Return a new model with values written into a row starting at col 0 (immutable).

    Returns the original model unchanged if sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return model
    result = model
    for col_idx, value in enumerate(values):
        result = set_cell_value(result, sheet_idx, row_idx, col_idx, str(value))
    return result


def sheet_names(model: dict[str, Any]) -> list[str]:
    """Return a list of sheet names from a workbook model dict.

    Args:
        model: Workbook model dict (as returned by load() or create_gnumeric()).

    Returns:
        List of sheet names in order.
    """
    return [s.get("name", "") for s in model.get("sheets", [])]


def row_count(model: dict[str, Any], sheet_idx: int) -> int:
    """Return the number of rows (max_row_index + 1) in the sheet.

    Returns 0 if sheet_idx is out of range or the sheet is empty.
    Does NOT raise on out-of-range sheet_idx (returns 0 instead).
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        return 0
    grid = sheets[sheet_idx].get("cell_grid", {})
    if not grid:
        return 0
    return max(r for r, _ in grid) + 1


def get_row_values(model: dict[str, Any], sheet_idx: int, row_idx: int) -> list[str]:
    """Return all cell values in a given row as a list of strings.

    Cells not present in the grid are returned as empty strings.
    The list length equals the maximum column index used in that row + 1.

    Args:
        model: Gnumeric neutral model dict.
        sheet_idx: Zero-based sheet index.
        row_idx: Zero-based row index.

    Returns:
        List of string cell values for the row. Empty list if row has no cells.

    Raises:
        IndexError: If sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise IndexError(f"sheet_idx {sheet_idx} out of range (have {len(sheets)} sheets)")
    grid = sheets[sheet_idx].get("cell_grid", {})
    row_cells = {c: v for (r, c), v in grid.items() if r == row_idx}
    if not row_cells:
        return []
    max_col = max(row_cells.keys())
    return [row_cells.get(c, "") for c in range(max_col + 1)]


def get_column_values(model: dict[str, Any], sheet_idx: int, col_idx: int) -> list[str]:
    """Return all cell values in a given column as a list of strings.

    Cells not present in the grid are returned as empty strings.
    The list length equals the maximum row index used in that column + 1.

    Args:
        model: Gnumeric neutral model dict.
        sheet_idx: Zero-based sheet index.
        col_idx: Zero-based column index.

    Returns:
        List of string cell values for the column. Empty list if column has no cells.

    Raises:
        IndexError: If sheet_idx is out of range.
    """
    sheets = model.get("sheets", [])
    if sheet_idx < 0 or sheet_idx >= len(sheets):
        raise IndexError(f"sheet_idx {sheet_idx} out of range (have {len(sheets)} sheets)")
    grid = sheets[sheet_idx].get("cell_grid", {})
    col_cells = {r: v for (r, c), v in grid.items() if c == col_idx}
    if not col_cells:
        return []
    max_row = max(col_cells.keys())
    return [col_cells.get(r, "") for r in range(max_row + 1)]


def min_column_value(model: dict[str, Any], sheet_idx: int, col_idx: int) -> "float | None":
    """Return the minimum numeric value in a column.

    Non-numeric string values are ignored. Returns None if no numeric values.
    """
    values = get_column_values(model, sheet_idx, col_idx)
    nums = []
    for v in values:
        try:
            nums.append(float(v))
        except (ValueError, TypeError):
            pass
    return min(nums) if nums else None


def max_column_value(model: dict[str, Any], sheet_idx: int, col_idx: int) -> "float | None":
    """Return the maximum numeric value in a column.

    Non-numeric string values are ignored. Returns None if no numeric values.
    """
    values = get_column_values(model, sheet_idx, col_idx)
    nums = []
    for v in values:
        try:
            nums.append(float(v))
        except (ValueError, TypeError):
            pass
    return max(nums) if nums else None


def average_column(model: dict[str, Any], sheet_idx: int, col_idx: int) -> float:
    """Return the average (mean) of numeric values in a column.

    Non-numeric string values are ignored. Returns 0.0 if no numeric values.
    """
    values = get_column_values(model, sheet_idx, col_idx)
    nums = []
    for v in values:
        try:
            nums.append(float(v))
        except (ValueError, TypeError):
            pass
    return sum(nums) / len(nums) if nums else 0.0


def average_row(model: dict[str, Any], sheet_idx: int, row_idx: int) -> float:
    """Return the average (mean) of numeric values in a row.

    Non-numeric string values are ignored. Returns 0.0 if no numeric values.
    """
    values = get_row_values(model, sheet_idx, row_idx)
    nums = []
    for v in values:
        try:
            nums.append(float(v))
        except (ValueError, TypeError):
            pass
    return sum(nums) / len(nums) if nums else 0.0


def correlation_columns(
    model: dict[str, Any],
    sheet_idx: int,
    col_a: int,
    col_b: int,
) -> float:
    """Compute Pearson correlation coefficient between two columns.

    Returns:
        Pearson r in [-1.0, 1.0], or 0.0 if insufficient data.
    """
    vals_a = get_column_values(model, sheet_idx, col_a)
    vals_b = get_column_values(model, sheet_idx, col_b)

    pairs = []
    for va, vb in zip(vals_a, vals_b):
        try:
            pairs.append((float(va), float(vb)))
        except (ValueError, TypeError):
            pass

    n = len(pairs)
    if n < 2:
        return 0.0

    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
    den_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
    denom = den_x * den_y
    if denom == 0.0:
        return 0.0
    return num / denom
