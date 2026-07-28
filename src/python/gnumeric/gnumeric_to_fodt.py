"""
gnumeric_to_fodt.py — Dogfood export: Gnumeric → FODT using Format Factory libraries.

Reads a Gnumeric file using Format Factory's Gnumeric codec and writes each row
as a FODT paragraph using Format Factory's FODT writer.

Each Gnumeric row becomes one FODT paragraph with cell values joined by ' | '.

Sprint: GNUMERIC-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-GNUMERIC-TO-FODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from gnumeric.gnumeric_codec import load as load_gnumeric  # FF source reader
from fodt.writer import write_fodt  # FF target writer


def gnumeric_to_fodt(
    gnumeric_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    separator: str = " | ",
) -> int:
    """Convert a Gnumeric file to a FODT flat text document, one paragraph per row.

    Each row from the first (or selected) sheet becomes one FODT paragraph.
    Cell values are joined with the separator string.

    Args:
        gnumeric_path: Path to the source .gnumeric file.
        dest_path: Path for the output .fodt file (parent dirs created).
        sheet_index: Which sheet to export (0-based, default 0).
        separator: String used to join cell values within a row.

    Returns:
        Number of paragraphs (rows) written.
    """
    gnumeric_path = Path(gnumeric_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_gnumeric(gnumeric_path)  # Format Factory gnumeric reader
    sheets = model.get("sheets", [])

    blocks: list[dict] = []
    if sheets and sheet_index < len(sheets):
        cell_grid: dict = sheets[sheet_index].get("cell_grid", {})
        if cell_grid:
            max_row = max(r for r, c in cell_grid)
            max_col = max(c for r, c in cell_grid)
            for row_idx in range(max_row + 1):
                row_vals = [
                    str(cell_grid.get((row_idx, col_idx), ""))
                    for col_idx in range(max_col + 1)
                ]
                blocks.append({"type": "paragraph", "text": separator.join(row_vals)})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["gnumeric_to_fodt"]
