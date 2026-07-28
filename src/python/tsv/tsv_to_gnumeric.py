"""
tsv_to_gnumeric.py — Dogfood export: TSV → Gnumeric using Format Factory libraries.

Sprint: TSV-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TSV-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from tsv.tsv_parser import parse_tsv_strict  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def tsv_to_gnumeric(
    tsv_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a TSV file to a Gnumeric spreadsheet."""
    tsv_path = Path(tsv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_tsv_strict(tsv_path)  # Format Factory tsv reader
    headers = result.get("headers") or []
    data_rows = result.get("rows") or []
    all_rows = ([headers] if headers else []) + list(data_rows)

    cell_grid: dict = {}
    for r, row in enumerate(all_rows):
        for c, val in enumerate(row):
            cell_grid[(r, c)] = str(val)

    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)  # Format Factory gnumeric writer
    return len(all_rows)


__all__ = ["tsv_to_gnumeric"]
