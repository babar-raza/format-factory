"""
toml_to_tsv.py — Dogfood export: TOML → TSV using Format Factory libraries.

Reads a TOML file using Format Factory's TOML codec and writes each
top-level key as a TSV row using Format Factory's TSV writer.

Each top-level key becomes one row with columns: key, value.
Table values are serialized as JSON strings; booleans as 'true'/'false'.

Sprint: TOML-TO-TSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TOML-TO-TSV-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import json
from pathlib import Path

from toml.toml_codec import load_toml  # Format Factory source reader
from tsv.tsv_parser import write_tsv  # Format Factory target writer


def toml_to_tsv(
    toml_path: str | Path,
    dest_path: str | Path,
    *,
    include_headers: bool = True,
) -> int:
    """Convert TOML top-level keys to TSV rows (key, value).

    Each top-level key in the TOML document becomes one TSV row.
    Table values are serialized as JSON strings.

    Args:
        toml_path: Path to the source .toml file.
        dest_path: Path for the output .tsv file (parent dirs created).
        include_headers: When True, emits a header row with key and value.

    Returns:
        Number of data rows written (not counting the header).
    """
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_toml(toml_path)  # Format Factory toml reader
    data = doc.get("data", {})
    top_level_keys = doc.get("top_level_keys", list(data.keys()))

    rows: list[list[str]] = []
    for key in top_level_keys:
        raw_value = data.get(key)
        if isinstance(raw_value, dict):
            value_str = json.dumps(raw_value)
        elif isinstance(raw_value, bool):
            value_str = str(raw_value).lower()
        elif raw_value is None:
            value_str = ""
        else:
            value_str = str(raw_value)
        rows.append([key, value_str])

    write_tsv(  # Format Factory tsv writer
        rows,
        dest_path,
        headers=["key", "value"] if include_headers else None,
    )
    return len(rows)


__all__ = ["toml_to_tsv"]
