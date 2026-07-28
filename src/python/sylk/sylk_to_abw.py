"""
sylk_to_abw.py — Dogfood export: SYLK → ABW using Format Factory libraries.

Reads a SYLK file using Format Factory's SYLK parser and writes each row
as an ABW paragraph using Format Factory's ABW writer.

Each SYLK row becomes one ABW paragraph with cell values joined by ' | '.

Sprint: SYLK-TO-ABW-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-ABW-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from sylk.sylk_parser import parse_sylk_strict  # FF source reader
from abw.abw_codec import write_abw  # FF target writer


def sylk_to_abw(
    sylk_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " | ",
) -> int:
    """Convert a SYLK file to an ABW document, one paragraph per row.

    The SYLK cell grid is rebuilt into row-major order. Cell values are
    joined with the separator string.

    Args:
        sylk_path: Path to the source .slk file.
        dest_path: Path for the output .abw file (parent dirs created).
        separator: String used to join cell values within a row.

    Returns:
        Number of paragraphs (rows) written.
    """
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(sylk_path)  # Format Factory sylk reader

    # Rebuild grid from sparse cell list (1-based row/col)
    grid: dict[int, dict[int, str]] = {}
    for cell in doc.cells:
        r, c = cell.row, cell.col
        grid.setdefault(r, {})[c] = str(cell.value) if cell.value is not None else ""

    paragraphs: list[str] = []
    if grid:
        max_row = max(grid)
        max_col = max(c for row_cells in grid.values() for c in row_cells)
        for row_idx in range(1, max_row + 1):
            row_cells = grid.get(row_idx, {})
            row_vals = [row_cells.get(col_idx, "") for col_idx in range(1, max_col + 1)]
            paragraphs.append(separator.join(row_vals))

    model = {"is_abw": True, "paragraphs": paragraphs}
    write_abw(model, dest_path)  # Format Factory abw writer
    return len(paragraphs)


__all__ = ["sylk_to_abw"]
