"""sylk_metrics.py — Extracted SYLK analytics functions.

Split out of sylk_analytics.py (TC-PA-017 monolith healing) to keep each source
module under the 800-LOC architecture cap. Pure analytics functions over parsed
SYLK document models; behavior is unchanged from the original definitions. Base
parser/metric names that remain in sylk_analytics.py are brought in via the
star-import below. Re-exported from sylk_analytics.py so every public name stays
importable from its original path.
"""
from __future__ import annotations

from .sylk_analytics import *  # noqa: F401,F403 - base parser/metrics reused at call time


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


# ---------------------------------------------------------------------------
# Analytics functions for deepening tests (TC-F-012)
# ---------------------------------------------------------------------------

def sylk_column_fill_rate(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to (max_col * max_row) space. 0.0 if empty."""
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return 0.0
    max_row = max(c.row for c in doc.cells)
    max_col = max(c.col for c in doc.cells)
    capacity = max_row * max_col
    if capacity == 0:
        return 0.0
    nonempty = sum(1 for c in doc.cells if c.value is not None and str(c.value).strip())
    return float(nonempty) / capacity


def sylk_distinct_string_count(file_path: "str | Path") -> int:
    """Return count of distinct non-empty string values in the document."""
    doc = parse_sylk_strict(file_path)
    strings = set()
    for cell in doc.cells:
        if cell.value is not None:
            s = str(cell.value).strip()
            if s:
                try:
                    float(s)
                except (ValueError, TypeError):
                    strings.add(s)
    return len(strings)


def sylk_cell_text_length_sum(file_path: "str | Path") -> int:
    """Return total character length of all cell string values."""
    doc = parse_sylk_strict(file_path)
    return sum(len(str(c.value)) for c in doc.cells if c.value is not None)


def sylk_numeric_value_sum(file_path: "str | Path") -> float:
    """Return sum of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_sylk_strict(file_path)
    total = 0.0
    for cell in doc.cells:
        if isinstance(cell.value, (int, float)):
            total += float(cell.value)
        elif cell.value is not None:
            try:
                total += float(str(cell.value))
            except (ValueError, TypeError):
                pass
    return total
