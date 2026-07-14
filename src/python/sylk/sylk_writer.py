"""
sylk_writer.py — SYLK writer for format-factory-sylk.

Public API:
  write_sylk(document, path) — writes SYLK to file
  write_sylk_str(document)   — returns SYLK string

Accepts a SylkDocument (from sylk_parser) or a list of SylkCell objects.
Emits valid SYLK: ID;P header, C;X{col};Y{row};K{value} cell records, E terminator.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class SylkWriteError(Exception):
    """Raised when SYLK output fails."""


def _cell_record(row: int, col: int, value: Any) -> str:
    """Emit a single SYLK cell record."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"C;X{col};Y{row};K{value}"
    escaped = str(value).replace('"', '""')
    return f'C;X{col};Y{row};K"{escaped}"'


def write_sylk_str(document: Any) -> str:
    """Serialize a SylkDocument (or cell list) to SYLK string.

    Args:
        document: SylkDocument with a .cells attribute, or a list of objects
                  with .row, .col, .value attributes.

    Returns:
        SYLK string with LF line endings.
    """
    if document is None:
        raise SylkWriteError("document must not be None")

    cells = getattr(document, "cells", document)
    if not hasattr(cells, "__iter__"):
        raise SylkWriteError("document must have a .cells attribute or be iterable")

    lines: list[str] = ["ID;P"]
    for cell in cells:
        row = getattr(cell, "row", None)
        col = getattr(cell, "col", None)
        val = getattr(cell, "value", None)
        if row is None or col is None:
            raise SylkWriteError(f"Cell missing row or col: {cell!r}")
        lines.append(_cell_record(row, col, val))
    lines.append("E")
    return "\n".join(lines) + "\n"


def write_sylk(document: Any, path: str | Path) -> None:
    """Write a SylkDocument to a SYLK file. Creates parent dirs as needed. UTF-8."""
    if not path:
        raise SylkWriteError("path must not be empty")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    content = write_sylk_str(document)
    p.write_text(content, encoding="utf-8")
