"""
sylk_to_fodt.py — Dogfood export: SYLK → FODT using Format Factory libraries.

Reads a SYLK file using Format Factory's SYLK parser and writes each row
as a FODT paragraph using Format Factory's FODT writer.

Each SYLK row becomes one FODT paragraph with cell values joined by ' | '.

Sprint: SYLK-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-FODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "sylk"))

from sylk.sylk_parser import parse_sylk_strict  # FF source reader
from fodt.writer import write_fodt  # FF target writer


def sylk_to_fodt(
    sylk_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " | ",
) -> int:
    """Convert a SYLK file to a FODT flat text document, one paragraph per row.

    SYLK uses 1-based (row, col) coordinates. Cells are rebuilt into a grid
    and written row by row as FODT paragraphs.

    Args:
        sylk_path: Path to the source .slk file.
        dest_path: Path for the output .fodt file (parent dirs created).
        separator: String used to join cell values within a row.

    Returns:
        Number of paragraphs (rows) written.
    """
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(sylk_path)  # Format Factory sylk reader

    grid: dict[int, dict[int, str]] = {}
    for cell in doc.cells:
        r, c = cell.row, cell.col
        grid.setdefault(r, {})[c] = str(cell.value) if cell.value is not None else ""

    blocks: list[dict] = []
    if grid:
        max_row = max(grid)
        max_col = max(c for row_cells in grid.values() for c in row_cells)
        for r in range(1, max_row + 1):
            row_cells = grid.get(r, {})
            row_vals = [row_cells.get(c, "") for c in range(1, max_col + 1)]
            blocks.append({"type": "paragraph", "text": separator.join(row_vals)})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["sylk_to_fodt"]
