"""
fodt_to_ppm.py — Dogfood export: FODT → PPM using Format Factory libraries.

Sprint: FODT-TO-PPM-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-PPM-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fodt.parser import parse_fodt  # FF source reader
from ppm.ppm_parser import write_ppm  # FF target writer


def fodt_to_ppm(
    src_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert a FODT file to a PPM bitmap, one RGB-row per data row."""
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
    pixels: list[tuple[int, int, int]] = []
    for row in grid:
        padded = row + [""] * (width - len(row))
        pixels.extend([(min(255, ord(v[0:1] or chr(0))), min(255, ord(v[1:2] or chr(0))), min(255, len(v))) for v in padded])
    if not pixels:
        pixels = [(0, 0, 0)] * (width * height)

    write_ppm(pixels, width, height, 255, dest_path)  # Format Factory ppm writer
    return height


__all__ = ["fodt_to_ppm"]
