"""
toml_to_ndjson.py

Dogfood export: TOML -> NDJSON

Converts a TOML configuration file into NDJSON records using:
  - Format Factory toml library (load_toml) as the source reader
  - Format Factory ndjson library (write_ndjson) as the target writer

Each top-level TOML key becomes one NDJSON record with fields:
  key, value, value_type, and optionally key_index.

Sprint: TOML-TO-NDJSON-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TOML-TO-NDJSON-DOGFOOD-001
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "toml"))
sys.path.insert(0, str(_REPO / "src" / "python" / "ndjson"))

from toml.toml_codec import load_toml  # Format Factory source reader
from ndjson.ndjson_codec import write_ndjson  # Format Factory target writer


def toml_to_ndjson(
    toml_path: str | Path,
    dest_path: str | Path,
    *,
    include_key_index: bool = True,
) -> int:
    """
    Convert a TOML file to NDJSON records using Format Factory writers.

    Each top-level key in the TOML document becomes one NDJSON record.
    Nested tables (dict values) are serialized as JSON strings.

    Parameters
    ----------
    toml_path:
        Path to the source .toml file.
    dest_path:
        Path to write the target .ndjson file.
    include_key_index:
        If True, adds a 0-based key_index field to each record.

    Returns
    -------
    int
        Number of NDJSON records written.
    """
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)

    doc = load_toml(toml_path)  # Format Factory toml reader
    data: dict = doc.get("data", {})
    top_level_keys: list[str] = doc.get("top_level_keys", list(data.keys()))

    records: list[dict] = []
    for idx, key in enumerate(top_level_keys):
        raw_value = data.get(key)
        if isinstance(raw_value, dict):
            value_str = json.dumps(raw_value)
            value_type = "table"
        elif isinstance(raw_value, list):
            value_str = json.dumps(raw_value)
            value_type = "array"
        elif isinstance(raw_value, bool):
            value_str = str(raw_value).lower()
            value_type = "boolean"
        elif isinstance(raw_value, int):
            value_str = str(raw_value)
            value_type = "integer"
        elif isinstance(raw_value, float):
            value_str = str(raw_value)
            value_type = "float"
        else:
            value_str = str(raw_value) if raw_value is not None else ""
            value_type = "string"

        record: dict = {"key": key, "value": value_str, "value_type": value_type}
        if include_key_index:
            record["key_index"] = idx

        records.append(record)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    write_ndjson(records, dest_path)  # Format Factory ndjson writer
    return len(records)


__all__ = ["toml_to_ndjson"]
