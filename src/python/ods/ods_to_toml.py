"""
ods_to_toml.py — Dogfood export: ODS → TOML using Format Factory libraries.

Reads an ODS file using Format Factory's ODS parser and writes the rows
as a TOML file using Format Factory's TOML writer.

Each ODS row becomes a [[rows]] array table entry in TOML.

Sprint: ODS-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODS-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ods.ods_parser import parse_ods_strict  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def ods_to_toml(
    ods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    table_key: str = "rows",
) -> int:
    """Convert an ODS spreadsheet to a TOML file, one [[rows]] entry per row.

    Cell values are coerced to strings. Columns are named col_0, col_1, etc.

    Args:
        ods_path: Path to the source .ods file.
        dest_path: Path for the output .toml file (parent dirs created).
        sheet_index: Which sheet to export (0-based, default 0).
        table_key: Name for the TOML array table (default "rows").

    Returns:
        Number of data rows written.
    """
    ods_path = Path(ods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_ods_strict(ods_path)  # Format Factory ods reader
    sheets = doc.sheets if hasattr(doc, "sheets") else []

    toml_rows: list[dict] = []
    if sheets and sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        for row in sheet.rows:
            entry: dict[str, str] = {}
            for i, cell in enumerate(row.cells):
                text = cell.text if cell.text else (str(cell.value) if cell.value is not None else "")
                entry[f"col_{i}"] = text
            toml_rows.append(entry)

    write_toml({table_key: toml_rows}, dest_path)  # Format Factory toml writer
    return len(toml_rows)


__all__ = ["ods_to_toml"]
