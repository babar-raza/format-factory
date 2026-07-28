"""
abw_to_tsv.py — Dogfood export: ABW → TSV using Format Factory libraries.

Reads an AbiWord (.abw) document using Format Factory's ABW codec and
writes each paragraph as a TSV row using Format Factory's TSV writer.

Each non-empty paragraph becomes one row with a 'text' column.

Sprint: ABW-TO-TSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-TSV-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from abw.abw_codec import load as load_abw  # Format Factory source reader
from tsv.tsv_parser import write_tsv  # Format Factory target writer


def abw_to_tsv(
    abw_path: str | Path,
    dest_path: str | Path,
    *,
    include_headers: bool = True,
    skip_empty: bool = True,
) -> int:
    """Convert an ABW file to TSV, one row per paragraph.

    Each paragraph in the ABW document becomes one TSV row with
    a single 'text' column.

    Args:
        abw_path: Path to the source .abw file.
        dest_path: Path for the output .tsv file (parent dirs created).
        include_headers: When True, writes a header row with 'text'.
        skip_empty: When True, paragraphs with empty text are omitted.

    Returns:
        Number of data rows written (not counting the header).
    """
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_abw(abw_path)  # Format Factory abw reader
    paragraphs = model.get("paragraphs", [])

    rows: list[list[str]] = []
    for text in paragraphs:
        if skip_empty and not text:
            continue
        rows.append([text])

    write_tsv(  # Format Factory tsv writer
        rows,
        dest_path,
        headers=["text"] if include_headers else None,
    )
    return len(rows)


__all__ = ["abw_to_tsv"]
