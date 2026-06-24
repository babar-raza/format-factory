"""
tsv_parser.py — TSV (Tab-Separated Values) parser for format-factory-tsv.

Public API:
  parse_tsv(file_path)        — returns result dict (never raises)
  parse_tsv_strict(file_path) — raises TsvError on failure
  probe_tsv(file_path)        — returns header metadata without full parse

Implements Gate 4 prototype + Gate 5 neutral model.
Parses TSV files (tab delimiter) using simple line/tab splitting.
Tab is always the delimiter (unlike CSV which sniffs).
Technology: Python stdlib only (no stdlib csv module needed).

NOTE: Does NOT import the stdlib 'csv' module; TSV rows are split by tab
directly, which is correct for standard TSV (no quoted tab-containing fields).

R55 Train H: TSV Gate 4 prototype (TC-ACQN-TSV-001).

License: Apache-2.0
spec_concept: IANA text/tab-separated-values row/cell
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_ROWS = 1_000_000
DELIMITER = "\t"


class TsvError(Exception):
    """Base exception for TSV parser errors."""


class TsvInputError(TsvError):
    """Raised when the file cannot be read."""


class TsvSizeError(TsvError):
    """Raised when the file exceeds size or row limits."""


class TsvParseError(TsvError):
    """Raised when the TSV content is malformed."""


def parse_tsv_strict(file_path: str | Path) -> dict[str, Any]:
    """Parse a TSV file and return the neutral model dict.

    Returns:
        {
          "format": "tsv",
          "path": str,
          "row_count": int,
          "column_count": int,
          "headers": list[str] | None,
          "rows": list[list[str]],
          "has_header": bool,
          "delimiter": "\\t",
        }

    Raises:
        TsvInputError:  file not found or not readable
        TsvSizeError:   file exceeds 64 MiB or 1M rows
        TsvParseError:  malformed TSV
    """
    path = Path(file_path)
    if not path.exists():
        raise TsvInputError(f"File not found: {path}")
    if not path.is_file():
        raise TsvInputError(f"Path is not a regular file: {path}")

    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise TsvSizeError(f"File size {size} exceeds limit of {MAX_FILE_SIZE}")

    try:
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError as exc:
        raise TsvInputError(f"Cannot read file {path}: {exc}") from exc

    return _parse_tsv_text(raw, str(path))


def _parse_tsv_text(raw: str, path_str: str) -> dict[str, Any]:
    """Core TSV parse from string using simple tab splitting."""
    lines = raw.splitlines()
    # Strip trailing empty lines
    while lines and not lines[-1].strip():
        lines.pop()

    all_rows = [line.split(DELIMITER) for line in lines]

    if len(all_rows) > MAX_ROWS:
        raise TsvSizeError(f"Row count {len(all_rows)} exceeds limit of {MAX_ROWS}")

    if not all_rows:
        return {
            "format": "tsv",
            "path": path_str,
            "row_count": 0,
            "column_count": 0,
            "headers": None,
            "rows": [],
            "has_header": False,
            "delimiter": DELIMITER,
        }

    # First row as headers if rows[1:] have same column count (common TSV convention)
    has_header = len(all_rows) > 1 and len(all_rows[0]) == len(all_rows[1])

    if has_header:
        headers = all_rows[0]
        rows = all_rows[1:]
    else:
        headers = None
        rows = all_rows

    column_count = len(all_rows[0]) if all_rows else 0

    return {
        "format": "tsv",
        "path": path_str,
        "row_count": len(rows),
        "column_count": column_count,
        "headers": headers,
        "rows": rows,
        "has_header": has_header,
        "delimiter": DELIMITER,
    }


def parse_tsv(file_path: str | Path) -> dict[str, Any]:
    """Parse a TSV file, returning a result dict (never raises)."""
    try:
        return parse_tsv_strict(file_path)
    except Exception as exc:
        return {
            "format": "tsv",
            "ok": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
        }


def probe_tsv(file_path: str | Path) -> dict[str, Any]:
    """Probe a TSV file for metadata without full parse."""
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
        result["delimiter"] = DELIMITER
        if lines:
            result["column_count"] = lines[0].count(DELIMITER) + 1
    except Exception as exc:
        result["probe_error"] = str(exc)
    return result


# ---------------------------------------------------------------------------
# Gate 5 — Neutral model: capability declaration
# ---------------------------------------------------------------------------

SUPPORTED_FEATURES: frozenset[str] = frozenset({
    "tsv_parse",
    "tab_delimiter",
    "header_detection",
    "utf8_bom_strip",
    "probe",
    "row_count",
    "column_count",
    "size_guard",
})

UNSUPPORTED_FEATURES: frozenset[str] = frozenset({
    "encoding_to_tsv",
    "streaming_decode",
    "typed_cell_inference",
    "formula_cells",
    "multi_sheet",
    "escaped_tabs",
    "quoted_fields_with_tabs",
})


def get_capabilities() -> dict[str, Any]:
    """Return a capability descriptor for the TSV parser (Gate 5 neutral model)."""
    return {
        "format": "tsv",
        "gate": 4,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
    }


# ---------------------------------------------------------------------------
# Internal helper — parse bytes or file path
# ---------------------------------------------------------------------------

def _load_tsv_data(data: Any) -> dict[str, Any]:
    """Parse TSV from bytes, str path, or Path object."""
    if isinstance(data, bytes):
        text = data.decode("utf-8-sig", errors="replace")
        return _parse_tsv_text(text, "<bytes>")
    elif isinstance(data, (str, Path)):
        return parse_tsv_strict(data)
    else:
        raise TsvInputError(f"Unsupported input type: {type(data).__name__}")


# ---------------------------------------------------------------------------
# R122 — write_tsv
# ---------------------------------------------------------------------------

def write_tsv(
    rows: list[list[str]],
    dest: str | Path,
    *,
    headers: list[str] | None = None,
) -> None:
    """Write rows to a TSV file. Tabs and newlines in cell values are replaced with spaces."""
    def _sanitize(val: Any) -> str:
        return str(val).replace("\t", " ").replace("\n", " ").replace("\r", " ")

    lines: list[str] = []
    if headers:
        lines.append("\t".join(_sanitize(h) for h in headers))
    for row in rows:
        lines.append("\t".join(_sanitize(c) for c in row))
    content = "\n".join(lines) + "\n" if lines else ""
    Path(dest).write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# R125 — load_tsv
# ---------------------------------------------------------------------------

def load_tsv(data: Any) -> dict[str, Any]:
    """Load TSV from bytes, str path, or Path object. Returns neutral model dict."""
    if isinstance(data, bytes):
        text = data.decode("utf-8-sig", errors="replace")
        return _parse_tsv_text(text, "<bytes>")
    elif isinstance(data, (str, Path)):
        return parse_tsv_strict(data)
    else:
        raise TsvInputError(f"Unsupported input type: {type(data).__name__}")


# ---------------------------------------------------------------------------
# R126 — get_headers
# ---------------------------------------------------------------------------

def get_headers(file_path: str | Path) -> list[str] | None:
    """Return the detected header row from a TSV file, or None if no header detected."""
    result = parse_tsv_strict(file_path)
    return result["headers"]


# ---------------------------------------------------------------------------
# R128 — Expanded functions
# ---------------------------------------------------------------------------

def get_column(data: Any, col_name: str) -> list[str]:
    """Return all values in the named column. Returns [] if column not found."""
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        return []
    idx = result["headers"].index(col_name)
    return [row[idx] for row in result["rows"] if idx < len(row)]


def write_tsv_strict(
    rows: list[list[str]],
    dest: str | Path,
    *,
    headers: list[str] | None = None,
) -> None:
    """Write rows to a TSV file. Raises TsvError if any cell contains tab or newline."""
    def _check(val: Any) -> str:
        s = str(val)
        if "\t" in s:
            raise TsvError(f"Cell contains tab character: {s!r}")
        if "\n" in s or "\r" in s:
            raise TsvError(f"Cell contains newline character: {s!r}")
        return s

    lines: list[str] = []
    if headers:
        lines.append("\t".join(_check(h) for h in headers))
    for row in rows:
        lines.append("\t".join(_check(c) for c in row))
    content = "\n".join(lines) + "\n" if lines else ""
    Path(dest).write_text(content, encoding="utf-8")


def get_row(data: Any, index: int) -> list[str]:
    """Return the data row at zero-based index. Raises IndexError for negative or out-of-range."""
    if index < 0:
        raise IndexError(f"Row index {index} is negative")
    result = _load_tsv_data(data)
    rows = result["rows"]
    if index >= len(rows):
        raise IndexError(f"Row index {index} out of range (row_count={len(rows)})")
    return rows[index]


def validate_headers(data: Any, expected: list[str]) -> dict[str, Any]:
    """Validate that TSV headers match expected list (order-sensitive).

    Returns {valid, missing, extra, actual, expected}.
    """
    result = _load_tsv_data(data)
    actual = result["headers"] or []
    actual_set = set(actual)
    expected_set = set(expected)
    missing = [h for h in expected if h not in actual_set]
    extra = [h for h in actual if h not in expected_set]
    valid = (actual == expected)
    return {
        "valid": valid,
        "missing": missing,
        "extra": extra,
        "actual": actual,
        "expected": list(expected),
    }


def count_rows(data: Any) -> int:
    """Return the number of data rows (excluding header)."""
    result = _load_tsv_data(data)
    return result["row_count"]


def to_csv(data: Any) -> str:
    """Convert TSV data to CSV string with CRLF line endings. Quotes fields with commas."""
    result = _load_tsv_data(data)

    def _csv_field(val: Any) -> str:
        s = str(val)
        if "," in s or '"' in s or "\n" in s or "\r" in s:
            s = '"' + s.replace('"', '""') + '"'
        return s

    lines: list[str] = []
    if result["headers"]:
        lines.append(",".join(_csv_field(h) for h in result["headers"]))
    for row in result["rows"]:
        lines.append(",".join(_csv_field(c) for c in row))
    return "\r\n".join(lines) + "\r\n" if lines else ""


def deduplicate_rows(data: Any) -> list[list[str]]:
    """Return unique rows preserving insertion order."""
    result = _load_tsv_data(data)
    seen: set[tuple[str, ...]] = set()
    unique: list[list[str]] = []
    for row in result["rows"]:
        key = tuple(row)
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def get_row_by_key(data: Any, col_name: str, value: str) -> list[str] | None:
    """Return the first data row where col_name equals value, or None if not found.

    Raises TsvError if col_name does not exist.
    """
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    for row in result["rows"]:
        if idx < len(row) and row[idx] == value:
            return row
    return None


# ---------------------------------------------------------------------------
# R129 — Advanced functions
# ---------------------------------------------------------------------------

def merge_tsv(data_a: Any, data_b: Any) -> dict[str, Any]:
    """Merge two TSV datasets with identical headers into one. Raises TsvError on mismatch."""
    r_a = _load_tsv_data(data_a)
    r_b = _load_tsv_data(data_b)
    if r_a["headers"] != r_b["headers"]:
        raise TsvError(f"Header mismatch: {r_a['headers']} vs {r_b['headers']}")
    rows = r_a["rows"] + r_b["rows"]
    return {"headers": r_a["headers"], "rows": rows, "row_count": len(rows)}


def min_column_tsv(data: Any, col_name: str) -> float:
    """Return the minimum numeric value in a column. Returns 0.0 if no numeric values."""
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    vals: list[float] = []
    for row in result["rows"]:
        if idx < len(row):
            try:
                vals.append(float(row[idx]))
            except (ValueError, TypeError):
                pass
    return min(vals) if vals else 0.0


def sample_rows(data: Any, n: int) -> dict[str, Any]:
    """Return first n data rows with headers."""
    result = _load_tsv_data(data)
    rows = result["rows"][:n] if n > 0 else []
    return {"headers": result["headers"], "rows": rows}


def sum_column_tsv(data: Any, col_name: str) -> float:
    """Return the sum of numeric values in a column. Skips non-numeric cells."""
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    total = 0.0
    for row in result["rows"]:
        if idx < len(row):
            try:
                total += float(row[idx])
            except (ValueError, TypeError):
                pass
    return total


def sort_rows(data: Any, col_name: str, *, reverse: bool = False) -> dict[str, Any]:
    """Return rows sorted by the named column. Raises TsvError if column missing."""
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column missing: {col_name}")
    idx = result["headers"].index(col_name)
    rows = sorted(result["rows"], key=lambda r: r[idx] if idx < len(r) else "", reverse=reverse)
    return {"headers": result["headers"], "rows": rows}


def drop_column(data: Any, col_name: str) -> dict[str, Any]:
    """Return TSV data with the named column removed. Raises TsvError if column not found."""
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    new_headers = [h for h in result["headers"] if h != col_name]
    new_rows = [[c for i, c in enumerate(row) if i != idx] for row in result["rows"]]
    return {"headers": new_headers, "rows": new_rows}


def add_column(data: Any, col_name: str, values: list[str]) -> dict[str, Any]:
    """Return TSV data with a new column appended. Raises TsvError if values length mismatches."""
    result = _load_tsv_data(data)
    if len(values) != len(result["rows"]):
        raise TsvError(
            f"Values length {len(values)} does not match row count {len(result['rows'])}"
        )
    new_headers = (result["headers"] or []) + [col_name]
    new_rows = [row + [v] for row, v in zip(result["rows"], values)]
    return {"headers": new_headers, "rows": new_rows}


def rename_column(data: Any, old_name: str, new_name: str) -> dict[str, Any]:
    """Return TSV data with old_name column renamed to new_name. Raises TsvError if not found."""
    result = _load_tsv_data(data)
    if not result["headers"] or old_name not in result["headers"]:
        raise TsvError(f"Column not found: {old_name}")
    new_headers = [new_name if h == old_name else h for h in result["headers"]]
    return {"headers": new_headers, "rows": result["rows"]}


# ---------------------------------------------------------------------------
# R150 — get_column_values, max_column_tsv
# ---------------------------------------------------------------------------

def get_column_values(data: Any, col_name: str) -> list[str]:
    """Return all values in the named column. Raises TsvError if column not found."""
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    return [row[idx] if idx < len(row) else "" for row in result["rows"]]


def max_column_tsv(data: Any, col_name: str) -> float:
    """Return the maximum numeric value in a column. Returns 0.0 if no numeric values."""
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    vals: list[float] = []
    for row in result["rows"]:
        if idx < len(row):
            try:
                vals.append(float(row[idx]))
            except (ValueError, TypeError):
                pass
    return max(vals) if vals else 0.0


# ---------------------------------------------------------------------------
# R152 — column_count
# ---------------------------------------------------------------------------

def column_count(data: Any) -> int:
    """Return the number of header columns, or 0 if no header detected."""
    result = _load_tsv_data(data)
    if result["headers"] is None:
        return 0
    return len(result["headers"])


# ---------------------------------------------------------------------------
# pfgi-rnext — average_column_tsv
# FORMAT_FACTORY_EXECUTION: taskcard=PFGI-TC-003; method=MANUAL_GOVERNED_BY_SKILL; skill=add-python-api; idempotency=fa552d78fe7e8ee870cff37a1a3cdd2c2949ae1648034aea445eb56a0d183118; evidence=.local/evidences/product-first-governed-implementation-rnext/evidence-declaration.yaml
# ---------------------------------------------------------------------------

def average_column_tsv(data: Any, col_name: str) -> float:
    """Return the arithmetic mean of numeric values in a column.

    Non-numeric cells are skipped. Returns 0.0 if the column has no numeric values.

    Args:
        data: TSV bytes, path, or pre-loaded dict.
        col_name: Header name of the column to average.

    Returns:
        Float mean of numeric cells, or 0.0 if none found.

    Raises:
        TsvError: If col_name is not found in headers.
    """
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    vals: list[float] = []
    for row in result["rows"]:
        if idx < len(row):
            try:
                vals.append(float(row[idx]))
            except (ValueError, TypeError):
                pass
    return sum(vals) / len(vals) if vals else 0.0


# pige-rnext — median_column_tsv
# FORMAT_FACTORY_EXECUTION: taskcard=PIGE-TC-003; method=AGENT_GOVERNED_DIRECT_EXECUTION; skill=add-python-api; idempotency=b4b8bf4be603b13f62505f3990388204195fc462ec098fcd7f17a676ffe8bc8f; evidence=.local/evidences/product-integration-governed-expansion-rnext/evidence-declaration.yaml
def median_column_tsv(data: Any, col_name: str) -> float:
    """Return the median of numeric values in a column.

    Non-numeric cells are skipped. Returns 0.0 if the column has no numeric values.

    Args:
        data: TSV bytes, path, or pre-loaded dict.
        col_name: Header name of the column.

    Returns:
        Float median of numeric cells, or 0.0 if none found.

    Raises:
        TsvError: If col_name is not found in headers.
    """
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    vals: list[float] = []
    for row in result["rows"]:
        if idx < len(row):
            try:
                vals.append(float(row[idx]))
            except (ValueError, TypeError):
                pass
    if not vals:
        return 0.0
    vals.sort()
    n = len(vals)
    mid = n // 2
    if n % 2 == 1:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2.0


# pige-rnext — std_column_tsv
# FORMAT_FACTORY_EXECUTION: taskcard=PIGE-TC-003; method=AGENT_GOVERNED_DIRECT_EXECUTION; skill=add-python-api; idempotency=5dd59adb627eca7302d0773437191827bd40ace09efb4e480d2f0a5bda94c802; evidence=.local/evidences/product-integration-governed-expansion-rnext/evidence-declaration.yaml
def std_column_tsv(data: Any, col_name: str) -> float:
    """Return the population standard deviation of numeric values in a column.

    Non-numeric cells are skipped. Returns 0.0 if the column has fewer than 1 numeric value.

    Args:
        data: TSV bytes, path, or pre-loaded dict.
        col_name: Header name of the column.

    Returns:
        Float standard deviation, or 0.0 if insufficient data.

    Raises:
        TsvError: If col_name is not found in headers.
    """
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        raise TsvError(f"Column not found: {col_name}")
    idx = result["headers"].index(col_name)
    vals: list[float] = []
    for row in result["rows"]:
        if idx < len(row):
            try:
                vals.append(float(row[idx]))
            except (ValueError, TypeError):
                pass
    if not vals:
        return 0.0
    mean = sum(vals) / len(vals)
    variance = sum((v - mean) ** 2 for v in vals) / len(vals)
    return variance ** 0.5


# ---------------------------------------------------------------------------
# broad-rnext — filter_rows
# ---------------------------------------------------------------------------

def filter_rows(
    data: Any,
    col_name: str,
    value: str,
    *,
    exact: bool = True,
    case_sensitive: bool = True,
) -> dict[str, Any]:
    """Return rows where col_name matches value. Supports exact/substring and case options."""
    result = _load_tsv_data(data)
    if not result["headers"] or col_name not in result["headers"]:
        return {
            "format": "tsv",
            "path": result.get("path", "<bytes>"),
            "row_count": 0,
            "headers": result.get("headers"),
            "rows": [],
        }
    idx = result["headers"].index(col_name)
    matched: list[list[str]] = []
    for row in result["rows"]:
        if idx >= len(row):
            continue
        cell = row[idx]
        cmp_cell = cell if case_sensitive else cell.lower()
        cmp_val = value if case_sensitive else value.lower()
        matches = (cmp_cell == cmp_val) if exact else (cmp_val in cmp_cell)
        if matches:
            matched.append(row)
    return {
        "format": "tsv",
        "path": result.get("path", "<bytes>"),
        "row_count": len(matched),
        "headers": result["headers"],
        "rows": matched,
    }


# ---------------------------------------------------------------------------
# cap-append — append_row
# ---------------------------------------------------------------------------

def append_row(file_path: str | Path, row: list[Any]) -> None:
    """Append a single row to a TSV file. Creates file if it does not exist."""
    def _sanitize(val: Any) -> str:
        return str(val).replace("\t", " ").replace("\n", " ").replace("\r", " ")

    line = "\t".join(_sanitize(c) for c in row) + "\n"
    Path(file_path).open("a", encoding="utf-8").write(line)


# ---------------------------------------------------------------------------
# rnext3 — roundtrip
# ---------------------------------------------------------------------------

def roundtrip(src: Any, dest: str | Path) -> dict[str, Any]:
    """Read TSV from src (bytes or path), write to dest, return the neutral model dict."""
    result = _load_tsv_data(src)
    write_tsv(result.get("rows", []), dest, headers=result.get("headers"))
    return result


# FORMAT_FACTORY_EXECUTION: taskcard=SHQ-L2-001; method=QUEUE_DISPATCHED_EXECUTION; queue_item=shq-q-001; sprint_id=FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001
def append_rows(data: Any, rows: "list[list[str]]") -> "dict[str, Any]":
    """Append multiple rows to a TSV data model (in-memory, returns updated model).

    Unlike append_row() which writes to a file path, this function operates on
    the neutral model dict and returns the updated model. Suitable for batch
    in-memory operations.

    Args:
        data: TSV data dict (with 'rows' key), or raw bytes/path for auto-loading.
        rows: List of rows to append; each row is a list of string values.
              Values are sanitized (tabs/newlines replaced with spaces).

    Returns:
        Updated data model dict with new rows appended and row_count updated.
    """
    if isinstance(data, dict):
        model = data
    else:
        model = _load_tsv_data(data)
    existing: list = list(model.get("rows", []))
    for row in rows:
        sanitized = [
            str(c).replace("\t", " ").replace("\n", " ").replace("\r", " ")
            for c in row
        ]
        existing.append(sanitized)
    model = dict(model)
    model["rows"] = existing
    model["row_count"] = len(existing)
    return model


def find_rows_containing(data: Any, text: str, case_sensitive: bool = True) -> list[int]:
    """Return 0-based indices of data rows where any cell contains text as a substring.

    Args:
        data: TSV data dict, file path, or raw bytes.
        text: The substring to search for in cell values.
        case_sensitive: If False, search is case-insensitive. Default True.

    Returns:
        Sorted list of 0-based row indices with a matching cell.
        Returns empty list if no matches found.
    """
    if isinstance(data, dict):
        model = data
    else:
        model = _load_tsv_data(data)
    rows: list[list[str]] = model.get("rows") or []
    search = text if case_sensitive else text.lower()
    result = []
    for idx, row in enumerate(rows):
        for cell in row:
            haystack = cell if case_sensitive else cell.lower()
            if search in haystack:
                result.append(idx)
                break
    return result


def get_numeric_columns(data: Any) -> list[str]:
    """Return the names of columns whose data rows are all parseable as float.

    A column is considered numeric if every non-empty value in that column
    can be converted to float. Columns with no data rows or all-empty values
    are excluded.

    Args:
        data: TSV data dict, file path, or raw bytes.

    Returns:
        List of column names (from header) that are entirely numeric.
        Returns empty list if no header or no data rows.
    """
    if isinstance(data, dict):
        model = data
    else:
        model = _load_tsv_data(data)
    headers: list[str] = model.get("headers") or []
    rows: list[list[str]] = model.get("rows") or []
    if not headers or not rows:
        return []

    numeric: list[str] = []
    for col_idx, col_name in enumerate(headers):
        values = []
        for row in rows:
            if col_idx < len(row):
                cell = row[col_idx].strip()
                if cell:
                    values.append(cell)
        if not values:
            continue
        all_numeric = True
        for v in values:
            try:
                float(v)
            except (ValueError, TypeError):
                all_numeric = False
                break
        if all_numeric:
            numeric.append(col_name)
    return numeric


def unique_column_values(data: Any, col_name: str) -> list[str]:
    """Return sorted list of unique values in a TSV column."""
    values = get_column_values(data, col_name)
    return sorted(set(values))


# ---------------------------------------------------------------------------
# Analytics functions moved to tsv_analytics.py (TC-HEAL-FORMATS-BATCH1)
# ---------------------------------------------------------------------------
try:
    from .tabular_document import *  # noqa: F401, F403
except ImportError:
    pass
