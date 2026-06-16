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
"""

from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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
    row: int = 1
    col: int = 1
    value: Any = None
    value_type: str = "empty"  # "numeric", "string", "empty"


@dataclass
class SylkDocument:
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


def sylk_nonempty_rows(file_path: "str | Path") -> int:
    """Return the count of rows that contain at least one non-empty cell."""
    doc = parse_sylk_strict(file_path)
    rows_with_data = set()
    for cell in doc.cells:
        val = cell.value
        if val is not None and str(val).strip() != "":
            rows_with_data.add(cell.row)
    return len(rows_with_data)


def sylk_numeric_cell_count(file_path: "str | Path") -> int:
    """Return the count of cells that contain a numeric (int or float) value.

    Args:
        file_path: Path to SYLK (.slk) file.

    Returns:
        Integer count of numeric cells.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    count = 0
    for cell in doc.cells:
        val = cell.value
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            count += 1
    return count


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


def sylk_empty_cell_count(file_path: "str | Path") -> int:
    """Return the count of cells whose value is None or an empty string.

    Args:
        file_path: Path to a SYLK (.slk) file.

    Returns:
        Integer count of empty/null cells. Returns 0 if all cells have values.

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    return sum(1 for cell in doc.cells if cell.value is None or cell.value == "")


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
