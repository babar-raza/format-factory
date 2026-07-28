"""
ndjson_to_sylk.py — Dogfood export: NDJSON → SYLK using Format Factory libraries.

Sprint: NDJSON-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-NDJSON-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ndjson.ndjson_codec import load_ndjson  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def ndjson_to_sylk(
    ndjson_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert an NDJSON file to a SYLK spreadsheet, one row per record."""
    ndjson_path = Path(ndjson_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(ndjson_path)  # Format Factory ndjson reader

    cells: list[SylkCell] = []
    for r, record in enumerate(records, start=1):
        if isinstance(record, dict):
            parts = [f"{k}={v}" for k, v in record.items()]
        else:
            parts = [str(record)]
        for c, part in enumerate(parts, start=1):
            cells.append(SylkCell(row=r, col=c, value=part, value_type="string"))

    max_row = max((cell.row for cell in cells), default=0)
    max_col = max((cell.col for cell in cells), default=0)
    doc = SylkDocument(cells=cells, rows=max_row, cols=max_col)
    write_sylk(doc, dest_path)  # Format Factory sylk writer
    return max_row


__all__ = ["ndjson_to_sylk"]
