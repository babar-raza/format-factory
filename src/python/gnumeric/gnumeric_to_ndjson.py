"""
gnumeric_to_ndjson.py — Dogfood export: Gnumeric → NDJSON using Format Factory libraries.

Reads a Gnumeric spreadsheet using Format Factory's Gnumeric codec and writes
each cell from a selected sheet as a JSON record to an NDJSON file using
Format Factory's NDJSON writer.

The first row of the sheet is optionally treated as column headers; otherwise
keys are col_0, col_1, ... col_N.

License: Apache-2.0
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "gnumeric"))
sys.path.insert(0, str(_REPO / "src" / "python" / "ndjson"))

from gnumeric.gnumeric_codec import load as load_gnumeric
from ndjson.ndjson_codec import write_ndjson


def gnumeric_to_ndjson(
    gnumeric_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    use_first_row_as_headers: bool = True,
    include_row_index: bool = False,
) -> int:
    """Convert one Gnumeric sheet to NDJSON, one record per data row.

    Gnumeric's cell_grid uses 0-based (row, col) integer tuple keys.
    When use_first_row_as_headers=True, row 0 values become JSON keys.

    Args:
        gnumeric_path: Path to the source .gnumeric file.
        dest_path: Path for the output .ndjson file (parent dirs created).
        sheet_index: Zero-based index of the sheet to export (default 0).
        use_first_row_as_headers: When True, row 0 values become JSON keys.
        include_row_index: When True, adds a ``row_index`` field (0-based).

    Returns:
        Number of NDJSON records written.
    """
    gnumeric_path = Path(gnumeric_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_gnumeric(gnumeric_path)
    sheets = model.get("sheets", [])
    if not sheets or sheet_index >= len(sheets):
        write_ndjson([], dest_path)
        return 0

    sheet = sheets[sheet_index]
    cell_grid = sheet.get("cell_grid", {})

    if not cell_grid:
        write_ndjson([], dest_path)
        return 0

    max_row = max(r for r, c in cell_grid)
    max_col = max(c for r, c in cell_grid)

    # Build full row list as strings
    all_rows: list[list[str]] = []
    for row_idx in range(max_row + 1):
        row = [str(cell_grid.get((row_idx, col_idx), "")) for col_idx in range(max_col + 1)]
        all_rows.append(row)

    # Determine headers and data rows
    if use_first_row_as_headers and all_rows:
        headers = all_rows[0]
        data_rows = all_rows[1:]
        data_start = 1
    else:
        headers = None
        data_rows = all_rows
        data_start = 0

    records = []
    for row_idx, row in enumerate(data_rows):
        if headers:
            keys = headers
        else:
            keys = [f"col_{i}" for i in range(len(row))]
        record = {key: (row[i] if i < len(row) else "") for i, key in enumerate(keys)}
        if include_row_index:
            record["row_index"] = data_start + row_idx
        records.append(record)

    write_ndjson(records, dest_path)
    return len(records)
