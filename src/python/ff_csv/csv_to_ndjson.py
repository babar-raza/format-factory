"""
csv_to_ndjson.py — Dogfood export: CSV → NDJSON using Format Factory libraries.

Reads a CSV file using Format Factory's CSV parser and writes each data row
as a JSON object to an NDJSON file using Format Factory's NDJSON writer.

When the CSV has headers, each record uses header names as keys.
When there are no headers, keys are col_0, col_1, ... col_N.

License: Apache-2.0
"""

from __future__ import annotations

from pathlib import Path

from ff_csv.csv_parser import parse_csv_strict
from ndjson.ndjson_codec import write_ndjson


def csv_to_ndjson(
    csv_path: str | Path,
    dest_path: str | Path,
    *,
    include_row_index: bool = False,
) -> int:
    """Convert a CSV file to NDJSON, one record per data row.

    Args:
        csv_path: Path to the source CSV file.
        dest_path: Path for the output NDJSON file (created with parent dirs).
        include_row_index: When True, adds a ``row_index`` field (0-based).

    Returns:
        Number of NDJSON records written.
    """
    csv_path = Path(csv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_csv_strict(csv_path)
    headers = doc.get("headers")
    rows = doc.get("rows", [])

    records = []
    for row_idx, row in enumerate(rows):
        if headers:
            keys = headers
        else:
            keys = [f"col_{i}" for i in range(len(row))]
        record: dict = {key: (row[i] if i < len(row) else "") for i, key in enumerate(keys)}
        if include_row_index:
            record["row_index"] = row_idx
        records.append(record)

    write_ndjson(records, dest_path)
    return len(records)
