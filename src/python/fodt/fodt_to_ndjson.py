"""
fodt_to_ndjson.py

Dogfood export: FODT → NDJSON

Converts a Flat OpenDocument Text (.fodt) file into NDJSON records using:
  - Format Factory fodt library (parse_fodt) as the source reader
  - Format Factory ndjson library (write_ndjson) as the target writer

Each FODT block (heading or paragraph) becomes one NDJSON record.

Sprint: autonomous-loop-20260621-220000-ed51041f
Authority: TASK-012 — Advance one dogfood export path
Ledger entry: R90-FODT-TO-NDJSON-DOGFOOD-001
"""
from __future__ import annotations

from pathlib import Path

from fodt.parser import parse_fodt  # Format Factory source reader
from ndjson.ndjson_codec import write_ndjson  # Format Factory target writer


def fodt_to_ndjson(
    fodt_path: str | Path,
    dest_path: str | Path,
    *,
    include_block_index: bool = True,
    include_heading_level: bool = True,
) -> int:
    """
    Convert a FODT file to NDJSON records using Format Factory writers.

    Each block (paragraph or heading) in the FODT document becomes one
    NDJSON record with fields: block_index, block_type, text, and
    optionally heading_level.

    Parameters
    ----------
    fodt_path:
        Path to the source .fodt file.
    dest_path:
        Path to write the target .ndjson file.
    include_block_index:
        If True, adds a 0-based block_index field to each record.
    include_heading_level:
        If True, adds heading_level field to heading records.

    Returns
    -------
    int
        Number of NDJSON records written.
    """
    fodt_path = Path(fodt_path)
    dest_path = Path(dest_path)

    doc = parse_fodt(str(fodt_path))  # Format Factory fodt reader
    blocks = doc.get("blocks", [])

    records: list[dict] = []
    for idx, block in enumerate(blocks):
        block_type = block.get("type", "paragraph")
        text = block.get("text", "")

        record: dict = {
            "block_type": block_type,
            "text": text,
        }
        if include_block_index:
            record["block_index"] = idx
        if include_heading_level and block_type == "heading":
            level = block.get("heading_level") or block.get("level")
            if level is not None:
                record["heading_level"] = level

        records.append(record)

    write_ndjson(records, dest_path)  # Format Factory ndjson writer
    return len(records)


__all__ = ["fodt_to_ndjson"]
