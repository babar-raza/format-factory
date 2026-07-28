"""ods_workbook_metrics.py — Extracted ODS workbook metric functions.

Split out of ods_analytics.py (TC-PA-017 monolith healing) to keep each source
module under the 800-LOC architecture cap. Pure analytics functions over parsed
ODS models; behavior is unchanged from the original definitions. Several of these
call base metric functions that remain in ods_analytics.py; those names (plus the
shared parser/Path imports) are brought in via the star-import below. Re-exported
from ods_analytics.py so every public name stays importable from its original path.
"""
from __future__ import annotations

from .ods_analytics import *  # noqa: F401,F403 - base metrics/parser reused at call time


def ods_empty_sheet_count(file_path: "str | Path") -> int:
    """Return number of sheets with zero non-empty cells."""
    doc = parse_ods_strict(file_path)
    count = 0
    for sheet in doc.sheets:
        has_data = False
        for row in sheet.rows:
            for cell in row.cells:
                if cell.value is not None and str(cell.value).strip():
                    has_data = True
                    break
            if has_data:
                break
        if not has_data:
            count += 1
    return count


def ods_numeric_sum(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return sum of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    total = 0.0
    for row in doc.sheets[sheet_index].rows:
        for cell in row.cells:
            if cell.value is not None:
                try:
                    total += float(str(cell.value))
                except (ValueError, TypeError):
                    pass
    return total


def ods_min_row_length(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return the minimum number of non-empty cells in any non-empty row. 0 if no rows."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    nonempty_rows = [
        row for row in sheet.rows
        if any(cell.value is not None and cell.value != "" for cell in row.cells)
    ]
    if not nonempty_rows:
        return 0
    return min(
        sum(1 for cell in row.cells if cell.value is not None and cell.value != "")
        for row in nonempty_rows
    )


def ods_avg_numeric_value(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return average of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    values = []
    for row in doc.sheets[sheet_index].rows:
        for cell in row.cells:
            if cell.value is not None:
                try:
                    values.append(float(str(cell.value)))
                except (ValueError, TypeError):
                    pass
    return sum(values) / len(values) if values else 0.0


def ods_nonempty_row_ratio(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return ratio of non-empty rows to total rows. 0.0 if no rows."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    rows = doc.sheets[sheet_index].rows
    if not rows:
        return 0.0
    nonempty = sum(
        1 for row in rows
        if any(cell.value is not None and str(cell.value).strip() for cell in row.cells)
    )
    return nonempty / len(rows)


def ods_longest_row_index(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return 0-based index of the row with the most non-empty cells. -1 if no rows."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return -1
    rows = doc.sheets[sheet_index].rows
    if not rows:
        return -1
    best_idx, best_count = 0, 0
    for i, row in enumerate(rows):
        count = sum(1 for cell in row.cells if cell.value is not None and str(cell.value).strip())
        if count > best_count:
            best_count = count
            best_idx = i
    return best_idx


def ods_numeric_sum_all(file_path: "str | Path") -> float:
    """Return sum of all numeric cell values across all sheets."""
    doc = parse_ods_strict(file_path)
    total = 0.0
    for sheet in doc.sheets:
        for row in sheet.rows:
            for cell in row.cells:
                if cell.value is not None:
                    try:
                        total += float(str(cell.value))
                    except (ValueError, TypeError):
                        pass
    return total


def ods_empty_column_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return number of columns that are entirely empty."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    rows = doc.sheets[sheet_index].rows
    if not rows:
        return 0
    max_cols = max((len(row.cells) for row in rows), default=0)
    empty_count = 0
    for col_idx in range(max_cols):
        col_empty = all(
            col_idx >= len(row.cells) or row.cells[col_idx].value is None
            or str(row.cells[col_idx].value).strip() == ""
            for row in rows
        )
        if col_empty:
            empty_count += 1
    return empty_count


def ods_max_numeric_sum(file_path: "str | Path") -> float:
    """Return sum of all numeric cell values across all sheets. 0.0 if none."""
    doc = parse_ods_strict(file_path)
    total = 0.0
    for sheet in doc.sheets:
        for row in sheet.rows:
            for cell in row.cells:
                if cell.value is not None:
                    try:
                        total += float(str(cell.value))
                    except (ValueError, TypeError):
                        pass
    return total


def ods_cell_density(file_path: "str | Path") -> float:
    """Return average number of non-empty cells per row. 0.0 if no rows."""
    doc = parse_ods_strict(file_path)
    total_rows = 0
    nonempty_cells = 0
    for sheet in doc.sheets:
        for row in sheet.rows:
            total_rows += 1
            for cell in row.cells:
                if cell.value is not None and str(cell.value).strip():
                    nonempty_cells += 1
    if total_rows == 0:
        return 0.0
    return nonempty_cells / total_rows


def ods_numeric_ratio(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return numeric cell count divided by total cell count. 0.0 if no cells."""
    total = ods_total_cell_count(file_path, sheet_index)
    if total == 0:
        return 0.0
    return ods_numeric_cell_count(file_path, sheet_index) / total


def ods_is_square(file_path: "str | Path", sheet_index: int = 0) -> bool:
    """Return True if row count equals column count for the given sheet."""
    return ods_row_count(file_path, sheet_index) == ods_column_count(file_path, sheet_index)


def ods_numeric_column_count(file_path: "str | Path", sheet_index: int = 0) -> int:
    """Return count of columns that contain at least one numeric value."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0
    sheet = doc.sheets[sheet_index]
    numeric_cols: set[int] = set()
    for row in sheet.rows:
        for ci, cell in enumerate(row.cells):
            if cell.value is not None:
                try:
                    float(str(cell.value))
                    numeric_cols.add(ci)
                except (ValueError, TypeError):
                    pass
    return len(numeric_cols)


def ods_row_cell_variance(file_path: "str | Path", sheet_index: int = 0) -> float:
    """Return variance of cell counts across rows. 0.0 if fewer than 2 rows."""
    doc = parse_ods_strict(file_path)
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        return 0.0
    sheet = doc.sheets[sheet_index]
    counts = [len(row.cells) for row in sheet.rows]
    if len(counts) < 2:
        return 0.0
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


# ---------------------------------------------------------------------------
# Analytics functions for deepening tests (TC-F-012)
# ---------------------------------------------------------------------------

def ods_string_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of string cells to all non-empty cells. 0.0 if no non-empty cells."""
    doc = parse_ods_strict(file_path)
    total = 0
    strings = 0
    for sheet in doc.sheets:
        for row in sheet.rows:
            for cell in row.cells:
                if cell.value is not None and str(cell.value).strip():
                    total += 1
                    if cell.value_type in ("string", "text") or (
                        cell.value_type not in ("float", "integer", "boolean", "date", "time")
                    ):
                        try:
                            float(str(cell.value))
                        except (ValueError, TypeError):
                            strings += 1
    if total == 0:
        return 0.0
    return float(strings) / total


def ods_widest_column_index(file_path: "str | Path") -> int:
    """Return index of the column with the most non-empty cells across all sheets. -1 if no cells."""
    doc = parse_ods_strict(file_path)
    col_counts: dict = {}
    for sheet in doc.sheets:
        for row in sheet.rows:
            for idx, cell in enumerate(row.cells):
                if cell.value is not None and str(cell.value).strip():
                    col_counts[idx] = col_counts.get(idx, 0) + 1
    if not col_counts:
        return -1
    return max(col_counts, key=col_counts.get)


def ods_numeric_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of numeric cells to all non-empty cells. 0.0 if no non-empty cells."""
    doc = parse_ods_strict(file_path)
    total = 0
    numeric = 0
    for sheet in doc.sheets:
        for row in sheet.rows:
            for cell in row.cells:
                if cell.value is not None and str(cell.value).strip():
                    total += 1
                    try:
                        float(str(cell.value))
                        numeric += 1
                    except (ValueError, TypeError):
                        pass
    if total == 0:
        return 0.0
    return float(numeric) / total


def ods_column_fill_rate(file_path: "str | Path") -> float:
    """Return average ratio of non-empty cells per column to row count. 0.0 if no data."""
    doc = parse_ods_strict(file_path)
    col_nonempty: dict = {}
    total_rows = 0
    for sheet in doc.sheets:
        total_rows += len(sheet.rows)
        for row in sheet.rows:
            for idx, cell in enumerate(row.cells):
                if cell.value is not None and str(cell.value).strip():
                    col_nonempty[idx] = col_nonempty.get(idx, 0) + 1
    if not col_nonempty or total_rows == 0:
        return 0.0
    fill_rates = [float(v) / total_rows for v in col_nonempty.values()]
    return sum(fill_rates) / len(fill_rates)


def ods_value_type_count(file_path: "str | Path") -> int:
    """Return count of distinct value_types found across all cells."""
    doc = parse_ods_strict(file_path)
    types = set()
    for sheet in doc.sheets:
        for row in sheet.rows:
            for cell in row.cells:
                if cell.value_type is not None:
                    types.add(cell.value_type)
    return len(types)


def ods_nonempty_cell_percentage(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    doc = parse_ods_strict(file_path)
    total = 0
    nonempty = 0
    for sheet in doc.sheets:
        for row in sheet.rows:
            for cell in row.cells:
                total += 1
                if cell.value is not None and str(cell.value).strip():
                    nonempty += 1
    if total == 0:
        return 0.0
    return float(nonempty) / total
