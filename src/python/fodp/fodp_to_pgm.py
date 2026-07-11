"""
fodp_to_pgm.py — Dogfood export: FODP → PGM using Format Factory libraries.

Sprint: FODP-TO-PGM-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-PGM-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fodp.fodp_codec import load as load_fodp  # FF source reader
from pgm.pgm_parser import write_pgm  # FF target writer


def fodp_to_pgm(
    src_path: str | Path,
    dest_path: str | Path
) -> int:
    """Convert a FODP file to a PGM bitmap, one grayscale-row per data row."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(src_path)  # Format Factory fodp reader
    grid = []
    for page in doc.get("pages", []):
        grid.append([page.get("name", "") or "", page.get("title", "") or "",
                     "; ".join(str(t) for t in page.get("text_content", []) if t)])

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


__all__ = ["fodp_to_pgm"]
