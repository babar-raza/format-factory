"""
sylk_to_ppm.py — Dogfood export: SYLK → PPM using Format Factory libraries.

Sprint: SYLK-TO-PPM-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-PPM-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from sylk.sylk_parser import parse_sylk_strict  # FF source reader
from ppm.ppm_parser import write_ppm  # FF target writer


def sylk_to_ppm(
    src_path: str | Path,
    dest_path: str | Path
) -> int:
    """Convert a SYLK file to a PPM bitmap, one RGB-row per data row."""
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
    pixels: list[tuple[int, int, int]] = []
    for row in grid:
        padded = row + [""] * (width - len(row))
        pixels.extend([(min(255, ord(v[0:1] or chr(0))), min(255, ord(v[1:2] or chr(0))), min(255, len(v))) for v in padded])
    if not pixels:
        pixels = [(0, 0, 0)] * (width * height)

    write_ppm(pixels, width, height, 255, dest_path)  # Format Factory ppm writer
    return height


__all__ = ["sylk_to_ppm"]
