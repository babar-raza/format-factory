"""
fodg_to_ndjson.py — Dogfood export: FODG → NDJSON using Format Factory libraries.

Reads a Flat ODF Graphics document using Format Factory's FODG codec and writes
each drawing page as a JSON record to an NDJSON file using Format Factory's
NDJSON writer.

Each page record contains: page_name, page_index, shape_count, and text_content
(list of text strings extracted from the page's shapes).

License: Apache-2.0
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodg"))
sys.path.insert(0, str(_REPO / "src" / "python" / "ndjson"))

from fodg.fodg_codec import load as load_fodg
from ndjson.ndjson_codec import write_ndjson


def fodg_to_ndjson(
    fodg_path: str | Path,
    dest_path: str | Path,
    *,
    include_page_index: bool = True,
    include_shape_count: bool = True,
) -> int:
    """Convert FODG drawing pages to NDJSON records, one record per page.

    Each record contains:
    - ``page_name``: the page name attribute (e.g. "Page1")
    - ``text_content``: list of text strings extracted from shapes on the page
    - ``page_index``: 0-based page index (when include_page_index=True)
    - ``shape_count``: number of shapes on the page (when include_shape_count=True)

    Args:
        fodg_path: Path to the source .fodg file.
        dest_path: Path for the output .ndjson file (parent dirs created).
        include_page_index: When True, adds a ``page_index`` field.
        include_shape_count: When True, adds a ``shape_count`` field.

    Returns:
        Number of NDJSON records written (one per page).
    """
    fodg_path = Path(fodg_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(fodg_path)
    pages = doc.get("pages", [])

    records = []
    for idx, page in enumerate(pages):
        record: dict = {
            "page_name": page.get("name", ""),
            "text_content": page.get("text_content", []),
        }
        if include_page_index:
            record["page_index"] = idx
        if include_shape_count:
            record["shape_count"] = page.get("shape_count", 0)
        records.append(record)

    write_ndjson(records, dest_path)
    return len(records)
