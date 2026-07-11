"""
odt_to_toml.py — Dogfood export: ODT → TOML using Format Factory libraries.

Reads an OpenDocument Text (.odt) file using Format Factory's ODT parser
and writes each element as a TOML array table entry using Format Factory's
TOML writer.

Each ODT element becomes a [[elements]] entry with element_type and text fields.

Sprint: ODT-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODT-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "odt"))
sys.path.insert(0, str(_REPO))

from odt.odt_parser import OdtHeading, parse_odt_strict  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def odt_to_toml(
    odt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
    table_key: str = "elements",
) -> int:
    """Convert an ODT file to a TOML file, one [[elements]] entry per element.

    Each element has keys: element_type ("heading" or "paragraph") and text.

    Args:
        odt_path: Path to the source .odt file.
        dest_path: Path for the output .toml file (parent dirs created).
        skip_empty: When True, elements with empty text are omitted.
        table_key: Name for the TOML array table (default "elements").

    Returns:
        Number of elements written.
    """
    odt_path = Path(odt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_odt_strict(odt_path)  # Format Factory odt reader
    elements = doc.elements

    toml_entries: list[dict] = []
    for elem in elements:
        text = elem.text if elem.text else ""
        if skip_empty and not text.strip():
            continue
        elem_type = "heading" if isinstance(elem, OdtHeading) else "paragraph"
        toml_entries.append({"element_type": elem_type, "text": text})

    write_toml({table_key: toml_entries}, dest_path)  # Format Factory toml writer
    return len(toml_entries)


__all__ = ["odt_to_toml"]
