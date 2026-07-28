"""
dif_to_ndjson.py — Dogfood export: DIF → NDJSON using Format Factory libraries.

Reads a DIF (Data Interchange Format) file using Format Factory's DIF parser
and writes each data row as a JSON record to an NDJSON file using Format
Factory's NDJSON writer.

Each record contains the row cells as values keyed by col_0, col_1, ... col_N
(or by header names if the first row is treated as headers).

License: Apache-2.0
"""

from __future__ import annotations

from pathlib import Path

from dif.dif_parser import parse_dif_strict
from ndjson.ndjson_codec import write_ndjson


def _cell_value_str(cell) -> str:
    """Convert a DifCell to a string."""
    if cell.value is None:
        return ""
    return str(cell.value)


def dif_to_ndjson(
    dif_path: str | Path,
    dest_path: str | Path,
    *,
    include_row_index: bool = False,
    include_value_types: bool = False,
) -> int:
    """Convert DIF rows to NDJSON records, one record per data row.

    Keys are col_0, col_1, ... col_N for each column.

    Args:
        dif_path: Path to the source .dif file.
        dest_path: Path for the output .ndjson file (parent dirs created).
        include_row_index: When True, adds a ``row_index`` field (0-based).
        include_value_types: When True, adds ``{col}_type`` fields for each column.

    Returns:
        Number of NDJSON records written.
    """
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(dif_path)
    rows = doc.rows

    records = []
    for row_idx, dif_row in enumerate(rows):
        record: dict = {}
        for col_idx, cell in enumerate(dif_row):
            key = f"col_{col_idx}"
            record[key] = _cell_value_str(cell)
            if include_value_types:
                record[f"{key}_type"] = cell.value_type or ""
        if include_row_index:
            record["row_index"] = row_idx
        records.append(record)

    write_ndjson(records, dest_path)
    return len(records)
