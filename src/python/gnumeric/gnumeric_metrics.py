"""gnumeric_metrics.py — Extracted GNUMERIC analytics functions.

Split out of gnumeric_analytics.py (TC-PA-017 monolith healing) to keep each source
module under the 800-LOC architecture cap. Pure analytics functions over parsed
Gnumeric workbook models; behavior is unchanged from the original definitions. Base
loaders/metrics that remain in gnumeric_analytics.py are brought in via the star-import
below. Re-exported from gnumeric_analytics.py so every public name stays importable
from its original path.
"""
from __future__ import annotations

from .gnumeric_analytics import *  # noqa: F401,F403 - base loaders/metrics reused at call time


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
