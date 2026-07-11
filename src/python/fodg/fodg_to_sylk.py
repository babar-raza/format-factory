"""
fodg_to_sylk.py — Dogfood export: FODG → SYLK using Format Factory libraries.

Sprint: FODG-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODG-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fodg.fodg_codec import load as load_fodg  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def fodg_to_sylk(
    fodg_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert a FODG drawing to a SYLK file, one row per page."""
    fodg_path = Path(fodg_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(fodg_path)  # Format Factory fodg reader
    pages = doc.get("pages", [])

    cells: list[SylkCell] = []
    for r, page in enumerate(pages, start=1):
        page_name = page.get("name", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = " ".join(str(t) for t in text_parts if t)
        shape_count = str(page.get("shape_count", 0))
        cells.append(SylkCell(row=r, col=1, value=page_name, value_type="string"))
        cells.append(SylkCell(row=r, col=2, value=text_content, value_type="string"))
        cells.append(SylkCell(row=r, col=3, value=shape_count, value_type="string"))

    max_row = max((cell.row for cell in cells), default=0)
    sylk_doc = SylkDocument(cells=cells, rows=max_row, cols=3 if cells else 0)
    write_sylk(sylk_doc, dest_path)  # Format Factory sylk writer
    return max_row


__all__ = ["fodg_to_sylk"]
