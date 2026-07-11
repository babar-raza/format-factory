"""
fods_to_csv.py — Dogfood export: FODS → CSV using Format Factory libraries.

Reads a Flat ODS spreadsheet using Format Factory's FODS parser and writes
one sheet's rows to a CSV file using Format Factory's CSV writer.

Each FODS row becomes a CSV row; cell values are converted to strings.
Covered cells (span overflows) are emitted as empty strings.

License: Apache-2.0
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "fods"))
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fods.parser import parse_fods_strict
from src.python.csv.csv_writer import write_csv_to_file


def fods_to_csv(
    fods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    skip_empty_rows: bool = True,
) -> int:
    """Convert one sheet of a FODS file to CSV.

    Args:
        fods_path: Path to the source .fods file.
        dest_path: Path for the output .csv file (parent dirs created).
        sheet_index: Zero-based index of the sheet to export (default 0).
        skip_empty_rows: When True, rows where all cells are empty are omitted.

    Returns:
        Number of CSV rows written.
    """
    fods_path = Path(fods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fods_strict(fods_path)
    sheets = doc.get("sheets", [])
    if not sheets:
        write_csv_to_file([], dest_path)
        return 0

    sheet = sheets[sheet_index]
    rows_data = sheet.get("rows", [])

    csv_rows: list[list[str]] = []
    for row in rows_data:
        cells = row.get("cells", [])
        fields: list[str] = []
        for cell in cells:
            if cell.get("is_covered"):
                fields.append("")
            else:
                value = cell.get("value")
                fields.append("" if value is None else str(value))
        if skip_empty_rows and all(f == "" for f in fields):
            continue
        csv_rows.append(fields)

    write_csv_to_file(csv_rows, dest_path)
    return len(csv_rows)
