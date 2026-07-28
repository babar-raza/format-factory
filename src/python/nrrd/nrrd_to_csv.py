"""
nrrd_to_csv.py — Dogfood export: nrrd → CSV using Format Factory libraries.

Reads an NRRD volume using Format Factory's nrrd codec and writes its
header fields and key/value metadata pairs as CSV rows using Format
Factory's CSV writer: one row per (field, value) pair. A metadata export
rather than a full array dump -- safe regardless of volume size, and the
shape most external tooling actually wants (searchable/filterable
metadata, not a potentially huge raw data table).

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from nrrd.nrrd_codec import load_nrrd
from ff_csv.csv_writer import write_csv_to_file


def nrrd_to_csv(
    nrrd_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
) -> int:
    """Convert header fields and key/value pairs to CSV rows.

    Args:
        nrrd_path: Path to the source .nrrd file.
        dest_path: Path for the output .csv file (parent dirs created).
        include_header: When True, emits a header row.

    Returns:
        Number of data rows written (not counting the header).
    """
    nrrd_path = Path(nrrd_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_nrrd(nrrd_path)

    rows: list[list[str]] = []
    header = ["field", "value", "source"]

    for field, value in model.get("header", {}).items():
        rows.append([str(field), str(value), "header"])
    for key, value in model.get("key_value_pairs", {}).items():
        rows.append([str(key), str(value), "key_value_pair"])

    write_csv_to_file(rows, dest_path, headers=header if include_header else None)
    return len(rows)
