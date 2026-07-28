"""
csv_to_dif.py — Dogfood export: CSV → DIF using Format Factory libraries.

Sprint: CSV-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-CSV-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ff_csv.csv_parser import parse_csv_strict  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def csv_to_dif(
    csv_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    title: str = "CSV Export",
) -> int:
    """Convert a CSV file to a DIF file."""
    csv_path = Path(csv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_csv_strict(csv_path)  # Format Factory csv reader
    headers = result.get("headers") or []
    data_rows = result.get("rows") or []
    all_rows = ([headers] if include_header and headers else []) + list(data_rows)

    dif_rows = []
    for row in all_rows:
        dif_rows.append([DifCell(value=str(v), value_type="string") for v in row])

    doc = DifDocument(title=title, rows=dif_rows)
    write_dif(doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["csv_to_dif"]
