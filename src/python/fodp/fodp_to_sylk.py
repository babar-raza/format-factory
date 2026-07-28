"""
fodp_to_sylk.py — Dogfood export: FODP → SYLK using Format Factory libraries.

Sprint: FODP-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodp.fodp_codec import load as load_fodp  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def fodp_to_sylk(
    fodp_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert a FODP presentation to a SYLK file, one row per slide."""
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)  # Format Factory fodp reader
    pages = doc.get("pages", [])

    cells: list[SylkCell] = []
    for r, page in enumerate(pages, start=1):
        slide_name = page.get("name", "") or ""
        title_val = page.get("title", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)
        cells.append(SylkCell(row=r, col=1, value=slide_name, value_type="string"))
        cells.append(SylkCell(row=r, col=2, value=title_val, value_type="string"))
        cells.append(SylkCell(row=r, col=3, value=text_content, value_type="string"))

    max_row = max((cell.row for cell in cells), default=0)
    sylk_doc = SylkDocument(cells=cells, rows=max_row, cols=3 if cells else 0)
    write_sylk(sylk_doc, dest_path)  # Format Factory sylk writer
    return max_row


__all__ = ["fodp_to_sylk"]
