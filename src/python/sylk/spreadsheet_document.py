"""
SYLK analytics functions extracted from sylk_parser.py (TC-HEAL-FORMATS-BATCH1).
"""
from __future__ import annotations


spec_qname = "slk:workbook"
spec_fact_ref = "FACT-SYLK-001"
namespace_uri = "urn:sylk:symbolic-link"

from pathlib import Path
from typing import Any

from .sylk_parser import (
    parse_sylk,
    parse_sylk_strict,
    get_row_count,
    get_column_count,
    get_cell_count,
    get_all_values,
    count_nonempty_cells,
    get_cell_value,
    get_row_values,
    get_column_values,
    sum_column,
    min_column_value,
    max_column_value,
    average_column,
    count_distinct_values,
    find_rows_by_value,
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


def sylk_max_string_length(file_path: "str | Path") -> int:
    """Return the maximum length of any string cell value. 0 if no string cells."""
    doc = parse_sylk_strict(file_path)
    lengths = [len(str(c.value)) for c in doc.cells if isinstance(c.value, str)]
    return max(lengths) if lengths else 0


def sylk_column_variance(file_path: "str | Path") -> float:
    """Return variance of cell counts per column. 0.0 if fewer than 2 columns."""
    doc = parse_sylk_strict(file_path)
    from collections import Counter
    col_counts = Counter(c.col for c in doc.cells)
    vals = list(col_counts.values())
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    return sum((v - mean) ** 2 for v in vals) / len(vals)


def sylk_is_empty(file_path: "str | Path") -> bool:
    """Return True if the SYLK document has no cells."""
    doc = parse_sylk_strict(file_path)
    return len(doc.cells) == 0


def sylk_has_empty_rows(file_path: "str | Path") -> bool:
    """Return True if any row in the grid has no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return True
    from collections import defaultdict
    row_cells = defaultdict(int)
    for c in doc.cells:
        row_cells[c.row] += 1
    max_row = max(c.row for c in doc.cells)
    for r in range(1, max_row + 1):
        if row_cells[r] == 0:
            return True
    return False


def sylk_avg_numeric_cell_length(file_path: "str | Path") -> float:
    """Return average string length of numeric cell values. 0.0 if none."""
    doc = parse_sylk_strict(file_path)
    lengths = []
    for c in doc.cells:
        if c.value is not None:
            try:
                float(c.value)
                lengths.append(len(str(c.value)))
            except (ValueError, TypeError):
                pass
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def sylk_unique_value_count(file_path: "str | Path") -> int:
    """Return the count of distinct cell values."""
    doc = parse_sylk_strict(file_path)
    return len({c.value for c in doc.cells})


def sylk_is_multi_row(file_path: "str | Path") -> bool:
    """Return True if the document has more than one row."""
    doc = parse_sylk_strict(file_path)
    rows = {c.row for c in doc.cells}
    return len(rows) > 1


def sylk_is_single_column(file_path: "str | Path") -> bool:
    """Return True if all cells are in the same column."""
    doc = parse_sylk_strict(file_path)
    cols = {c.col for c in doc.cells}
    return len(cols) == 1


def sylk_cell_count_variance(file_path: "str | Path") -> float:
    """Return variance of cell counts per row. 0.0 if fewer than 2 rows."""
    from collections import defaultdict
    doc = parse_sylk_strict(file_path)
    row_counts = defaultdict(int)
    for c in doc.cells:
        row_counts[c.row] += 1
    counts = list(row_counts.values())
    if len(counts) < 2:
        return 0.0
    mean = sum(counts) / len(counts)
    return sum((v - mean) ** 2 for v in counts) / len(counts)


def sylk_is_all_numeric(file_path: "str | Path") -> bool:
    """Return True if all cells have numeric values. False if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return False
    for c in doc.cells:
        if c.value is None:
            return False
        try:
            float(c.value)
        except (ValueError, TypeError):
            return False
    return True


def sylk_row_span(file_path: "str | Path") -> int:
    """Return the row span (max_row - min_row + 1). 0 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0
    rows = [c.row for c in doc.cells]
    return max(rows) - min(rows) + 1


def sylk_numeric_cell_count(file_path: "str | Path") -> int:
    """Return the count of cells that have numeric values."""
    doc = parse_sylk_strict(file_path)
    count = 0
    for c in doc.cells:
        if c.value is None:
            continue
        try:
            float(c.value)
            count += 1
        except (ValueError, TypeError):
            pass
    return count


def sylk_is_square(file_path: "str | Path") -> bool:
    """Return True if the number of unique rows equals the number of unique columns."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return False
    rows = set(c.row for c in doc.cells)
    cols = set(c.col for c in doc.cells)
    return len(rows) == len(cols)


def sylk_avg_cell_length(file_path: "str | Path") -> float:
    """Return average string length of all cell values. 0.0 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0.0
    total = sum(len(str(c.value)) for c in doc.cells if c.value is not None)
    return total / len(doc.cells)


def sylk_column_span(file_path: "str | Path") -> int:
    """Return the column span (max_col - min_col + 1). 0 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0
    cols = [c.col for c in doc.cells]
    return max(cols) - min(cols) + 1


def sylk_numeric_sum(file_path: "str | Path") -> float:
    """Return sum of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_sylk_strict(file_path)
    total = 0.0
    for c in doc.cells:
        if c.value is not None:
            try:
                total += float(c.value)
            except (ValueError, TypeError):
                pass
    return total


def sylk_avg_numeric_value(file_path: "str | Path") -> float:
    """Return average of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_sylk_strict(file_path)
    nums = []
    for c in doc.cells:
        if c.value is not None:
            try:
                nums.append(float(c.value))
            except (ValueError, TypeError):
                pass
    if not nums:
        return 0.0
    return sum(nums) / len(nums)


def sylk_total_string_length(file_path: "str | Path") -> int:
    """Return total character count of all cell string representations."""
    doc = parse_sylk_strict(file_path)
    return sum(len(str(c.value)) for c in doc.cells if c.value is not None)


def sylk_nonempty_row_ratio(file_path: "str | Path") -> float:
    """Return ratio of rows with at least one non-empty cell to total rows. 0.0 if empty."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0.0
    all_rows = set(c.row for c in doc.cells)
    nonempty_rows = set(
        c.row for c in doc.cells
        if c.value is not None and str(c.value).strip()
    )
    if not all_rows:
        return 0.0
    return len(nonempty_rows) / len(all_rows)


def sylk_longest_row_index(file_path: "str | Path") -> int:
    """Return the row index with the most cells. -1 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return -1
    from collections import Counter as _Counter
    row_counts = _Counter(c.row for c in doc.cells)
    return row_counts.most_common(1)[0][0]


def sylk_numeric_variance(file_path: "str | Path") -> float:
    """Return variance of numeric cell values. 0.0 if fewer than 2 numeric cells."""
    doc = parse_sylk_strict(file_path)
    nums = []
    for c in doc.cells:
        if c.value is not None:
            try:
                nums.append(float(str(c.value)))
            except (ValueError, TypeError):
                pass
    if len(nums) < 2:
        return 0.0
    mean = sum(nums) / len(nums)
    return sum((n - mean) ** 2 for n in nums) / len(nums)


def sylk_max_row_cell_count(file_path: "str | Path") -> int:
    """Return the maximum number of cells in any single row. 0 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0
    from collections import Counter as _Counter
    row_counts = _Counter(c.row for c in doc.cells)
    return max(row_counts.values())


def sylk_string_value_count(file_path: "str | Path") -> int:
    """Return count of cells whose value is a string type."""
    doc = parse_sylk_strict(file_path)
    return sum(1 for c in doc.cells if isinstance(c.value, str))


def sylk_has_empty_cells(file_path: "str | Path") -> bool:
    """Return True if any cell has a None or empty-string value."""
    doc = parse_sylk_strict(file_path)
    for c in doc.cells:
        if c.value is None or (isinstance(c.value, str) and not c.value.strip()):
            return True
    return False


def sylk_total_cells(file_path: "str | Path") -> int:
    """Return the total number of cells in the SYLK document."""
    doc = parse_sylk_strict(file_path)
    return len(doc.cells)


def sylk_nonempty_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    doc = parse_sylk_strict(file_path)
    total = len(doc.cells)
    if total == 0:
        return 0.0
    nonempty = sum(
        1 for c in doc.cells
        if c.value is not None and not (isinstance(c.value, str) and not c.value.strip())
    )
    return nonempty / total


def sylk_min_row_index(file_path: "str | Path") -> int:
    """Return the minimum row index present in the document. 0 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0
    return min(c.row for c in doc.cells)


def sylk_max_row_index(file_path: "str | Path") -> int:
    """Return the maximum row index present in the document. 0 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0
    return max(c.row for c in doc.cells)


def sylk_numeric_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of numeric cells to total cells. 0.0 if no cells."""
    doc = parse_sylk_strict(file_path)
    total = len(doc.cells)
    if total == 0:
        return 0.0
    numeric = sum(1 for c in doc.cells if isinstance(c.value, (int, float)))
    return numeric / total


def sylk_value_length_sum(file_path: "str | Path") -> int:
    """Return total string length of all cell values. 0 if no cells."""
    doc = parse_sylk_strict(file_path)
    return sum(len(str(c.value)) for c in doc.cells if c.value is not None)


def sylk_avg_row_density(file_path: "str | Path") -> float:
    """Return average number of cells per row. 0.0 if no cells."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0.0
    from collections import Counter as _Counter
    row_counts = _Counter(c.row for c in doc.cells)
    return sum(row_counts.values()) / len(row_counts)
