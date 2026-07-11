"""
dif_to_fodg.py — Dogfood export: DIF → FODG using Format Factory libraries.

Sprint: DIF-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from dif.dif_parser import parse_dif_strict  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def dif_to_fodg(
    dif_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert a DIF file to a FODG drawing, one page per row."""
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(dif_path)  # Format Factory dif reader

    pages_list = []
    for i, row in enumerate(doc.rows):
        texts = []
        for cell in row:
            raw = str(cell.value) if cell.value is not None else ""
            val = raw[1:-1] if raw.startswith('"') and raw.endswith('"') else raw
            texts.append(val)
        pages_list.append({"name": f"Row{i + 1}", "texts": texts})

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["dif_to_fodg"]
