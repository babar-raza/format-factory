"""
ndjson_to_csv.py

Dogfood export: NDJSON -> CSV

Converts a newline-delimited JSON (.ndjson) file to CSV using:
  - Format Factory ndjson library (load_ndjson) as the source reader
  - Format Factory csv library (write_csv_to_file) as the target writer

Each NDJSON record becomes one CSV row. Column headers are derived from
the union of all keys found across all records (in insertion order).

Sprint: NDJSON-TO-CSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-NDJSON-TO-CSV-DOGFOOD-001
"""
from __future__ import annotations

from pathlib import Path

from ndjson.ndjson_codec import load_ndjson  # Format Factory source reader
from ff_csv.csv_writer import write_csv_to_file  # Format Factory target writer


def ndjson_to_csv(
    ndjson_path: str | Path,
    dest_path: str | Path,
    *,
    include_headers: bool = True,
) -> int:
    """Convert an NDJSON file to CSV using Format Factory writers.

    Each JSON object record becomes one CSV row. Headers are collected
    from the union of all keys (in insertion order across records).
    Non-dict records are serialized as a single-column 'value' field.

    Args:
        ndjson_path: Path to the source .ndjson file.
        dest_path: Path to write the target .csv file (parent dirs created).
        include_headers: If True (default), write a header row as the first line.

    Returns:
        Number of data rows written (not counting the header row).
    """
    ndjson_path = Path(ndjson_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(ndjson_path)  # Format Factory ndjson reader

    if not records:
        write_csv_to_file([], dest_path)  # Format Factory csv writer
        return 0

    # Collect all keys in order (dict preserves insertion order in Python 3.7+)
    seen_keys: dict[str, None] = {}
    for rec in records:
        if isinstance(rec, dict):
            for k in rec:
                seen_keys[k] = None
    headers = list(seen_keys) if seen_keys else ["value"]

    rows: list[list[str]] = []
    for rec in records:
        if isinstance(rec, dict):
            row = [str(rec.get(h, "")) if rec.get(h) is not None else "" for h in headers]
        else:
            row = [str(rec)]
        rows.append(row)

    write_csv_to_file(  # Format Factory csv writer
        rows,
        dest_path,
        headers=headers if include_headers else None,
    )
    return len(rows)


__all__ = ["ndjson_to_csv"]
