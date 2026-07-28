"""
gnumeric_to_tsv.py — Dogfood export: Gnumeric → TSV using Format Factory libraries.

Reads a Gnumeric spreadsheet using Format Factory's Gnumeric codec and writes
each cell row from a selected sheet as a TSV row using Format Factory's TSV
writer.

The first row is optionally used as column headers; otherwise no header is
written and column data is emitted directly.

Sprint: GNUMERIC-TO-TSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-GNUMERIC-TO-TSV-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from gnumeric.gnumeric_codec import load as load_gnumeric  # Format Factory source reader
from tsv.tsv_parser import write_tsv  # Format Factory target writer


def gnumeric_to_tsv(
    gnumeric_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    use_first_row_as_headers: bool = True,
    include_row_index: bool = False,
) -> int:
    """Convert one Gnumeric sheet to TSV, one record per data row.

    Gnumeric's cell_grid uses 0-based (row, col) integer tuple keys.
    When use_first_row_as_headers=True, row 0 values become the TSV header.

    Args:
        gnumeric_path: Path to the source .gnumeric file.
        dest_path: Path for the output .tsv file (parent dirs created).
        sheet_index: Zero-based index of the sheet to export (default 0).
        use_first_row_as_headers: When True, row 0 values become TSV header.
        include_row_index: When True, adds a ``row_index`` column (0-based data row).

    Returns:
        Number of TSV data rows written.
    """
    gnumeric_path = Path(gnumeric_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_gnumeric(gnumeric_path)  # Format Factory gnumeric reader
    sheets = model.get("sheets", [])
    if not sheets or sheet_index >= len(sheets):
        write_tsv([], dest_path)
        return 0

    sheet = sheets[sheet_index]
    cell_grid = sheet.get("cell_grid", {})

    if not cell_grid:
        write_tsv([], dest_path)
        return 0

    max_row = max(r for r, c in cell_grid)
    max_col = max(c for r, c in cell_grid)

    all_rows = [
        [str(cell_grid.get((row_idx, col_idx), "")) for col_idx in range(max_col + 1)]
        for row_idx in range(max_row + 1)
    ]

    if use_first_row_as_headers and all_rows:
        headers = all_rows[0]
        data_rows = all_rows[1:]
        data_start = 1
    else:
        headers = None
        data_rows = all_rows
        data_start = 0

    rows: list[list[str]] = []
    for row_idx, row in enumerate(data_rows):
        tsv_row = list(row)
        if include_row_index:
            tsv_row.insert(0, str(data_start + row_idx))
        rows.append(tsv_row)

    write_tsv(rows, dest_path, headers=headers)  # Format Factory tsv writer
    return len(rows)


__all__ = ["gnumeric_to_tsv"]
