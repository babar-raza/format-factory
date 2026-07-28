"""
tsv_writer.py — TSV writer for format-factory-tsv.

Public API:
  write_tsv(rows, path, headers=None) — writes TSV to file
  write_tsv_str(rows, headers=None)   — returns TSV string

TSV convention: tabs within field values are illegal. This writer
raises TsvWriteError if any field value contains a tab character.
"""

from __future__ import annotations

from pathlib import Path
from .exceptions import TsvError, TsvParseError, TsvWriteError


def _format_field(value: object) -> str:
    s = "" if value is None else str(value)
    if "\t" in s:
        raise TsvWriteError(f"TSV field value must not contain tab characters: {s!r}")
    return s


def write_tsv_str(
    rows: list[list[object]],
    headers: list[str] | None = None,
) -> str:
    """Serialize rows to TSV string.

    Args:
        rows: Data rows, each a list of field values.
        headers: Optional header row prepended to output.

    Returns:
        TSV string with LF line endings.
    """
    if rows is None:
        raise TsvWriteError("rows must not be None")

    lines: list[str] = []
    if headers is not None:
        lines.append("\t".join(_format_field(h) for h in headers))

    for row in rows:
        lines.append("\t".join(_format_field(f) for f in row))

    return "\n".join(lines) + "\n" if lines else ""


def write_tsv(
    rows: list[list[object]],
    path: str | Path,
    headers: list[str] | None = None,
) -> None:
    """Write TSV rows to a file. Creates parent dirs as needed. UTF-8, no BOM."""
    if not path:
        raise TsvWriteError("path must not be empty")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    content = write_tsv_str(rows, headers=headers)
    p.write_text(content, encoding="utf-8")
