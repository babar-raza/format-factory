"""
fodt_to_fodg.py — Dogfood export: FODT → FODG using Format Factory libraries.

Sprint: FODT-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fodt.parser import parse_fodt  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def fodt_to_fodg(
    fodt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert a FODT document to a FODG drawing, one page per block."""
    fodt_path = Path(fodt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fodt(str(fodt_path))  # Format Factory fodt reader
    blocks = doc.get("blocks", [])

    pages_list = []
    for i, block in enumerate(blocks):
        text = block.get("text", "") or ""
        if skip_empty and not text.strip():
            continue
        block_type = block.get("type", "paragraph") or "paragraph"
        pages_list.append({"name": f"{block_type}{i + 1}", "texts": [block_type, text]})

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["fodt_to_fodg"]
