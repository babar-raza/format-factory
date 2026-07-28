"""
csv_to_tsv.py

Dogfood export: CSV -> TSV

Converts a CSV file to TSV using:
  - Format Factory csv library (parse_csv_strict) as the source reader
  - Format Factory tsv library (write_tsv) as the target writer

The CSV header row (if detected) becomes the TSV header row.
Each CSV data row becomes one TSV row.

Sprint: CSV-TO-TSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-CSV-TO-TSV-DOGFOOD-001
"""
from __future__ import annotations

from pathlib import Path

from ff_csv.csv_parser import parse_csv_strict  # Format Factory source reader
from tsv.tsv_parser import write_tsv  # Format Factory target writer


def csv_to_tsv(
    csv_path: str | Path,
    dest_path: str | Path,
    *,
    include_headers: bool = True,
) -> int:
    """Convert a CSV file to TSV using Format Factory parsers/writers.

    The CSV header row (when detected) is passed through as the TSV header.
    Each data row becomes one TSV row with tab-delimited fields.

    Args:
        csv_path: Path to the source .csv file.
        dest_path: Path to write the target .tsv file (parent dirs created).
        include_headers: If True (default) and the CSV has a header, write it
            as the TSV header row.

    Returns:
        Number of data rows written (not counting the header row).
    """
    csv_path = Path(csv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_csv_strict(csv_path)  # Format Factory csv reader
    rows: list[list[str]] = result.get("rows", [])
    headers: list[str] | None = result.get("headers")

    write_tsv(  # Format Factory tsv writer
        rows,
        dest_path,
        headers=headers if include_headers else None,
    )
    return len(rows)


__all__ = ["csv_to_tsv"]
