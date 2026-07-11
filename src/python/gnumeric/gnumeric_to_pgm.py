"""
gnumeric_to_pgm.py — Dogfood export: GNUMERIC → PGM using Format Factory libraries.

Sprint: GNUMERIC-TO-PGM-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-GNUMERIC-TO-PGM-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from gnumeric.gnumeric_codec import load as load_gnumeric  # FF source reader
from pgm.pgm_parser import write_pgm  # FF target writer


def gnumeric_to_pgm(
    src_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
) -> int:
    """Convert a GNUMERIC file to a PGM bitmap, one grayscale-row per data row."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_gnumeric(src_path)  # Format Factory gnumeric reader
    sheets = doc.get("sheets", []) if isinstance(doc, dict) else []
    grid = []
    if sheets:
        cg = sheets[0].get("cell_grid", {})
        rows_map = {}
        for (r0, c0), val in cg.items():
            rows_map.setdefault(r0, {})[c0] = str(val)
        for r in sorted(rows_map):
            cs = rows_map[r]
            grid.append([cs.get(c, "") for c in range(max(cs) + 1)])

    height = len(grid) if grid else 1
    width = max((len(row) for row in grid), default=1) if grid else 1
    pixels: list[int] = []
    for row in grid:
        padded = row + [""] * (width - len(row))
        pixels.extend([min(255, len(v)) for v in padded])
    if not pixels:
        pixels = [0] * (width * height)

    write_pgm(pixels, width, height, 255, dest_path)  # Format Factory pgm writer
    return height


__all__ = ["gnumeric_to_pgm"]
