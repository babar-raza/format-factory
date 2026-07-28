"""
odt_to_ndjson.py

Dogfood export: ODT -> NDJSON

Converts an OpenDocument Text (.odt) file into NDJSON records using:
  - Format Factory odt library (parse_odt_strict) as the source reader
  - Format Factory ndjson library (write_ndjson) as the target writer

Each ODT element (paragraph, heading, or list item) becomes one NDJSON record.

Sprint: ODT-TO-NDJSON-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODT-TO-NDJSON-DOGFOOD-001
"""
from __future__ import annotations

from pathlib import Path

from odt.odt_parser import OdtHeading, OdtListItem, OdtParagraph, parse_odt_strict  # Format Factory source reader
from ndjson.ndjson_codec import write_ndjson  # Format Factory target writer


def odt_to_ndjson(
    odt_path: str | Path,
    dest_path: str | Path,
    *,
    include_element_index: bool = True,
    include_heading_level: bool = True,
) -> int:
    """
    Convert an ODT file to NDJSON records using Format Factory writers.

    Each element (paragraph, heading, or list item) in the ODT document becomes
    one NDJSON record with fields: element_index, element_type, text, and
    optionally heading_level for headings.

    Parameters
    ----------
    odt_path:
        Path to the source .odt file.
    dest_path:
        Path to write the target .ndjson file.
    include_element_index:
        If True, adds a 0-based element_index field to each record.
    include_heading_level:
        If True, adds heading_level field to heading records.

    Returns
    -------
    int
        Number of NDJSON records written.
    """
    odt_path = Path(odt_path)
    dest_path = Path(dest_path)

    doc = parse_odt_strict(odt_path)  # Format Factory odt reader
    elements = doc.elements

    records: list[dict] = []
    for idx, elem in enumerate(elements):
        if isinstance(elem, OdtHeading):
            record: dict = {"element_type": "heading", "text": elem.text}
            if include_element_index:
                record["element_index"] = idx
            if include_heading_level:
                record["heading_level"] = elem.level
        elif isinstance(elem, OdtListItem):
            record = {"element_type": "list_item", "text": elem.text}
            if include_element_index:
                record["element_index"] = idx
        else:
            # OdtParagraph (default)
            record = {"element_type": "paragraph", "text": elem.text}
            if include_element_index:
                record["element_index"] = idx

        records.append(record)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    write_ndjson(records, dest_path)  # Format Factory ndjson writer
    return len(records)


__all__ = ["odt_to_ndjson"]
