"""
dif_to_toml.py — Dogfood export: DIF → TOML using Format Factory libraries.

Reads a DIF file using Format Factory's DIF parser and writes the rows
as a TOML file using Format Factory's TOML writer.

Each DIF row becomes a [[rows]] array table entry in TOML.

Sprint: DIF-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from dif.dif_parser import parse_dif_strict  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def dif_to_toml(
    dif_path: str | Path,
    dest_path: str | Path,
    *,
    table_key: str = "rows",
) -> int:
    """Convert a DIF file to a TOML file, one [[rows]] entry per row.

    Cell values are coerced to strings. DIF string values have surrounding
    quotes stripped. Columns are named col_0, col_1, etc.

    Args:
        dif_path: Path to the source .dif file.
        dest_path: Path for the output .toml file (parent dirs created).
        table_key: Name for the TOML array table (default "rows").

    Returns:
        Number of rows written.
    """
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(dif_path)  # Format Factory dif reader

    toml_rows: list[dict] = []
    for row in doc.rows:
        entry: dict[str, str] = {}
        for i, cell in enumerate(row):
            raw = str(cell.value) if cell.value is not None else ""
            val = raw[1:-1] if raw.startswith('"') and raw.endswith('"') else raw
            entry[f"col_{i}"] = val
        toml_rows.append(entry)

    write_toml({table_key: toml_rows}, dest_path)  # Format Factory toml writer
    return len(toml_rows)


__all__ = ["dif_to_toml"]
