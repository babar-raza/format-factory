"""
fods_cell_iterator.py — Spec-shaped cell iteration for FODS documents.

Authority: ODF 1.3 §9.1 — table:table-cell.
Spec QName: table:table-cell (urn:oasis:names:tc:opendocument:xmlns:table:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .models import FodsCell, FodsSheet
from .parser import parse_fods


def fods_iter_cells(source: "str | Path") -> Iterator[FodsCell]:
    """Yield spec-shaped FodsCell objects for every cell in a FODS document.

    Iterates all sheets, all rows, all cells in document order.

    Args:
        source: Path to a .fods flat XML OpenDocument Spreadsheet file.

    Yields:
        FodsCell instances (spec class: table:table-cell, SAL-FODS-00003).
    """
    model = parse_fods(str(Path(source).resolve()))
    for sheet_dict in model.get("sheets", []):
        sheet = FodsSheet(sheet_dict)
        for row in sheet.rows:
            row_cells = row.get("cells", []) if isinstance(row, dict) else row
            for cell_data in row_cells:
                if isinstance(cell_data, dict):
                    yield FodsCell(cell_data)
