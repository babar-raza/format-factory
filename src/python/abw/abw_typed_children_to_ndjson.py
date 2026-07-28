"""
abw_typed_children_to_ndjson.py — Dogfood export: ABW typed DOM → NDJSON.

Uses AbwDocument.typed_children() (D2 DOM) to iterate paragraphs as typed
AbwParagraph objects, then writes each as an NDJSON record via Format Factory's
ndjson library. Demonstrates the D2 typed-children API over the raw dict API.

Sprint: FORENSICS-HEALING-SPRINT-001
Authority: TC-DOGFOOD-001 -- Advance next dogfood export path
Ledger entry: R-ABW-TYPED-CHILDREN-TO-NDJSON-001
"""
from __future__ import annotations

from pathlib import Path


from abw.models import AbwDocument
from ndjson.ndjson_codec import write_ndjson


def abw_typed_children_to_ndjson(
    abw_path: "str | Path",
    dest_path: "str | Path",
    *,
    skip_empty: bool = True,
) -> int:
    """Convert ABW paragraphs to NDJSON using typed DOM children (D2 API).

    Loads the ABW file via AbwDocument, iterates paragraphs via
    typed_children(), and writes each non-empty paragraph as an NDJSON
    record with fields: index, text, word_count, char_count.

    Args:
        abw_path: Path to the source .abw file.
        dest_path: Path for the output .ndjson file (parent dirs created).
        skip_empty: When True, paragraphs with no text are omitted.

    Returns:
        Number of NDJSON records written.
    """
    doc = AbwDocument.from_file(abw_path)
    records = []
    for idx, para in enumerate(doc.typed_children()):
        if skip_empty and para.is_empty():
            continue
        records.append({
            "index": idx,
            "text": para.text,
            "word_count": para.word_count,
            "char_count": para.char_count,
        })
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    write_ndjson(records, dest_path)
    return len(records)
