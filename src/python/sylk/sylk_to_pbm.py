"""
sylk_to_pbm.py — Dogfood export: SYLK → PBM using Format Factory libraries.

Sprint: SYLK-TO-PBM-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-PBM-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from sylk.sylk_parser import parse_sylk_strict  # FF source reader
from pbm.pbm_parser import write_pbm  # FF target writer


def sylk_to_pbm(
    src_path: str | Path,
    dest_path: str | Path
) -> int:
    """Convert a SYLK file to a PBM bitmap, one pixel-row per data row."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(src_path)  # Format Factory sylk reader
    rows_map = {}
    for cell in doc.cells:
        rows_map.setdefault(cell.row, {})[cell.col] = str(cell.value) if cell.value is not None else ""
    grid = []
    for r in sorted(rows_map):
        cs = rows_map[r]
        grid.append([cs.get(c, "") for c in range(1, max(cs) + 1)])

    height = len(grid) if grid else 1
    width = max((len(row) for row in grid), default=1) if grid else 1
    pixels: list[int] = []
    for row in grid:
        padded = row + [""] * (width - len(row))
        pixels.extend([1 if v.strip() else 0 for v in padded])
    if not pixels:
        pixels = [0] * (width * height)

    write_pbm(pixels, width, height, dest_path)  # Format Factory pbm writer
    return height


__all__ = ["sylk_to_pbm"]
