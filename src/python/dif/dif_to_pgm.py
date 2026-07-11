"""
dif_to_pgm.py — Dogfood export: DIF → PGM using Format Factory libraries.

Sprint: DIF-TO-PGM-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-PGM-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from dif.dif_parser import parse_dif_strict  # FF source reader
from pgm.pgm_parser import write_pgm  # FF target writer


def dif_to_pgm(
    src_path: str | Path,
    dest_path: str | Path
) -> int:
    """Convert a DIF file to a PGM bitmap, one grayscale-row per data row."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(src_path)  # Format Factory dif reader
    grid = []
    for row in doc.rows:
        raw_cells = []
        for c in row:
            raw = str(c.value) if c.value is not None else ""
            raw_cells.append(raw[1:-1] if raw.startswith('"') and raw.endswith('"') else raw)
        grid.append(raw_cells)

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


__all__ = ["dif_to_pgm"]
