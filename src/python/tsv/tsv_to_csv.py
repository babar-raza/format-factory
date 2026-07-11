"""
tsv_to_csv.py

Dogfood export: TSV -> CSV

Converts a TSV file to CSV using:
  - Format Factory tsv library (parse_tsv_strict) as the source reader
  - Format Factory csv library (write_csv_to_file) as the target writer

The TSV header row (if detected) becomes the CSV header row.
Each TSV data row becomes one CSV row.

Sprint: TSV-TO-CSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TSV-TO-CSV-DOGFOOD-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "tsv"))
sys.path.insert(0, str(_REPO))

from tsv.tsv_parser import parse_tsv_strict  # Format Factory source reader
from src.python.csv.csv_writer import write_csv_to_file  # Format Factory target writer


def tsv_to_csv(
    tsv_path: str | Path,
    dest_path: str | Path,
    *,
    include_headers: bool = True,
) -> int:
    """Convert a TSV file to CSV using Format Factory parsers/writers.

    The TSV header row (when detected) is passed through as the CSV header.
    Each data row becomes one CSV row with comma-delimited fields.

    Args:
        tsv_path: Path to the source .tsv file.
        dest_path: Path to write the target .csv file (parent dirs created).
        include_headers: If True (default) and the TSV has a header, write it
            as the CSV header row.

    Returns:
        Number of data rows written (not counting the header row).
    """
    tsv_path = Path(tsv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_tsv_strict(tsv_path)  # Format Factory tsv reader
    rows: list[list[str]] = result.get("rows", [])
    headers: list[str] | None = result.get("headers")

    write_csv_to_file(  # Format Factory csv writer
        rows,
        dest_path,
        headers=headers if include_headers else None,
    )
    return len(rows)


__all__ = ["tsv_to_csv"]
