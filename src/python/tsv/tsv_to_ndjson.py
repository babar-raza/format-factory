"""
tsv_to_ndjson.py

Dogfood export: TSV -> NDJSON

Converts a Tab-Separated Values (.tsv) file to NDJSON records using:
  - Format Factory tsv library (parse_tsv_strict) as the source reader
  - Format Factory ndjson library (write_ndjson) as the target writer

Each TSV data row becomes one NDJSON record. If headers are present,
they become the JSON object keys; otherwise keys are 'col_0', 'col_1', etc.

Sprint: TSV-TO-NDJSON-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TSV-TO-NDJSON-DOGFOOD-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "tsv"))
sys.path.insert(0, str(_REPO / "src" / "python" / "ndjson"))

from tsv.tsv_parser import parse_tsv_strict  # Format Factory source reader
from ndjson.ndjson_codec import write_ndjson  # Format Factory target writer


def tsv_to_ndjson(
    tsv_path: str | Path,
    dest_path: str | Path,
    *,
    include_row_index: bool = False,
) -> int:
    """
    Convert a TSV file to NDJSON records using Format Factory writers.

    Each TSV data row becomes one JSON object record. If the TSV has headers,
    they become the record keys. Otherwise keys are 'col_0', 'col_1', etc.

    Parameters
    ----------
    tsv_path:
        Path to the source .tsv file.
    dest_path:
        Path to write the target .ndjson file.
    include_row_index:
        If True, adds a 0-based 'row_index' field to each record.

    Returns
    -------
    int
        Number of NDJSON records written.
    """
    tsv_path = Path(tsv_path)
    dest_path = Path(dest_path)

    doc = parse_tsv_strict(tsv_path)  # Format Factory tsv reader
    headers: list[str] = doc.get("headers", [])
    rows: list[list[str]] = doc.get("rows", [])

    records: list[dict] = []
    for row_idx, row in enumerate(rows):
        if headers:
            keys = headers
        else:
            keys = [f"col_{i}" for i in range(len(row))]

        record: dict = {}
        for i, key in enumerate(keys):
            record[key] = row[i] if i < len(row) else ""
        if include_row_index:
            record["row_index"] = row_idx

        records.append(record)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    write_ndjson(records, dest_path)  # Format Factory ndjson writer
    return len(records)


__all__ = ["tsv_to_ndjson"]
