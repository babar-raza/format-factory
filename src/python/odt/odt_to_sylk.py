"""
odt_to_sylk.py — Dogfood export: ODT → SYLK using Format Factory libraries.

Sprint: ODT-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODT-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from odt.odt_parser import OdtHeading, parse_odt_strict  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def odt_to_sylk(
    odt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert an ODT document to a SYLK file, one row per element (type, text)."""
    odt_path = Path(odt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_odt_strict(odt_path)  # Format Factory odt reader

    cells: list[SylkCell] = []
    row_idx = 1
    for elem in doc.elements:
        text = elem.text if elem.text else ""
        if skip_empty and not text.strip():
            continue
        elem_type = "heading" if isinstance(elem, OdtHeading) else "paragraph"
        cells.append(SylkCell(row=row_idx, col=1, value=elem_type, value_type="string"))
        cells.append(SylkCell(row=row_idx, col=2, value=text, value_type="string"))
        row_idx += 1

    max_row = max((cell.row for cell in cells), default=0)
    sylk_doc = SylkDocument(cells=cells, rows=max_row, cols=2 if cells else 0)
    write_sylk(sylk_doc, dest_path)  # Format Factory sylk writer
    return max_row


__all__ = ["odt_to_sylk"]
