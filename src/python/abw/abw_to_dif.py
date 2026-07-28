"""
abw_to_dif.py — Dogfood export: ABW → DIF using Format Factory libraries.

Sprint: ABW-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from abw.abw_codec import load as load_abw  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def abw_to_dif(
    abw_path: str | Path,
    dest_path: str | Path,
    *,
    title: str = "ABW Export",
) -> int:
    """Convert an ABW document to a DIF file, one row per paragraph."""
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_abw(abw_path)  # Format Factory abw reader
    paragraphs = model.get("paragraphs", [])

    dif_rows = []
    for para in paragraphs:
        text = para.get("text", "") if isinstance(para, dict) else str(para)
        dif_rows.append([DifCell(value=text, value_type="string")])

    doc = DifDocument(title=title, rows=dif_rows)
    write_dif(doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["abw_to_dif"]
