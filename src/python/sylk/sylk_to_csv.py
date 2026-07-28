"""
sylk_to_csv.py

Dogfood export: SYLK -> CSV

Converts a Symbolic Link (SYLK/SLK) spreadsheet file to CSV using:
  - Format Factory sylk library (parse_sylk_strict) as the source reader
  - Format Factory csv library (write_csv_to_file) as the target writer

SYLK uses 1-based row/col indices. Each row in the cell grid becomes one CSV row.

Sprint: SYLK-TO-CSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-CSV-DOGFOOD-001
"""
from __future__ import annotations

from pathlib import Path

from sylk.sylk_parser import parse_sylk_strict  # Format Factory source reader
from ff_csv.csv_writer import write_csv_to_file  # Format Factory target writer


def sylk_to_csv(
    sylk_path: str | Path,
    dest_path: str | Path,
) -> int:
    """
    Convert a SYLK spreadsheet to CSV using Format Factory writers.

    SYLK cells use 1-based row/col indices. The output CSV has one row per
    SYLK tuple, with empty strings for missing cells.

    Parameters
    ----------
    sylk_path:
        Path to the source .slk / .sylk file.
    dest_path:
        Path to write the target .csv file.

    Returns
    -------
    int
        Number of CSV rows written.

    Raises
    ------
    SylkError:
        If the SYLK file cannot be read or parsed.
    """
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)

    doc = parse_sylk_strict(sylk_path)  # Format Factory sylk reader

    if not doc.cells:
        write_csv_to_file([], dest_path)  # Format Factory csv writer
        return 0

    # SYLK uses 1-based indices; build grid
    max_row = max(c.row for c in doc.cells)
    max_col = max(c.col for c in doc.cells)

    # Build a lookup from (row, col) -> value
    grid: dict[tuple[int, int], str] = {}
    for cell in doc.cells:
        grid[(cell.row, cell.col)] = str(cell.value) if cell.value is not None else ""

    rows: list[list[str]] = []
    for row_idx in range(1, max_row + 1):
        row_fields = [grid.get((row_idx, col_idx), "") for col_idx in range(1, max_col + 1)]
        rows.append(row_fields)

    write_csv_to_file(rows, dest_path)  # Format Factory csv writer
    return len(rows)


__all__ = ["sylk_to_csv"]
