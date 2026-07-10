"""
dif_to_csv.py

Dogfood export: DIF -> CSV

Converts a Data Interchange Format (.dif) file to CSV using:
  - Format Factory dif library (parse_dif_strict) as the source reader
  - Format Factory csv library (write_csv_to_file) as the target writer

Each DIF data row becomes one CSV row.

Sprint: DIF-ABW-BATCH-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-CSV-DOGFOOD-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "dif"))
sys.path.insert(0, str(_REPO))

from dif.dif_parser import parse_dif_strict  # Format Factory source reader
from src.python.csv.csv_writer import write_csv_to_file  # Format Factory target writer


def dif_to_csv(
    dif_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty_rows: bool = True,
) -> int:
    """
    Convert a DIF spreadsheet to CSV using Format Factory writers.

    Parameters
    ----------
    dif_path:
        Path to the source .dif file.
    dest_path:
        Path to write the target .csv file.
    skip_empty_rows:
        If True, rows where all cells have None/empty values are skipped.

    Returns
    -------
    int
        Number of CSV rows written.

    Raises
    ------
    DifError:
        If the DIF file cannot be read or parsed.
    """
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)

    doc = parse_dif_strict(dif_path)  # Format Factory dif reader

    rows: list[list[str]] = []
    for dif_row in doc.rows:
        fields = [str(cell.value) if cell.value is not None else "" for cell in dif_row]
        if skip_empty_rows and all(f == "" for f in fields):
            continue
        rows.append(fields)

    write_csv_to_file(rows, dest_path)  # Format Factory csv writer
    return len(rows)


__all__ = ["dif_to_csv"]
