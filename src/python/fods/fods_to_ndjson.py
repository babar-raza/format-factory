"""
fods_to_ndjson.py — Dogfood export: FODS → NDJSON using Format Factory libraries.

Reads a Flat ODS spreadsheet using Format Factory's FODS parser and writes
each data row as a JSON record to an NDJSON file using Format Factory's
NDJSON writer.

The first row is optionally treated as column headers; otherwise keys are
col_0, col_1, ... col_N.

Sprint: FODS-TO-NDJSON-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODS-TO-NDJSON-DOGFOOD-001

License: Apache-2.0
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "fods"))
sys.path.insert(0, str(_REPO / "src" / "python" / "ndjson"))
sys.path.insert(0, str(_REPO))

from fods.parser import parse_fods_strict  # Format Factory source reader
from ndjson.ndjson_codec import write_ndjson  # Format Factory target writer


def fods_to_ndjson(
    fods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    use_first_row_as_headers: bool = True,
    include_row_index: bool = False,
) -> int:
    """Convert one FODS sheet to NDJSON, one record per data row.

    Args:
        fods_path: Path to the source .fods file.
        dest_path: Path for the output .ndjson file (parent dirs created).
        sheet_index: Zero-based index of the sheet to export (default 0).
        use_first_row_as_headers: When True, row 0 values become JSON keys.
        include_row_index: When True, adds a ``row_index`` field (0-based data row).

    Returns:
        Number of NDJSON records written.
    """
    fods_path = Path(fods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fods_strict(fods_path)
    sheets = doc.get("sheets", [])
    if not sheets or sheet_index >= len(sheets):
        write_ndjson([], dest_path)
        return 0

    sheet = sheets[sheet_index]
    rows_data = sheet.get("rows", [])
    if not rows_data:
        write_ndjson([], dest_path)
        return 0

    def _row_to_strings(row: dict) -> list[str]:
        fields: list[str] = []
        for cell in row.get("cells", []):
            if cell.get("is_covered"):
                fields.append("")
            else:
                value = cell.get("value")
                fields.append("" if value is None else str(value))
        return fields

    all_rows = [_row_to_strings(r) for r in rows_data]

    if use_first_row_as_headers and all_rows:
        headers = all_rows[0]
        data_rows = all_rows[1:]
    else:
        headers = None
        data_rows = all_rows

    records = []
    for row_idx, row in enumerate(data_rows):
        if headers:
            keys = headers
        else:
            keys = [f"col_{i}" for i in range(len(row))]
        record = {key: (row[i] if i < len(row) else "") for i, key in enumerate(keys)}
        if include_row_index:
            record["row_index"] = row_idx
        records.append(record)

    write_ndjson(records, dest_path)
    return len(records)


__all__ = ["fods_to_ndjson"]
