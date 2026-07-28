"""
ndjson_to_fodt.py — Dogfood export: NDJSON → FODT using Format Factory libraries.

Reads an NDJSON file using Format Factory's NDJSON codec and writes each record
as a FODT paragraph using Format Factory's FODT writer.

Each NDJSON record becomes one FODT paragraph serialized as key=value pairs.

Sprint: NDJSON-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-NDJSON-TO-FODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from ndjson.ndjson_codec import load_ndjson  # FF source reader
from fodt.writer import write_fodt  # FF target writer


def ndjson_to_fodt(
    ndjson_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " | ",
) -> int:
    """Convert an NDJSON file to a FODT flat text document, one paragraph per record.

    Each NDJSON record becomes one FODT paragraph. Dict records are serialized as
    key=value pairs joined by separator. Non-dict records are converted to string.

    Args:
        ndjson_path: Path to the source .ndjson file.
        dest_path: Path for the output .fodt file (parent dirs created).
        separator: String used to join key=value pairs within a record.

    Returns:
        Number of paragraphs (records) written.
    """
    ndjson_path = Path(ndjson_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(ndjson_path)  # Format Factory ndjson reader

    blocks: list[dict] = []
    for rec in records:
        if isinstance(rec, dict):
            text = separator.join(f"{k}={v}" for k, v in rec.items())
        else:
            text = str(rec)
        blocks.append({"type": "paragraph", "text": text})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["ndjson_to_fodt"]
