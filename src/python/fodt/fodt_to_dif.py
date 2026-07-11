"""
fodt_to_dif.py — Dogfood export: FODT → DIF using Format Factory libraries.

Sprint: FODT-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodt"))
sys.path.insert(0, str(_REPO))

from fodt.parser import parse_fodt  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def fodt_to_dif(
    fodt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
    title: str = "FODT Export",
) -> int:
    """Convert a FODT document to a DIF file, one row per block (type, text)."""
    fodt_path = Path(fodt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fodt(str(fodt_path))  # Format Factory fodt reader
    blocks = doc.get("blocks", [])

    dif_rows = []
    for block in blocks:
        text = block.get("text", "") or ""
        if skip_empty and not text.strip():
            continue
        block_type = block.get("type", "paragraph") or "paragraph"
        dif_rows.append([
            DifCell(value=block_type, value_type="string"),
            DifCell(value=text, value_type="string"),
        ])

    dif_doc = DifDocument(title=title, rows=dif_rows)
    write_dif(dif_doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["fodt_to_dif"]
