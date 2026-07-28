"""
ndjson_to_abw.py — Dogfood export: NDJSON → ABW using Format Factory libraries.

Reads an NDJSON file using Format Factory's NDJSON codec and writes each record
as an ABW paragraph using Format Factory's ABW writer.

Each NDJSON record becomes one ABW paragraph (key=value for dicts, string for scalars).

Sprint: NDJSON-TO-ABW-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-NDJSON-TO-ABW-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from ndjson.ndjson_codec import load_ndjson  # FF source reader
from abw.abw_codec import write_abw  # FF target writer


def ndjson_to_abw(
    ndjson_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = ", ",
) -> int:
    """Convert an NDJSON file to an ABW document, one paragraph per record.

    Dict records become paragraphs with 'key=value' pairs joined by the separator.
    Scalar records become paragraphs with str() representation.

    Args:
        ndjson_path: Path to the source .ndjson file.
        dest_path: Path for the output .abw file (parent dirs created).
        separator: String used to join key=value pairs for dict records.

    Returns:
        Number of paragraphs (records) written.
    """
    ndjson_path = Path(ndjson_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(ndjson_path)  # Format Factory ndjson reader

    paragraphs: list[str] = []
    for rec in records:
        if isinstance(rec, dict):
            text = separator.join(f"{k}={v}" for k, v in rec.items())
        else:
            text = str(rec)
        paragraphs.append(text)

    model = {"is_abw": True, "paragraphs": paragraphs}
    write_abw(model, dest_path)  # Format Factory abw writer
    return len(paragraphs)


__all__ = ["ndjson_to_abw"]
