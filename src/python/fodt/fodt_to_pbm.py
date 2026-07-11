"""
fodt_to_pbm.py — Dogfood export: FODT → PBM using Format Factory libraries.

Sprint: FODT-TO-PBM-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-PBM-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fodt.parser import parse_fodt  # FF source reader
from pbm.pbm_parser import write_pbm  # FF target writer


def fodt_to_pbm(
    src_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert a FODT file to a PBM bitmap, one pixel-row per data row."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fodt(str(src_path))  # Format Factory fodt reader
    grid = []
    for block in doc.get("blocks", []):
        text = block.get("text", "") or ""
        if skip_empty and not text.strip():
            continue
        grid.append([block.get("type", "paragraph") or "paragraph", text])

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


__all__ = ["fodt_to_pbm"]
