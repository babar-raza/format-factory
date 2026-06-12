"""
csv_parser.py — CSV (RFC 4180) parser for format-factory-csv.

Public API:
  parse_csv(file_path)        — returns result dict (never raises)
  parse_csv_strict(file_path) — raises CsvError on failure
  probe_csv(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype + Gate 5 neutral model.
Parses CSV files per RFC 4180 using an inline state-machine parser.
Detects delimiter (comma/tab/semicolon/pipe heuristic), headers (first row),
row count. Technology: Python stdlib only (no stdlib csv module needed).

NOTE: Does NOT import the stdlib 'csv' module to avoid namespace collision
with src/python/csv/ when running under conftest.py sys.path injection.

R55 Train H: CSV Gate 4 prototype (TC-ACQN-CSV-001).

License: Apache-2.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_ROWS = 1_000_000


class CsvError(Exception):
    """Base exception for CSV parser errors."""


class CsvInputError(CsvError):
    """Raised when the file cannot be read."""


class CsvSizeError(CsvError):
    """Raised when the file exceeds size or row limits."""


class CsvParseError(CsvError):
    """Raised when the CSV content is malformed."""


def _sniff_delimiter(sample: str) -> str:
    """Heuristic delimiter detection from a text sample."""
    candidates = [",", "\t", ";", "|"]
    lines = [ln for ln in sample.splitlines()[:10] if ln.strip()]
    if not lines:
        return ","
    best = ","
    best_score = -1
    for delim in candidates:
        counts = [ln.count(delim) for ln in lines]
        min_c = min(counts)
        if min_c > best_score:
            best_score = min_c
            best = delim
    return best


def _parse_rfc4180(text: str, delimiter: str = ",") -> list[list[str]]:
    """Parse RFC 4180 CSV text; returns list of rows (each row is list of fields)."""
    rows: list[list[str]] = []
    row: list[str] = []
    field: list[str] = []
    in_quotes = False
    i = 0
    n = len(text)

    while i < n:
        c = text[i]
        if in_quotes:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                else:
                    in_quotes = False
                    i += 1
            else:
                field.append(c)
                i += 1
        else:
            if c == '"':
                in_quotes = True
                i += 1
            elif c == delimiter:
                row.append("".join(field))
                field = []
                i += 1
            elif c == "\r":
                row.append("".join(field))
                field = []
                rows.append(row)
                row = []
                i += 1
                if i < n and text[i] == "\n":
                    i += 1
            elif c == "\n":
                row.append("".join(field))
                field = []
                rows.append(row)
                row = []
                i += 1
            else:
                field.append(c)
                i += 1

    if field or row:
        row.append("".join(field))
        rows.append(row)

    # Strip trailing empty row from files ending with newline
    while rows and rows[-1] == [""]:
        rows.pop()

    return rows


def _has_header_heuristic(rows: list[list[str]]) -> bool:
    """Return True if first row looks like a text header over numeric data rows."""
    if len(rows) < 2:
        return False
    first = rows[0]
    for f in first:
        try:
            float(f.strip())
            return False
        except ValueError:
            pass
    for row in rows[1:3]:
        for f in row:
            try:
                float(f.strip())
                return True
            except ValueError:
                pass
    return False


def parse_csv_strict(file_path: str | Path) -> dict[str, Any]:
    """Parse a CSV file and return the neutral model dict.

    Returns:
        {
          "format": "csv",
          "path": str,
          "row_count": int,      # number of data rows (excluding header if detected)
          "column_count": int,   # number of columns in first row
          "headers": list[str] | None,  # first row used as headers
          "rows": list[list[str]],      # data rows
          "has_header": bool,
          "delimiter": str,
        }

    Raises:
        CsvInputError:  file not found or not readable
        CsvSizeError:   file exceeds 64 MiB or 1M rows
        CsvParseError:  malformed CSV
    """
    path = Path(file_path)
    if not path.exists():
        raise CsvInputError(f"File not found: {path}")
    if not path.is_file():
        raise CsvInputError(f"Path is not a regular file: {path}")

    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise CsvSizeError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")

    try:
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError as exc:
        raise CsvInputError(f"Cannot read file {path}: {exc}") from exc

    return _parse_csv_text(raw, str(path))


def _parse_csv_text(raw: str, path_str: str) -> dict[str, Any]:
    """Core CSV parse from string."""
    delimiter = _sniff_delimiter(raw[:4096])
    all_rows = _parse_rfc4180(raw, delimiter)

    if len(all_rows) > MAX_ROWS:
        raise CsvSizeError(f"Row count {len(all_rows)} exceeds limit of {MAX_ROWS}")

    if not all_rows:
        return {
            "format": "csv",
            "path": path_str,
            "row_count": 0,
            "column_count": 0,
            "headers": None,
            "rows": [],
            "has_header": False,
            "delimiter": delimiter,
        }

    has_header = _has_header_heuristic(all_rows)

    if has_header and len(all_rows) > 1:
        headers = all_rows[0]
        rows = all_rows[1:]
    else:
        headers = None
        rows = all_rows

    column_count = len(all_rows[0]) if all_rows else 0

    return {
        "format": "csv",
        "path": path_str,
        "row_count": len(rows),
        "column_count": column_count,
        "headers": headers,
        "rows": rows,
        "has_header": has_header,
        "delimiter": delimiter,
    }


def parse_csv(file_path: str | Path) -> dict[str, Any]:
    """Parse a CSV file, returning a result dict (never raises)."""
    try:
        return parse_csv_strict(file_path)
    except Exception as exc:
        return {
            "format": "csv",
            "ok": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
        }


def probe_csv(file_path: str | Path) -> dict[str, Any]:
    """Probe a CSV file for metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        size = path.stat().st_size
        result["size_bytes"] = size
        sample = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
        lines = sample.splitlines()
        result["first_line"] = lines[0] if lines else ""
        result["sample_line_count"] = len(lines)
        result["delimiter"] = _sniff_delimiter(sample)
    except Exception as exc:
        result["probe_error"] = str(exc)
    return result


# ---------------------------------------------------------------------------
# Gate 5 — Neutral model: capability declaration
# ---------------------------------------------------------------------------

SUPPORTED_FEATURES: frozenset[str] = frozenset({
    "rfc4180_parse",
    "delimiter_sniff",
    "header_detection",
    "utf8_bom_strip",
    "probe",
    "row_count",
    "column_count",
    "size_guard",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "encoding_to_csv",
    "streaming_decode",
    "typed_cell_inference",
    "formula_cells",
    "multi_sheet",
    "binary_csv",
    "excel_dialect_quirks",
})


def get_capabilities() -> dict[str, Any]:
    """Return a capability descriptor for the CSV parser (Gate 5 neutral model)."""
    return {
        "format": "csv",
        "gate": 4,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
    }


def get_row_count(file_path: "str | Path") -> int:
    """Return the number of data rows in a CSV file (excluding header if present).

    Args:
        file_path: Path to the CSV file.

    Returns:
        Integer count of data rows. Returns 0 if file is empty or header-only.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    return len(rows)


def get_column_names(file_path: "str | Path") -> "list[str]":
    """Return the column names (header row) from a CSV file.

    Args:
        file_path: Path to the CSV file.

    Returns:
        List of column name strings. Empty list if no header detected.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    return list(model.get("headers", []) or [])


def get_cell_value(file_path: "str | Path", row: int, col: int) -> "str | None":
    """Return the string value at the given row and column position.

    Args:
        file_path: Path to the CSV file.
        row: 0-based row index (excluding header).
        col: 0-based column index.

    Returns:
        Cell value as a string, or None if out of range.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if row < 0 or row >= len(rows):
        return None
    row_data = rows[row]
    if col < 0 or col >= len(row_data):
        return None
    return str(row_data[col])


def count_empty_cells(file_path: "str | Path", col_name: str) -> int:
    """Return the number of empty (blank) cells in a named column.

    Args:
        file_path: Path to the CSV file.
        col_name:  Column header name to inspect.

    Returns:
        Count of cells in that column whose stripped value is empty string.
        Returns 0 if the column is not found or the file has no data rows.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    headers = model.get("headers") or []
    if col_name not in headers:
        return 0
    col_idx = headers.index(col_name)
    rows = model.get("rows", [])
    return sum(1 for row in rows if col_idx >= len(row) or row[col_idx].strip() == "")


def csv_to_dicts(file_path: "str | Path") -> "list[dict[str, str]]":
    """Return CSV rows as a list of dicts mapping column names to string values.

    If the file has a detected header row, column names come from the header.
    Otherwise, columns are named "col_0", "col_1", etc.

    Args:
        file_path: Path to the CSV file.

    Returns:
        List of dicts, one per data row. Empty list if file has no data rows.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return []
    headers = model.get("headers")
    if headers:
        keys = headers
    else:
        col_count = max(len(r) for r in rows)
        keys = [f"col_{i}" for i in range(col_count)]
    result = []
    for row in rows:
        d = {keys[i]: row[i] if i < len(row) else "" for i in range(len(keys))}
        result.append(d)
    return result


def csv_column_count(file_path: "str | Path") -> int:
    """Return the number of columns in the CSV file (length of the header/first row).

    Args:
        file_path: Path to a CSV file.

    Returns:
        Integer column count. Returns 0 for empty files.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    return model.get("column_count", 0)


def csv_has_header(file_path: "str | Path") -> bool:
    """Return True if the CSV file was detected as having a header row.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Boolean indicating whether a header row was detected.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    return bool(model.get("has_header", False))


def csv_numeric_row_count(file_path: "str | Path") -> int:
    """Return the count of rows where all non-empty cells are numeric.

    A row is considered numeric if every non-empty cell value can be parsed as float.

    Args:
        file_path: Path to a CSV file.

    Returns:
        Integer count of all-numeric rows. Returns 0 if no such rows exist.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    count = 0
    for row in model.get("rows", []):
        non_empty = [str(c) for c in row if str(c).strip()]
        if not non_empty:
            continue
        try:
            for c in non_empty:
                float(c)
            count += 1
        except ValueError:
            pass
    return count


def count_distinct_values(file_path: "str | Path", col_name: str) -> int:
    """Return the count of distinct non-empty values in a CSV column.

    Args:
        file_path: Path to the CSV file.
        col_name: Column header name to inspect.

    Returns:
        Integer count of unique non-empty cell values.
        Returns 0 if the column is not found.

    Raises:
        CsvError subclasses on parse failure.
    """
    model = parse_csv_strict(file_path)
    headers = model.get("headers") or []
    rows = model.get("rows", [])
    # When header detection fails (all-text CSV), check the first data row
    if col_name not in headers and rows:
        first_row = rows[0]
        if col_name in first_row:
            headers = first_row
            rows = rows[1:]
    if col_name not in headers:
        return 0
    col_idx = headers.index(col_name)
    distinct: set[str] = set()
    for row in rows:
        if col_idx < len(row):
            val = str(row[col_idx]).strip()
            if val:
                distinct.add(val)
    return len(distinct)
