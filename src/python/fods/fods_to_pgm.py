"""
fods_to_pgm.py — Dogfood export: FODS → PGM using Format Factory libraries.

Sprint: FODS-TO-PGM-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODS-TO-PGM-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "fods"))
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fods.parser import parse_fods_strict  # FF source reader
from pgm.pgm_parser import write_pgm  # FF target writer


def fods_to_pgm(
    src_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
) -> int:
    """Convert a FODS file to a PGM bitmap, one grayscale-row per data row."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fods_strict(src_path)  # Format Factory fods reader
    sheets = doc.get("sheets", []) if isinstance(doc, dict) else []
    grid = []
    if sheets:
        for row in sheets[0].get("rows", []):
            grid.append([str(c.get("value", "")) for c in row.get("cells", []) if c.get("value") is not None])

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


__all__ = ["fods_to_pgm"]
