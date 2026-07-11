"""
toml_to_abw.py — Dogfood export: TOML → ABW using Format Factory libraries.

Reads a TOML file using Format Factory's TOML codec and writes key-value pairs
as ABW paragraphs using Format Factory's ABW writer.

Each top-level TOML key-value pair becomes one ABW paragraph.

Sprint: TOML-TO-ABW-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TOML-TO-ABW-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.toml_codec import load_toml  # FF source reader
from abw.abw_codec import write_abw  # FF target writer


def toml_to_abw(
    toml_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert a TOML file to an ABW document, one paragraph per key-value pair.

    Top-level scalar key=value pairs each become one ABW paragraph.
    List or table values are represented as their string form.

    Args:
        toml_path: Path to the source .toml file.
        dest_path: Path for the output .abw file (parent dirs created).

    Returns:
        Number of paragraphs written.
    """
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    data = load_toml(toml_path)  # Format Factory toml reader

    paragraphs: list[str] = []
    for key, value in data.items():
        paragraphs.append(f"{key} = {value}")

    model = {"is_abw": True, "paragraphs": paragraphs}
    write_abw(model, dest_path)  # Format Factory abw writer
    return len(paragraphs)


__all__ = ["toml_to_abw"]
