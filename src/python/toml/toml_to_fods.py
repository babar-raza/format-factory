"""
toml_to_fods.py — Dogfood export: TOML → FODS using Format Factory libraries.

Reads a TOML file using Format Factory's TOML codec and writes each top-level
key-value pair as a FODS row using Format Factory's FODS writer.

Each top-level TOML entry becomes one FODS row with columns: key, value.

Sprint: TOML-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TOML-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import json as _json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "toml"))

from toml.toml_codec import load_toml  # FF source reader
from fods.writer import write_fods  # FF target writer


def toml_to_fods(
    toml_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a TOML file to a FODS flat spreadsheet, one row per top-level key.

    Each top-level TOML key becomes one FODS row with columns key and value.
    Tables and arrays are serialized as compact JSON strings.

    Args:
        toml_path: Path to the source .toml file.
        dest_path: Path for the output .fods file (parent dirs created).
        include_header: When True, writes a header row (key, value).
        sheet_name: Name of the FODS sheet tab.

    Returns:
        Number of data rows written (not counting the header).
    """
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    data = load_toml(toml_path)  # Format Factory toml reader

    def _make_row(values: list[str]) -> dict:
        return {
            "cells": [
                {"value": v, "value_type": "string", "text_content": v}
                for v in values
            ]
        }

    fods_rows: list[dict] = []
    if include_header:
        fods_rows.append(_make_row(["key", "value"]))

    data_count = 0
    for key, value in data.items():
        if isinstance(value, bool):
            val_str = "true" if value else "false"
        elif isinstance(value, (dict, list)):
            val_str = _json.dumps(value, ensure_ascii=False)
        else:
            val_str = str(value)
        fods_rows.append(_make_row([key, val_str]))
        data_count += 1

    workbook = {"sheets": [{"name": sheet_name, "rows": fods_rows}]}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return data_count


__all__ = ["toml_to_fods"]
