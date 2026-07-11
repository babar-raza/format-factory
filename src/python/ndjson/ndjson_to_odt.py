"""
ndjson_to_odt.py — Dogfood export: NDJSON → ODT using Format Factory libraries.

Reads an NDJSON file using Format Factory's NDJSON codec and writes each
record as a paragraph in an ODT document using Format Factory's ODT writer.

Each NDJSON record becomes one paragraph (JSON-formatted or key=value string).

Sprint: NDJSON-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-NDJSON-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import json as _json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import load_ndjson  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def ndjson_to_odt(
    ndjson_path: str | Path,
    dest_path: str | Path,
    *,
    format_as_json: bool = False,
) -> int:
    """Convert an NDJSON file to an ODT document, one paragraph per record.

    Each JSON record becomes one paragraph. Dict records are formatted as
    "key: value, key: value, ..." (or as compact JSON if format_as_json=True).
    Scalar records become their string representation.

    Args:
        ndjson_path: Path to the source .ndjson file.
        dest_path: Path for the output .odt file (parent dirs created).
        format_as_json: When True, serialize each record as compact JSON.

    Returns:
        Number of paragraphs written.
    """
    ndjson_path = Path(ndjson_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(ndjson_path)  # Format Factory ndjson reader

    paragraphs: list[str] = []
    for rec in records:
        if format_as_json:
            paragraphs.append(_json.dumps(rec, ensure_ascii=False))
        elif isinstance(rec, dict):
            parts = [f"{k}: {v}" for k, v in rec.items()]
            paragraphs.append(", ".join(parts))
        else:
            paragraphs.append(str(rec))

    write_odt(paragraphs, dest_path)  # Format Factory odt writer
    return len(paragraphs)


__all__ = ["ndjson_to_odt"]
