"""
toml_to_fodt.py — Dogfood export: TOML → FODT using Format Factory libraries.

Reads a TOML file using Format Factory's TOML codec and writes each top-level
key-value pair as a FODT paragraph using Format Factory's FODT writer.

Each TOML entry becomes one FODT paragraph in the form 'key = value'.

Sprint: TOML-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TOML-TO-FODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import json as _json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "toml"))

from toml.toml_codec import load_toml  # FF source reader
from fodt.writer import write_fodt  # FF target writer


def toml_to_fodt(
    toml_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert a TOML file to a FODT document, one paragraph per top-level key.

    Each top-level TOML key becomes one FODT paragraph in the form 'key = value'.
    Tables and arrays are serialized as compact JSON strings.

    Args:
        toml_path: Path to the source .toml file.
        dest_path: Path for the output .fodt file (parent dirs created).

    Returns:
        Number of paragraphs (keys) written.
    """
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    data = load_toml(toml_path)  # Format Factory toml reader

    blocks: list[dict] = []
    for key, value in data.items():
        if isinstance(value, bool):
            val_str = "true" if value else "false"
        elif isinstance(value, (dict, list)):
            val_str = _json.dumps(value, ensure_ascii=False)
        else:
            val_str = str(value)
        blocks.append({"type": "paragraph", "text": f"{key} = {val_str}"})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["toml_to_fodt"]
