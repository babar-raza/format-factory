"""
ndjson_to_fods.py — Dogfood export: NDJSON → FODS using Format Factory libraries.

Reads an NDJSON file using Format Factory's NDJSON codec and writes it as a
Flat ODS (.fods) spreadsheet using Format Factory's FODS writer.

Each NDJSON record becomes one FODS row. Record keys become column headers.

Sprint: NDJSON-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-NDJSON-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from ndjson.ndjson_codec import load_ndjson  # FF source reader
from fods.writer import write_fods  # FF target writer


def ndjson_to_fods(
    ndjson_path: str | Path,
    dest_path: str | Path,
    *,
    include_headers: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert an NDJSON file to a FODS flat spreadsheet.

    Each JSON record becomes one FODS row. For dict records, the union of
    all keys becomes the column headers. Non-dict records get a single
    'value' column.

    Args:
        ndjson_path: Path to the source .ndjson file.
        dest_path: Path for the output .fods file (parent dirs created).
        include_headers: When True, the header row is written first.
        sheet_name: Name for the FODS sheet tab.

    Returns:
        Number of data rows written (not counting the header row).
    """
    ndjson_path = Path(ndjson_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(ndjson_path)  # Format Factory ndjson reader

    if not records:
        workbook = {"sheets": [{"name": sheet_name, "rows": []}]}
        write_fods(workbook, dest_path)  # Format Factory fods writer
        return 0

    # Determine headers — union of all dict keys (preserving insertion order)
    all_dict = all(isinstance(r, dict) for r in records)
    if all_dict:
        keys: list[str] = []
        seen: set[str] = set()
        for rec in records:
            for k in rec:
                if k not in seen:
                    keys.append(k)
                    seen.add(k)
    else:
        keys = ["value"]

    def _make_fods_row(values: list[str]) -> dict:
        return {
            "cells": [
                {"value": v, "value_type": "string", "text_content": v}
                for v in values
            ]
        }

    fods_rows: list[dict] = []
    if include_headers:
        fods_rows.append(_make_fods_row(keys))

    for rec in records:
        if all_dict:
            row_vals = [str(rec.get(k, "")) if rec.get(k) is not None else "" for k in keys]
        else:
            row_vals = [str(rec)]
        fods_rows.append(_make_fods_row(row_vals))

    workbook = {"sheets": [{"name": sheet_name, "rows": fods_rows}]}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return len(records)


__all__ = ["ndjson_to_fods"]
