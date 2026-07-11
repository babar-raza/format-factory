"""
sylk_to_odt.py — Dogfood export: SYLK → ODT using Format Factory libraries.

Reads a SYLK (.slk) file using Format Factory's SYLK parser and writes each
row as an ODT paragraph using Format Factory's ODT writer.

SYLK cells use 1-based row/col coordinates. Cells are assembled into a grid,
then each row becomes one ODT paragraph with cell values joined by a separator.

Sprint: SYLK-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "sylk"))
sys.path.insert(0, str(_REPO))

from sylk.sylk_parser import parse_sylk_strict  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def sylk_to_odt(
    sylk_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = "\t",
) -> int:
    """Convert a SYLK file to an ODT document, one paragraph per SYLK row.

    Args:
        sylk_path: Path to the source .slk file.
        dest_path: Path for the output .odt file (parent dirs created).
        separator: String used to join cell values within each paragraph.

    Returns:
        Number of paragraphs written.
    """
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(sylk_path)  # Format Factory sylk reader

    if not doc.cells:
        write_odt([], dest_path)  # Format Factory odt writer
        return 0

    # Build grid from 1-based (row, col) coords
    grid: dict[int, dict[int, str]] = {}
    for cell in doc.cells:
        r, c = cell.row, cell.col
        grid.setdefault(r, {})[c] = str(cell.value) if cell.value is not None else ""

    max_row = max(grid)
    max_col = max(c for row_cells in grid.values() for c in row_cells)

    paragraphs: list[str] = []
    for r in range(1, max_row + 1):
        row_cells = grid.get(r, {})
        parts = [row_cells.get(c, "") for c in range(1, max_col + 1)]
        paragraphs.append(separator.join(parts))

    write_odt(paragraphs, dest_path)  # Format Factory odt writer
    return len(paragraphs)


__all__ = ["sylk_to_odt"]
