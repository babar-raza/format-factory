"""
tsv_to_dif.py — Dogfood export: TSV → DIF using Format Factory libraries.

Sprint: TSV-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TSV-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from tsv.tsv_parser import parse_tsv_strict  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def tsv_to_dif(
    tsv_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    title: str = "TSV Export",
) -> int:
    """Convert a TSV file to a DIF file."""
    tsv_path = Path(tsv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_tsv_strict(tsv_path)  # Format Factory tsv reader
    headers = result.get("headers") or []
    data_rows = result.get("rows") or []
    all_rows = ([headers] if include_header and headers else []) + list(data_rows)

    dif_rows = []
    for row in all_rows:
        dif_rows.append([DifCell(value=str(v), value_type="string") for v in row])

    doc = DifDocument(title=title, rows=dif_rows)
    write_dif(doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["tsv_to_dif"]
