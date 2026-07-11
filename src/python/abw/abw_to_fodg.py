"""
abw_to_fodg.py — Dogfood export: ABW → FODG using Format Factory libraries.

Sprint: ABW-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from abw.abw_codec import load as load_abw  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def abw_to_fodg(
    abw_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert an ABW document to a FODG drawing, one page per paragraph."""
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_abw(abw_path)  # Format Factory abw reader
    paragraphs = doc.get("paragraphs", []) if isinstance(doc, dict) else []

    pages_list = [
        {"name": f"Para{i + 1}", "texts": [str(para)]}
        for i, para in enumerate(paragraphs)
        if para is not None
    ]

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["abw_to_fodg"]
