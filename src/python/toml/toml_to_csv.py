"""
toml_to_csv.py — Dogfood export: TOML → CSV using Format Factory libraries.

Reads a TOML file using Format Factory's TOML codec and writes the
top-level key-value pairs as CSV rows using Format Factory's CSV writer.

Each top-level TOML key becomes one CSV row with two columns: key and value.
This produces a simple two-column CSV representation of the TOML document.

License: Apache-2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "toml"))
sys.path.insert(0, str(_REPO))

from toml.toml_codec import load_toml
from src.python.csv.csv_writer import write_csv_to_file


def toml_to_csv(
    toml_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    include_value_type: bool = False,
) -> int:
    """Convert TOML top-level keys to CSV rows (key, value).

    Each top-level key in the TOML document becomes one CSV row.
    Table values are serialized as JSON strings.

    Args:
        toml_path: Path to the source .toml file.
        dest_path: Path for the output .csv file (parent dirs created).
        include_header: When True, emits a header row "key,value[,type]".
        include_value_type: When True, adds a third column "type" to each row.

    Returns:
        Number of data rows written (not counting the header).
    """
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_toml(toml_path)
    data = doc.get("data", {})
    top_level_keys = doc.get("top_level_keys", list(data.keys()))

    rows: list[list[str]] = []

    if include_header:
        header = ["key", "value"]
        if include_value_type:
            header.append("type")
        rows.append(header)

    for key in top_level_keys:
        raw_value = data.get(key)
        if isinstance(raw_value, dict):
            value_str = json.dumps(raw_value)
            value_type = "table"
        elif isinstance(raw_value, bool):
            value_str = str(raw_value).lower()
            value_type = "boolean"
        elif isinstance(raw_value, int):
            value_str = str(raw_value)
            value_type = "integer"
        elif isinstance(raw_value, float):
            value_str = str(raw_value)
            value_type = "float"
        elif raw_value is None:
            value_str = ""
            value_type = "null"
        else:
            value_str = str(raw_value)
            value_type = "string"

        row = [key, value_str]
        if include_value_type:
            row.append(value_type)
        rows.append(row)

    write_csv_to_file(rows, dest_path)
    # Return only data row count (exclude header)
    return len(rows) - (1 if include_header else 0)
