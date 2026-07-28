"""
csv_to_fods.py — Dogfood export: CSV → FODS using Format Factory libraries.

Reads a CSV file using Format Factory's CSV parser and writes the rows to a
Flat ODS (.fods) spreadsheet using Format Factory's FODS writer.

Each CSV row becomes one FODS row; the optional header row is included.

Sprint: CSV-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-CSV-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ff_csv.csv_parser import parse_csv_strict  # FF source reader
from fods.writer import write_fods  # FF target writer


def csv_to_fods(
    csv_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
    include_headers: bool = True,
) -> int:
    """Convert a CSV file to FODS flat spreadsheet.

    Args:
        csv_path: Path to the source .csv file.
        dest_path: Path for the output .fods file (parent dirs created).
        sheet_name: Name for the FODS sheet tab.
        include_headers: When True, the header row is included as the first row.

    Returns:
        Number of data rows written (not counting the header row).
    """
    csv_path = Path(csv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_csv_strict(csv_path)  # Format Factory csv reader
    headers = result.get("headers") or []
    rows = result.get("rows") or []

    def _make_row(values: list) -> dict:
        return {
            "cells": [
                {"value": str(v), "value_type": "string", "text_content": str(v)}
                for v in values
            ]
        }

    fods_rows: list[dict] = []
    if include_headers and headers:
        fods_rows.append(_make_row(headers))

    for row in rows:
        fods_rows.append(_make_row(row))

    workbook = {"sheets": [{"name": sheet_name, "rows": fods_rows}]}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return len(rows)


__all__ = ["csv_to_fods"]
