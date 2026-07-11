"""
fodg_to_csv.py — Dogfood export: FODG → CSV using Format Factory libraries.

Reads a Flat OpenDocument Graphics (.fodg) file using Format Factory's FODG
codec and writes each drawing page as a CSV row using Format Factory's CSV
writer.

Each page becomes one row with columns: page_name, text_content, shape_count.

Sprint: FODG-TO-CSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODG-TO-CSV-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodg"))
sys.path.insert(0, str(_REPO))

from fodg.fodg_codec import load as load_fodg  # Format Factory source reader
from src.python.csv.csv_writer import write_csv_to_file  # Format Factory target writer


def fodg_to_csv(
    fodg_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    include_page_index: bool = False,
    include_shape_count: bool = True,
) -> int:
    """Convert a FODG drawing file to CSV, one row per page.

    Each drawing page becomes one CSV row with columns page_name,
    text_content (joined), and optionally shape_count and page_index.

    Args:
        fodg_path: Path to the source .fodg file.
        dest_path: Path for the output .csv file (parent dirs created).
        include_header: When True, writes a header row.
        include_page_index: When True, adds page_index column (0-based).
        include_shape_count: When True, adds shape_count column.

    Returns:
        Number of data rows written (not counting the header).
    """
    fodg_path = Path(fodg_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(fodg_path)  # Format Factory fodg reader
    pages = doc.get("pages", [])

    headers: list[str] = []
    if include_page_index:
        headers.append("page_index")
    headers.append("page_name")
    headers.append("text_content")
    if include_shape_count:
        headers.append("shape_count")

    rows: list[list[str]] = []
    for idx, page in enumerate(pages):
        page_name = page.get("name", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)
        shape_count = str(page.get("shape_count", 0))

        row: list[str] = []
        if include_page_index:
            row.append(str(idx))
        row.append(page_name)
        row.append(text_content)
        if include_shape_count:
            row.append(shape_count)
        rows.append(row)

    write_csv_to_file(  # Format Factory csv writer
        rows,
        dest_path,
        headers=headers if include_header else None,
    )
    return len(rows)


__all__ = ["fodg_to_csv"]
