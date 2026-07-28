"""
tsv_to_sylk.py — Dogfood export: TSV → SYLK using Format Factory libraries.

Sprint: TSV-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TSV-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from tsv.tsv_parser import parse_tsv_strict  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def tsv_to_sylk(
    tsv_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
) -> int:
    """Convert a TSV file to a SYLK spreadsheet."""
    tsv_path = Path(tsv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_tsv_strict(tsv_path)  # Format Factory tsv reader
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


__all__ = ["tsv_to_sylk"]
