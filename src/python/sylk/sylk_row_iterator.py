"""
sylk_row_iterator.py — Spec-shaped row iteration for SYLK documents.

Authority: SYLK format — R (row) record.
Spec QName: sylk:row (urn:format:sylk:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .sylk_parser import parse_sylk_strict
from .spec.row.row import Row


def sylk_iter_rows(source: "str | Path") -> Iterator[Row]:
    """Yield spec-shaped Row objects for every row in a SYLK document.

    Cells are grouped by row index and yielded in order.

    Args:
        source: Path to a .slk SYLK file.

    Yields:
        Row instances (spec class: sylk:row, FACT-SYLK-002).
    """
    doc = parse_sylk_strict(str(Path(source).resolve()))
    rows_dict: dict[int, list] = {}
    for cell in doc.cells:
        row_idx = cell.row
        rows_dict.setdefault(row_idx, []).append(cell.value)
    for row_idx in sorted(rows_dict):
        yield Row(row_idx, rows_dict[row_idx])
