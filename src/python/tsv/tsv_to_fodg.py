"""
tsv_to_fodg.py — Dogfood export: TSV → FODG using Format Factory libraries.

Sprint: TSV-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TSV-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from tsv.tsv_parser import parse_tsv_strict  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def tsv_to_fodg(
    tsv_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
) -> int:
    """Convert a TSV file to a FODG drawing, one page per row."""
    tsv_path = Path(tsv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_tsv_strict(tsv_path)  # Format Factory tsv reader
    headers = result.get("headers") or []
    data_rows = result.get("rows") or []

    pages_list = []
    if include_header and headers:
        pages_list.append({"name": "Header", "texts": [str(h) for h in headers]})
    for i, row in enumerate(data_rows):
        pages_list.append({"name": f"Row{i + 1}", "texts": [str(v) for v in row]})

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["tsv_to_fodg"]
