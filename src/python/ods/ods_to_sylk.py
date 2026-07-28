"""
ods_to_sylk.py — Dogfood export: ODS → SYLK using Format Factory libraries.

Sprint: ODS-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODS-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ods.ods_parser import parse_ods_strict  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def ods_to_sylk(
    ods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
) -> int:
    """Convert an ODS spreadsheet to a SYLK file."""
    ods_path = Path(ods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_ods_strict(ods_path)  # Format Factory ods reader

    cells: list[SylkCell] = []
    sheets = doc.sheets if hasattr(doc, "sheets") else []
    if sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        rows = sheet.rows if hasattr(sheet, "rows") else []
        for r, row in enumerate(rows, start=1):
            row_cells = row.cells if hasattr(row, "cells") else []
            for c, cell in enumerate(row_cells, start=1):
                val = str(cell.value) if cell.value is not None else ""
                cells.append(SylkCell(row=r, col=c, value=val, value_type="string"))

    max_row = max((cell.row for cell in cells), default=0)
    max_col = max((cell.col for cell in cells), default=0)
    sylk_doc = SylkDocument(cells=cells, rows=max_row, cols=max_col)
    write_sylk(sylk_doc, dest_path)  # Format Factory sylk writer
    return max_row


__all__ = ["ods_to_sylk"]
