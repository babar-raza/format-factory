"""
csv_to_sylk.py — Dogfood export: CSV → SYLK using Format Factory libraries.

Sprint: CSV-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-CSV-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ff_csv.csv_parser import parse_csv_strict  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def csv_to_sylk(
    csv_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
) -> int:
    """Convert a CSV file to a SYLK spreadsheet."""
    csv_path = Path(csv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_csv_strict(csv_path)  # Format Factory csv reader
    headers = result.get("headers") or []
    data_rows = result.get("rows") or []

    cells: list[SylkCell] = []
    row_idx = 1

    if include_header and headers:
        for c, h in enumerate(headers, start=1):
            cells.append(SylkCell(row=row_idx, col=c, value=str(h), value_type="string"))
        row_idx += 1

    for row in data_rows:
        for c, val in enumerate(row, start=1):
            cells.append(SylkCell(row=row_idx, col=c, value=str(val), value_type="string"))
        row_idx += 1

    max_row = max((cell.row for cell in cells), default=0)
    max_col = max((cell.col for cell in cells), default=0)
    doc = SylkDocument(cells=cells, rows=max_row, cols=max_col)
    write_sylk(doc, dest_path)  # Format Factory sylk writer
    return max_row


__all__ = ["csv_to_sylk"]
