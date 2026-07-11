"""
fods_to_sylk.py — Dogfood export: FODS → SYLK using Format Factory libraries.

Sprint: FODS-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODS-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "fods"))
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fods.parser import parse_fods_strict  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def fods_to_sylk(
    fods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
) -> int:
    """Convert a FODS flat spreadsheet to a SYLK file."""
    fods_path = Path(fods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fods_strict(fods_path)  # Format Factory fods reader
    sheets = doc.get("sheets", []) if isinstance(doc, dict) else []

    cells: list[SylkCell] = []
    if sheets and sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        for r, row in enumerate(sheet.get("rows", []), start=1):
            for c, cell in enumerate(row.get("cells", []), start=1):
                val = str(cell.get("value", "")) if cell.get("value") is not None else ""
                cells.append(SylkCell(row=r, col=c, value=val, value_type="string"))

    max_row = max((cell.row for cell in cells), default=0)
    max_col = max((cell.col for cell in cells), default=0)
    sylk_doc = SylkDocument(cells=cells, rows=max_row, cols=max_col)
    write_sylk(sylk_doc, dest_path)  # Format Factory sylk writer
    return max_row


__all__ = ["fods_to_sylk"]
