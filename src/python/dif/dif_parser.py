"""
dif_parser.py — Data Interchange Format (DIF) parser for format-factory-dif.

Public API:
  parse_dif(file_path)        — returns result dict (never raises)
  parse_dif_strict(file_path) — raises DifError on failure
  probe_dif(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype scope.
Parses TABLE, VECTORS, TUPLES, DATA sections.
Technology: Python stdlib only (open/read/split).

License: Apache-2.0
"""

from __future__ import annotations

import csv
import html as _html_module
import io
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_ROWS = 1_048_576
MAX_COLUMNS = 16_384


class DifError(Exception):
    """Base exception for DIF parser errors."""


class DifInvalidFormatError(DifError):
    """Raised when file structure is not valid DIF."""


class DifSizeError(DifError):
    """Raised when file or data exceeds limits."""


@dataclass
class DifCell:
    spec_qname: str = "dif:cell"
    value: Any = None
    value_type: str = "string"  # "numeric", "string", "special"


@dataclass
class DifDocument:
    spec_qname: str = "dif:document"
    title: str = ""
    vectors: int = 0  # columns
    tuples: int = 0   # rows
    rows: list[list[DifCell]] = field(default_factory=list)


def _read_lines(file_path: Path) -> list[str]:
    """Read file and return lines (stripping CR/LF)."""
    size = os.path.getsize(file_path)
    if size > MAX_FILE_SIZE:
        raise DifSizeError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")
    text = file_path.read_text(encoding="utf-8", errors="replace")
    return text.splitlines()


def _expect_section(lines: list[str], pos: int, name: str) -> int:
    """Assert that line at pos matches section name. Returns next pos."""
    if pos >= len(lines):
        raise DifInvalidFormatError(f"Expected '{name}' section, got end of file")
    if lines[pos].strip().upper() != name:
        raise DifInvalidFormatError(
            f"Expected '{name}', got '{lines[pos].strip()}'"
        )
    return pos + 1


def _read_header_triplet(lines: list[str], pos: int) -> tuple[str, int, str, int]:
    """Read a DIF header triplet: section_name, numeric_pair, string_value.

    Returns (section_name, numeric_value, string_value, next_pos).
    """
    if pos + 2 >= len(lines):
        raise DifInvalidFormatError("Unexpected end of file in header triplet")
    section = lines[pos].strip()
    pair_line = lines[pos + 1].strip()
    str_line = lines[pos + 2].strip()

    # Parse numeric pair: "0,1" -> second value
    parts = pair_line.split(",")
    if len(parts) != 2:
        raise DifInvalidFormatError(f"Invalid numeric pair: '{pair_line}'")
    try:
        num_val = int(parts[1])
    except ValueError:
        # Try float
        try:
            num_val = int(float(parts[1]))
        except ValueError:
            raise DifInvalidFormatError(f"Invalid numeric value: '{parts[1]}'")

    # Strip quotes from string value
    if str_line.startswith('"') and str_line.endswith('"'):
        str_val = str_line[1:-1]
    else:
        str_val = str_line

    return section, num_val, str_val, pos + 3


def parse_dif_strict(file_path: str | Path) -> DifDocument:
    """Parse a DIF file, raising DifError on any problem."""
    path = Path(file_path)
    if not path.exists():
        raise DifError(f"File not found: {path}")

    lines = _read_lines(path)
    if not lines:
        raise DifInvalidFormatError("Empty file")

    doc = DifDocument()
    pos = 0

    # Parse TABLE header
    section, num_val, str_val, pos = _read_header_triplet(lines, pos)
    if section.upper() != "TABLE":
        raise DifInvalidFormatError(f"Expected TABLE header, got '{section}'")
    doc.title = str_val

    # Parse VECTORS header
    section, num_val, str_val, pos = _read_header_triplet(lines, pos)
    if section.upper() != "VECTORS":
        raise DifInvalidFormatError(f"Expected VECTORS header, got '{section}'")
    doc.vectors = num_val
    if doc.vectors > MAX_COLUMNS:
        raise DifSizeError(f"Vectors {doc.vectors} exceeds limit of {MAX_COLUMNS}")

    # Parse TUPLES header
    section, num_val, str_val, pos = _read_header_triplet(lines, pos)
    if section.upper() != "TUPLES":
        raise DifInvalidFormatError(f"Expected TUPLES header, got '{section}'")
    doc.tuples = num_val
    if doc.tuples > MAX_ROWS:
        raise DifSizeError(f"Tuples {doc.tuples} exceeds limit of {MAX_ROWS}")

    # Find DATA section
    pos = _expect_section(lines, pos, "DATA")

    # Skip DATA's value pair line and string line
    if pos + 1 >= len(lines):
        raise DifInvalidFormatError("DATA section has no content")
    pos += 2  # Skip "0,0" and '""'

    # Parse data cells
    current_row: list[DifCell] = []
    while pos + 1 < len(lines):
        type_line = lines[pos].strip()
        value_line = lines[pos + 1].strip()
        pos += 2

        parts = type_line.split(",")
        if len(parts) != 2:
            raise DifInvalidFormatError(f"Invalid data type pair: '{type_line}'")

        try:
            type_indicator = int(parts[0])
            numeric_value = float(parts[1])
        except ValueError:
            raise DifInvalidFormatError(f"Invalid data values: '{type_line}'")

        if type_indicator == -1 and value_line.upper() == "BOT":
            # Beginning of tuple — save current row if not empty, start new
            if current_row:
                doc.rows.append(current_row)
                if len(doc.rows) > MAX_ROWS:
                    raise DifSizeError(f"Row count exceeds limit of {MAX_ROWS}")
            current_row = []
        elif type_indicator == -1 and value_line.upper() == "EOD":
            # End of data
            if current_row:
                doc.rows.append(current_row)
            break
        elif type_indicator == 0:
            # Numeric cell
            cell = DifCell(value=numeric_value, value_type="numeric")
            current_row.append(cell)
        elif type_indicator == 1:
            # String cell
            if value_line.startswith('"') and value_line.endswith('"'):
                str_val = value_line[1:-1]
            else:
                str_val = value_line
            cell = DifCell(value=str_val, value_type="string")
            current_row.append(cell)
        elif type_indicator == -1:
            # Special value (V = valid, NA = not available, ERROR, TRUE, FALSE)
            if value_line.upper() == "V":
                # V means the previous cell's numeric value is valid — already handled
                pass
            elif value_line.upper() == "NA":
                cell = DifCell(value=None, value_type="special")
                current_row.append(cell)
            elif value_line.upper() == "TRUE":
                cell = DifCell(value=True, value_type="boolean")
                current_row.append(cell)
            elif value_line.upper() == "FALSE":
                cell = DifCell(value=False, value_type="boolean")
                current_row.append(cell)
            else:
                cell = DifCell(value=value_line, value_type="special")
                current_row.append(cell)
        else:
            # Unknown type — store as-is
            cell = DifCell(value=value_line, value_type="unknown")
            current_row.append(cell)

    return doc


def parse_dif(file_path: str | Path) -> dict[str, Any]:
    """Parse a DIF file, returning a result dict (never raises)."""
    try:
        doc = parse_dif_strict(file_path)
        return {
            "ok": True,
            "title": doc.title,
            "vectors": doc.vectors,
            "tuples": doc.tuples,
            "row_count": len(doc.rows),
            "rows": [
                [{"value": c.value, "type": c.value_type} for c in row]
                for row in doc.rows
            ],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


def probe_dif(file_path: str | Path) -> dict[str, Any]:
    """Probe a DIF file for header metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        lines = _read_lines(path)
        if not lines:
            result["valid_header"] = False
            result["error"] = "Empty file"
            return result
        section, num_val, str_val, pos = _read_header_triplet(lines, 0)
        if section.upper() != "TABLE":
            result["valid_header"] = False
            result["error"] = f"Expected TABLE, got '{section}'"
            return result
        result["valid_header"] = True
        result["title"] = str_val
        # Try VECTORS
        if pos + 2 < len(lines):
            section2, num_val2, _, _ = _read_header_triplet(lines, pos)
            if section2.upper() == "VECTORS":
                result["vectors"] = num_val2
    except Exception as exc:
        result["valid_header"] = False
        result["error"] = str(exc)
    return result


# ---------------------------------------------------------------------------
# R117 — write_dif: serialize DifDocument back to DIF format
# ---------------------------------------------------------------------------


def write_dif(doc: DifDocument, file_path: str | Path) -> None:
    """Write a DifDocument to a DIF-format file.

    Produces a valid DIF file that can be parsed back by parse_dif_strict.

    DIF structure:
        TABLE / 0,<version> / "<title>"
        VECTORS / 0,<num_cols> / ""
        TUPLES / 0,<num_rows> / ""
        DATA / 0,0 / ""
        For each row: -1,0/BOT then cells then final -1,0/EOD

    Args:
        doc: DifDocument to serialize.
        file_path: Destination file path.

    Added in R117.
    """
    path = Path(file_path)
    lines: list[str] = []

    # Determine actual column count from rows if doc.vectors == 0
    vectors = doc.vectors
    if vectors == 0 and doc.rows:
        vectors = max((len(r) for r in doc.rows), default=0)

    tuples = doc.tuples
    if tuples == 0:
        tuples = len(doc.rows)

    # Header triplets
    title = doc.title or ""
    lines += ["TABLE", "0,1", f'"{title}"']
    lines += ["VECTORS", f"0,{vectors}", '""']
    lines += ["TUPLES", f"0,{tuples}", '""']
    lines += ["DATA", "0,0", '""']

    # Data rows
    for row in doc.rows:
        lines += ["-1,0", "BOT"]
        for cell in row:
            if cell.value_type == "numeric":
                val = cell.value
                if isinstance(val, float) and val == int(val):
                    numeric_str = str(int(val))
                else:
                    numeric_str = str(val) if val is not None else "0"
                lines += [f"0,{numeric_str}", "V"]
            elif cell.value_type in ("string", "unknown"):
                str_val = str(cell.value) if cell.value is not None else ""
                str_val = str_val.replace('"', '""')
                lines += ["1,0", f'"{str_val}"']
            elif cell.value_type == "boolean":
                val_str = "TRUE" if cell.value else "FALSE"
                lines += ["-1,0", val_str]
            else:
                # special / None
                val_str = "NA" if cell.value is None else str(cell.value)
                lines += ["-1,0", val_str]

    lines += ["-1,0", "EOD"]

    # Use newline="" to suppress platform CRLF double-translation on Windows
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write("\r\n".join(lines) + "\r\n")


# ---------------------------------------------------------------------------
# Gate 5 — Neutral model: capability declaration
# ---------------------------------------------------------------------------

SUPPORTED_FEATURES: frozenset[str] = frozenset({
    "table_header_parse",
    "vectors_tuples_count",
    "numeric_cells",
    "string_cells",
    "bot_eod_markers",
    "probe",
    "title_extraction",
    "size_guard",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "comments_in_data",
    "special_values_na_error",
    "boolean_cells",
    "formula_cells",
    "date_cells",
    "time_cells",
    "currency_cells",
    "multi_table_dif",
    "encoding_detection",
    "crlf_normalization",
})


def get_capabilities() -> dict[str, Any]:
    """Return a capability descriptor for the DIF parser (Gate 5 neutral model)."""
    return {
        "format": "dif",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
    }


# ---------------------------------------------------------------------------
# R84 Train N: DIF CSV export
# ---------------------------------------------------------------------------

def get_cell_value(file_path: str | Path, row: int, col: int) -> Any:
    """Return the value at (row, col) in a DIF file (0-based indices).

    Returns None if the cell is empty or the coordinates are out of range.

    Args:
        file_path: Path to DIF file.
        row:       0-based row index.
        col:       0-based column index.

    Returns:
        Cell value (numeric, str, bool, or None for empty/missing).

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    if row < 0 or row >= len(doc.rows):
        return None
    r = doc.rows[row]
    if col < 0 or col >= len(r):
        return None
    return r[col].value


def set_cell_value(
    file_path: str | Path,
    dest_path: str | Path,
    row: int,
    col: int,
    value: Any,
    value_type: str = "string",
) -> dict[str, Any]:
    """Set a cell value in a DIF file and write the result.

    Parses the source file, modifies the cell at (row, col) (0-based),
    and writes the updated document to dest_path.

    Args:
        file_path:  Source DIF file path.
        dest_path:  Destination file path for the modified document.
        row:        0-based row index.
        col:        0-based column index.
        value:      New cell value.
        value_type: One of "numeric", "string", "boolean", "special".

    Returns:
        Dict with ok, row, col, old_value, new_value keys.

    Raises:
        DifError on parse failure or invalid coordinates.
    """
    doc = parse_dif_strict(file_path)
    if row < 0 or row >= len(doc.rows):
        raise DifError(f"Row {row} out of range (0..{len(doc.rows) - 1})")
    r = doc.rows[row]
    if col < 0 or col >= len(r):
        raise DifError(f"Col {col} out of range (0..{len(r) - 1})")
    old_value = r[col].value
    r[col] = DifCell(value=value, value_type=value_type)
    write_dif(doc, dest_path)
    return {
        "ok": True,
        "row": row,
        "col": col,
        "old_value": old_value,
        "new_value": value,
    }


def get_row_values(file_path: str | Path, row: int) -> list[Any]:
    """Return all cell values for a given row (0-based) as a list.

    Args:
        file_path: Path to DIF file.
        row:       0-based row index.

    Returns:
        List of cell values. Returns empty list if row is out of range.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    if row < 0 or row >= len(doc.rows):
        return []
    return [cell.value for cell in doc.rows[row]]


def get_title(file_path: str | Path) -> str:
    """Return the TABLE title from a DIF file.

    Args:
        file_path: Path to DIF file.

    Returns:
        Title string (may be empty if no title set).

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    return doc.title


def get_row_count(file_path: str | Path) -> int:
    """Return the number of data rows in a DIF file.

    Args:
        file_path: Path to DIF file.

    Returns:
        Integer row count.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    return len(doc.rows)


def get_column_count(file_path: str | Path) -> int:
    """Return the number of columns (vectors) declared in a DIF file.

    Args:
        file_path: Path to DIF file.

    Returns:
        Integer column count from the VECTORS header.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    return doc.vectors


def get_column_values(file_path: str | Path, col: int) -> list[Any]:
    """Return all cell values for a given column (0-based) as a list.

    Args:
        file_path: Path to DIF file.
        col:       0-based column index.

    Returns:
        List of cell values from each row at the given column.
        Returns empty list if column is out of range for all rows.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    result: list[Any] = []
    for row in doc.rows:
        if col < 0 or col >= len(row):
            result.append(None)
        else:
            result.append(row[col].value)
    return result


def count_nonempty_cells(file_path: str | Path) -> int:
    """Count non-empty cells in a DIF file.

    A cell is non-empty if its value is not None and not an empty string.

    Args:
        file_path: Path to DIF file.

    Returns:
        Count of non-empty cells.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    count = 0
    for row in doc.rows:
        for cell in row:
            if cell.value is not None and cell.value != "":
                count += 1
    return count


def total_cell_count(file_path: str | Path) -> int:
    """Return the total number of cells in a DIF file (all rows, all columns).

    Args:
        file_path: Path to DIF file.

    Returns:
        Total cell count across all rows.

    Raises:
        DifError subclasses on parse failure.
    """
    doc = parse_dif_strict(file_path)
    return sum(len(row) for row in doc.rows)


def get_all_values(file_path: str | Path) -> list[Any]:
    """Return a flat list of all cell values in a DIF file, row by row."""
    doc = parse_dif_strict(file_path)
    result: list[Any] = []
    for row in doc.rows:
        for cell in row:
            result.append(cell.value)
    return result


def min_column_value(file_path: str | Path, col: int) -> Any:
    """Return the minimum numeric value in a column (0-based).

    Non-numeric values are ignored. Returns None if no numeric values found.
    """
    doc = parse_dif_strict(file_path)
    values = []
    for row in doc.rows:
        if 0 <= col < len(row):
            v = row[col].value
            if isinstance(v, (int, float)):
                values.append(v)
    return min(values) if values else None


def max_column_value(file_path: str | Path, col: int) -> Any:
    """Return the maximum numeric value in a column (0-based).

    Non-numeric values are ignored. Returns None if no numeric values found.
    """
    doc = parse_dif_strict(file_path)
    values = []
    for row in doc.rows:
        if 0 <= col < len(row):
            v = row[col].value
            if isinstance(v, (int, float)):
                values.append(v)
    return max(values) if values else None


def sum_column(file_path: str | Path, col: int) -> float:
    """Return the sum of numeric values in a column (0-based).

    Non-numeric values are ignored. Returns 0.0 if no numeric values found.
    """
    doc = parse_dif_strict(file_path)
    total = 0.0
    for row in doc.rows:
        if 0 <= col < len(row):
            v = row[col].value
            if isinstance(v, (int, float)):
                total += v
    return total


def average_column(file_path: str | Path, col: int) -> float:
    """Return the average (mean) of numeric values in a column (0-based).

    Non-numeric values are ignored. Returns 0.0 if no numeric values found.
    """
    doc = parse_dif_strict(file_path)
    values = []
    for row in doc.rows:
        if 0 <= col < len(row):
            v = row[col].value
            if isinstance(v, (int, float)):
                values.append(v)
    return sum(values) / len(values) if values else 0.0




# Analytics functions are in interchange_document.py to keep this file within policy limits.
try:
    from .interchange_document import *  # noqa: F401, F403
except ImportError:
    pass
