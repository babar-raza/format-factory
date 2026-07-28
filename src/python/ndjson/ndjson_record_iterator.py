"""
ndjson_record_iterator.py — Spec-shaped record iteration for NDJSON documents.

Authority: NDJSON specification (ndjson.org).
Spec QName: ndjson:record (urn:format:ndjson:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .ndjson_codec import load_ndjson
from .spec.record.record import Record


def ndjson_iter_records(source: "str | Path") -> Iterator[Record]:
    """Yield spec-shaped Record objects for every record in an NDJSON file.

    Args:
        source: Path to a .ndjson / .jsonl file.

    Yields:
        Record instances (spec class: ndjson:record, SAL-NDJSON-00001).

    Raises:
        NdjsonError subclasses on parse failure.
    """
    raw_records = load_ndjson(str(Path(source).resolve()))
    for raw in raw_records:
        if isinstance(raw, dict):
            yield Record(raw)
