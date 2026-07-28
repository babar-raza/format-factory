"""
csv_to_fodt.py — Dogfood export: CSV → FODT using Format Factory libraries.

Reads a CSV file using Format Factory's CSV parser and writes each row
as a FODT paragraph using Format Factory's FODT writer.

Each CSV row becomes one FODT paragraph with cells joined by ' | '.

Sprint: CSV-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-CSV-TO-FODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ff_csv.csv_parser import parse_csv_strict  # FF source reader
from fodt.writer import write_fodt  # FF target writer


def csv_to_fodt(
    csv_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " | ",
    include_header: bool = True,
) -> int:
    """Convert a CSV file to a FODT flat text document, one paragraph per row.

    Each CSV row (including the header if present) becomes one FODT paragraph.
    Cell values within each row are joined with the separator string.

    Args:
        csv_path: Path to the source .csv file.
        dest_path: Path for the output .fodt file (parent dirs created).
        separator: String used to join cell values within a row.
        include_header: When True, the header row is included as the first paragraph.

    Returns:
        Number of paragraphs (rows) written.
    """
    csv_path = Path(csv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_csv_strict(csv_path)  # Format Factory csv reader
    headers = result.get("headers") or []
    rows = result.get("rows") or []

    blocks: list[dict] = []
    if include_header and headers:
        blocks.append({"type": "paragraph", "text": separator.join(str(h) for h in headers)})

    for row in rows:
        blocks.append({"type": "paragraph", "text": separator.join(str(v) for v in row)})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["csv_to_fodt"]
