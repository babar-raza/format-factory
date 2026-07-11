"""
fodt_to_sylk.py — Dogfood export: FODT → SYLK using Format Factory libraries.

Sprint: FODT-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fodt.parser import parse_fodt  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def fodt_to_sylk(
    fodt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert a FODT document to a SYLK file, one row per block (type, text)."""
    fodt_path = Path(fodt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fodt(str(fodt_path))  # Format Factory fodt reader
    blocks = doc.get("blocks", [])

    cells: list[SylkCell] = []
    row_idx = 1
    for block in blocks:
        text = block.get("text", "") or ""
        if skip_empty and not text.strip():
            continue
        block_type = block.get("type", "paragraph") or "paragraph"
        cells.append(SylkCell(row=row_idx, col=1, value=block_type, value_type="string"))
        cells.append(SylkCell(row=row_idx, col=2, value=text, value_type="string"))
        row_idx += 1

    max_row = max((cell.row for cell in cells), default=0)
    sylk_doc = SylkDocument(cells=cells, rows=max_row, cols=2 if cells else 0)
    write_sylk(sylk_doc, dest_path)  # Format Factory sylk writer
    return max_row


__all__ = ["fodt_to_sylk"]
