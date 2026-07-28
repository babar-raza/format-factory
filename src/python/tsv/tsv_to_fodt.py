"""
tsv_to_fodt.py — Dogfood export: TSV → FODT using Format Factory libraries.

Reads a TSV file using Format Factory's TSV parser and writes each row
as a FODT paragraph using Format Factory's FODT writer.

Each TSV row becomes one FODT paragraph with cells joined by ' | '.

Sprint: TSV-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TSV-TO-FODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from tsv.tsv_parser import parse_tsv_strict  # FF source reader
from fodt.writer import write_fodt  # FF target writer


def tsv_to_fodt(
    tsv_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " | ",
    include_header: bool = True,
) -> int:
    """Convert a TSV file to a FODT flat text document, one paragraph per row.

    Each TSV row becomes one FODT paragraph. Cell values are joined with separator.

    Args:
        tsv_path: Path to the source .tsv file.
        dest_path: Path for the output .fodt file (parent dirs created).
        separator: String used to join cell values within a row.
        include_header: When True, the header row is included as the first paragraph.

    Returns:
        Number of paragraphs (rows) written.
    """
    tsv_path = Path(tsv_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    result = parse_tsv_strict(tsv_path)  # Format Factory tsv reader
    headers = result.get("headers") or []
    rows = result.get("rows") or []

    blocks: list[dict] = []
    if include_header and headers:
        blocks.append({"type": "paragraph", "text": separator.join(str(h) for h in headers)})

    for row in rows:
        blocks.append({"type": "paragraph", "text": separator.join(str(v) for v in row)})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["tsv_to_fodt"]
