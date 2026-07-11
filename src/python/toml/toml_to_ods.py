"""
toml_to_ods.py — Dogfood export: TOML → ODS using Format Factory libraries.

Reads a TOML file using Format Factory's TOML codec and writes each top-level
key-value pair as an ODS row using Format Factory's ODS writer.

Each top-level TOML entry becomes one ODS row with columns: key, value, value_type.

Sprint: TOML-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TOML-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import json as _json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "toml"))

from toml.toml_codec import load_toml  # FF source reader
from ods.ods_parser import OdsCell, OdsDocument, OdsRow, OdsSheet  # FF ODS model
from ods.ods_writer import write_ods  # FF target writer


def toml_to_ods(
    toml_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    include_value_type: bool = False,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a TOML file to an ODS spreadsheet, one row per top-level key.

    Each top-level TOML key becomes one ODS row with columns key and value.
    Tables and arrays are serialized as compact JSON strings.

    Args:
        toml_path: Path to the source .toml file.
        dest_path: Path for the output .ods file (parent dirs created).
        include_header: When True, writes a header row.
        include_value_type: When True, adds value_type column.
        sheet_name: Name of the output sheet (default "Sheet1").

    Returns:
        Number of data rows written (not counting the header).
    """
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    data = load_toml(toml_path)  # Format Factory toml reader

    col_headers = ["key", "value"]
    if include_value_type:
        col_headers.append("value_type")

    ods_rows: list[OdsRow] = []
    if include_header:
        ods_rows.append(OdsRow(cells=[OdsCell(text=h) for h in col_headers]))

    data_count = 0
    for key, value in data.items():
        if isinstance(value, bool):
            val_str = "true" if value else "false"
            vtype = "boolean"
        elif isinstance(value, int):
            val_str = str(value)
            vtype = "integer"
        elif isinstance(value, float):
            val_str = str(value)
            vtype = "float"
        elif isinstance(value, dict):
            val_str = _json.dumps(value, ensure_ascii=False)
            vtype = "table"
        elif isinstance(value, list):
            val_str = _json.dumps(value, ensure_ascii=False)
            vtype = "array"
        else:
            val_str = str(value)
            vtype = "string"

        cells = [OdsCell(text=key), OdsCell(text=val_str)]
        if include_value_type:
            cells.append(OdsCell(text=vtype))
        ods_rows.append(OdsRow(cells=cells))
        data_count += 1

    sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    doc = OdsDocument(sheets=[sheet])
    write_ods(doc, dest_path)  # Format Factory ods writer
    return data_count


__all__ = ["toml_to_ods"]
