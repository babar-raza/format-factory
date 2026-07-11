"""
abw_to_pbm.py — Dogfood export: ABW → PBM using Format Factory libraries.

Sprint: ABW-TO-PBM-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-PBM-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from abw.abw_codec import load as load_abw  # FF source reader
from pbm.pbm_parser import write_pbm  # FF target writer


def abw_to_pbm(
    src_path: str | Path,
    dest_path: str | Path
) -> int:
    """Convert a ABW file to a PBM bitmap, one pixel-row per data row."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_abw(src_path)  # Format Factory abw reader
    paras = doc.get("paragraphs", []) if isinstance(doc, dict) else []
    grid = [[str(p)] for p in paras if p is not None]

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


__all__ = ["abw_to_pbm"]
