"""
toml_to_fodg.py — Dogfood export: TOML → FODG using Format Factory libraries.

Sprint: TOML-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TOML-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from toml.toml_codec import load_toml  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def toml_to_fodg(
    toml_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert a TOML file to a FODG drawing, one page per top-level key."""
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_toml(toml_path)  # Format Factory toml reader
    data = doc.get("data", doc) if isinstance(doc, dict) else doc

    pages_list = []
    if isinstance(data, dict):
        for key, val in data.items():
            pages_list.append({"name": str(key), "texts": [str(key), str(val)]})

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["toml_to_fodg"]
