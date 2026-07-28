"""
fodg_to_dif.py — Dogfood export: FODG → DIF using Format Factory libraries.

Sprint: FODG-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODG-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodg.fodg_codec import load as load_fodg  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def fodg_to_dif(
    fodg_path: str | Path,
    dest_path: str | Path,
    *,
    title: str = "FODG Export",
) -> int:
    """Convert a FODG drawing to a DIF file, one row per page."""
    fodg_path = Path(fodg_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(fodg_path)  # Format Factory fodg reader
    pages = doc.get("pages", [])

    dif_rows = []
    for page in pages:
        page_name = page.get("name", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = " ".join(str(t) for t in text_parts if t)
        shape_count = str(page.get("shape_count", 0))
        dif_rows.append([
            DifCell(value=page_name, value_type="string"),
            DifCell(value=text_content, value_type="string"),
            DifCell(value=shape_count, value_type="string"),
        ])

    dif_doc = DifDocument(title=title, rows=dif_rows)
    write_dif(dif_doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["fodg_to_dif"]
