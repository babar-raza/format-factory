"""
csv_to_gnumeric.py --- Dogfood export: CSV to Gnumeric using Format Factory libraries.

Sprint: CSV-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-CSV-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations
from pathlib import Path
from ff_csv.csv_parser import parse_csv_strict  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer

def csv_to_gnumeric(csv_path, dest_path, *, sheet_name="Sheet1"):
    """Convert a CSV file to Gnumeric format using Format Factory libraries.

    Returns the number of data rows written (excluding header row).
    """
    csv_path = Path(csv_path); dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    result = parse_csv_strict(csv_path)
    headers = result.get("headers") or []
    data_rows = result.get("rows") or []
    all_rows = ([headers] if headers else []) + list(data_rows)
    cell_grid = {}
    for r, row in enumerate(all_rows):
        for c, val in enumerate(row):
            cell_grid[(r, c)] = str(val)
    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)
    return len(all_rows)

__all__ = ["csv_to_gnumeric"]
