"""
toml_to_dif.py — Dogfood export: TOML → DIF using Format Factory libraries.

Sprint: TOML-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TOML-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from toml.toml_codec import load_toml  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def toml_to_dif(
    toml_path: str | Path,
    dest_path: str | Path,
    *,
    title: str = "TOML Export",
) -> int:
    """Convert a TOML file to a DIF file, one row per key-value pair."""
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_toml(toml_path)  # Format Factory toml reader
    data = doc.get("data", doc) if isinstance(doc, dict) else doc

    dif_rows = []
    for key, value in data.items():
        dif_rows.append([
            DifCell(value=str(key), value_type="string"),
            DifCell(value=str(value), value_type="string"),
        ])

    doc = DifDocument(title=title, rows=dif_rows)
    write_dif(doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["toml_to_dif"]
