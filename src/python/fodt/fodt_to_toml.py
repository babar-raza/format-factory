"""
fodt_to_toml.py — Dogfood export: FODT → TOML using Format Factory libraries.

Reads a Flat OpenDocument Text (.fodt) file using Format Factory's FODT parser
and writes each block as a TOML array table entry using Format Factory's TOML writer.

Each FODT block becomes a [[blocks]] entry with block_type and text fields.

Sprint: FODT-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodt.parser import parse_fodt  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def fodt_to_toml(
    fodt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
    table_key: str = "blocks",
) -> int:
    """Convert a FODT flat text document to a TOML file, one [[blocks]] entry per block.

    Each block has keys: block_type ("paragraph" or "heading") and text.

    Args:
        fodt_path: Path to the source .fodt file.
        dest_path: Path for the output .toml file (parent dirs created).
        skip_empty: When True, blocks with empty text are omitted.
        table_key: Name for the TOML array table (default "blocks").

    Returns:
        Number of blocks written.
    """
    fodt_path = Path(fodt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fodt(str(fodt_path))  # Format Factory fodt reader
    blocks = doc.get("blocks", [])

    toml_entries: list[dict] = []
    for block in blocks:
        text = block.get("text", "") or ""
        if skip_empty and not text.strip():
            continue
        block_type = block.get("type", "paragraph") or "paragraph"
        toml_entries.append({"block_type": block_type, "text": text})

    write_toml({table_key: toml_entries}, dest_path)  # Format Factory toml writer
    return len(toml_entries)


__all__ = ["fodt_to_toml"]
