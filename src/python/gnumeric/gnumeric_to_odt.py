"""
gnumeric_to_odt.py — Dogfood export: Gnumeric → ODT using Format Factory libraries.

Reads a Gnumeric (.gnumeric) file using Format Factory's Gnumeric codec and writes
each row as an ODT paragraph using Format Factory's ODT writer.

Each row in the selected sheet's cell_grid becomes one ODT paragraph, with cell
values joined by a configurable separator.

Sprint: GNUMERIC-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-GNUMERIC-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "gnumeric"))
sys.path.insert(0, str(_REPO))

from gnumeric.gnumeric_codec import load as load_gnumeric  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def gnumeric_to_odt(
    gnumeric_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    separator: str = "\t",
    include_row_index: bool = False,
) -> int:
    """Convert a Gnumeric spreadsheet to an ODT document.

    Args:
        gnumeric_path: Path to the source .gnumeric file.
        dest_path: Path for the output .odt file (parent dirs created).
        sheet_index: Which sheet to export (0-based, default 0).
        separator: String used to join cell values within each paragraph.
        include_row_index: When True, prepend a 0-based row number to each paragraph.

    Returns:
        Number of paragraphs written.
    """
    from gnumeric.exceptions import GnumericError

    gnumeric_path = Path(gnumeric_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_gnumeric(gnumeric_path)  # Format Factory gnumeric reader

    sheets: list = model.get("sheets", [])
    if not sheets:
        write_odt([], dest_path)  # Format Factory odt writer
        return 0

    if sheet_index < 0 or sheet_index >= len(sheets):
        raise GnumericError(
            f"sheet_index {sheet_index} out of range (0..{len(sheets) - 1})"
        )

    sheet = sheets[sheet_index]
    cell_grid: dict = sheet.get("cell_grid", {})

    if not cell_grid:
        write_odt([], dest_path)  # Format Factory odt writer
        return 0

    max_row = max(r for r, c in cell_grid)
    max_col = max(c for r, c in cell_grid)

    paragraphs: list[str] = []
    for row_idx in range(max_row + 1):
        parts: list[str] = []
        if include_row_index:
            parts.append(str(row_idx))
        for col_idx in range(max_col + 1):
            parts.append(str(cell_grid.get((row_idx, col_idx), "")))
        paragraphs.append(separator.join(parts))

    write_odt(paragraphs, dest_path)  # Format Factory odt writer
    return len(paragraphs)


__all__ = ["gnumeric_to_odt"]
