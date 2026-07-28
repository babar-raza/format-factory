"""
ods_to_csv.py

Dogfood export: ODS -> CSV

Converts an OpenDocument Spreadsheet (.ods) file to CSV using:
  - Format Factory ods library (parse_ods_strict) as the source reader
  - Format Factory csv library (write_csv_to_file) as the target writer

Each row in the selected sheet becomes one CSV row.

Sprint: ODS-TO-CSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODS-TO-CSV-DOGFOOD-001
"""
from __future__ import annotations

from pathlib import Path

from ods.ods_parser import parse_ods_strict  # Format Factory source reader
from ff_csv.csv_writer import write_csv_to_file  # Format Factory target writer


def ods_to_csv(
    ods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    skip_empty_rows: bool = True,
) -> int:
    """
    Convert an ODS spreadsheet sheet to CSV using Format Factory writers.

    Parameters
    ----------
    ods_path:
        Path to the source .ods file.
    dest_path:
        Path to write the target .csv file.
    sheet_index:
        Which sheet to export (0-based, default 0).
    skip_empty_rows:
        If True, rows with all-empty cells are skipped.

    Returns
    -------
    int
        Number of CSV rows written.

    Raises
    ------
    OdsError:
        If the ODS file cannot be read or the sheet index is invalid.
    """
    from ods.ods_parser import OdsError

    ods_path = Path(ods_path)
    dest_path = Path(dest_path)

    doc = parse_ods_strict(ods_path)  # Format Factory ods reader

    if not doc.sheets:
        raise OdsError("Document has no sheets")
    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        raise OdsError(
            f"sheet_index {sheet_index} out of range (0..{len(doc.sheets) - 1})"
        )

    sheet = doc.sheets[sheet_index]
    rows: list[list[str]] = []
    for row in sheet.rows:
        fields = [cell.text if cell.text else (str(cell.value) if cell.value is not None else "") for cell in row.cells]
        if skip_empty_rows and all(f == "" for f in fields):
            continue
        rows.append(fields)

    write_csv_to_file(rows, dest_path)  # Format Factory csv writer
    return len(rows)


__all__ = ["ods_to_csv"]
