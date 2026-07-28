"""
sylk_to_ndjson.py — Dogfood export: SYLK → NDJSON using Format Factory libraries.

Reads a SYLK spreadsheet using Format Factory's SYLK parser and writes
each row as a JSON record to an NDJSON file using Format Factory's NDJSON writer.

SYLK uses 1-based (row, col) coordinates in SylkCell objects. The export
groups cells by row, optionally uses the first row as headers, and emits
one NDJSON record per data row.

License: Apache-2.0
"""

from __future__ import annotations

from pathlib import Path

from sylk.sylk_parser import parse_sylk_strict
from ndjson.ndjson_codec import write_ndjson


def sylk_to_ndjson(
    sylk_path: str | Path,
    dest_path: str | Path,
    *,
    use_first_row_as_headers: bool = True,
    include_row_index: bool = False,
) -> int:
    """Convert SYLK rows to NDJSON records, one record per data row.

    SYLK cells use 1-based row/col indices. When use_first_row_as_headers=True,
    row 1 values become JSON keys; otherwise keys are col_0, col_1, ... col_N.

    Args:
        sylk_path: Path to the source .slk file.
        dest_path: Path for the output .ndjson file (parent dirs created).
        use_first_row_as_headers: When True, row 1 values become JSON keys.
        include_row_index: When True, adds a ``row_index`` field (1-based SYLK row).

    Returns:
        Number of NDJSON records written.
    """
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(sylk_path)
    cells = doc.cells

    if not cells:
        write_ndjson([], dest_path)
        return 0

    # Build grid: {row_1based: {col_1based: str(value)}}
    max_row = max(c.row for c in cells)
    max_col = max(c.col for c in cells)
    grid: dict[int, dict[int, str]] = {}
    for cell in cells:
        row_dict = grid.setdefault(cell.row, {})
        row_dict[cell.col] = "" if cell.value is None else str(cell.value)

    # Build full rows as lists
    all_rows: dict[int, list[str]] = {}
    for row_idx in range(1, max_row + 1):
        row_dict = grid.get(row_idx, {})
        all_rows[row_idx] = [row_dict.get(col_idx, "") for col_idx in range(1, max_col + 1)]

    # Determine headers and data rows
    if use_first_row_as_headers and 1 in all_rows:
        headers = all_rows[1]
        data_row_indices = [r for r in sorted(all_rows) if r != 1]
    else:
        headers = None
        data_row_indices = sorted(all_rows.keys())

    records = []
    for row_idx in data_row_indices:
        row = all_rows[row_idx]
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
