"""
fodp_to_dif.py — Dogfood export: FODP → DIF using Format Factory libraries.

Sprint: FODP-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodp.fodp_codec import load as load_fodp  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def fodp_to_dif(
    fodp_path: str | Path,
    dest_path: str | Path,
    *,
    title: str = "FODP Export",
) -> int:
    """Convert a FODP presentation to a DIF file, one row per slide."""
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)  # Format Factory fodp reader
    pages = doc.get("pages", [])

    dif_rows = []
    for page in pages:
        slide_name = page.get("name", "") or ""
        title_val = page.get("title", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)
        dif_rows.append([
            DifCell(value=slide_name, value_type="string"),
            DifCell(value=title_val, value_type="string"),
            DifCell(value=text_content, value_type="string"),
        ])

    dif_doc = DifDocument(title=title, rows=dif_rows)
    write_dif(dif_doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["fodp_to_dif"]
