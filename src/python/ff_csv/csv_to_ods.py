"""
csv_to_ods.py — Dogfood export: CSV → ODS using Format Factory libraries.

Reads a CSV file using Format Factory's CSV parser and writes it as an ODS
spreadsheet using Format Factory's ODS writer.

Each CSV row becomes one ODS row in Sheet1.

Sprint: CSV-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-CSV-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from src.python.ff_csv.csv_parser import parse_csv_strict  # FF source reader
from ods.ods_parser import OdsCell, OdsDocument, OdsRow, OdsSheet  # FF ODS model
from ods.ods_writer import write_ods  # FF target writer


def csv_to_ods(
    csv_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a CSV file to an ODS spreadsheet.

    Each CSV row (including the optional header row) becomes one ODS row in
    a single sheet named sheet_name.

    Args:
        csv_path: Path to the source .csv file.
        dest_path: Path for the output .ods file (parent dirs created).
        sheet_name: Name of the output sheet (default "Sheet1").

    Returns:
        Number of data rows written (not counting headers).
    """
    csv_path = Path(csv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_csv_strict(csv_path)  # Format Factory csv reader
    headers = result.get("headers") or []
    rows = result.get("rows") or []

    ods_rows: list[OdsRow] = []
    if headers:
        ods_rows.append(OdsRow(cells=[OdsCell(text=str(h)) for h in headers]))

    for row in rows:
        ods_rows.append(OdsRow(cells=[OdsCell(text=str(v)) for v in row]))

    sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    doc = OdsDocument(sheets=[sheet])
    write_ods(doc, dest_path)  # Format Factory ods writer
    return len(rows)


__all__ = ["csv_to_ods"]
