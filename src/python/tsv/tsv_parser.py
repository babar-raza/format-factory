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
