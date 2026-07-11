"""
sylk_to_ods.py — Dogfood export: SYLK → ODS using Format Factory libraries.

Reads a SYLK file using Format Factory's SYLK parser and writes it as an ODS
spreadsheet using Format Factory's ODS writer.

Each SYLK row becomes one ODS row.

Sprint: SYLK-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "sylk"))

from sylk.sylk_parser import parse_sylk_strict  # FF source reader
from ods.ods_parser import OdsCell, OdsDocument, OdsRow, OdsSheet  # FF ODS model
from ods.ods_writer import write_ods  # FF target writer


def sylk_to_ods(
    sylk_path: str | Path,
    dest_path: str | Path,
    *,
    use_first_row_as_headers: bool = True,
    include_row_index: bool = False,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a SYLK file to an ODS spreadsheet.

    SYLK uses 1-based (row, col) coordinates. Cells are collected into a grid
    and written row by row. The first row can optionally become the ODS header.

    Args:
        sylk_path: Path to the source .slk file.
        dest_path: Path for the output .ods file (parent dirs created).
        use_first_row_as_headers: When True, the first SYLK row is written as
            the first ODS row (no special treatment — SYLK has no header flag).
        include_row_index: When True, prepends a 1-based row number column.
        sheet_name: Name of the output sheet (default "Sheet1").

    Returns:
        Number of data rows written.
    """
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(sylk_path)  # Format Factory sylk reader

    # Build a grid: {row: {col: value_str}}
    grid: dict[int, dict[int, str]] = {}
    for cell in doc.cells:
        r, c = cell.row, cell.col
        grid.setdefault(r, {})[c] = str(cell.value) if cell.value is not None else ""

    if not grid:
        sheet = OdsSheet(name=sheet_name, rows=[])
        document = OdsDocument(sheets=[sheet])
        write_ods(document, dest_path)
        return 0

    max_row = max(grid)
    max_col = max(c for row_cells in grid.values() for c in row_cells)

    ods_rows: list[OdsRow] = []
    for r in range(1, max_row + 1):
        row_cells = grid.get(r, {})
        cells: list[OdsCell] = []
        if include_row_index:
            cells.append(OdsCell(text=str(r)))
        for c in range(1, max_col + 1):
            cells.append(OdsCell(text=row_cells.get(c, "")))
        ods_rows.append(OdsRow(cells=cells))

    sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    document = OdsDocument(sheets=[sheet])
    write_ods(document, dest_path)  # Format Factory ods writer
    return len(ods_rows)


__all__ = ["sylk_to_ods"]
