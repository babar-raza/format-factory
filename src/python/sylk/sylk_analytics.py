"""
SYLK analytics functions for Symbolic Link spreadsheet format.

Pure analytics functions operating on parsed SYLK document models.
No spec_qname claim at module scope — analytics modules do not represent
SYLK format element types. Parser source: sylk_parser.py (parse_sylk_strict).
"""
from __future__ import annotations

from pathlib import Path

from .sylk_parser import (
    parse_sylk_strict,
)


def sylk_nonempty_rows(file_path: "str | Path") -> int:
    """Return the count of rows that contain at least one non-empty cell."""
    doc = parse_sylk_strict(file_path)
    rows_with_data = set()
    for cell in doc.cells:
        val = cell.value
        if val is not None and str(val).strip() != "":
            rows_with_data.add(cell.row)
    return len(rows_with_data)


def sylk_string_cell_count(file_path: "str | Path") -> int:
    """Return the count of cells that contain a string value.

    Args:
        file_path: Path to SYLK (.slk) file.

    Returns:
        Integer count of string cells.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    count = 0
    for cell in doc.cells:
        if isinstance(cell.value, str):
            count += 1
    return count


def sylk_max_column_index(file_path: "str | Path") -> int:
    """Return the maximum column index across all cells in the SYLK file.

    Column indices are 1-based in SYLK format.

    Args:
        file_path: Path to SYLK (.slk) file.

    Returns:
        Integer maximum column index. Returns 0 if no cells exist.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0
    return max(cell.col for cell in doc.cells)


def sylk_row_count(file_path: "str | Path") -> int:
    """Return the number of distinct row indices present in the SYLK document.

    Args:
        file_path: Path to a SYLK (.slk) file.

    Returns:
        Integer count of distinct rows. Returns 0 if no cells exist.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    rows = {cell.row for cell in doc.cells}
    return len(rows)


def sylk_total_sum(file_path: "str | Path") -> float:
    """Return the sum of all numeric cell values across the entire SYLK document.

    Iterates every cell in the document and accumulates the sum of all values
    that are integers or floats. String and None values are skipped.

    Args:
        file_path: Path to a SYLK (.slk) file.

    Returns:
        Float sum of all numeric cell values. Returns 0.0 if no numeric cells exist.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    total = 0.0
    for cell in doc.cells:
        if isinstance(cell.value, (int, float)):
            total += cell.value
    return total


def sylk_column_count(file_path: "str | Path") -> int:
    """Return the number of distinct column indices present in the SYLK document.

    Args:
        file_path: Path to a SYLK (.slk) file.

    Returns:
        Integer count of unique column indices.
    """
    doc = parse_sylk_strict(file_path)
    cols = {cell.col for cell in doc.cells}
    return len(cols)


def sylk_unique_values(file_path: "str | Path", col: int) -> "list":
    """Return a sorted list of unique non-None values in the given column.

    Args:
        file_path: Path to a SYLK (.slk) file.
        col: 1-based column index to inspect.

    Returns:
        Sorted list of unique values found in that column (excluding None/empty).
    """
    doc = parse_sylk_strict(file_path)
    seen: set = set()
    for cell in doc.cells:
        if cell.col == col and cell.value is not None:
            seen.add(cell.value)
    try:
        return sorted(seen)
    except TypeError:
        # mixed types (str + int) — sort by string representation
        return sorted(seen, key=str)


def sylk_cell_type_distribution(file_path: "str | Path") -> "dict[str, int]":
    """Return a distribution of cell types in a SYLK file.

    Classifies every cell as 'numeric', 'string', or 'empty' and returns
    the count for each type.

    Args:
        file_path: Path to a SYLK (.slk) file.

    Returns:
        Dict with keys 'numeric', 'string', 'empty' mapping to integer counts.
    """
    doc = parse_sylk_strict(file_path)
    counts: dict[str, int] = {"numeric": 0, "string": 0, "empty": 0}
    for cell in doc.cells:
        if cell.value is None or (isinstance(cell.value, str) and not cell.value.strip()):
            counts["empty"] += 1
        elif isinstance(cell.value, (int, float)):
            counts["numeric"] += 1
        else:
            s = str(cell.value).strip()
            try:
                float(s)
                counts["numeric"] += 1
            except (ValueError, TypeError):
                counts["string"] += 1
    return counts


def sylk_has_header(file_path: "str | Path") -> bool:
    """Heuristic: detect if row 1 of a SYLK file is a header row.

    A row is considered a header if it has at least one cell AND every cell
    in row 1 is a string (non-numeric). If row 1 has no cells or contains
    any numeric value, returns False.

    Args:
        file_path: Path to a SYLK (.slk) file.

    Returns:
        True if row 1 appears to be a header, False otherwise.
    """
    doc = parse_sylk_strict(file_path)
    row1_cells = [c for c in doc.cells if c.row == 1]
    if not row1_cells:
        return False
    return all(c.value_type == "string" for c in row1_cells)


def sylk_average_numeric_value(file_path: "str | Path") -> float:
    """Return the average value of all numeric cells in a SYLK file.

    Args:
        file_path: Path to a SYLK (.slk) file.

    Returns:
        Float average. Returns 0.0 if there are no numeric cells.
    """
    doc = parse_sylk_strict(file_path)
    nums: list[float] = []
    for c in doc.cells:
        if c.value_type in ("number", "numeric"):
            try:
                nums.append(float(c.value))
            except (ValueError, TypeError):
                pass
    if not nums:
        return 0.0
    return sum(nums) / len(nums)


def sylk_max_row_length(file_path: "str | Path") -> int:
    """Return the maximum number of cells in any single row of a SYLK file.

    Args:
        file_path: Path to a SYLK (.slk) file.

    Returns:
        Integer max row length. Returns 0 if file has no cells.
    """
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0
    row_counts: dict[int, int] = {}
    for c in doc.cells:
        row_counts[c.row] = row_counts.get(c.row, 0) + 1
    return max(row_counts.values())


def sylk_numeric_density(file_path: "str | Path") -> float:
    """Return the ratio of numeric cells to total cells. 0.0 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0.0
    numeric = sum(1 for c in doc.cells if c.value_type in ("number", "numeric"))
    return numeric / len(doc.cells)


def sylk_total_cell_count(file_path: "str | Path") -> int:
    """Return the total number of cells in the SYLK file."""
    doc = parse_sylk_strict(file_path)
    return len(doc.cells)


def sylk_string_density(file_path: "str | Path") -> float:
    """Return the ratio of string cells to total cells. 0.0 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0.0
    string_count = sum(1 for c in doc.cells if c.value_type in ("string", "text"))
    return string_count / len(doc.cells)


def sylk_nonempty_cell_count(file_path: "str | Path") -> int:
    """Return the number of cells with non-empty values."""
    doc = parse_sylk_strict(file_path)
    return sum(1 for c in doc.cells if c.value is not None and str(c.value).strip() != "")


def sylk_avg_row_length(file_path: "str | Path") -> float:
    """Return the average number of cells per row.

    Args:
        file_path: Path to a SYLK file.

    Returns:
        Float average cells per row, or 0.0 if no rows.
    """
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0.0
    rows: dict[int, int] = {}
    for c in doc.cells:
        rows[c.row] = rows.get(c.row, 0) + 1
    return sum(rows.values()) / len(rows)


def sylk_min_col_index(file_path: "str | Path") -> int:
    """Return the minimum column index used in the SYLK file.

    Args:
        file_path: Path to a SYLK file.

    Returns:
        Minimum column index (1-based), or 0 if no cells.
    """
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0
    return min(c.col for c in doc.cells)


def sylk_data_sparsity(file_path: "str | Path") -> float:
    """Return the sparsity of the SYLK grid: empty / (rows * cols).

    Measures how much of the logical grid (rows x columns) is unused.
    1.0 = completely empty; 0.0 = every cell in the grid is occupied.

    Args:
        file_path: Path to a SYLK file.

    Returns:
        Float sparsity ratio 0.0-1.0. Returns 0.0 if no cells exist.
    """
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0.0
    max_row = max(c.row for c in doc.cells)
    max_col = max(c.col for c in doc.cells)
    grid_size = max_row * max_col
    if grid_size == 0:
        return 0.0
    occupied = len(doc.cells)
    return 1.0 - (occupied / grid_size)


def sylk_max_cell_value_length(file_path: "str | Path") -> int:
    """Return the length of the longest cell value (as string).

    Args:
        file_path: Path to a SYLK file.

    Returns:
        Integer max length. Returns 0 if no cells or all cells are empty.
    """
    doc = parse_sylk_strict(file_path)
    max_len = 0
    for cell in doc.cells:
        if cell.value is not None:
            max_len = max(max_len, len(str(cell.value)))
    return max_len


def sylk_empty_cell_count(file_path: "str | Path") -> int:
    """Return the count of cells with no value (None or empty string).

    Args:
        file_path: Path to a SYLK file.

    Returns:
        Integer count of cells whose value is None or empty/whitespace.
    """
    doc = parse_sylk_strict(file_path)
    count = 0
    for cell in doc.cells:
        if cell.value is None or str(cell.value).strip() == "":
            count += 1
    return count


def sylk_min_cell_value_length(file_path: "str | Path") -> int:
    """Return the length of the shortest non-empty cell value string.

    Args:
        file_path: Path to a SYLK file.

    Returns:
        Integer min length of cell value string, or 0 if no non-empty cells.
    """
    doc = parse_sylk_strict(file_path)
    min_len = None
    for cell in doc.cells:
        if cell.value is not None:
            s = str(cell.value).strip()
            if s:
                length = len(str(cell.value))
                if min_len is None or length < min_len:
                    min_len = length
    return min_len if min_len is not None else 0


def sylk_max_numeric_value(file_path: "str | Path") -> "float | None":
    """Return the maximum numeric cell value.

    Args:
        file_path: Path to a SYLK file.

    Returns:
        Float max numeric value, or None if no numeric cells.
    """
    doc = parse_sylk_strict(file_path)
    max_val = None
    for cell in doc.cells:
        if cell.value is None:
            continue
        try:
            v = float(cell.value)
            if max_val is None or v > max_val:
                max_val = v
        except (ValueError, TypeError):
            pass
    return max_val


def sylk_min_numeric_value(file_path: "str | Path") -> "float | None":
    """Return the minimum numeric cell value.

    Args:
        file_path: Path to a SYLK file.

    Returns:
        Float min numeric value, or None if no numeric cells.
    """
    doc = parse_sylk_strict(file_path)
    min_val = None
    for cell in doc.cells:
        if cell.value is None:
            continue
        try:
            v = float(cell.value)
            if min_val is None or v < min_val:
                min_val = v
        except (ValueError, TypeError):
            pass
    return min_val


def sylk_numeric_range(file_path: "str | Path") -> float:
    """Return the range (max - min) of numeric cell values.

    Args:
        file_path: Path to a SYLK file.

    Returns:
        Float range, or 0.0 if fewer than 2 numeric cells.
    """
    max_val = sylk_max_numeric_value(file_path)
    min_val = sylk_min_numeric_value(file_path)
    if max_val is None or min_val is None:
        return 0.0
    return max_val - min_val


def sylk_is_rectangular(file_path: "str | Path") -> bool:
    """Return True if all rows have the same number of cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return True
    row_counts: dict[int, int] = {}
    for c in doc.cells:
        row_counts[c.row] = row_counts.get(c.row, 0) + 1
    counts = list(row_counts.values())
    return len(set(counts)) <= 1


def sylk_min_row_length(file_path: "str | Path") -> int:
    """Return the number of cells in the narrowest row. 0 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0
    row_counts: dict[int, int] = {}
    for c in doc.cells:
        row_counts[c.row] = row_counts.get(c.row, 0) + 1
    return min(row_counts.values())


def sylk_has_string_cells(file_path: "str | Path") -> bool:
    """Return True if any cell contains a string value.

    Args:
        file_path: Path to a SYLK (.slk) file.

    Returns:
        True if at least one cell has a string value.
    """
    doc = parse_sylk_strict(file_path)
    return any(isinstance(c.value, str) and c.value.strip() for c in doc.cells)


def sylk_unique_row_count(file_path: "str | Path") -> int:
    """Return the number of distinct row indices in the spreadsheet.

    Args:
        file_path: Path to a SYLK (.slk) file.

    Returns:
        Count of unique row indices.
    """
    doc = parse_sylk_strict(file_path)
    return len(set(c.row for c in doc.cells))


def sylk_unique_column_count(file_path: "str | Path") -> int:
    """Return the number of distinct column indices in the spreadsheet."""
    doc = parse_sylk_strict(file_path)
    return len(set(c.col for c in doc.cells))


def sylk_has_numeric_cells(file_path: "str | Path") -> bool:
    """Return True if any cell has a numeric value type."""
    doc = parse_sylk_strict(file_path)
    return any(c.value_type in ("number", "numeric") for c in doc.cells)


def sylk_data_density(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    total = sylk_total_cell_count(file_path)
    if total == 0:
        return 0.0
    nonempty = sylk_nonempty_cell_count(file_path)
    return nonempty / total


def sylk_avg_cell_value_length(file_path: "str | Path") -> float:
    """Return the average string length of all cell values. 0.0 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0.0
    return sum(len(str(c.value)) for c in doc.cells) / len(doc.cells)


def sylk_is_single_row(file_path: "str | Path") -> bool:
    """Return True if the file contains exactly one row of data."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return False
    rows = {c.row for c in doc.cells}
    return len(rows) == 1


# ---------------------------------------------------------------------------
# Re-export extracted functions (TC-PA-017 monolith healing — pure refactor)
# ---------------------------------------------------------------------------
from .sylk_metrics import *  # noqa: F401,F403,E402
