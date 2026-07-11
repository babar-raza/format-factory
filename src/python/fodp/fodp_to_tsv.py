"""
fodp_to_tsv.py — Dogfood export: FODP → TSV using Format Factory libraries.

Reads a Flat OpenDocument Presentation (.fodp) file using Format Factory's
FODP codec and writes each presentation slide as a TSV row using Format
Factory's TSV writer.

Each slide becomes one row with columns: slide_name, title, text_content.

Sprint: FODP-TO-TSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-TSV-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodp"))

from fodp.fodp_codec import load as load_fodp  # Format Factory source reader
from tsv.tsv_parser import write_tsv  # Format Factory target writer


def fodp_to_tsv(
    fodp_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    include_slide_index: bool = False,
) -> int:
    """Convert a FODP presentation to TSV, one row per slide.

    Each slide becomes one TSV row with columns slide_name, title,
    and text_content (joined as a semicolon-separated string).

    Args:
        fodp_path: Path to the source .fodp file.
        dest_path: Path for the output .tsv file (parent dirs created).
        include_header: When True, writes a header row.
        include_slide_index: When True, adds slide_index column (0-based).

    Returns:
        Number of data rows written (not counting the header).
    """
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)  # Format Factory fodp reader
    pages = doc.get("pages", [])

    col_headers: list[str] = []
    if include_slide_index:
        col_headers.append("slide_index")
    col_headers.extend(["slide_name", "title", "text_content"])

    rows: list[list[str]] = []
    for idx, page in enumerate(pages):
        slide_name = page.get("name", "") or ""
        title = page.get("title", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)

        row: list[str] = []
        if include_slide_index:
            row.append(str(idx))
        row.extend([slide_name, title, text_content])
        rows.append(row)

    write_tsv(  # Format Factory tsv writer
        rows,
        dest_path,
        headers=col_headers if include_header else None,
    )
    return len(rows)


__all__ = ["fodp_to_tsv"]
