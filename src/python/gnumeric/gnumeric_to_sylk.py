"""
gnumeric_to_sylk.py — Dogfood export: Gnumeric → SYLK using Format Factory libraries.

Sprint: GNUMERIC-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-GNUMERIC-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from gnumeric.gnumeric_codec import load as load_gnumeric  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def gnumeric_to_sylk(
    gnumeric_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
) -> int:
    """Convert a Gnumeric spreadsheet to a SYLK file."""
    gnumeric_path = Path(gnumeric_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_gnumeric(gnumeric_path)  # Format Factory gnumeric reader
    sheets = doc.get("sheets", []) if isinstance(doc, dict) else []

    cells: list[SylkCell] = []
    if sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        cell_grid = sheet.get("cell_grid", {})
        for (r0, c0), val in cell_grid.items():
            # gnumeric cell_grid is 0-based; SYLK is 1-based
            cells.append(SylkCell(row=r0 + 1, col=c0 + 1, value=str(val), value_type="string"))

    max_row = max((cell.row for cell in cells), default=0)
    max_col = max((cell.col for cell in cells), default=0)
    sylk_doc = SylkDocument(cells=cells, rows=max_row, cols=max_col)
    write_sylk(sylk_doc, dest_path)  # Format Factory sylk writer
    return max_row


__all__ = ["gnumeric_to_sylk"]
