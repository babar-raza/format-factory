"""
ndjson_field_iterator.py — Spec-shaped field iteration for NDJSON documents.

Authority: NDJSON — key-value field within a record.
Spec QName: ndjson:field (urn:format:ndjson:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .ndjson_codec import load_ndjson
from .spec.record.field import Field


def ndjson_iter_fields(source: "str | Path") -> Iterator[Field]:
    """Yield spec-shaped Field objects for every field in every record of an NDJSON document.

    Iterates all records in document order, and all fields within each record in key order.

    Args:
        source: Path to an .ndjson Newline Delimited JSON file.

    Yields:
        Field instances (spec class: ndjson:field, SAL-NDJSON-00002).
    """
    raw_records = load_ndjson(str(Path(source).resolve()))
    for record in raw_records:
        if isinstance(record, dict):
            for key, value in record.items():
                yield Field(key, value)
