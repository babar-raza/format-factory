"""
ods_to_ndjson.py — Dogfood export: ODS → NDJSON using Format Factory libraries.

Reads an ODS spreadsheet using Format Factory's ODS parser and writes each
data row as a JSON object to an NDJSON file using Format Factory's NDJSON writer.

When the first row looks like a header (all text, next rows have data), those
values become JSON object keys. Otherwise keys are col_0, col_1, ... col_N.

License: Apache-2.0
"""

from __future__ import annotations

from pathlib import Path

from ods.ods_parser import parse_ods_strict
from ndjson.ndjson_codec import write_ndjson


def _cell_to_str(cell) -> str:
    """Convert an OdsCell to a string value."""
    if cell.text:
        return cell.text
    if cell.value is not None:
        return str(cell.value)
    return ""


def ods_to_ndjson(
    ods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    use_first_row_as_headers: bool = True,
    include_row_index: bool = False,
) -> int:
    """Convert one sheet of an ODS file to NDJSON, one record per data row.

    Args:
        ods_path: Path to the source .ods file.
        dest_path: Path for the output .ndjson file (parent dirs created).
        sheet_index: Zero-based index of the sheet to export (default 0).
        use_first_row_as_headers: When True, treat the first row as header
            keys; when False, use col_0/col_1/... for all rows.
        include_row_index: When True, adds a ``row_index`` field (0-based).

    Returns:
        Number of NDJSON records written.
    """
    ods_path = Path(ods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_ods_strict(ods_path)
    if not doc.sheets or sheet_index >= len(doc.sheets):
        write_ndjson([], dest_path)
        return 0

    sheet = doc.sheets[sheet_index]
    all_rows = sheet.rows

    if not all_rows:
        write_ndjson([], dest_path)
        return 0

    # Determine headers and data rows
    if use_first_row_as_headers and len(all_rows) > 0:
        header_cells = all_rows[0].cells
        headers = [_cell_to_str(c) for c in header_cells] or None
        data_rows = all_rows[1:] if len(all_rows) > 1 else []
    else:
        headers = None
        data_rows = all_rows

    records = []
    for row_idx, row in enumerate(data_rows):
        cells = row.cells
        n = len(cells)
        if headers:
            keys = headers
        else:
            keys = [f"col_{i}" for i in range(n)]
        record = {key: (_cell_to_str(cells[i]) if i < n else "") for i, key in enumerate(keys)}
        if include_row_index:
            record["row_index"] = row_idx
        records.append(record)

    write_ndjson(records, dest_path)
    return len(records)
