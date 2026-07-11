"""
fods_to_toml.py — Dogfood export: FODS → TOML using Format Factory libraries.

Reads a FODS file using Format Factory's FODS parser and writes the rows
as a TOML file using Format Factory's TOML writer.

Each FODS row becomes a [[rows]] array table entry in TOML.

Sprint: FODS-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODS-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "fods"))
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fods.parser import parse_fods_strict  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def fods_to_toml(
    fods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    table_key: str = "rows",
) -> int:
    """Convert a FODS flat spreadsheet to a TOML file, one [[rows]] entry per row.

    Cell values are coerced to strings. Columns are named col_0, col_1, etc.

    Args:
        fods_path: Path to the source .fods file.
        dest_path: Path for the output .toml file (parent dirs created).
        sheet_index: Which sheet to export (0-based, default 0).
        table_key: Name for the TOML array table (default "rows").

    Returns:
        Number of data rows written.
    """
    fods_path = Path(fods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fods_strict(fods_path)  # Format Factory fods reader
    sheets = doc.get("sheets", [])

    toml_rows: list[dict] = []
    if sheets and sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        for row in sheet.get("rows", []):
            cells = row.get("cells", [])
            entry: dict[str, str] = {}
            for i, cell in enumerate(cells):
                if cell.get("is_covered"):
                    entry[f"col_{i}"] = ""
                else:
                    value = cell.get("value")
                    entry[f"col_{i}"] = "" if value is None else str(value)
            toml_rows.append(entry)

    write_toml({table_key: toml_rows}, dest_path)  # Format Factory toml writer
    return len(toml_rows)


__all__ = ["fods_to_toml"]
