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
    value: Any = None
    value_type: str = "string"  # "numeric", "string", "special"


@dataclass
class DifDocument:
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
                lines += [f"1,0", f'"{str_val}"']
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
