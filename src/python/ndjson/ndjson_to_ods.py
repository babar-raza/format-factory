"""
ndjson_to_ods.py — Dogfood export: NDJSON → ODS using Format Factory libraries.

Reads an NDJSON file using Format Factory's NDJSON codec and writes it as an
ODS spreadsheet using Format Factory's ODS writer.

Each NDJSON record becomes one ODS row. Record keys become column headers.

Sprint: NDJSON-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-NDJSON-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from ndjson.ndjson_codec import load_ndjson  # FF source reader
from ods.ods_parser import OdsCell, OdsDocument, OdsRow, OdsSheet  # FF ODS model
from ods.ods_writer import write_ods  # FF target writer


def ndjson_to_ods(
    ndjson_path: str | Path,
    dest_path: str | Path,
    *,
    include_headers: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert an NDJSON file to an ODS spreadsheet.

    Each JSON record becomes one ODS row. For dict records, the union of
    all keys becomes the column headers. Non-dict records get a single
    'value' column.

    Args:
        ndjson_path: Path to the source .ndjson file.
        dest_path: Path for the output .ods file (parent dirs created).
        include_headers: When True, writes a header row.
        sheet_name: Name of the output sheet (default "Sheet1").

    Returns:
        Number of data rows written (not counting the header).
    """
    ndjson_path = Path(ndjson_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(ndjson_path)  # Format Factory ndjson reader

    # Determine headers from union of all dict record keys
    seen_keys: dict[str, None] = {}
    for rec in records:
        if isinstance(rec, dict):
            for k in rec:
                seen_keys[k] = None
    headers = list(seen_keys) if seen_keys else ["value"]

    # Build ODS rows
    ods_rows: list[OdsRow] = []
    if include_headers:
        ods_rows.append(OdsRow(cells=[OdsCell(text=str(h)) for h in headers]))

    data_rows: list[list[str]] = []
    for rec in records:
        if isinstance(rec, dict):
            row = [str(rec.get(h, "")) if rec.get(h) is not None else "" for h in headers]
        else:
            row = [str(rec)]
        data_rows.append(row)
        ods_rows.append(OdsRow(cells=[OdsCell(text=v) for v in row]))

    sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    doc = OdsDocument(sheets=[sheet])
    write_ods(doc, dest_path)  # Format Factory ods writer
    return len(data_rows)


__all__ = ["ndjson_to_ods"]
