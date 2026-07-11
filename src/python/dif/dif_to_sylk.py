"""
dif_to_sylk.py — Dogfood export: DIF → SYLK using Format Factory libraries.

Sprint: DIF-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from dif.dif_parser import parse_dif_strict  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def dif_to_sylk(
    dif_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert a DIF file to a SYLK spreadsheet."""
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(dif_path)  # Format Factory dif reader

    cells: list[SylkCell] = []
    for r, row in enumerate(doc.rows, start=1):
        for c, cell in enumerate(row, start=1):
            raw = str(cell.value) if cell.value is not None else ""
            val = raw[1:-1] if raw.startswith('"') and raw.endswith('"') else raw
            cells.append(SylkCell(row=r, col=c, value=val, value_type="string"))

    max_row = max((cell.row for cell in cells), default=0)
    max_col = max((cell.col for cell in cells), default=0)
    sylk_doc = SylkDocument(cells=cells, rows=max_row, cols=max_col)
    write_sylk(sylk_doc, dest_path)  # Format Factory sylk writer
    return len(doc.rows)


__all__ = ["dif_to_sylk"]
