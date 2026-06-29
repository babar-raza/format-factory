"""
sylk_cell_iterator.py — Spec-shaped cell iteration for SYLK documents.

Authority: SYLK (Symbolic Link) format specification.
Spec QName: sylk:cell (urn:format:sylk:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .sylk_parser import parse_sylk_strict
from .spec.row.cell import Cell


def sylk_iter_cells(file_path: "str | Path") -> Iterator[Cell]:
    """Yield spec-shaped Cell objects for every cell in a SYLK document.

    Cells are yielded in row-major order (sorted by row, then column).

    Args:
        file_path: Path to a SYLK (.slk) file.

    Yields:
        Cell instances (spec class: sylk:cell).

    Raises:
        SylkError subclasses on parse failure.
    """
    doc = parse_sylk_strict(file_path)
    for raw in sorted(doc.cells, key=lambda c: (c.row, c.col)):
        yield Cell(row=raw.row, col=raw.col, value=raw.value)
