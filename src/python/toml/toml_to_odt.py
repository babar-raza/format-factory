"""
toml_to_odt.py — Dogfood export: TOML → ODT using Format Factory libraries.

Reads a TOML file using Format Factory's TOML codec and writes each top-level
key-value pair as a paragraph in an ODT document using Format Factory's ODT
writer.

Each top-level TOML entry becomes one ODT paragraph.

Sprint: TOML-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TOML-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import json as _json
from pathlib import Path

from toml.toml_codec import load_toml  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def toml_to_odt(
    toml_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert a TOML file to an ODT document, one paragraph per top-level key.

    Each top-level TOML key becomes one paragraph formatted as "key = value".
    Tables and arrays are serialized as compact JSON strings.

    Args:
        toml_path: Path to the source .toml file.
        dest_path: Path for the output .odt file (parent dirs created).

    Returns:
        Number of paragraphs written.
    """
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_toml(toml_path)  # Format Factory toml reader
    data = doc.get("data", doc) if isinstance(doc, dict) else doc

    paragraphs: list[str] = []
    for key, value in data.items():
        if isinstance(value, bool):
            val_str = "true" if value else "false"
        elif isinstance(value, (dict, list)):
            val_str = _json.dumps(value, ensure_ascii=False)
        else:
            val_str = str(value)
        paragraphs.append(f"{key} = {val_str}")

    write_odt(paragraphs, dest_path)  # Format Factory odt writer
    return len(paragraphs)


__all__ = ["toml_to_odt"]
