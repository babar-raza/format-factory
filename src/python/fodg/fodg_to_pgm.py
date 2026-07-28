"""
fodg_to_pgm.py — Dogfood export: FODG → PGM using Format Factory libraries.

Sprint: FODG-TO-PGM-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODG-TO-PGM-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodg.fodg_codec import load as load_fodg  # FF source reader
from pgm.pgm_parser import write_pgm  # FF target writer


def fodg_to_pgm(
    src_path: str | Path,
    dest_path: str | Path
) -> int:
    """Convert a FODG file to a PGM bitmap, one grayscale-row per data row."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(src_path)  # Format Factory fodg reader
    grid = []
    for page in doc.get("pages", []):
        grid.append([page.get("name", "") or "",
                     " ".join(str(t) for t in page.get("text_content", []) if t),
                     str(page.get("shape_count", 0))])

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


__all__ = ["fodg_to_pgm"]
