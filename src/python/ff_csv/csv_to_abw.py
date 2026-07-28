"""
csv_to_abw.py — Dogfood export: CSV → ABW using Format Factory libraries.

Reads a CSV file using Format Factory's CSV parser and writes each row
as an ABW paragraph using Format Factory's ABW writer.

Sprint: CSV-TO-ABW-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-CSV-TO-ABW-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ff_csv.csv_parser import parse_csv_strict  # FF source reader
from abw.abw_codec import write_abw  # FF target writer


def csv_to_abw(
    csv_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " | ",
    include_header: bool = True,
) -> int:
    """Convert a CSV file to an ABW document, one paragraph per row."""
    csv_path = Path(csv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_csv_strict(csv_path)  # Format Factory csv reader (returns dict)
    headers = result.get("headers") or []
    data_rows = result.get("rows") or []

    paragraphs: list[str] = []
    if include_header and headers:
        paragraphs.append(separator.join(str(h) for h in headers))
    for row in data_rows:
        paragraphs.append(separator.join(str(v) for v in row))

    model = {"is_abw": True, "paragraphs": paragraphs}
    write_abw(model, dest_path)  # Format Factory abw writer
    return len(paragraphs)


__all__ = ["csv_to_abw"]
