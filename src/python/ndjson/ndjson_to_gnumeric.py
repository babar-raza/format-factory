"""
ndjson_to_gnumeric.py — Dogfood export: NDJSON → Gnumeric using Format Factory libraries.

Sprint: NDJSON-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-NDJSON-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from ndjson.ndjson_codec import load_ndjson  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def ndjson_to_gnumeric(
    ndjson_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert NDJSON to a Gnumeric spreadsheet, one row per record."""
    ndjson_path = Path(ndjson_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(ndjson_path)  # Format Factory ndjson reader

    cell_grid: dict = {}
    for r, rec in enumerate(records):
        if isinstance(rec, dict):
            for c, (k, v) in enumerate(rec.items()):
                cell_grid[(r, c)] = f"{k}={v}"
        else:
            cell_grid[(r, 0)] = str(rec)

    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)  # Format Factory gnumeric writer
    return len(records)


__all__ = ["ndjson_to_gnumeric"]
