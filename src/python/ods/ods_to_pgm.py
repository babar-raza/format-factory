"""
ods_to_pgm.py — Dogfood export: ODS → PGM using Format Factory libraries.

Sprint: ODS-TO-PGM-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODS-TO-PGM-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from ods.ods_parser import parse_ods_strict  # FF source reader
from pgm.pgm_parser import write_pgm  # FF target writer


def ods_to_pgm(
    src_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
) -> int:
    """Convert a ODS file to a PGM bitmap, one grayscale-row per data row."""
    src_path = Path(src_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_ods_strict(src_path)  # Format Factory ods reader
    sheets = doc.sheets if hasattr(doc, "sheets") else []
    grid = []
    if sheets:
        for row in (sheets[0].rows if hasattr(sheets[0], "rows") else []):
            cells = row.cells if hasattr(row, "cells") else []
            grid.append([str(c.value) if c.value is not None else "" for c in cells])

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


__all__ = ["ods_to_pgm"]
