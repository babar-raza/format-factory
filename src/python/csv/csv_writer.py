"""
csv_writer.py — CSV writer for format-factory-csv.

Public API:
  write_csv(rows, headers=None)  — returns CSV string (RFC 4180)
  write_csv_to_file(rows, path, headers=None) — writes CSV to file

NOTE: Does NOT import the stdlib 'csv' module (same reason as csv_parser.py).

Sprint: MAINSTREAM-MEGATRAIN-20260610
License: Apache-2.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class CsvWriteError(Exception):
    """Raised when CSV output fails."""


def _escape_field(value: str | None) -> str:
    """Escape a single CSV field per RFC 4180."""
    if value is None:
        return ""
    s = str(value)
    if not s:
        return ""
    needs_quoting = any(c in s for c in (",", '"', "\n", "\r"))
    if needs_quoting:
        return '"' + s.replace('"', '""') + '"'
    return s


def write_csv(
    rows: list[list[str | None]],
    headers: list[str] | None = None,
    delimiter: str = ",",
) -> str:
    """Serialize rows to RFC 4180 CSV string.

    Args:
        rows: Data rows, each a list of field values.
        headers: Optional header row prepended to output.
        delimiter: Field delimiter (default comma).

    Returns:
        CSV string with LF line endings.
    """
    if rows is None:
        raise CsvWriteError("rows must not be None")

    lines: list[str] = []
    if headers is not None:
        lines.append(delimiter.join(_escape_field(h) for h in headers))

    for row in rows:
        lines.append(delimiter.join(_escape_field(f) for f in row))

    return "\n".join(lines) + "\n" if lines else ""


def write_csv_to_file(
    rows: list[list[str | None]],
    path: str | Path,
    headers: list[str] | None = None,
    delimiter: str = ",",
) -> None:
    """Write CSV rows to a file. Creates parent dirs as needed. UTF-8, no BOM."""
    if not path:
        raise CsvWriteError("path must not be empty")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    content = write_csv(rows, headers=headers, delimiter=delimiter)
    p.write_text(content, encoding="utf-8")


def parse_and_rewrite(
    input_path: str | Path,
    output_path: str | Path,
    transform: Any = None,
) -> dict[str, Any]:
    """Roundtrip: read CSV, optionally transform, write back.

    Args:
        input_path: Source CSV file.
        output_path: Destination CSV file.
        transform: Optional callable(rows, headers) -> (rows, headers).

    Returns:
        Dict with row_count, column_count.
    """
    from .csv_parser import parse_csv_strict

    result = parse_csv_strict(input_path)
    headers = result.get("headers")
    rows = result.get("rows", [])

    if transform is not None:
        rows, headers = transform(rows, headers)

    write_csv_to_file(rows, output_path, headers=headers, delimiter=result.get("delimiter", ","))

    return {
        "row_count": len(rows),
        "column_count": len(headers) if headers else (len(rows[0]) if rows else 0),
    }
