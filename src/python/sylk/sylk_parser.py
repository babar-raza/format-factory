"""
sylk_parser.py — SYLK (Symbolic Link) parser for format-factory-sylk.

Public API:
  parse_sylk(file_path)        — returns result dict (never raises)
  parse_sylk_strict(file_path) — raises SylkError on failure
  probe_sylk(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype + Gate 5 neutral model.
Parses SYLK files: ID record, C records (cells with X/Y/K fields), E record.
Technology: Python stdlib only (open/read/split).

License: Apache-2.0
spec_concept: SYLK symbolic link B-record cell (row/col/value)
"""

from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar


MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_ROWS = 1_048_576
MAX_COLUMNS = 16_384


class SylkError(Exception):
    """Base exception for SYLK parser errors."""


class SylkInvalidFormatError(SylkError):
    """Raised when file does not start with ID record."""


class SylkSizeError(SylkError):
    """Raised when file size or dimensions exceed limits."""


class SylkParseError(SylkError):
    """Raised when record parsing fails."""


@dataclass
class SylkCell:
    spec_qname: ClassVar[str] = "slk:cell"
    row: int = 1
    col: int = 1
    value: Any = None
    value_type: str = "empty"  # "numeric", "string", "empty"


@dataclass
class SylkDocument:
    spec_qname: ClassVar[str] = "sylk:document"
    cells: list[SylkCell] = field(default_factory=list)
    rows: int = 0
    cols: int = 0
    path: str = ""
    id_line: str = ""


def parse_sylk_strict(file_path: str | Path) -> SylkDocument:
    """Parse a SYLK file, raising SylkError on any problem."""
    path = Path(file_path)
    if not path.exists():
        raise SylkError(f"File not found: {path}")

    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise SylkSizeError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")

    raw = path.read_text(encoding="ascii", errors="replace")
    lines = raw.strip().split("\n")
    lines = [line.strip("\r") for line in lines]

    if not lines:
        raise SylkInvalidFormatError("Empty file")

    # First record must be ID
    if not lines[0].startswith("ID"):
        raise SylkInvalidFormatError(
            f"Missing ID record: first line is '{lines[0][:40]}'"
        )

    id_line = lines[0]
    cells: list[SylkCell] = []
    current_x = 1
    current_y = 1
    max_row = 0
    max_col = 0
    found_end = False

    for i, line in enumerate(lines[1:], start=2):
        if not line:
            continue

        record_type = line[0] if line else ""

        if line == "E":
            found_end = True
            break

        if record_type == "C":
            # Parse C record: C;X<col>;Y<row>;K<value>
            parts = line.split(";")
            x = current_x
            y = current_y
            value: Any = None
            value_type = "empty"

            for part in parts[1:]:
                if part.startswith("X"):
                    try:
                        x = int(part[1:])
                    except ValueError as exc:
                        raise SylkParseError(
                            f"Line {i}: invalid X field: {part}"
                        ) from exc
                elif part.startswith("Y"):
                    try:
                        y = int(part[1:])
                    except ValueError as exc:
                        raise SylkParseError(
                            f"Line {i}: invalid Y field: {part}"
                        ) from exc
                elif part.startswith("K"):
                    raw_val = part[1:]
                    if raw_val.startswith('"') and raw_val.endswith('"'):
                        value = raw_val[1:-1]
                        value_type = "string"
                    else:
                        try:
                            value = int(raw_val)
                        except ValueError:
                            try:
                                value = float(raw_val)
                            except ValueError:
                                value = raw_val
                        value_type = "numeric"

            if x > MAX_COLUMNS:
                raise SylkSizeError(f"Column {x} exceeds limit of {MAX_COLUMNS}")
            if y > MAX_ROWS:
                raise SylkSizeError(f"Row {y} exceeds limit of {MAX_ROWS}")

            current_x = x
            current_y = y
            max_row = max(max_row, y)
            max_col = max(max_col, x)

            cells.append(SylkCell(row=y, col=x, value=value, value_type=value_type))

        # Skip F, B, and other record types for now (unsupported)

    if not found_end:
        raise SylkParseError("Missing E (end) record")

    return SylkDocument(
        cells=cells,
        rows=max_row,
        cols=max_col,
        path=str(path),
        id_line=id_line,
    )


def parse_sylk(file_path: str | Path) -> dict[str, Any]:
    """Parse a SYLK file, returning a result dict (never raises)."""
    try:
        doc = parse_sylk_strict(file_path)
        return {
            "ok": True,
            "path": doc.path,
            "rows": doc.rows,
            "cols": doc.cols,
            "cell_count": len(doc.cells),
            "id_line": doc.id_line,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


def probe_sylk(file_path: str | Path) -> dict[str, Any]:
    """Probe a SYLK file for header metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        raw = path.read_bytes()[:1024].decode("ascii", errors="replace")
        lines = raw.strip().split("\n")
        if not lines or not lines[0].startswith("ID"):
            result["valid_header"] = False
            result["error"] = f"Missing ID record: {lines[0][:40] if lines else 'empty'}"
            return result
        result["valid_header"] = True
        result["id_line"] = lines[0].strip("\r")
    except Exception as exc:
        result["valid_header"] = False
        result["error"] = str(exc)
    return result


# ---------------------------------------------------------------------------
# Gate 5 — Neutral model: capability declaration
# ---------------------------------------------------------------------------

SUPPORTED_FEATURES: frozenset[str] = frozenset({
    "id_record_parse",
    "c_record_parse",
    "numeric_cell_values",
    "string_cell_values",
    "probe",
    "dimension_extraction",
    "size_guard",
    "end_record_validation",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "f_record_formatting",
    "b_record_bounds",
    "p_record_format_definitions",
    "formula_cells",
    "date_values",
    "encoding_to_sylk",
    "multi_sheet",
    "cell_references",
    "named_ranges",
    "streaming_parse",
})


def get_capabilities() -> dict[str, Any]:
    """Return a capability descriptor for the SYLK parser (Gate 5 neutral model)."""
    return {
        "format": "sylk",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
    }


# ---------------------------------------------------------------------------
# R84 Train N: SYLK CSV export
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# R93 Train P: SYLK write capability
# ---------------------------------------------------------------------------

def write_sylk(doc: SylkDocument, file_path: str | Path) -> None:
    """Write a SylkDocument to a SYLK file.

    Writes an ID header, one C record per non-empty cell, and an E footer.
    String values are quoted; numeric values are written as-is.
    Rows and columns are 1-based (as required by the SYLK spec).

    Args:
        doc: A SylkDocument to serialize.
        file_path: Destination file path.

    Raises:
        SylkError: If file_path is invalid or write fails.

    Added in R93 Train P.
    """
    path = Path(file_path)
    lines: list[str] = ["ID;P"]
    for cell in doc.cells:
        if cell.value is None:
            continue
        x = cell.col
        y = cell.row
        if cell.value_type == "string":
            k = f'"{cell.value}"'
        else:
            k = str(cell.value)
        lines.append(f"C;X{x};Y{y};K{k}")
    lines.append("E")
    try:
        path.write_bytes(("\r\n".join(lines) + "\r\n").encode("ascii"))
    except Exception as exc:
        raise SylkError(f"Failed to write SYLK file: {exc}") from exc


def sylk_to_csv(file_path: str | Path) -> str:
    """Export a SYLK file as CSV text (RFC 4180 CRLF line endings).

    Builds a 2D grid from the cell coordinates (1-based row/col), then
    serializes every row as a CSV line. Empty cells produce empty fields.

    Returns:
        CSV string with CRLF line endings (RFC 4180).

    Raises:
        SylkError subclasses on parse failure.

    Added in R84 Train N.
    """
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return ""

    # Build a grid: row_idx (0-based) -> col_idx (0-based) -> value
    grid: dict[int, dict[int, Any]] = {}
    for cell in doc.cells:
        r = cell.row - 1  # convert 1-based to 0-based
        c = cell.col - 1
        if r not in grid:
            grid[r] = {}
        grid[r][c] = cell.value if cell.value is not None else ""

    max_row = doc.rows
    max_col = doc.cols
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\r\n")
    for r in range(max_row):
        row_data = grid.get(r, {})
        row = [row_data.get(c, "") for c in range(max_col)]
        writer.writerow(row)
    return buf.getvalue()


def get_cell_value(file_path: str | Path, row: int, col: int) -> Any:
    """Return the value at (row, col) in a SYLK file (1-based coordinates).

    Returns None if the cell is empty or the coordinates are out of range.

    Args:
        file_path: Path to SYLK file.
        row:       1-based row index.
        col:       1-based column index.

    Returns:
        Cell value (numeric, str, or None for empty/missing).

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    for cell in doc.cells:
        if cell.row == row and cell.col == col:
            return cell.value
    return None


def get_row_values(file_path: str | Path, row: int) -> list[Any]:
    """Return all cell values for a given row (1-based) as a list.

    Values are ordered by column index. Empty cells within the row range
    are represented as None. Returns an empty list if the row has no cells.

    Args:
        file_path: Path to SYLK file.
        row:       1-based row index.

    Returns:
        List of cell values in column order. Empty cells are None.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    row_cells = [c for c in doc.cells if c.row == row]
    if not row_cells:
        return []
    max_col = max(c.col for c in row_cells)
    result: list[Any] = [None] * max_col
    for cell in row_cells:
        result[cell.col - 1] = cell.value
    return result


def get_row_count(file_path: str | Path) -> int:
    """Return the number of rows in a SYLK file.

    The row count is the maximum row index found among all cells.

    Args:
        file_path: Path to SYLK file.

    Returns:
        Integer row count.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    return doc.rows


def get_column_count(file_path: str | Path) -> int:
    """Return the number of columns in a SYLK file.

    The column count is the maximum column index found among all cells.

    Args:
        file_path: Path to SYLK file.

    Returns:
        Integer column count.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    return doc.cols


def get_cell_count(file_path: str | Path) -> int:
    """Return the number of non-empty cells in a SYLK file.

    Args:
        file_path: Path to SYLK file.

    Returns:
        Integer count of cells with non-None values.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    return sum(1 for c in doc.cells if c.value is not None)


def get_all_values(file_path: str | Path) -> list[Any]:
    """Return a flat list of all cell values in a SYLK file."""
    doc = parse_sylk_strict(file_path)
    return [c.value for c in doc.cells]


def set_cell_value(
    file_path: str | Path,
    dest_path: str | Path,
    row: int,
    col: int,
    value: Any,
    value_type: str = "string",
) -> dict[str, Any]:
    """Set a cell value in a SYLK file and write the result.

    Parses the source file, modifies the cell at (row, col) (1-based),
    and writes the updated document to dest_path.

    Args:
        file_path:  Source SYLK file path.
        dest_path:  Destination file path.
        row:        1-based row index.
        col:        1-based column index.
        value:      New cell value.
        value_type: One of "numeric", "string".

    Returns:
        Dict with ok, row, col, old_value, new_value keys.

    Raises:
        SylkError on parse failure or invalid coordinates.
    """
    doc = parse_sylk_strict(file_path)
    if row < 1:
        raise SylkError(f"Row {row} must be >= 1")
    if col < 1:
        raise SylkError(f"Col {col} must be >= 1")
    old_value = None
    found = False
    for cell in doc.cells:
        if cell.row == row and cell.col == col:
            old_value = cell.value
            cell.value = value
            cell.value_type = value_type
            found = True
            break
    if not found:
        doc.cells.append(SylkCell(row=row, col=col, value=value, value_type=value_type))
        doc.rows = max(doc.rows, row)
        doc.cols = max(doc.cols, col)
    write_sylk(doc, dest_path)
    return {
        "ok": True,
        "row": row,
        "col": col,
        "old_value": old_value,
        "new_value": value,
    }


def get_column_values(file_path: str | Path, col: int) -> list[Any]:
    """Return all cell values for a given column (1-based) as a list.

    Values are ordered by row index. Empty cells within the row range
    are represented as None. Returns an empty list if the column has no cells.

    Args:
        file_path: Path to SYLK file.
        col:       1-based column index.

    Returns:
        List of cell values in row order. Empty cells within the column
        row span are None.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    col_cells = [c for c in doc.cells if c.col == col]
    if not col_cells:
        return []
    max_row = max(c.row for c in col_cells)
    result: list[Any] = [None] * max_row
    for cell in col_cells:
        result[cell.row - 1] = cell.value
    return result


def add_row(file_path: str | Path, dest_path: str | Path, values: list[Any]) -> dict[str, Any]:
    """Add a row of values to the end of a SYLK document and write to dest_path.

    Args:
        file_path: Path to source SYLK file.
        dest_path: Path to write modified SYLK file.
        values: List of cell values for the new row.

    Returns:
        Result dict with success, row_index, cell_count.
    """
    doc = parse_sylk_strict(file_path)
    new_row = max((c.row for c in doc.cells), default=0) + 1
    for col_idx, val in enumerate(values, start=1):
        vtype = "numeric" if isinstance(val, (int, float)) else "string"
        doc.cells.append(SylkCell(row=new_row, col=col_idx, value=val, value_type=vtype))
    write_sylk(doc, dest_path)
    return {"success": True, "row_index": new_row, "cell_count": len(values)}


def delete_row(file_path: str | Path, dest_path: str | Path, row: int) -> dict[str, Any]:
    """Delete a row (1-based) from a SYLK document and write to dest_path.

    Cells in the target row are removed. Cells in higher rows are shifted down.

    Args:
        file_path: Path to source SYLK file.
        dest_path: Path to write modified SYLK file.
        row: 1-based row index to delete.

    Returns:
        Result dict with success, deleted_count.
    """
    doc = parse_sylk_strict(file_path)
    deleted = [c for c in doc.cells if c.row == row]
    remaining = [c for c in doc.cells if c.row != row]
    # Shift rows above the deleted row down by 1
    for c in remaining:
        if c.row > row:
            c.row -= 1
    doc.cells = remaining
    write_sylk(doc, dest_path)
    return {"success": True, "deleted_count": len(deleted)}


def count_nonempty_cells(file_path: str | Path) -> int:
    """Count non-empty cells in a SYLK file.

    A cell is non-empty if its value is not None and not an empty string.
    """
    doc = parse_sylk_strict(file_path)
    return sum(1 for c in doc.cells if c.value is not None and c.value != "")


def sum_column(file_path: str | Path, col: int) -> float:
    """Sum all numeric values in a column (1-based, matching SYLK conventions).

    Non-numeric values are ignored. Returns 0.0 if no numeric values found.
    """
    doc = parse_sylk_strict(file_path)
    total = 0.0
    for c in doc.cells:
        if c.col == col and isinstance(c.value, (int, float)):
            total += c.value
    return total


def sylk_to_html(file_path: str | Path) -> str:
    """Export a SYLK file as an HTML table string.

    Builds a 2D grid from cell coordinates and produces a simple HTML table.
    Cell values are HTML-escaped.

    Returns:
        HTML string containing a <table> element.

    Raises:
        SylkError subclasses on parse failure.
    """
    from html import escape
    doc = parse_sylk_strict(file_path)
    if not doc.cells:
        return "<table></table>"

    grid: dict[int, dict[int, Any]] = {}
    max_row = 0
    max_col = 0
    for cell in doc.cells:
        r = cell.row - 1
        c = cell.col - 1
        if r not in grid:
            grid[r] = {}
        grid[r][c] = cell.value if cell.value is not None else ""
        max_row = max(max_row, r)
        max_col = max(max_col, c)

    lines = ["<table>"]
    for r in range(max_row + 1):
        lines.append("  <tr>")
        for c in range(max_col + 1):
            val = grid.get(r, {}).get(c, "")
            lines.append(f"    <td>{escape(str(val))}</td>")
        lines.append("  </tr>")
    lines.append("</table>")
    return "\n".join(lines)


# Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
# Queue: broad-accel-q-005

def min_column_value(file_path: str | Path, col: int) -> Any:
    """Return the minimum numeric value in a column (1-based).

    Non-numeric values are ignored. Returns None if no numeric values found.
    """
    doc = parse_sylk_strict(file_path)
    nums = [c.value for c in doc.cells if c.col == col and isinstance(c.value, (int, float))]
    return min(nums) if nums else None


def max_column_value(file_path: str | Path, col: int) -> Any:
    """Return the maximum numeric value in a column (1-based).

    Non-numeric values are ignored. Returns None if no numeric values found.
    """
    doc = parse_sylk_strict(file_path)
    nums = [c.value for c in doc.cells if c.col == col and isinstance(c.value, (int, float))]
    return max(nums) if nums else None


def average_column(file_path: "str | Path", col: int) -> "float":
    """Return the average of numeric values in the given 1-based column.

    Non-numeric values are ignored. Returns 0.0 if no numeric values found.

    Args:
        file_path: Path to a SYLK file.
        col: 1-based column index.

    Returns:
        Average of numeric values, or 0.0 if none found.
    """
    doc = parse_sylk_strict(file_path)
    nums = [c.value for c in doc.cells if c.col == col and isinstance(c.value, (int, float))]
    return sum(nums) / len(nums) if nums else 0.0


def find_value(file_path: str | Path, value: Any) -> tuple[int, int] | None:
    """Return the (row, col) of the first cell matching value (1-based), or None.

    Searches cells in row-then-column order. Returns the coordinates of the
    first cell whose value equals the given value, or None if not found.

    Args:
        file_path: Path to SYLK file.
        value: Value to search for (equality check).

    Returns:
        Tuple (row, col) of the first matching cell (1-based), or None.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    # Sort cells by row then column for deterministic first-match
    sorted_cells = sorted(doc.cells, key=lambda c: (c.row, c.col))
    for cell in sorted_cells:
        if cell.value == value:
            return (cell.row, cell.col)
    return None


def count_distinct_values(file_path: "str | Path", col: int) -> int:
    """Count distinct non-empty values in a column (1-based).

    Empty strings and None values are excluded from the count.

    Args:
        file_path: Path to SYLK file.
        col: 1-based column index.

    Returns:
        Integer count of distinct non-empty values.

    Raises:
        SylkError subclasses on parse failure.
    """
    values = get_column_values(file_path, col=col)
    distinct: set[Any] = set()
    for v in values:
        if v is not None and v != "":
            distinct.add(v)
    return len(distinct)


def find_rows_by_value(file_path: "str | Path", value: "Any") -> "list[int]":
    """Return 1-based row indices where the given value appears in any cell.

    Args:
        file_path: Path to a SYLK file.
        value: The value to search for (compared by equality).

    Returns:
        Sorted list of 1-based row numbers that contain a cell with the given value.
        Returns empty list if value is not found.
    """
    doc = parse_sylk_strict(file_path)
    matching: set[int] = set()
    for cell in doc.cells:
        if cell.value == value:
            matching.add(cell.row)
    return sorted(matching)


# ---------------------------------------------------------------------------
# Analytics in sylk_analytics.py (TC-HEAL-FORMATS-BATCH1)
try:
    from .spreadsheet_document import *  # noqa: F401, F403
except ImportError:
    pass
