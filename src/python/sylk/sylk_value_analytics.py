"""
SYLK value analytics — cell value statistics for Symbolic Link spreadsheet format.

Extends sylk_analytics.py with additional value-level analytics.
No spec_qname claim — analytics modules do not represent SYLK element types.
"""
from __future__ import annotations

from pathlib import Path

from .sylk_parser import (
    parse_sylk_strict,
)

spec_qname = "sylk:cell"
spec_fact_ref = "FACT-SYLK-001"
namespace_uri = "urn:sylk:spreadsheet"


def sylk_has_duplicate_values(file_path: "str | Path") -> bool:
    """Return True if any non-empty cell value appears more than once."""
    doc = parse_sylk_strict(file_path)
    seen: set = set()
    for cell in doc.cells:
        v = cell.value
        if v is not None and str(v).strip():
            key = str(v)
            if key in seen:
                return True
            seen.add(key)
    return False


def sylk_duplicate_value_count(file_path: "str | Path") -> int:
    """Return count of distinct values that appear more than once."""
    doc = parse_sylk_strict(file_path)
    counts: dict = {}
    for cell in doc.cells:
        v = cell.value
        if v is not None and str(v).strip():
            key = str(v)
            counts[key] = counts.get(key, 0) + 1
    return sum(1 for c in counts.values() if c > 1)


def sylk_numeric_median(file_path: "str | Path") -> float:
    """Return median of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_sylk_strict(file_path)
    nums = sorted(float(c.value) for c in doc.cells if isinstance(c.value, (int, float)))
    if not nums:
        return 0.0
    n = len(nums)
    if n % 2 == 1:
        return nums[n // 2]
    return (nums[n // 2 - 1] + nums[n // 2]) / 2.0


def sylk_has_mixed_types(file_path: "str | Path") -> bool:
    """Return True if both string and numeric cells are present in the document."""
    doc = parse_sylk_strict(file_path)
    has_str = any(isinstance(c.value, str) and c.value.strip() for c in doc.cells)
    has_num = any(isinstance(c.value, (int, float)) for c in doc.cells)
    return has_str and has_num


def sylk_string_to_numeric_ratio(file_path: "str | Path") -> float:
    """Return ratio of string cells to numeric cells. 0.0 if no numeric cells."""
    doc = parse_sylk_strict(file_path)
    str_count = sum(1 for c in doc.cells if isinstance(c.value, str) and c.value.strip())
    num_count = sum(1 for c in doc.cells if isinstance(c.value, (int, float)))
    if num_count == 0:
        return 0.0
    return str_count / num_count


def sylk_max_row_numeric_sum(file_path: "str | Path") -> float:
    """Return the maximum numeric sum among all rows. 0.0 if no numeric cells."""
    doc = parse_sylk_strict(file_path)
    row_sums: dict = {}
    for cell in doc.cells:
        if isinstance(cell.value, (int, float)):
            row_sums[cell.row] = row_sums.get(cell.row, 0.0) + float(cell.value)
    return max(row_sums.values(), default=0.0)


def sylk_min_row_numeric_sum(file_path: "str | Path") -> float:
    """Return the minimum numeric sum among rows that have at least one numeric cell."""
    doc = parse_sylk_strict(file_path)
    row_sums: dict = {}
    for cell in doc.cells:
        if isinstance(cell.value, (int, float)):
            row_sums[cell.row] = row_sums.get(cell.row, 0.0) + float(cell.value)
    return min(row_sums.values(), default=0.0)


def sylk_numeric_cells_per_row(file_path: "str | Path") -> float:
    """Return average number of numeric cells per non-empty row."""
    doc = parse_sylk_strict(file_path)
    row_num_counts: dict = {}
    for cell in doc.cells:
        if isinstance(cell.value, (int, float)):
            row_num_counts[cell.row] = row_num_counts.get(cell.row, 0) + 1
    if not row_num_counts:
        return 0.0
    return sum(row_num_counts.values()) / len(row_num_counts)


# --- Grid-level analytics (use parse_sylk probe dict) ---

def _sylk_probe(file_path: "str | Path") -> dict:
    """Return the parse_sylk probe dict for grid-level stats."""
    from .sylk_parser import parse_sylk
    return parse_sylk(file_path)


def sylk_has_data(file_path: "str | Path") -> bool:
    """Return True if the SYLK file contains at least one cell.

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        bool — True if cell_count > 0.
    """
    return _sylk_probe(file_path).get("cell_count", 0) > 0


def sylk_is_square_grid(file_path: "str | Path") -> bool:
    """Return True if the row count equals the column count.

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        bool — True if rows == cols.
    """
    probe = _sylk_probe(file_path)
    return probe.get("rows", 0) == probe.get("cols", 0)


def sylk_grid_size(file_path: "str | Path") -> int:
    """Return the total grid size as rows * cols.

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        int — rows * cols. 0 if either dimension is 0.
    """
    probe = _sylk_probe(file_path)
    return probe.get("rows", 0) * probe.get("cols", 0)


def sylk_cell_fill_ratio(file_path: "str | Path") -> float:
    """Return the ratio of actual cells to grid capacity (rows * cols).

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        float — cell_count / (rows * cols). 0.0 if grid_size is 0.
    """
    probe = _sylk_probe(file_path)
    grid = probe.get("rows", 0) * probe.get("cols", 0)
    if grid == 0:
        return 0.0
    return probe.get("cell_count", 0) / grid


def sylk_is_wide(file_path: "str | Path") -> bool:
    """Return True if the number of columns exceeds the number of rows.

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        bool — True if cols > rows.
    """
    probe = _sylk_probe(file_path)
    return probe.get("cols", 0) > probe.get("rows", 0)


def sylk_is_tall(file_path: "str | Path") -> bool:
    """Return True if the number of rows exceeds the number of columns.

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        bool — True if rows > cols.
    """
    probe = _sylk_probe(file_path)
    return probe.get("rows", 0) > probe.get("cols", 0)


def sylk_col_count(file_path: "str | Path") -> int:
    """Return the number of columns in the SYLK document.

    Spec: SYLK B;Y record column count (FACT-SYLK-001)
    """
    doc = parse_sylk_strict(file_path)
    return doc.cols


def sylk_id_line(file_path: "str | Path") -> str:
    """Return the ID line (first record) of the SYLK file.

    Spec: SYLK ID; record (FACT-SYLK-001)
    """
    doc = parse_sylk_strict(file_path)
    return doc.id_line


def sylk_all_cells_same_type(file_path: "str | Path") -> bool:
    """Return True if all cells in the SYLK document have the same value_type.

    True vacuously when there are no cells.

    Spec: SYLK C; record value type (FACT-SYLK-001)
    """
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return True
    types = {c.value_type for c in doc.cells}
    return len(types) == 1


def sylk_has_only_strings(file_path: "str | Path") -> bool:
    """Return True if all cells have value_type 'string'.

    False if no cells.

    Spec: SYLK C; record string value (FACT-SYLK-001)
    """
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return False
    return all(c.value_type == "string" for c in doc.cells)


def sylk_has_only_numeric(file_path: "str | Path") -> bool:
    """Return True if all cells have value_type 'numeric'.

    False if no cells.

    Spec: SYLK C; record numeric value (FACT-SYLK-001)
    """
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return False
    return all(c.value_type == "numeric" for c in doc.cells)


def sylk_first_cell_value(file_path: "str | Path") -> object:
    """Return the value of the first cell in row/col order. None if no cells.

    Spec: SYLK C; record value (FACT-SYLK-001)
    """
    doc = parse_sylk_strict(file_path)
    return doc.cells[0].value if doc.cells else None


def sylk_cell_count(file_path: "str | Path") -> int:
    """Return total count of cells in the SYLK document.

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        int — total cell count.
    """
    return _sylk_probe(file_path).get("cell_count", 0)


def sylk_row_count(file_path: "str | Path") -> int:
    """Return the number of rows in the SYLK document.

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        int — row count.
    """
    return _sylk_probe(file_path).get("rows", 0)


def sylk_unique_value_count(file_path: "str | Path") -> int:
    """Return count of distinct cell values (as strings) across all cells.

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        int — number of unique value strings.
    """
    doc = parse_sylk_strict(file_path)
    return len({str(c.value) for c in doc.cells if c.value is not None})


def sylk_numeric_cell_count(file_path: "str | Path") -> int:
    """Return count of cells with value_type 'numeric'.

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        int — numeric cell count.
    """
    doc = parse_sylk_strict(file_path)
    return sum(1 for c in doc.cells if c.value_type == "numeric")


def sylk_string_cell_count(file_path: "str | Path") -> int:
    """Return count of cells with value_type 'string'.

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        int — string cell count.
    """
    doc = parse_sylk_strict(file_path)
    return sum(1 for c in doc.cells if c.value_type == "string")


def sylk_last_cell_value(file_path: "str | Path") -> object:
    """Return the value of the last cell in document order. None if no cells.

    Args:
        file_path: Path to the .slk SYLK file.

    Returns:
        object — last cell value, or None.
    """
    doc = parse_sylk_strict(file_path)
    return doc.cells[-1].value if doc.cells else None
