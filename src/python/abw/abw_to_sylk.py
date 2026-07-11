"""
abw_to_sylk.py — Dogfood export: ABW → SYLK using Format Factory libraries.

Sprint: ABW-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from abw.abw_codec import load as load_abw  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def abw_to_sylk(
    abw_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert an ABW document to a SYLK file, one row per paragraph."""
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_abw(abw_path)  # Format Factory abw reader
    paragraphs = doc.get("paragraphs", []) if isinstance(doc, dict) else []

    cells: list[SylkCell] = []
    for r, para in enumerate(paragraphs, start=1):
        text = str(para) if para is not None else ""
        cells.append(SylkCell(row=r, col=1, value=text, value_type="string"))

    max_row = max((cell.row for cell in cells), default=0)
    sylk_doc = SylkDocument(cells=cells, rows=max_row, cols=1 if cells else 0)
    write_sylk(sylk_doc, dest_path)  # Format Factory sylk writer
    return max_row


__all__ = ["abw_to_sylk"]
