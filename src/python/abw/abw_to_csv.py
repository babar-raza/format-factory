"""
abw_to_csv.py — Dogfood export: ABW → CSV using Format Factory libraries.

Reads an AbiWord document using Format Factory's ABW codec and writes
each paragraph as a CSV row using Format Factory's CSV writer.

Each paragraph becomes one row with a "text" column (and an optional
"paragraph_index" column).

License: Apache-2.0
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "abw"))
sys.path.insert(0, str(_REPO))

from abw.abw_codec import load as load_abw
from src.python.csv.csv_writer import write_csv_to_file


def abw_to_csv(
    abw_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    include_paragraph_index: bool = False,
    skip_empty: bool = True,
) -> int:
    """Convert ABW paragraphs to CSV rows, one row per paragraph.

    Args:
        abw_path: Path to the source .abw file.
        dest_path: Path for the output .csv file (parent dirs created).
        include_header: When True, emits a header row.
        include_paragraph_index: When True, adds a paragraph_index column.
        skip_empty: When True, empty paragraphs are omitted.

    Returns:
        Number of data rows written (not counting the header).
    """
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_abw(abw_path)
    paragraphs = model.get("paragraphs", [])

    rows: list[list[str]] = []

    if include_header:
        header = ["text"]
        if include_paragraph_index:
            header.insert(0, "paragraph_index")
        rows.append(header)

    para_idx = 0
    data_count = 0
    for text in paragraphs:
        if skip_empty and not text:
            para_idx += 1
            continue
        row = [text]
        if include_paragraph_index:
            row.insert(0, str(para_idx))
        rows.append(row)
        data_count += 1
        para_idx += 1

    write_csv_to_file(rows, dest_path)
    return data_count
