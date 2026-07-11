"""
fodt_to_csv.py — Dogfood export: FODT → CSV using Format Factory libraries.

Reads a Flat OpenDocument Text (.fodt) file using Format Factory's FODT parser
and writes each document block (paragraph or heading) as a CSV row using
Format Factory's CSV writer.

Each block becomes one row with columns: block_type, text.

Sprint: FODT-TO-CSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-CSV-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodt"))
sys.path.insert(0, str(_REPO))

from fodt.parser import parse_fodt  # Format Factory source reader
from src.python.csv.csv_writer import write_csv_to_file  # Format Factory target writer


def fodt_to_csv(
    fodt_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    skip_empty: bool = True,
) -> int:
    """Convert a FODT file to CSV, one row per document block.

    Each paragraph or heading becomes one CSV row with columns
    block_type and text.

    Args:
        fodt_path: Path to the source .fodt file.
        dest_path: Path for the output .csv file (parent dirs created).
        include_header: When True, writes a header row (block_type,text).
        skip_empty: When True, blocks with empty text are omitted.

    Returns:
        Number of data rows written (not counting the header).
    """
    fodt_path = Path(fodt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fodt(str(fodt_path))  # Format Factory fodt reader
    blocks = doc.get("blocks", [])

    rows: list[list[str]] = []
    for block in blocks:
        block_type = block.get("type", "paragraph")
        text = block.get("text", "")
        if skip_empty and not text:
            continue
        rows.append([block_type, text])

    write_csv_to_file(  # Format Factory csv writer
        rows,
        dest_path,
        headers=["block_type", "text"] if include_header else None,
    )
    return len(rows)


__all__ = ["fodt_to_csv"]
