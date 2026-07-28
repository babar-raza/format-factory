"""
ndjson_to_fodg.py — Dogfood export: NDJSON → FODG using Format Factory libraries.

Sprint: NDJSON-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-NDJSON-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ndjson.ndjson_codec import load_ndjson  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def ndjson_to_fodg(
    ndjson_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert an NDJSON file to a FODG drawing, one page per record."""
    ndjson_path = Path(ndjson_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(ndjson_path)  # Format Factory ndjson reader

    pages_list = []
    for i, record in enumerate(records):
        if isinstance(record, dict):
            texts = [f"{k}={v}" for k, v in record.items()]
        else:
            texts = [str(record)]
        pages_list.append({"name": f"Record{i + 1}", "texts": texts})

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["ndjson_to_fodg"]
