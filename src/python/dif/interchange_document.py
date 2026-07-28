"""
DIF analytics — extracted analytics/computation functions.

Separated from dif_parser.py to keep it within policy limits (800 LOC / 60 functions).
Core functions imported from dif_parser.
"""

from __future__ import annotations


spec_qname = "dif:data"
spec_fact_ref = "SAL-DIF-00001"
namespace_uri = "urn:dif:data-interchange-format"

import html as _html_module
from pathlib import Path
from typing import Any

from .dif_parser import DifCell, DifDocument, get_column_values, parse_dif, parse_dif_strict

# dogfood_status: IMPLEMENTED — DIF→CSV uses FF csv_writer.write_csv (add-dogfood-export 2026-06-22)
try:
    from ff_csv.csv_writer import write_csv as _ff_write_csv
except ModuleNotFoundError:  # Repository-root imports before package installation.
    from src.python.ff_csv.csv_writer import write_csv as _ff_write_csv


def dif_to_csv(file_path: str | Path) -> str:
    """Export a DIF file as CSV using FF csv_writer.write_csv (dogfood export).

    dogfood_backend: src/python/ff_csv/csv_writer.py::write_csv
    dogfood_status: IMPLEMENTED
    """
    doc = parse_dif_strict(file_path)
    if not doc.rows:
        return ""
    output_rows: list[list[str | None]] = []
    for row in doc.rows:
        csv_row: list[str | None] = []
        for cell in row:
            if cell.value is None:
                csv_row.append(None)
            elif cell.value_type == "numeric":
                val = cell.value
                csv_row.append(str(int(val)) if isinstance(val, float) and val == int(val) else str(val))
            else:
                csv_row.append(str(cell.value))
        output_rows.append(csv_row)
    return _ff_write_csv(output_rows)

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
        """Return a sort tuple for the row based on the target column value."""
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


from .dif_interchange_analytics import *  # noqa: F401, F403
