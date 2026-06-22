"""
DIF analytics — extracted analytics/computation functions.

Separated from dif_parser.py to keep it within policy limits (800 LOC / 60 functions).
Core functions imported from dif_parser.
"""

from __future__ import annotations

import csv
import html as _html_module
import io
from pathlib import Path
from typing import Any

from .dif_parser import DifCell, DifDocument, get_column_values, parse_dif, parse_dif_strict, total_cell_count

def dif_to_csv(file_path: str | Path) -> str:
    """Export a DIF file as CSV text (RFC 4180 CRLF line endings).

    Each DIF tuple (row) becomes one CSV row. Cell values are serialized
    as strings; None becomes an empty field.

    Returns:
        CSV string with CRLF line endings (RFC 4180).

    Raises:
        DifError subclasses on parse failure.

    Added in R84 Train N.
    """
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return ""

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\r\n")
    for row in doc.rows:
        csv_row = []
        for cell in row:
            if cell.value is None:
                csv_row.append("")
            elif cell.value_type == "numeric":
                # Format integers without trailing .0 when possible
                val = cell.value
                if isinstance(val, float) and val == int(val):
                    csv_row.append(str(int(val)))
                else:
                    csv_row.append(str(val))
            else:
                csv_row.append(str(cell.value))
        writer.writerow(csv_row)
    return buf.getvalue()

def add_row(doc: DifDocument, values: list[Any]) -> dict[str, Any]:
    """Append a row of values to a DifDocument (in-memory).

    Args:
        doc: DifDocument to modify.
        values: List of cell values for the new row.

    Returns:
        Result dict with success, row_index, cell_count.
    """
    cells = []
    for val in values:
        if isinstance(val, (int, float)):
            cells.append(DifCell(value=val, value_type="numeric"))
        else:
            cells.append(DifCell(value=val, value_type="string"))
    doc.rows.append(cells)
    doc.tuples = len(doc.rows)
    if len(values) > doc.vectors:
        doc.vectors = len(values)
    return {"success": True, "row_index": len(doc.rows), "cell_count": len(values)}

def delete_row(doc: DifDocument, row: int) -> dict[str, Any]:
    """Delete a row (1-based) from a DifDocument (in-memory).

    Args:
        doc: DifDocument to modify.
        row: 1-based row index to delete.

    Returns:
        Result dict with success, deleted_count.
    """
    idx = row - 1
    if idx < 0 or idx >= len(doc.rows):
        return {"success": False, "deleted_count": 0, "error": f"Row {row} out of range"}
    deleted = doc.rows.pop(idx)
    doc.tuples = len(doc.rows)
    return {"success": True, "deleted_count": len(deleted)}

# Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
# Queue: broad-accel-q-006

def export_to_html(file_path: "str | Path") -> str:
    """Export DIF spreadsheet data as an HTML table string.

    Args:
        file_path: Path to the DIF file.

    Returns:
        HTML string containing a <table> element with the data.
        Empty cells are rendered as empty <td> elements.
    """
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return "<table></table>"

    lines = ["<table>"]
    for row in doc.rows:
        lines.append("  <tr>")
        for cell in row:
            val = "" if cell is None or cell.value is None else str(cell.value)
            lines.append(f"    <td>{_html_module.escape(val)}</td>")
        lines.append("  </tr>")
    lines.append("</table>")
    return "\n".join(lines)


def sum_row(file_path: str | Path, row: int) -> float:
    """Return the sum of numeric values in a row.

    Args:
        file_path: Path to a DIF file.
        row: 0-based row index.

    Returns:
        Sum of numeric values in the row. Returns 0.0 if row out of range
        or no numeric values found.
    """
    doc = parse_dif_strict(file_path)
    if row < 0 or row >= len(doc.rows):
        return 0.0
    total = 0.0
    for cell in doc.rows[row]:
        val = cell.value
        if isinstance(val, (int, float)):
            total += val
    return total


# FORMAT_FACTORY_EXECUTION: taskcard=PD-Q-002; method=QUEUE_DISPATCHED_EXECUTION; queue_item=pdrnext-q-002
def filter_rows_by_value(data, col, value):
    """Filter rows in a DIF data model by matching a column value.

    Args:
        data: DIF data dict (output of parse_dif). Must have a 'data' key
              containing a list of rows, where each row is a list of cell values.
        col: Zero-based column index to filter on.
        value: Value to match (equality check, case-sensitive for strings).

    Returns:
        List of rows (each a list of cell values) where data[row][col] == value.
        Returns empty list if no rows match or col is out of range.
    """
    rows = data.get("data", [])
    result = []
    for row in rows:
        if not isinstance(row, list):
            continue
        if col < 0 or col >= len(row):
            continue
        if row[col] == value:
            result.append(row)
    return result


def sort_rows_by_column(
    file_path: "str | Path",
    col: int,
    reverse: bool = False,
) -> "DifDocument":
    """Sort rows in a DIF document by the values in a given column.

    Args:
        file_path: Path to the DIF file.
        col: Zero-based column index to sort by.
        reverse: If True, sort in descending order.

    Returns:
        A new DifDocument with rows sorted by the specified column.
        Rows where col is out-of-range are placed at the end.
    """
    doc = parse_dif_strict(file_path)

    def sort_key(row: "list[DifCell]") -> "tuple":
        if col < 0 or col >= len(row):
            return (1, 0, "")
        v = row[col].value
        if isinstance(v, (int, float)):
            return (0, v, "")
        return (0, 0, str(v) if v is not None else "")

    sorted_rows = sorted(doc.rows, key=sort_key, reverse=reverse)
    new_doc = DifDocument(
        title=doc.title,
        vectors=doc.vectors,
        tuples=doc.tuples,
        rows=sorted_rows,
    )
    return new_doc


def get_row_as_dict(doc: "DifDocument", row_idx: int) -> dict:
    """Return a row from a DifDocument as a dict with column indices as keys.

    Args:
        doc: A DifDocument (from parse_dif_strict).
        row_idx: Zero-based row index.

    Returns:
        Dict mapping column index (int) to cell value, or {} if out of range.
    """
    if row_idx < 0 or row_idx >= len(doc.rows):
        return {}
    return {i: cell.value for i, cell in enumerate(doc.rows[row_idx])}


def get_vector_count(file_path: str | Path) -> int:
    """Return the number of vectors (columns) declared in a DIF file header.

    Args:
        file_path: Path to DIF file.

    Returns:
        Integer vector count from the DIF TABLE header (number of columns).

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    return doc.vectors


def get_header_info(file_path: str | Path) -> dict[str, Any]:
    """Return header metadata from a DIF file as a single convenience dict.

    Args:
        file_path: Path to DIF file.

    Returns:
        Dict with keys: title, vectors, tuples, row_count.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    return {
        "title": doc.title,
        "vectors": doc.vectors,
        "tuples": doc.tuples,
        "row_count": len(doc.rows),
    }


def count_distinct_values(file_path: str | Path, col: int) -> int:
    """Count distinct non-empty values in a column (0-based).

    Empty strings and None values are excluded from the count.

    Args:
        file_path: Path to DIF file.
        col: 0-based column index.

    Returns:
        Integer count of distinct non-empty values.

    Raises:
        DifError subclasses on parse failure.
    """
    values = get_column_values(file_path, col=col)
    distinct: set[Any] = set()
    for v in values:
        if v is not None and v != "":
            distinct.add(v)
    return len(distinct)


def dif_nonempty_row_count(file_path: str | Path) -> int:
    """Return the count of rows that contain at least one non-empty cell.

    Args:
        file_path: Path to DIF file.

    Returns:
        Integer count of rows with at least one non-None, non-empty-string value.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    count = 0
    for row in doc.rows:
        for cell in row:
            val = cell.value if hasattr(cell, "value") else cell
            if val is not None and str(val).strip() != "":
                count += 1
                break
    return count


def dif_max_row_length(file_path: "str | Path") -> int:
    """Return the maximum number of cells in any single row of the DIF file.

    Args:
        file_path: Path to DIF file.

    Returns:
        Integer maximum row length. Returns 0 if the file has no rows.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return 0
    return max(len(row) for row in doc.rows)


def dif_string_row_count(file_path: "str | Path") -> int:
    """Return the count of rows containing at least one string cell value.

    Args:
        file_path: Path to DIF file.

    Returns:
        Integer count of rows with at least one string value. Returns 0 if no
        such rows exist.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    count = 0
    for row in doc.rows:
        if any(isinstance(cell.value, str) for cell in row):
            count += 1
    return count


def dif_column_unique_count(file_path: "str | Path", col_idx: int) -> int:
    """Return the count of unique non-None values in a specific column (0-based).

    Args:
        file_path: Path to a DIF file.
        col_idx: 0-based column index.

    Returns:
        Integer count of distinct non-None values in the column.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    values = set()
    for row in doc.rows:
        if col_idx < len(row):
            v = row[col_idx].value
            if v is not None:
                values.add(str(v))
    return len(values)


def dif_vectors_count(file_path: "str | Path") -> int:
    """Return the number of vectors (columns) declared in a DIF file.

    Args:
        file_path: Path to a DIF file.

    Returns:
        Integer vector count from the DIF header. Returns 0 if header is absent.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    return doc.vectors


def dif_numeric_cell_count(file_path: "str | Path") -> int:
    """Return the count of numeric cells in a DIF file.

    Counts all cells whose value_type is 'numeric' across all rows.

    Args:
        file_path: Path to a DIF file.

    Returns:
        Integer count of numeric cells.
    """
    doc = parse_dif_strict(file_path)
    return sum(
        1 for row in doc.rows for cell in row if cell.value_type == "numeric"
    )


def dif_total_cell_count(file_path: "str | Path") -> int:
    """Return the total number of cells across all rows in a DIF file.

    Args:
        file_path: Path to a DIF file.

    Returns:
        Integer total cell count.
    """
    doc = parse_dif_strict(file_path)
    return sum(len(row) for row in doc.rows)


def dif_column_types(file_path: "str | Path") -> list[str]:
    """Infer the dominant data type for each column.

    For each column index, counts how many cells are 'numeric', 'string',
    or 'special', and returns the type with the highest count. Empty
    columns return 'empty'. Ties are broken as numeric > string > special.

    Args:
        file_path: Path to a DIF file.

    Returns:
        List of type strings, one per column. Possible values:
        'numeric', 'string', 'special', 'empty'.
    """
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return []
    max_cols = max(len(row) for row in doc.rows) if doc.rows else 0
    result: list[str] = []
    for col_idx in range(max_cols):
        counts: dict[str, int] = {"numeric": 0, "string": 0, "special": 0}
        for row in doc.rows:
            if col_idx < len(row):
                vt = row[col_idx].value_type
                if vt in counts:
                    counts[vt] += 1
        total = sum(counts.values())
        if total == 0:
            result.append("empty")
        elif counts["numeric"] >= counts["string"] and counts["numeric"] >= counts["special"]:
            result.append("numeric")
        elif counts["string"] >= counts["special"]:
            result.append("string")
        else:
            result.append("special")
    return result


def dif_row_value_counts(file_path: "str | Path") -> list[int]:
    """Return the count of non-empty cells per row.

    Args:
        file_path: Path to a DIF file.

    Returns:
        List of integers, one per row, counting cells with non-None values.
    """
    doc = parse_dif_strict(file_path)
    return [sum(1 for cell in row if cell.value is not None) for row in doc.rows]


def dif_empty_cell_count(file_path: "str | Path") -> int:
    """Return the count of cells with None value across all rows.

    Args:
        file_path: Path to a DIF file.

    Returns:
        Integer count of empty (None-valued) cells.
    """
    doc = parse_dif_strict(file_path)
    return sum(1 for row in doc.rows for cell in row if cell.value is None)


def dif_has_header(file_path: "str | Path") -> bool:
    """Heuristic: detect if the first row of a DIF file is a header.

    A row is considered a header if it has at least one cell and all
    cells are of type 'string'.

    Args:
        file_path: Path to a DIF file.

    Returns:
        True if the first row appears to be a header, False otherwise.
    """
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return False
    first_row = doc.rows[0]
    if not first_row:
        return False
    return all(cell.value_type == "string" for cell in first_row)


def dif_row_count(file_path: "str | Path") -> int:
    """Return the number of data rows in a DIF file."""
    doc = parse_dif_strict(file_path)
    return len(doc.rows)


def dif_column_count(file_path: "str | Path") -> int:
    """Return the number of columns (max row width) in a DIF file. 0 if no rows."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return 0
    return max(len(row) for row in doc.rows)


def dif_string_density(file_path: "str | Path") -> float:
    """Return the fraction of cells that are string type.

    Args:
        file_path: Path to a DIF file.

    Returns:
        Float in [0.0, 1.0]. 0.0 if no cells.
    """
    doc = parse_dif_strict(file_path)
    total = 0
    string_count = 0
    for row in doc.rows:
        for cell in row:
            total += 1
            if cell.value_type == "string":
                string_count += 1
    if total == 0:
        return 0.0
    return string_count / total


def dif_max_cell_length(file_path: "str | Path") -> int:
    """Return the length of the longest cell value in a DIF file.

    Args:
        file_path: Path to a DIF file.

    Returns:
        Integer max length. 0 if no cells.
    """
    doc = parse_dif_strict(file_path)
    max_len = 0
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            max_len = max(max_len, len(str(val)))
    return max_len


def dif_has_empty_cells(file_path: "str | Path") -> bool:
    """Return True if any cell has an empty or None value."""
    doc = parse_dif_strict(file_path)
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            if str(val).strip() == "":
                return True
    return False


def dif_avg_row_length(file_path: "str | Path") -> float:
    """Return the average number of cells per row.

    Args:
        file_path: Path to a DIF file.

    Returns:
        Float average cells per row, or 0.0 if no rows.
    """
    doc = parse_dif_strict(file_path)
    rows = doc.rows
    if not rows:
        return 0.0
    total = sum(len(row) for row in rows)
    return total / len(rows)


def dif_all_numeric(file_path: "str | Path") -> bool:
    """Return True if all non-empty cells contain numeric values.

    Args:
        file_path: Path to a DIF file.

    Returns:
        True if every non-empty cell value is numeric; False otherwise.
        Returns True for files with no non-empty cells (vacuously true).
    """
    doc = parse_dif_strict(file_path)
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            s = str(val).strip()
            if not s:
                continue
            try:
                float(s)
            except (ValueError, TypeError):
                return False
    return True


def dif_all_numeric_column(file_path: "str | Path", col_index: int = 0) -> bool:
    """Return True if all non-empty cells in a specific column are numeric.

    Args:
        file_path: Path to a DIF file.
        col_index: Zero-based column index to check.

    Returns:
        True if every non-empty cell in the column is numeric; False otherwise.
        Returns True if the column has no non-empty cells (vacuously true).
    """
    doc = parse_dif_strict(file_path)
    for row in doc.rows:
        if col_index >= len(row):
            continue
        cell = row[col_index]
        val = cell.value if cell.value is not None else ""
        s = str(val).strip()
        if not s:
            continue
        try:
            float(s)
        except (ValueError, TypeError):
            return False
    return True


def dif_numeric_density(file_path: "str | Path") -> float:
    """Return the ratio of numeric cells to total cells. 0.0 if no cells."""
    total = dif_total_cell_count(file_path)
    if total == 0:
        return 0.0
    numeric = dif_numeric_cell_count(file_path)
    return numeric / total


def dif_min_cell_length(file_path: "str | Path") -> int:
    """Return the length of the shortest non-empty cell value. 0 if no data."""
    doc = parse_dif_strict(file_path)
    min_len = None
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            s = str(val).strip()
            if s:
                if min_len is None or len(s) < min_len:
                    min_len = len(s)
    return min_len if min_len is not None else 0


def dif_has_string_cells(file_path: "str | Path") -> bool:
    """Return True if any cell contains a string value.

    Args:
        file_path: Path to a DIF file.

    Returns:
        True if at least one cell has a non-empty string value.
    """
    doc = parse_dif_strict(file_path)
    for row in doc.rows:
        for cell in row:
            if isinstance(cell.value, str) and cell.value.strip():
                return True
    return False


def dif_max_numeric_value(file_path: "str | Path"):
    """Return the maximum numeric cell value, or None if no numeric cells.

    Args:
        file_path: Path to a DIF file.

    Returns:
        Maximum float value across all numeric cells, or None.
    """
    doc = parse_dif_strict(file_path)
    nums = [cell.value for row in doc.rows for cell in row if isinstance(cell.value, float)]
    return max(nums) if nums else None


def dif_min_numeric_value(file_path: "str | Path"):
    """Return the minimum numeric cell value, or None if no numeric cells."""
    doc = parse_dif_strict(file_path)
    nums = [cell.value for row in doc.rows for cell in row if isinstance(cell.value, float)]
    return min(nums) if nums else None


def dif_is_rectangular(file_path: "str | Path") -> bool:
    """Return True if all rows have the same number of cells."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return True
    first_len = len(doc.rows[0])
    return all(len(row) == first_len for row in doc.rows)


def dif_data_density(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    total = dif_total_cell_count(file_path)
    if total == 0:
        return 0.0
    empty = dif_empty_cell_count(file_path)
    return (total - empty) / total


def dif_avg_cell_length(file_path: "str | Path") -> float:
    """Return the average string length of all cell values. 0.0 if no cells."""
    doc = parse_dif_strict(file_path)
    lengths = []
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            lengths.append(len(str(val)))
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def dif_is_single_column(file_path: "str | Path") -> bool:
    """Return True if the DIF file has exactly one column."""
    return dif_column_count(file_path) == 1


def dif_max_string_length(file_path: "str | Path") -> int:
    """Return the maximum length of any string cell value. 0 if no string cells."""
    doc = parse_dif_strict(file_path)
    lengths = [
        len(str(cell.value))
        for row in doc.rows
        for cell in row
        if isinstance(cell.value, str)
    ]
    return max(lengths) if lengths else 0


def dif_col_count_variance(file_path: "str | Path") -> float:
    """Return variance of column counts per row. 0.0 if fewer than 2 rows."""
    doc = parse_dif_strict(file_path)
    if len(doc.rows) < 2:
        return 0.0
    counts = [len(row) for row in doc.rows]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def dif_numeric_mean(file_path: "str | Path") -> float:
    """Return mean of all numeric cell values. 0.0 if none."""
    doc = parse_dif_strict(file_path)
    nums = []
    for row in doc.rows:
        for cell in row:
            if isinstance(cell.value, (int, float)):
                nums.append(float(cell.value))
    if not nums:
        return 0.0
    return sum(nums) / len(nums)


def dif_is_empty(file_path: "str | Path") -> bool:
    """Return True if the DIF document has no data rows."""
    doc = parse_dif_strict(file_path)
    return len(doc.rows) == 0


def dif_unique_value_count(file_path: "str | Path") -> int:
    """Return total number of unique cell values across all rows."""
    doc = parse_dif_strict(file_path)
    values = set()
    for row in doc.rows:
        for cell in row:
            if cell.value is not None:
                values.add(str(cell.value))
    return len(values)


def dif_tuple_count(file_path: "str | Path") -> int:
    """Return the TUPLES dimension from the DIF header (declared row count)."""
    result = parse_dif(file_path)
    return result.get("tuples", 0)


def dif_is_multi_vector(file_path: "str | Path") -> bool:
    """Return True if the DIF file has more than one vector (column)."""
    result = parse_dif(file_path)
    return result.get("vectors", 0) > 1


def dif_is_single_vector(file_path: "str | Path") -> bool:
    """Return True if the DIF file has exactly one vector (column)."""
    result = parse_dif(file_path)
    return result.get("vectors", 0) == 1


def dif_vector_length_variance(file_path: "str | Path") -> float:
    """Return variance of cell counts per row. 0.0 if fewer than 2 rows."""
    doc = parse_dif_strict(file_path)
    if len(doc.rows) < 2:
        return 0.0
    counts = [len(row) for row in doc.rows]
    mean = sum(counts) / len(counts)
    return sum((c - mean) ** 2 for c in counts) / len(counts)


def dif_is_all_string(file_path: "str | Path") -> bool:
    """Return True if all non-empty cells contain string (non-numeric) values."""
    doc = parse_dif_strict(file_path)
    has_data = False
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            s = str(val).strip()
            if not s:
                continue
            has_data = True
            try:
                float(s)
                return False
            except (ValueError, TypeError):
                pass
    return has_data


def dif_nonempty_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    total = dif_total_cell_count(file_path)
    if total == 0:
        return 0.0
    nonempty = 0
    doc = parse_dif_strict(file_path)
    for row in doc.rows:
        for cell in row:
            val = cell.value if cell.value is not None else ""
            if str(val).strip():
                nonempty += 1
    return nonempty / total


def dif_avg_numeric_value(file_path: "str | Path") -> float:
    """Return average of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_dif_strict(file_path)
    nums = []
    for row in doc.rows:
        for cell in row:
            if cell.value is not None:
                try:
                    nums.append(float(str(cell.value)))
                except (ValueError, TypeError):
                    pass
    if not nums:
        return 0.0
    return sum(nums) / len(nums)


def dif_row_length_variance(file_path: "str | Path") -> float:
    """Return variance of row lengths. 0.0 if fewer than 2 rows."""
    doc = parse_dif_strict(file_path)
    if len(doc.rows) < 2:
        return 0.0
    lengths = [len(row) for row in doc.rows]
    mean = sum(lengths) / len(lengths)
    return sum((l - mean) ** 2 for l in lengths) / len(lengths)


def dif_numeric_sum(file_path: "str | Path") -> float:
    """Return sum of all numeric cell values. 0.0 if no numeric cells."""
    doc = parse_dif_strict(file_path)
    total = 0.0
    for row in doc.rows:
        for cell in row:
            if cell.value is not None:
                try:
                    total += float(str(cell.value))
                except (ValueError, TypeError):
                    pass
    return total


def dif_is_single_row(file_path: "str | Path") -> bool:
    """Return True if the document has exactly one data row."""
    doc = parse_dif_strict(file_path)
    return len(doc.rows) == 1


def dif_empty_column_count(file_path: "str | Path") -> int:
    """Return number of columns that are entirely empty across all rows."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return 0
    col_count = max(len(row) for row in doc.rows)
    empty_cols = 0
    for ci in range(col_count):
        if all(
            ci >= len(row) or row[ci].value is None or str(row[ci].value).strip() == ""
            for row in doc.rows
        ):
            empty_cols += 1
    return empty_cols


def dif_longest_row_index(file_path: "str | Path") -> int:
    """Return 0-based index of the row with the most cells. -1 if no rows."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return -1
    return max(range(len(doc.rows)), key=lambda i: len(doc.rows[i]))


def dif_total_string_length(file_path: "str | Path") -> int:
    """Return total character count of all string cell values combined."""
    doc = parse_dif_strict(file_path)
    total = 0
    for row in doc.rows:
        for cell in row:
            if cell.value is not None:
                total += len(str(cell.value))
    return total


def dif_nonempty_row_ratio(file_path: "str | Path") -> float:
    """Return ratio of non-empty rows to total rows. 0.0 if no rows."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return 0.0
    nonempty = sum(
        1 for row in doc.rows
        if any(cell.value is not None and str(cell.value).strip() for cell in row)
    )
    return nonempty / len(doc.rows)


def dif_numeric_cell_count(file_path: "str | Path") -> int:
    """Return the count of cells with numeric values."""
    doc = parse_dif_strict(file_path)
    return sum(
        1 for row in doc.rows for cell in row
        if cell.value_type == "numeric"
    )


def dif_has_string_cells(file_path: "str | Path") -> bool:
    """Return True if any cell has value_type 'string'."""
    doc = parse_dif_strict(file_path)
    return any(
        cell.value_type == "string"
        for row in doc.rows for cell in row
    )


def dif_avg_cell_length_variance(file_path: "str | Path") -> float:
    """Return variance of cell value string lengths. 0.0 if fewer than 2 cells."""
    doc = parse_dif_strict(file_path)
    lengths = []
    for row in doc.rows:
        for cell in row:
            if cell.value is not None:
                lengths.append(len(str(cell.value)))
    if len(lengths) < 2:
        return 0.0
    mean = sum(lengths) / len(lengths)
    return sum((l - mean) ** 2 for l in lengths) / len(lengths)


def dif_column_density(file_path: "str | Path") -> float:
    """Return ratio of non-empty columns to total columns. 0.0 if no columns."""
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return 0.0
    max_cols = max(len(row) for row in doc.rows) if doc.rows else 0
    if max_cols == 0:
        return 0.0
    nonempty_cols = 0
    for c in range(max_cols):
        for row in doc.rows:
            if c < len(row) and row[c].value is not None and str(row[c].value).strip():
                nonempty_cols += 1
                break
    return nonempty_cols / max_cols


def dif_string_value_count(file_path: "str | Path") -> int:
    """Return count of cells with string-type values."""
    doc = parse_dif_strict(file_path)
    return sum(
        1 for row in doc.rows for cell in row
        if cell.value_type == "string"
    )


def dif_max_numeric_length(file_path: "str | Path") -> int:
    """Return max string length of any numeric cell value. 0 if no numeric cells."""
    doc = parse_dif_strict(file_path)
    max_len = 0
    for row in doc.rows:
        for cell in row:
            if cell.value_type == "numeric" and cell.value is not None:
                l = len(str(cell.value))
                if l > max_len:
                    max_len = l
    return max_len


def dif_value_type_variance(file_path: "str | Path") -> float:
    """Return variance of numeric vs string cell counts per row. 0.0 if fewer than 2 rows."""
    doc = parse_dif_strict(file_path)
    if len(doc.rows) < 2:
        return 0.0
    numeric_counts = []
    for row in doc.rows:
        nc = sum(1 for cell in row if cell.value_type == "numeric")
        numeric_counts.append(nc)
    mean = sum(numeric_counts) / len(numeric_counts)
    return sum((n - mean) ** 2 for n in numeric_counts) / len(numeric_counts)


def dif_total_cell_length(file_path: "str | Path") -> int:
    """Return total string length of all cell values. 0 if no cells."""
    doc = parse_dif_strict(file_path)
    return sum(
        len(str(cell.value)) for row in doc.rows for cell in row
        if cell.value is not None
    )
