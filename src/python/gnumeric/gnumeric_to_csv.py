"""
gnumeric_to_csv.py

Dogfood export: Gnumeric -> CSV

Converts a Gnumeric spreadsheet (.gnumeric) file to CSV using:
  - Format Factory gnumeric library (load) as the source reader
  - Format Factory csv library (write_csv_to_file) as the target writer

Each row in the selected sheet's cell_grid becomes one CSV row.

Sprint: GNUMERIC-TO-CSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-GNUMERIC-TO-CSV-DOGFOOD-001
"""
from __future__ import annotations

from pathlib import Path

from gnumeric.gnumeric_codec import load as load_gnumeric  # Format Factory source reader
from ff_csv.csv_writer import write_csv_to_file  # Format Factory target writer


def gnumeric_to_csv(
    gnumeric_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
) -> int:
    """
    Convert a Gnumeric spreadsheet sheet to CSV using Format Factory writers.

    Parameters
    ----------
    gnumeric_path:
        Path to the source .gnumeric file.
    dest_path:
        Path to write the target .csv file.
    sheet_index:
        Which sheet to export (0-based, default 0).

    Returns
    -------
    int
        Number of CSV rows written.

    Raises
    ------
    GnumericError:
        If the Gnumeric file cannot be read or sheet index is invalid.
    """
    from gnumeric.exceptions import GnumericError

    gnumeric_path = Path(gnumeric_path)
    dest_path = Path(dest_path)

    model = load_gnumeric(gnumeric_path)  # Format Factory gnumeric reader

    sheets: list = model.get("sheets", [])
    if not sheets:
        raise GnumericError("Document has no sheets")
    if sheet_index < 0 or sheet_index >= len(sheets):
        raise GnumericError(
            f"sheet_index {sheet_index} out of range (0..{len(sheets) - 1})"
        )

    sheet = sheets[sheet_index]
    cell_grid: dict = sheet.get("cell_grid", {})

    if not cell_grid:
        write_csv_to_file([], dest_path)  # Format Factory csv writer
        return 0

    # Determine grid dimensions from (row, col) tuple keys
    max_row = max(r for r, c in cell_grid)
    max_col = max(c for r, c in cell_grid)

    rows: list[list[str]] = []
    for row_idx in range(max_row + 1):
        row_fields = [
            str(cell_grid.get((row_idx, col_idx), ""))
            for col_idx in range(max_col + 1)
        ]
        rows.append(row_fields)

    write_csv_to_file(rows, dest_path)  # Format Factory csv writer
    return len(rows)


__all__ = ["gnumeric_to_csv"]
