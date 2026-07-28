"""
fodp_to_ndjson.py — Dogfood export: FODP → NDJSON using Format Factory libraries.

Reads a Flat ODF Presentation file using Format Factory's FODP codec and writes
each slide as a JSON record to an NDJSON file using Format Factory's NDJSON writer.

Each slide record contains: slide_name, slide_index, title, text_content (list),
and shape_count.

License: Apache-2.0
"""

from __future__ import annotations

from pathlib import Path

from fodp.fodp_codec import load as load_fodp
from ndjson.ndjson_codec import write_ndjson


def fodp_to_ndjson(
    fodp_path: str | Path,
    dest_path: str | Path,
    *,
    include_slide_index: bool = True,
    include_shape_count: bool = True,
) -> int:
    """Convert FODP slides to NDJSON records, one record per slide.

    Each record contains:
    - ``slide_name``: the slide name attribute (e.g. "Slide1")
    - ``title``: the slide title text
    - ``text_content``: list of text strings found in the slide
    - ``slide_index``: 0-based slide index (when include_slide_index=True)
    - ``shape_count``: number of shapes on the slide (when include_shape_count=True)

    Args:
        fodp_path: Path to the source .fodp file.
        dest_path: Path for the output .ndjson file (parent dirs created).
        include_slide_index: When True, adds a ``slide_index`` field.
        include_shape_count: When True, adds a ``shape_count`` field.

    Returns:
        Number of NDJSON records written (one per slide).
    """
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)
    pages = doc.get("pages", [])

    records = []
    for idx, page in enumerate(pages):
        record: dict = {
            "slide_name": page.get("name", ""),
            "title": page.get("title", "") or "",
            "text_content": page.get("text_content", []),
        }
        if include_slide_index:
            record["slide_index"] = idx
        if include_shape_count:
            record["shape_count"] = page.get("shape_count", 0)
        records.append(record)

    write_ndjson(records, dest_path)
    return len(records)
