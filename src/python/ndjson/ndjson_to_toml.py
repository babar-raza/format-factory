"""
ndjson_to_toml.py — Dogfood export: NDJSON → TOML using Format Factory libraries.

Reads an NDJSON file using Format Factory's NDJSON codec and writes the records
as a TOML file using Format Factory's TOML writer.

Dict records become [[records]] array table entries. Non-dict records are stored
in a "values" scalar list.

Sprint: NDJSON-TO-TOML-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-NDJSON-TO-TOML-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from ndjson.ndjson_codec import load_ndjson  # FF source reader
from toml.toml_codec import write_toml  # FF target writer


def ndjson_to_toml(
    ndjson_path: str | Path,
    dest_path: str | Path,
    *,
    table_key: str = "records",
) -> int:
    """Convert an NDJSON file to a TOML file.

    Dict records are written as TOML array table entries ([[table_key]]).
    Non-dict records are converted to strings and stored as a "values" list.

    Args:
        ndjson_path: Path to the source .ndjson file.
        dest_path: Path for the output .toml file (parent dirs created).
        table_key: Name for the TOML array table (default "records").

    Returns:
        Number of records written.
    """
    ndjson_path = Path(ndjson_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(ndjson_path)  # Format Factory ndjson reader

    if not records:
        write_toml({table_key: []}, dest_path)
        return 0

    all_dict = all(isinstance(r, dict) for r in records)
    if all_dict:
        # Coerce all values to strings for TOML compatibility
        toml_records = [
            {k: str(v) if v is not None else "" for k, v in rec.items()}
            for rec in records
        ]
        data = {table_key: toml_records}
    else:
        data = {"values": [str(r) for r in records]}

    write_toml(data, dest_path)  # Format Factory toml writer
    return len(records)


__all__ = ["ndjson_to_toml"]
