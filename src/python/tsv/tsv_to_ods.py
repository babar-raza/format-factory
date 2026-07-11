"""
tsv_to_ods.py — Dogfood export: TSV → ODS using Format Factory libraries.

Reads a TSV file using Format Factory's TSV parser and writes it as an ODS
spreadsheet using Format Factory's ODS writer.

Each TSV row becomes one ODS row in Sheet1.

Sprint: TSV-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TSV-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import parse_tsv_strict  # FF source reader
from ods.ods_parser import OdsCell, OdsDocument, OdsRow, OdsSheet  # FF ODS model
from ods.ods_writer import write_ods  # FF target writer


def tsv_to_ods(
    tsv_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a TSV file to an ODS spreadsheet.

    Each TSV row (including the optional header row) becomes one ODS row in
    a single sheet named sheet_name.

    Args:
        tsv_path: Path to the source .tsv file.
        dest_path: Path for the output .ods file (parent dirs created).
        sheet_name: Name of the output sheet (default "Sheet1").

    Returns:
        Number of data rows written (not counting headers).
    """
    tsv_path = Path(tsv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_tsv_strict(tsv_path)  # Format Factory tsv reader
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


__all__ = ["tsv_to_ods"]
