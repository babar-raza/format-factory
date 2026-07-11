"""
sylk_to_fodg.py — Dogfood export: SYLK → FODG using Format Factory libraries.

Sprint: SYLK-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from sylk.sylk_parser import parse_sylk_strict  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def sylk_to_fodg(
    sylk_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert a SYLK file to a FODG drawing, one page per row."""
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(sylk_path)  # Format Factory sylk reader

    # Rebuild rows from cells (SYLK is 1-based)
    rows: dict[int, dict[int, str]] = {}
    for cell in doc.cells:
        rows.setdefault(cell.row, {})[cell.col] = str(cell.value) if cell.value is not None else ""

    pages_list = []
    for r in sorted(rows):
        texts = [rows[r][c] for c in sorted(rows[r])]
        pages_list.append({"name": f"Row{r}", "texts": texts})

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["sylk_to_fodg"]
