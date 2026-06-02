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
        path.write_text("\r\n".join(lines) + "\r\n", encoding="ascii")
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
