"""
tsv_to_odt.py — Dogfood export: TSV → ODT using Format Factory libraries.

Reads a TSV file using Format Factory's TSV parser and writes each row as
a paragraph in an ODT document using Format Factory's ODT writer.

Each TSV row becomes one paragraph (tab-separated values).

Sprint: TSV-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TSV-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import parse_tsv_strict  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def tsv_to_odt(
    tsv_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = "\t",
    include_header_as_heading: bool = False,
) -> int:
    """Convert a TSV file to an ODT document, one paragraph per row.

    Each TSV data row becomes one paragraph with values separated by
    the separator character (default tab).

    Args:
        tsv_path: Path to the source .tsv file.
        dest_path: Path for the output .odt file (parent dirs created).
        separator: Character used to join cell values within a paragraph.
        include_header_as_heading: When True, the header row becomes the
            document heading instead of a paragraph.

    Returns:
        Number of paragraph rows written (not counting the heading).
    """
    tsv_path = Path(tsv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_tsv_strict(tsv_path)  # Format Factory tsv reader
    headers = result.get("headers") or []
    rows = result.get("rows") or []

    heading: str | None = None
    if include_header_as_heading and headers:
        heading = separator.join(str(h) for h in headers)

    paragraphs: list[str] = []
    if headers and not include_header_as_heading:
        paragraphs.append(separator.join(str(h) for h in headers))

    for row in rows:
        paragraphs.append(separator.join(str(v) for v in row))

    write_odt(paragraphs, dest_path, heading=heading)  # Format Factory odt writer
    return len(rows)


__all__ = ["tsv_to_odt"]
