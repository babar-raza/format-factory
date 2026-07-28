"""
toml_to_gnumeric.py — Dogfood export: TOML → Gnumeric using Format Factory libraries.

Sprint: TOML-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TOML-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from toml.toml_codec import load_toml  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def toml_to_gnumeric(
    toml_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert TOML to a Gnumeric spreadsheet, one row per key-value pair."""
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_toml(toml_path)  # Format Factory toml reader
    data = doc.get("data", doc) if isinstance(doc, dict) else doc

    cell_grid: dict = {}
    for r, (key, value) in enumerate(data.items()):
        cell_grid[(r, 0)] = str(key)
        cell_grid[(r, 1)] = str(value)

    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)  # Format Factory gnumeric writer
    return len(data)


__all__ = ["toml_to_gnumeric"]
